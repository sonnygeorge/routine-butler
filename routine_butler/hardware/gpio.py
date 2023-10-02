from loguru import logger

try:
    import RPi.GPIO as GPIO

    GPIO_IS_MOCK = False
except Exception:  # noqa
    import Mock.GPIO as GPIO

    GPIO_IS_MOCK = True

logger.info(f"GPIO_IS_MOCK: {GPIO_IS_MOCK} | GPIO: {GPIO.__name__}")
