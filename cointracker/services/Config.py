from dataclasses import dataclass
from dataclasses import is_dataclass


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper


@dataclass
class DBConfig:
    host: str
    port: int
    db: int
    password: str
    migrate: bool
    use_fakeredis: bool


@dataclass
class CoinmarketcapApiConfig:
    api_key: str
    sandbox: bool


@dataclass
class TelegramConfig:
    api_key: str


@dataclass
class LoggingConfig:
    root_logging_level: str
    file_logging_level: str
    console_logging_level: str
    other_loggers_enabled: bool


@dataclass
class PreloadData:
    do_preload: bool
    data: dict


@nested_dataclass
class Config:
    db: DBConfig
    coinmarketcap: CoinmarketcapApiConfig
    telegram: TelegramConfig
    logging: LoggingConfig
    preload_data: PreloadData
