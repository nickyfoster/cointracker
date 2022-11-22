import collections.abc
from json import JSONDecodeError
from pathlib import Path

import yaml

from tracker.DBConnectors.RedisConnector import RedisConnector
from tracker.services.Config import Config


def load_yml(file):
    file = Path(file)
    try:
        with file.open() as f:
            d = yaml.full_load(f)
            if d is None:
                d = dict()
    except (FileNotFoundError, JSONDecodeError):
        d = dict()
    return d


def update_nested_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_nested_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def get_config() -> Config:
    source_config = load_yml(Path(__file__).parent / '..' / 'config.yml')
    local_source_config = load_yml(Path(__file__).parent / '..' / 'config-local.yml')
    _res_config = update_nested_dict(source_config, local_source_config)
    etc_config = load_yml('/etc/cointracker/config.yml')
    res_config = update_nested_dict(_res_config, etc_config)
    config = Config(**res_config)

    return config


def get_db_connector(db_config=get_config().db):
    return RedisConnector(db_config)
