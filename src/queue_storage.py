"""
queue_storage.py
~~~~~~~~~~~~~~~~

Provides interfaces/classes to handle task storage in memory or Redis.
"""

import json
import time
import queue
import redis  # pip install redis
from typing import Optional, List, Dict
from .logger import logger
from .config import settings


class Task:
    """
    Represents a shell-command-based task (no Python code to run).
    """

    def __init__(self, name: str, interval_seconds: int, shell_command: str):
        self.name = name
        self.interval_seconds = interval_seconds
        self.shell_command = shell_command


class TaskQueueInterface:
    """
    Interface for a generic Task queue. Must be implemented by any concrete queue.
    """

    def push(self, task: Task) -> None:
        """
        Pushes a task into the queue.
        """
        raise NotImplementedError

    def pop(self) -> Optional[Task]:
        """
        Pops a task from the queue (or returns None if empty).
        """
        raise NotImplementedError

    def requeue(self, task: Task) -> None:
        """
        Puts the task back for future scheduling (if needed).
        """
        raise NotImplementedError


class MemoryQueue(TaskQueueInterface):
    """
    A simple in-memory queue using Python's queue.Queue.
    """

    def __init__(self) -> None:
        self._queue = queue.Queue()

    def push(self, task: Task) -> None:
        self._queue.put(task)

    def pop(self) -> Optional[Task]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def requeue(self, task: Task) -> None:
        self._queue.put(task)


class RedisQueue(TaskQueueInterface):
    """
    A queue stored in Redis. We use a Redis list to store tasks as JSON.
    """

    def __init__(
        self, redis_key: str = "qzark:tasks", redis_url: str = "redis://localhost:6379/0"
    ) -> None:
        """
        Args:
            redis_key (str): Key under which tasks are stored in Redis.
            redis_url (str): The Redis connection URL.
        """
        self.redis_key = redis_key
        self.r = redis.from_url(redis_url)

    def push(self, task: Task) -> None:
        """
        Push a Task to the end (right) of a Redis list.
        """
        task_data = {
            "name": task.name,
            "interval_seconds": task.interval_seconds,
            "shell_command": task.shell_command,
        }
        self.r.rpush(self.redis_key, json.dumps(task_data))

    def pop(self) -> Optional[Task]:
        """
        Pop from the left of the Redis list (non-blocking).
        If empty, return None.
        """
        task_json = self.r.lpop(self.redis_key)
        if not task_json:
            return None
        data = json.loads(task_json)
        return Task(
            name=data["name"],
            interval_seconds=data["interval_seconds"],
            shell_command=data["shell_command"],
        )

    def requeue(self, task: Task) -> None:
        """
        Reinsert the task at the right end for future scheduling.
        """
        self.push(task)
