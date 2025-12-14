#!/usr/bin/env python3
"""
Main entry point for the Video Analytics Telegram Bot
"""

import asyncio
from bot.telegram_bot import main as run_bot


if __name__ == "__main__":
    print("Starting Video Analytics Telegram Bot...")
    asyncio.run(run_bot())

