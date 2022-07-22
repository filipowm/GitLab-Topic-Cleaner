import logger


def against_none(obj, obj_name):
    if obj is None:
        logger.error(f"{obj_name} was not provided and is none.")
        raise RuntimeError()


def against_empty(obj, obj_name):
    if len(obj) == 0:
        logger.error(f"{obj_name} is empty!")
        raise RuntimeError()


def this_or_default(obj, default):
    return default if obj is None else obj
