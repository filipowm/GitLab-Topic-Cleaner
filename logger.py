import logging

import click

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

global_logger = logging.getLogger("GitLabTopicsCleaner")


def log(msg, level=logging.DEBUG, err=False, color=None):
    if global_logger.isEnabledFor(level):
        if color is not None:
            msg = f"{color}{msg}{NC}"
        click.echo(msg, err=err, color=False if color is None else True)


def debug(msg=None, color=None):
    log(msg, level=logging.DEBUG, color=color)


def info(msg=None, color=None):
    log(msg, level=logging.INFO, color=color)


def warn(msg=None):
    log(msg, level=logging.WARN, color=YELLOW)


def error(msg=None):
    log(msg, level=logging.ERROR, color=RED)
