from loguru import logger

from utils import BaseWithPrettyStrMethod


class Configs(BaseWithPrettyStrMethod):
    # example
    content_width = "75%"


configs = Configs()
logger.debug(f"Created configs: {configs}")
