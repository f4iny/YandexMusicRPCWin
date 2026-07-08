import multiprocessing
import time  # Добавили для задержки при ошибках сети

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

        # Защита от отсутствия сети/прокси при автозагрузке
        max_retries = 6
        for attempt in range(max_retries):
            try:
                Presence.client = Client(token=state.ya_token).init()

                from .tray import get_account_name, update_account_name

                log(f"Logged in as - {get_account_name()}", LogType.Update_Status)
                if Is_run_by_exe() and state.mainMenu:
                    update_account_name(state.mainMenu, get_account_name())

                break  # Успешно подключились, выходим из цикла попыток
            except Exception as exception:
                error_str = str(exception)
                # Проверяем, связана ли ошибка с DNS или недоступностью хоста
                if (
                    "getaddrinfo failed" in error_str
                    or "Max retries" in error_str
                    or "NameResolutionError" in error_str
                ):
                    log(f"Network error to Yandex API. Retrying in 5s... ({attempt + 1}/{max_retries})", LogType.Error)
                    time.sleep(5)
                    if attempt == max_retries - 1:
                        Presence.client = None
                        Handle_exception(exception)
                else:
                    # Ошибка не сетевая (например, Яндекс отклонил токен), не пытаемся снова
                    Presence.client = None
                    Handle_exception(exception)
                    break
    else:
        Presence.client = None

    if not Presence.client:
        log("Couldn't get the token. Try again.", LogType.Default)
