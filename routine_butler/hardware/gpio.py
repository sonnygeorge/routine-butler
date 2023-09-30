from loguru import logger

try:
    import RPi.GPIO as GPIO

    GPIO_IS_MOCK = False
except Exception as e:  # noqa
    import Mock.GPIO as GPIO

    logger.warning(f"Failed to import RPi.GPIO: {e} - using Mock.GPIO instead")
    GPIO_IS_MOCK = True
