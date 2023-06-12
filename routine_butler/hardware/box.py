import time

from loguru import logger

from routine_butler.hardware.hx711 import HX711
from routine_butler.utils import HW_LOG_LVL

try:
    import RPi.GPIO as GPIO

    MOCK = False
except Exception as e:
    import Mock.GPIO as GPIO

    logger.warning(f"Failed to import RPi.GPIO: {e} - using Mock.GPIO instead")
    MOCK = True

HX711_GAIN = 128
HX711_BITS_TO_READ = 24
HX711_DOUT_PIN = 14
HX711_PD_SCK_PIN = 15
LOCK_PIN = 9
UNLOCK_PIN = 10
IS_CLOSED_CIRCUIT_PIN = 12
GREEN_LED_PIN = 20
RED_LED_PIN = 21
DEFAULT_TARGET_GRAMS = 200
DEFAULT_TOLERANCE_GRAMS = 200
LOCK_WAIT_SECONDS = 3.5

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class Box:
    def __init__(self, target_grams, tolerance_grams):
        self.target_grams = target_grams
        self.tolerance_grams = tolerance_grams
        self.hx711 = HX711(
            dout=HX711_DOUT_PIN,
            pd_sck=HX711_PD_SCK_PIN,
            gain=HX711_GAIN,
            bitsToRead=HX711_BITS_TO_READ,
        )

    def zero_scale(self):
        logger.log(HW_LOG_LVL, "Zeroing scale...")
        if not MOCK:
            self.hx711.tare()

    def passes_weight_check(self) -> bool:
        if MOCK:
            return True
        current_weight_grams = self.hx711.getWeight()
        logger.log(HW_LOG_LVL, f"Read {current_weight_grams} grams on scale")
        return (
            self.target_grams - self.tolerance_grams
            <= current_weight_grams
            <= self.target_grams + self.tolerance_grams
        )

    def is_closed(self) -> bool:
        if MOCK:
            return True
        GPIO.setup(IS_CLOSED_CIRCUIT_PIN, GPIO.IN)
        is_closed = GPIO.input(IS_CLOSED_CIRCUIT_PIN) == 1
        logger.log(HW_LOG_LVL, f"Box IS {'' if is_closed else 'NOT '}closed")
        return is_closed

    def lock(self):
        logger.log(HW_LOG_LVL, "Locking box...")
        GPIO.setup(LOCK_PIN, GPIO.OUT)
        GPIO.output(LOCK_PIN, GPIO.LOW)
        time.sleep(LOCK_WAIT_SECONDS)
        GPIO.output(LOCK_PIN, GPIO.HIGH)

    def unlock(self):
        logger.log(HW_LOG_LVL, "Unlocking box...")
        GPIO.setup(UNLOCK_PIN, GPIO.OUT)
        GPIO.output(UNLOCK_PIN, GPIO.LOW)
        time.sleep(LOCK_WAIT_SECONDS)
        GPIO.output(UNLOCK_PIN, GPIO.HIGH)

    def turn_green_led_on():
        logger.log(HW_LOG_LVL, "Turning green LED on...")
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)

    def turn_green_led_off():
        logger.log(HW_LOG_LVL, "Turning green LED off...")
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    def turn_red_led_on():
        logger.log(HW_LOG_LVL, "Turning red LED on...")
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.output(RED_LED_PIN, GPIO.HIGH)

    def turn_red_led_off():
        logger.log(HW_LOG_LVL, "Turning red LED off...")
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.output(RED_LED_PIN, GPIO.LOW)


box = Box(DEFAULT_TARGET_GRAMS, DEFAULT_TOLERANCE_GRAMS)
