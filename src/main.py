"""
main.py
~~~~~~~

Entry point for the Qzark application:
1) Reads tasks from `tasks.yaml` (no tasks are hardcoded).
2) Schedules them internally (no external cron).
3) Uses notification settings from `config.py` to send alerts on failure.
4) Implements a queue-based mechanism for task management.
"""

import argparse
import time
import queue
import yaml
import threading
import subprocess
import requests
import smtplib
from typing import Dict, Any, List, Optional

from .logger import logger as logger
from .config import settings  # Settings from config.py


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments, including --timeout and --log-level.
    """
    parser = argparse.ArgumentParser(
        description="Crontab-like task runner written in Python to control HTTP or command invokes."
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
        default=None,  # We handle 'None' in configure_logger, defaulting to INFO if not set
        help="Logging level. Defaults to INFO if not provided. Choose from INFO or DEBUG.",
    )

    return parser.parse_args()


def configure_logger(log_level: Optional[str]) -> None:
    """
    Configures the logger's level. If log_level is provided (INFO or DEBUG),
    set that level. Otherwise, default to INFO.

    Args:
        log_level (Optional[str]): The desired log level from command-line arguments.
    """
    import logging
    import sys

    # If not provided, default to INFO
    effective_level = logging.INFO
    if log_level == "DEBUG":
        effective_level = logging.DEBUG

    logger.setLevel(effective_level)

    # If the logger has no handlers, add a StreamHandler
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Log a message showing what level we ended up with
    logger.debug("Logger configured to level: %s", logging.getLevelName(effective_level))


class NotificationManager:
    """
    Handles sending notifications to Telegram, Discord, or SMTP.
    Configuration is provided by `config.py`.
    """

    def __init__(self) -> None:
        """
        Initializes the NotificationManager using global `settings`
        from config.py.
        """
        self.settings = settings

    def notify_failure(self, task_name: str, error_message: str) -> None:
        """
        Sends a failure notification to any configured channel.

        Args:
            task_name (str): Name of the failing task.
            error_message (str): Error details from the failure.
        """
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
        """
        Sends a message to Telegram if configured.
        """
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
        """
        Sends a message to Discord if configured.
        """
        try:
            resp = requests.post(
                self.settings.discord_webhook_url, json={"content": message}, timeout=10
            )
            resp.raise_for_status()
            logger.info("Discord notification sent.")
        except Exception as exc:
            logger.error("Failed to send Discord notification: %s", exc)

    def _send_email(self, message: str) -> None:
        """
        Sends an email via SMTP if configured.
        """
        try:
            server = self.settings.smtp_server
            port = self.settings.smtp_port or 25
            username = self.settings.smtp_username
            password = self.settings.smtp_password
            from_email = self.settings.smtp_from_email
            to_email = self.settings.smtp_to_email

            smtp_obj = smtplib.SMTP(server, port)
            smtp_obj.starttls()
            if username and password:
                smtp_obj.login(username, password)

            subject = "Qzark Task Failure Notification"
            body = f"Subject: {subject}\n\n{message}"
            smtp_obj.sendmail(from_email, [to_email], body)
            smtp_obj.quit()

            logger.info("SMTP email notification sent.")
        except Exception as exc:
            logger.error("Failed to send SMTP email notification: %s", exc)


class Task:
    """
    Represents a shell-command-based task (no Python code to run).
    """

    def __init__(self, name: str, interval_seconds: int, shell_command: str):
        self.name = name
        self.interval_seconds = interval_seconds
        self.shell_command = shell_command


class TaskManager(threading.Thread):
    """
    Runs tasks in a separate thread, checking intervals.
    Uses a queue-based approach, plus an in-memory cache to track last run times.
    If a task fails (non-zero exit code), a notification is sent.
    """

    def __init__(self, tasks: List[Task], notifier: NotificationManager) -> None:
        super().__init__()
        self.task_queue = queue.Queue()
        self.notifier = notifier
        self.running = True

        # Populate the queue with initial tasks
        for task in tasks:
            self.task_queue.put(task)

        # A simple in-memory "cache" dict to track last-run times by task name
        self.task_cache: Dict[str, float] = {}

    def run(self) -> None:
        logger.info("TaskManager started (queue-based, no external cron).")

        while self.running:
            try:
                task = self.task_queue.get_nowait()
            except queue.Empty:
                time.sleep(1)
                continue

            # Check if the task is due
            last_run = self.task_cache.get(task.name, 0.0)
            now = time.time()
            if (now - last_run) >= task.interval_seconds:
                # It's time to run the task
                self._run_task(task)
                self.task_cache[task.name] = now
            else:
                # Not time yet; put it back to the queue
                pass

            # Reinsert the task to queue for future checks
            self.task_queue.put(task)

            # Sleep a bit to avoid tight loop
            time.sleep(1)

        logger.info("TaskManager stopping.")

    def stop(self) -> None:
        self.running = False

    def _run_task(self, task: Task) -> None:
        logger.info("Running task '%s': %s", task.name, task.shell_command)
        try:
            # Execute the shell command, capturing stdout/stderr
            result = subprocess.run(
                task.shell_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,  # or any suitable default
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


def load_tasks(file_path: str) -> List[Task]:
    """
    Loads tasks from a YAML file and returns them as a list of Task objects.

    Args:
        file_path (str): Path to the tasks YAML file.

    Returns:
        List[Task]: A list of Task objects configured from the file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("Tasks file not found: %s", file_path)
        return []
    except yaml.YAMLError as exc:
        logger.error("Error parsing YAML: %s", exc)
        return []

    tasks_data = data.get("tasks", [])
    tasks_list = []
    for item in tasks_data:
        name = item.get("name")
        interval = item.get("interval_seconds", 60)
        cmd = item.get("shell_command")

        if not name or not cmd:
            logger.warning("Invalid task definition: %s", item)
            continue

        tasks_list.append(Task(name=name, interval_seconds=interval, shell_command=cmd))
    logger.info("Loaded %d tasks from '%s'.", len(tasks_list), file_path)
    return tasks_list


def main() -> None:
    """
    Main entry point. Loads tasks from `tasks.yaml`, starts the TaskManager,
    and runs indefinitely (or until Ctrl+C).
    """
    start_time = time.time()

    # 1) Parse command-line arguments
    args = parse_arguments()

    # 2) Configure logger based on --log-level (if provided), else default INFO
    configure_logger(args.log_level)

    # Determine final timeout from CLI or fallback to settings.timeout
    timeout = args.timeout if args.timeout else settings.timeout
    logger.info("Using timeout: %d seconds", timeout)

    logger.info("Starting Qzark application (queue-based tasks in YAML).")

    # 3) Load tasks from tasks.yaml
    tasks = load_tasks("tasks.yaml")

    # 4) Prepare NotificationManager from config.py
    notifier = NotificationManager()

    # 5) Start TaskManager in its own thread
    task_manager = TaskManager(tasks, notifier)
    task_manager.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Ctrl+C received, stopping TaskManager...")
    finally:
        end_time = time.time()
        time_elapsed = end_time - start_time
        logger.debug("End. Session time: %.4f seconds", time_elapsed)
        task_manager.stop()
        task_manager.join()

    logger.info("Qzark application finished.")


if __name__ == "__main__":
    main()
