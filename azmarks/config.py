import logging
import sys

import yaml

logger = logging.getLogger(__name__)


def load_config():
    """
    Load and parse the configuration from 'config.yaml'.

    :return: The configuration dictionary.
    """
    logger.debug("Loading configuration from 'config.yaml'...")
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)
            logger.debug(f"Configuration loaded: {config}")
            return config
    except FileNotFoundError:
        logger.error("Configuration file 'config.yaml' not found.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing 'config.yaml': {e}")
        sys.exit(1)
