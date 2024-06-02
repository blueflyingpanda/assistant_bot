import json
from telegram import Update, Bot

from main import application, BOT_TOKEN


async def handler(event, context):
    # TODO: test ya cloud integration
    body = json.loads(event['body'])
    print(body)

    bot = Bot(token=BOT_TOKEN)

    update = Update.de_json(body, bot)
    await bot.initialize()
    await application.initialize()
    await application.process_update(update)
    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
