"""
main.py
~~~~~~~

Entry point for the Qzark-like application:
1) Reads tasks from `tasks.yaml` (or you can store them in Redis).
2) Schedules them internally (no external cron).
3) Uses notification settings from `config.py` to send alerts on failure.
4) Supports a queue-backend that can be memory-based or Redis-based.
"""

import argparse
import time
import threading
import subprocess
import requests
import smtplib
from typing import List, Dict, Any, Optional
import yaml
from src.logger import logger
from src.config import settings
from src.queue_storage import Task, TaskQueueInterface, MemoryQueue, RedisQueue


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments for the Qzark application.
    """
    parser = argparse.ArgumentParser(
        description="Qzark-lke task runner with optional Redis queue storage."
    )
    parser.add_argument(
        "--timeout",
        type=int,
        choices=range(10, 300),
        metavar="[10-300]",
        help="Timeout in seconds. Defaults to 50 seconds. Must be between 10 to 300.",
    )
    parser.add_argument(
        "--log-level",
        choices=["INFO", "DEBUG"],
        default="INFO",
        help="Logging level. Defaults to INFO. Choose from: INFO, DEBUG.",
    )
    parser.add_argument(
        "--queue-backend",
        choices=["memory", "redis"],
        default="memory",
        help="Select queue backend: memory or redis. Defaults to memory.",
    )
    parser.add_argument(
        "--redis-url",
        type=str,
        default="redis://localhost:6379/0",
        help="Redis connection URL, if using --queue-backend=redis.",
    )
    return parser.parse_args()


# ----------------------------------------
# Notification Logic
# ----------------------------------------
class NotificationManager:
    """
    Handles sending notifications to Telegram, Discord, or SMTP.
    """

    def __init__(self) -> None:
        self.settings = settings

    def notify_failure(self, task_name: str, error_message: str) -> None:
        message = f"Task '{task_name}' failed.\nError: {error_message}"
        logger.error("Notifying about failure: %s", message)

        # Telegram
        if self.settings.telegram_bot_token and self.settings.telegram_chat_id:
            self._send_telegram_message(message)

        # Discord
        if self.settings.discord_webhook_url:
            self._send_discord_message(message)

        # SMTP
        if (
            self.settings.smtp_server
            and self.settings.smtp_from_email
            and self.settings.smtp_to_email
        ):
            self._send_email(message)

    def _send_telegram_message(self, message: str) -> None:
        try:
            url = (
                f"https://api.telegram.org/bot{self.settings.telegram_bot_token}"
                f"/sendMessage?chat_id={self.settings.telegram_chat_id}"
                f"&text={message}"
            )
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            logger.info("Telegram notification sent.")
        except Exception as exc:
            logger.error("Failed to send Telegram notification: %s", exc)

    def _send_discord_message(self, message: str) -> None:
        try:
            resp = requests.post(
                self.settings.discord_webhook_url, json={"content": message}, timeout=10
            )
            resp.raise_for_status()
            logger.info("Discord notification sent.")
        except Exception as exc:
            logger.error("Failed to send Discord notification: %s", exc)

    def _send_email(self, message: str) -> None:
        try:
            smtp_obj = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port or 25)
            smtp_obj.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp_obj.login(self.settings.smtp_username, self.settings.smtp_password)

            subject = "Qzark Task Failure Notification"
            body = f"Subject: {subject}\n\n{message}"
            smtp_obj.sendmail(self.settings.smtp_from_email, [self.settings.smtp_to_email], body)
            smtp_obj.quit()
            logger.info("SMTP email notification sent.")
        except Exception as exc:
            logger.error("Failed to send SMTP email notification: %s", exc)


# ----------------------------------------
# TaskManager
# ----------------------------------------
class TaskManager(threading.Thread):
    """
    A manager that pulls tasks from the queue, checks intervals, and runs them.
    If a task fails (non-zero exit code), sends a notification.
    """

    def __init__(self, task_queue: TaskQueueInterface, notifier: NotificationManager) -> None:
        super().__init__()
        self.task_queue = task_queue
        self.notifier = notifier
        self.running = True

        # Cache to store last-run times by task name
        self.task_cache: Dict[str, float] = {}

    def run(self) -> None:
        logger.info("TaskManager started using queue-based approach.")
        while self.running:
            task = self.task_queue.pop()
            if task is None:
                # No tasks in queue; wait a bit
                time.sleep(1)
                continue

            # Check if it's time to run
            last_run = self.task_cache.get(task.name, 0.0)
            now = time.time()
            if (now - last_run) >= task.interval_seconds:
                self._run_task(task)
                self.task_cache[task.name] = now
            else:
                # Not time yet
                pass

            # Always requeue the task for future scheduling
            self.task_queue.requeue(task)
            time.sleep(1)

        logger.info("TaskManager thread stopping.")

    def stop(self) -> None:
        self.running = False

    def _run_task(self, task: Task) -> None:
        logger.info("Running task '%s': %s", task.name, task.shell_command)
        try:
            result = subprocess.run(
                task.shell_command, shell=True, capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip() or "Unknown error"
                logger.error(
                    "Task '%s' failed with code %d: %s", task.name, result.returncode, error_msg
                )
                self.notifier.notify_failure(task.name, error_msg)
            else:
                logger.info("Task '%s' completed successfully.", task.name)
        except Exception as exc:
            logger.error("Error running task '%s': %s", task.name, exc)
            self.notifier.notify_failure(task.name, str(exc))


# ----------------------------------------
# Helper: Load tasks from YAML
# ----------------------------------------
def load_tasks_from_yaml(file_path: str) -> List[Task]:
    """
    Loads tasks from a YAML file into a list of Task objects.

    Args:
        file_path (str): path to tasks.yaml

    Returns:
        List[Task]: all tasks declared in YAML.
    """
    tasks_list = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("tasks.yaml file not found at: %s", file_path)
        return tasks_list
    except Exception as exc:
        logger.error("Error reading tasks.yaml: %s", exc)
        return tasks_list

    raw_tasks = data.get("tasks", [])
    for item in raw_tasks:
        name = item.get("name")
        interval = item.get("interval_seconds", 60)
        cmd = item.get("shell_command")
        if not name or not cmd:
            logger.warning("Invalid task definition: %s", item)
            continue
        tasks_list.append(Task(name, interval, cmd))
    logger.info("Loaded %d tasks from %s", len(tasks_list), file_path)
    return tasks_list


# ----------------------------------------
# Main
# ----------------------------------------
def main() -> None:
    """
    Main entry point for the Qzark application, supporting
    memory or Redis-based queue, user-defined logging level,
    and dynamic tasks from tasks.yaml.
    """
    args = parse_arguments()

    # Fallback to config.py timeout if CLI not given
    final_timeout = args.timeout if args.timeout else (settings.timeout or 50)
    logger.info("Using final timeout: %d seconds", final_timeout)

    # Decide which queue to use
    if args.queue_backend == "redis":
        logger.info("Using RedisQueue at %s", args.redis_url)
        task_queue = RedisQueue(redis_url=args.redis_url)
    else:
        logger.info("Using MemoryQueue in local process memory.")
        task_queue = MemoryQueue()

    # Load tasks from tasks.yaml
    tasks = load_tasks_from_yaml("tasks.yaml")
    # Push them into whichever queue we decided on
    for t in tasks:
        task_queue.push(t)

    notifier = NotificationManager()

    # Start up the TaskManager with our chosen queue
    manager = TaskManager(task_queue, notifier)
    manager.start()

    start_time = time.time()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received; stopping manager.")
    finally:
        manager.stop()
        manager.join()

        end_time = time.time()
        logger.info("Qzark application finished. Elapsed: %.4f seconds", end_time - start_time)


if __name__ == "__main__":
    main()
