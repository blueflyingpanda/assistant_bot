import json

from conf import BOT_TOKEN
from tg import TgUpdater


async def handler(event, context):
    result = await TgUpdater(BOT_TOKEN).cloud_run(event)
    return {
        'statusCode': 200,
        'body': result
    }

