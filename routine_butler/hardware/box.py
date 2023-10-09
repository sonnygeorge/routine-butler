import time

from loguru import logger

from routine_butler.hardware.gpio import GPIO, GPIO_IS_MOCK
from routine_butler.hardware.hx711 import HX711
from routine_butler.utils.logging import BOX_LOG_LVL

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1.
# Call get_weight before and after putting 1000g weight on your sensor.
# Divide difference with grams (1000g) and use it as reference unit.
HX711_REFERENCE_UNIT = 397

HX711_GAIN = 128
HX711_BITS_TO_READ = 24
HX711_DOUT_PIN = 14
HX711_PD_SCK_PIN = 15
LOCK_PIN = 9
UNLOCK_PIN = 10
IS_CLOSED_CIRCUIT_PIN = 12
GREEN_LED_PIN = 20
RED_LED_PIN = 21
DEFAULT_TARGET_GRAMS = 2200
DEFAULT_TOLERANCE_GRAMS = 150
LOCK_WAIT_SECONDS = 3.5

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class Box:
    def __init__(self, target_grams, tolerance_grams):
        self._target_grams = target_grams
        self._tolerance_grams = tolerance_grams
        self._update_tolerance_bounds()
        self.last_weight_measurement = None
        self.hx711 = HX711(
            dout=HX711_DOUT_PIN,
            pd_sck=HX711_PD_SCK_PIN,
            gain=HX711_GAIN,
            bitsToRead=HX711_BITS_TO_READ,
        )
        self.hx711.setReferenceUnit(HX711_REFERENCE_UNIT)

    def _update_tolerance_bounds(self):
        self._allowed_grams_upper_bound = (
            self._target_grams + self._tolerance_grams
        )
        self._allowed_grams_lower_bound = (
            self._target_grams - self._tolerance_grams
        )

    def set_target_grams(self, target_grams: int):
        self._target_grams = target_grams
        self._update_tolerance_bounds()

    def set_tolerance_grams(self, tolerance_grams: int):
        self._tolerance_grams = tolerance_grams
        self._update_tolerance_bounds()

    def zero_scale(self):
        logger.log(BOX_LOG_LVL, "Zeroing scale...")
        if not GPIO_IS_MOCK:
            self.hx711.reset()
            self.hx711.tare()

    def passes_weight_check(self) -> bool:
        if GPIO_IS_MOCK:
            self.last_weight_measurement = self._target_grams
        else:
            self.last_weight_measurement = self.hx711.getWeight()
        msg = f"Scale check: {self._allowed_grams_lower_bound} <= "
        msg += f"{self.last_weight_measurement} <= "
        msg += f"{self._allowed_grams_upper_bound}"
        logger.log(BOX_LOG_LVL, msg)
        return (
            self._allowed_grams_lower_bound
            <= self.last_weight_measurement
            <= self._allowed_grams_upper_bound
        )

    def is_closed(self) -> bool:
        if GPIO_IS_MOCK:
            return True
        GPIO.setup(IS_CLOSED_CIRCUIT_PIN, GPIO.IN)
        is_closed = GPIO.input(IS_CLOSED_CIRCUIT_PIN) == 1
        logger.log(BOX_LOG_LVL, f"Box IS {'' if is_closed else 'NOT '}closed")
        return is_closed

    def lock(self):
        logger.info("Locking box...")
        GPIO.setup(LOCK_PIN, GPIO.OUT)
        GPIO.output(LOCK_PIN, GPIO.LOW)
        time.sleep(LOCK_WAIT_SECONDS)
        GPIO.output(LOCK_PIN, GPIO.HIGH)

    def unlock(self):
        logger.log(BOX_LOG_LVL, "Unlocking box...")
        GPIO.setup(UNLOCK_PIN, GPIO.OUT)
        GPIO.output(UNLOCK_PIN, GPIO.LOW)
        time.sleep(LOCK_WAIT_SECONDS)
        GPIO.output(UNLOCK_PIN, GPIO.HIGH)

    def turn_green_led_on():
        logger.log(BOX_LOG_LVL, "Turning green LED on...")
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.output(GREEN_LED_PIN, GPIO.HIGH)

    def turn_green_led_off():
        logger.log(BOX_LOG_LVL, "Turning green LED off...")
        GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
        GPIO.output(GREEN_LED_PIN, GPIO.LOW)

    def turn_red_led_on():
        logger.log(BOX_LOG_LVL, "Turning red LED on...")
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.output(RED_LED_PIN, GPIO.HIGH)

    def turn_red_led_off():
        logger.log(BOX_LOG_LVL, "Turning red LED off...")
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.output(RED_LED_PIN, GPIO.LOW)


box = Box(DEFAULT_TARGET_GRAMS, DEFAULT_TOLERANCE_GRAMS)
