import dataclasses

import logging


logger = logging.getLogger(__name__)


def log_config(config) -> None:
    assert dataclasses.is_dataclass(config)
    for field in dataclasses.fields(config):
        logger.debug(f'Config: {field.name}: {getattr(config, field.name)}')
