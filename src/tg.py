import json

from telegram import Update, Bot
from telegram.ext import ApplicationBuilder

from handlers import HANDLERS, error_handler
from logs import custom_logger


class TgUpdater:

    def __init__(self, token: str):
        if not token:
            raise Exception('Missing bot token!')

        application = ApplicationBuilder().token(token).build()

        application.add_handlers(HANDLERS)
        application.add_error_handler(error_handler)

        self.application = application
        self.bot = Bot(token=token)

    def local_run(self):
        self.application.run_polling()

    async def cloud_run(self, event):
        try:
            body = json.loads(event['body'])
            update = Update.de_json(body, self.bot)
            await self.bot.initialize()
            await self.application.initialize()

            async with self.application:
                await self.application.start()
                await self.application.process_update(update)
                await self.application.stop()

            return 'Success'

        except Exception as exc:
            custom_logger.info(f"Failed to process update with {exc}")
        return 'Failure'