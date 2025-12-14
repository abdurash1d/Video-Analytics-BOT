"""
Telegram Bot for Video Analytics using aiogram
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config.settings import settings
from bot.nlp_processor import NLPProcessor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoAnalyticsBot:
    def __init__(self):
        self.bot = Bot(token=settings.telegram_bot_token)
        self.dp = Dispatcher()
        self.nlp_processor = NLPProcessor()
        self.setup_handlers()

    def setup_handlers(self):
        """Setup message and command handlers"""

        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            """Handle /start command"""
            welcome_text = (
                "Привет! Я бот для аналитики видео. "
                "Задайте вопрос на русском языке о статистике видео, "
                "и я отвечу числом.\n\n"
                "Примеры вопросов:\n"
                "• Сколько всего видео есть в системе?\n"
                "• Сколько видео у креатора с id abc123 вышло с 1 ноября 2025 по 5 ноября 2025?\n"
                "• Сколько видео набрало больше 100 000 просмотров?\n"
                "• На сколько просмотров в сумме выросли все видео 28 ноября 2025?\n"
                "• Сколько разных видео получали новые просмотры 27 ноября 2025?"
            )
            await message.reply(welcome_text)

        @self.dp.message(Command("help"))
        async def help_command(message: types.Message):
            """Handle /help command"""
            help_text = (
                "Я понимаю вопросы на русском языке о статистике видео. "
                "Все ответы - это числа.\n\n"
                "Примеры:\n"
                "• Сколько всего видео?\n"
                "• Сколько видео вышло в ноябре 2025?\n"
                "• На сколько выросли просмотры вчера?"
            )
            await message.reply(help_text)

        @self.dp.message()
        async def handle_text_message(message: types.Message):
            """Handle regular text messages (natural language queries)"""
            user_query = message.text.strip()

            if not user_query:
                await message.reply("Пожалуйста, введите вопрос.")
                return

            # Show typing indicator
            await self.bot.send_chat_action(message.chat.id, "typing")

            try:
                # Process the query
                result = self.nlp_processor.process_query(user_query)

                if result is not None:
                    # Send the numeric result
                    await message.reply(str(result))
                else:
                    # Handle processing failure
                    error_text = (
                        "Извините, не удалось обработать ваш запрос. "
                        "Пожалуйста, уточните вопрос или попробуйте другой формат."
                    )
                    await message.reply(error_text)
                    logger.error(f"Failed to process query: {user_query}")

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await message.reply("Произошла ошибка при обработке запроса. Попробуйте позже.")

    async def start_polling(self):
        """Start the bot with polling"""
        logger.info("Starting bot polling...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Error during polling: {e}")
            raise

    async def shutdown(self):
        """Shutdown the bot gracefully"""
        logger.info("Shutting down bot...")
        await self.bot.session.close()


async def main():
    """Main function to run the bot"""
    bot = VideoAnalyticsBot()
    try:
        await bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
