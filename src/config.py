"""
config.py
~~~~~~~~~

Stores notification settings (e.g., Telegram, Discord, SMTP) using Pydantic.
You can also add other configuration items here if needed.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Holds configuration for various notification channels, used by Qzark to
    send failure alerts when tasks fail.
    """

    # Global Configuration
    timeout: Optional[int] = Field(default=50, description="Timeout in seconds")

    telegram_bot_token: Optional[str] = Field(default=None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(
        default=None, description="Telegram chat ID to send messages to"
    )
    discord_webhook_url: Optional[str] = Field(
        default=None, description="Discord webhook URL for sending messages"
    )
    smtp_server: Optional[str] = Field(default=None, description="SMTP server address")
    smtp_port: Optional[int] = Field(default=None, description="SMTP server port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_from_email: Optional[str] = Field(default=None, description="Sender email address")
    smtp_to_email: Optional[str] = Field(default=None, description="Recipient email address")


# You can load these settings from environment variables or a .env file
# if you want. For simplicity, let's just instantiate them directly here:

settings = Settings()
