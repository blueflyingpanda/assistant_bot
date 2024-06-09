from conf import BOT_TOKEN
from tg import TgUpdater


def main():
    TgUpdater(BOT_TOKEN).local_run()


if __name__ == '__main__':
    main()
