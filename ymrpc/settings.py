from .enums import ButtonConfig, LanguageConfig, LogType
from .logger import log
from . import state
from .presence import Presence


def get_saves_settings(fromStart: bool = False):
    state.auto_start_windows = False

    state.button_config = state.config_manager.get_enum_setting(
        "UserSettings", "buttons_settings", ButtonConfig, fallback=ButtonConfig.BOTH
    )
    state.language_config = state.config_manager.get_enum_setting(
        "UserSettings", "language", LanguageConfig, fallback=LanguageConfig.RUSSIAN
    )

    if fromStart:
        log(
            f"Loaded settings: button_config = {state.button_config.name}, "
            f"language_config = {state.language_config.name}",
            LogType.Update_Status,
        )


def convert_to_enum(enum_class, value):
    if isinstance(value, enum_class):
        return value
    value_str = str(value)
    try:
        return enum_class[value_str]
    except KeyError:
        log(f"Invalid type: {value_str}")
        return None


def set_button_config(value):
    value = convert_to_enum(ButtonConfig, value)
    state.config_manager.set_enum_setting("UserSettings", "buttons_settings", value)
    log(f"Setting has been changed : buttons_settings to {value.name}")
    get_saves_settings()
    Presence.need_restart()


def set_language_config(value):
    value = convert_to_enum(LanguageConfig, value)
    state.config_manager.set_enum_setting("UserSettings", "language", value)
    log(f"Setting has been changed : language to {value.name}")
    get_saves_settings()
    Presence.need_restart()
