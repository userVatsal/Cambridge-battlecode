"""Entry point: dispatch draft and gameplay; a failed turn is logged and still yields."""
import cambc

import draft
from bot import Bot


def main():
    bot = Bot()
    while True:
        try:
            if cambc.is_draft():
                draft.play()
            else:
                bot.play_turn()
        except Exception as error:  # never let one bad turn crash the bot
            print(f"goldrush error: {error!r}", flush=True)
        cambc.end_turn()


if __name__ == "__main__":
    main()
