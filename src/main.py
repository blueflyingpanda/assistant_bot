from assistant_bot.src.conf import BOT_TOKEN
from assistant_bot.src.tg import TgUpdater


def main():
    TgUpdater(BOT_TOKEN).local_run()


if __name__ == '__main__':
    main()