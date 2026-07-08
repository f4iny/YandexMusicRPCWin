import multiprocessing
import time

from yandex_music import Client

from . import getToken
from .enums import LogType
from .logger import log
from .utils import Blur_string
from . import state
from .windows import Get_IconPath, Is_run_by_exe
from .error_handling import Handle_exception
from .presence import Presence


def Remove_yaToken_From_Memory():
    if state.config_manager.get_setting("Auth", "token") is not None:
        state.config_manager.set_setting("Auth", "token", "")
        log("Old token has been removed from memory.", LogType.Update_Status)
        state.ya_token = str()


def update_token_task(icon_path, queue):
    result = getToken.get_yandex_music_token(icon_path)
    queue.put(result)


def Init_yaToken(forceGet: bool = False):
    token = str()

    if forceGet:
        try:
            Remove_yaToken_From_Memory()
            process = multiprocessing.Process(target=update_token_task, args=(Get_IconPath(), state.result_queue))
            process.start()
            process.join()
            token = state.result_queue.get()
            if token is not None and len(token) > 10:
                state.config_manager.set_setting("Auth", "token", token)
                log(f"Successfully received the token: {Blur_string(token)}", LogType.Update_Status)
        except Exception as exception:
            log(f"Something happened when trying to initialize token: {exception}", LogType.Error)
        finally:
            Presence.need_restart()

    elif state.ya_token:
        token = state.ya_token
        log(f"Loaded token from script: {Blur_string(token)}", LogType.Update_Status)

    else:
        try:
            token = state.config_manager.get_setting("Auth", "token")
            if token:
                log(f"Loaded token: {Blur_string(token)}", LogType.Update_Status)
        except Exception as exception:
            log(f"Something happened when trying to initialize token: {exception}", LogType.Error)

    if token is not None and len(token) > 10:
        state.ya_token = token

        # Бесконечный цикл для выбора действий при отсутствии сети
        while True:
            connected = False
            max_retries = 6

            for attempt in range(max_retries):
                try:
                    Presence.client = Client(token=state.ya_token).init()

                    from .tray import get_account_name, update_account_name

                    log(f"Logged in as - {get_account_name()}", LogType.Update_Status)
                    if Is_run_by_exe() and state.mainMenu:
                        update_account_name(state.mainMenu, get_account_name())

                    connected = True
                    break  # Успешно подключились, выходим из for
                except Exception as exception:
                    error_str = str(exception)
                    if (
                        "getaddrinfo failed" in error_str
                        or "Max retries" in error_str
                        or "NameResolutionError" in error_str
                    ):
                        log(
                            f"Network error to Yandex API. Retrying in 5s... ({attempt + 1}/{max_retries})",
                            LogType.Error,
                        )
                        time.sleep(5)
                    else:
                        # Ошибка не связана с сетью, выходим из авторизации
                        Presence.client = None
                        Handle_exception(exception)
                        return

            if connected:
                break  # Выходим из бесконечного цикла while, всё ок

            # Если за 30 секунд (6 попыток по 5 сек) сеть не появилась — выводим выбор
            print("\n" + "=" * 60)
            print("[YandexMusicRPC] Не удалось связаться с серверами Яндекс Музыки.")
            print("Возможно, сетевой интерфейс, VPN или прокси ещё не успели подняться.")
            print("-" * 60)
            print("1. Пробовать дальше (запустить ожидание ещё на 30 секунд)")
            print("2. Удалить этот токен и создать новую сессию (перезайти в аккаунт)")
            print("=" * 60)

            try:
                choice = input("Выберите вариант (1 или 2, по умолчанию 1): ").strip()
            except Exception:
                choice = "1"

            if choice == "2":
                log("Выбран сброс авторизации. Удаление сохраненного токена...", LogType.Default)
                Remove_yaToken_From_Memory()
                Presence.client = None
                # Рекурсивно вызываем создание новой сессии с окном авторизации
                Init_yaToken(forceGet=True)
                return
            else:
                log("Выбрано продолжение ожидания. Повторный цикл проверки сети...", LogType.Default)
                # Цикл while True уходит на следующую итерацию и снова пробует 6 раз
    else:
        Presence.client = None

    if not Presence.client:
        log("Couldn't get the token. Try again.", LogType.Default)
