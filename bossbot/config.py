from typing import Dict

from configparser import ConfigParser


def read_config(cfg_file: str):
    config = ConfigParser()
    config.read(cfg_file)
    return config
