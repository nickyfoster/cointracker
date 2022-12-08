import collections.abc
import logging
import os
import socket
from datetime import datetime
from json import JSONDecodeError
from logging.handlers import RotatingFileHandler
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


def get_hostname():
    return socket.gethostname()


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


class CustomRotatingFileHandler(RotatingFileHandler):
    def doRollover(self):
        super(CustomRotatingFileHandler, self).doRollover()
        old_log = self.baseFilename + ".1"
        with open(old_log, 'rb') as log:
            now = datetime.now().strftime("%d-%m-%y-%H:%M:%S")
            with gzip.open(self.baseFilename + now + '.gz', 'wb') as comp_log:
                comp_log.writelines(log)
        os.remove(old_log)


def fix_all_loggers():
    is_active = get_config().logging.other_loggers_enabled
    for logger in logging.Logger.manager.loggerDict:
        if logger != 'main' and not is_active:
            logging.getLogger(logger).setLevel(logging.FATAL)


def prepare_coin_data(data: dict):
    res = {}
    n_coins = len(data)
    last_updated = 0
    for coin_name, coin_data in data.items():
        holdings_amount = float(coin_data["amount"])
        price = coin_data["quote"]["USD"]["price"]
        holdings_price = holdings_amount * price
        res[coin_name] = {
            "price": round(price, 4),
            "holdings_amount": round(holdings_amount, 4),
            "holdings_price": round(holdings_price, 2),
            "change_24h": round(coin_data["quote"]["USD"]["percent_change_24h"], 2)
        }
        last_updated += coin_data["last_updated"]

    res["last_updated"] = last_updated / n_coins
    return res
