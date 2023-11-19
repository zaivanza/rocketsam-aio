from modules.utils.titles import TITLE, TITLE_COLOR
from runner import main
from termcolor import cprint
import asyncio

if __name__ == "__main__":
    cprint(TITLE, TITLE_COLOR)
    cprint(f'\nsubscribe to us : https://t.me/hodlmodeth\n', TITLE_COLOR)
    asyncio.run(main())

