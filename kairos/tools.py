# File: tools.py
import os
from kairos import debug
from collections import OrderedDict
from configparser import RawConfigParser

log = debug.create_log()


def get_config(current_dir):
    config = RawConfigParser(allow_no_value=True, strict=False, empty_lines_in_values=False, dict_type=ConfigParserMultiValues, converters={"list": ConfigParserMultiValues.getlist})
    config_file = os.path.join(current_dir, "kairos.cfg")
    if os.path.exists(config_file):
        config.read(config_file)
        if config.getboolean('logging', 'clear_on_start_up'):
            debug.clear_log()
        log.setLevel(config.getint('logging', 'level'))
    else:
        log.error("File " + config_file + " does not exist")
        log.exception(FileNotFoundError)
        exit(0)
    return config


class ConfigParserMultiValues(OrderedDict):

    def __setitem__(self, key, value):
        if key in self and isinstance(value, list):
            self[key].extend(value)
        else:
            super().__setitem__(key, value)

    @staticmethod
    def getlist(value):
        value = str(value).strip().replace('\r\n', '\n')
        value = value.replace('\r', '\n')
        result = str(value).split('\n')
        return result


class Switch:
    def __init__(self, value): self._val = value

    def __enter__(self): return self

    # Allows traceback to occur
    def __exit__(self, type, value, traceback): return False

    def __call__(self, *mconds): return self._val in mconds
