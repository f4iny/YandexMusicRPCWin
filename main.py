import asyncio
import multiprocessing

from ymrpc.constants import REPO_URL
from ymrpc.logger import log
from ymrpc.presence import Presence
from ymrpc.settings import get_saves_settings
from ymrpc.token_manager import Init_yaToken
from ymrpc.version_check import GetLastVersion


def main():
    multiprocessing.freeze_support()

    try:
        log("Launched YandexMusicRPC on Linux...")
        GetLastVersion(REPO_URL)

        # Загрузка сохраненных настроек
        get_saves_settings(True)

        # Инициализация токена Яндекс.Музыки
        Init_yaToken(False)

        # Запуск асинхронного цикла Presence
        asyncio.run(Presence.start())

    except KeyboardInterrupt:
        log("Keyboard interrupt received, stopping...")
        Presence.stop()


if __name__ == "__main__":
    main()
