#!/usr/bin/env python3
"""
Setup script for the Video Analytics Telegram Bot
"""

import os
import sys
from pathlib import Path


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return

    print("Creating .env file...")

    # Get user input for tokens
    telegram_token = input("Enter your Telegram Bot Token: ").strip()
    openai_key = input("Enter your OpenAI API Key: ").strip()

    if not telegram_token or not openai_key:
        print("❌ Both tokens are required")
        sys.exit(1)

    env_content = f"""# Telegram Bot Token
TELEGRAM_BOT_TOKEN={telegram_token}

# OpenAI API Key
OPENAI_API_KEY={openai_key}

# Database URL (default for docker-compose)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/video_analytics
"""

    with open(env_path, 'w') as f:
        f.write(env_content)

    print("✅ .env file created successfully")


def setup_database():
    """Setup database schema"""
    print("Setting up database...")
    os.system("python scripts/migrate.py")


def import_data():
    """Import video data"""
    data_file = "data/videos.json"
    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return

    print("Importing video data...")
    os.system(f"python scripts/import_data.py {data_file}")


def main():
    """Main setup function"""
    print("🚀 Video Analytics Bot Setup")
    print("=" * 40)

    # Create .env file
    create_env_file()

    # Setup database
    setup_database()

    # Import data
    import_data()

    print("\n✅ Setup completed!")
    print("\nTo run the bot:")
    print("  docker-compose up --build")
    print("\nOr locally:")
    print("  python main.py")


if __name__ == "__main__":
    main()

