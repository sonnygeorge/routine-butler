from loguru import logger

try:

    GPIO_IS_MOCK = False
except Exception as e:  # noqa

    logger.warning(f"Failed to import RPi.GPIO: {e} - using Mock.GPIO instead")
    GPIO_IS_MOCK = True
