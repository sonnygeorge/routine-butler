from loguru import logger

DATABASE_LOG_LVL = "DB EVENT"
HARDWARE_LOG_LVL = "HW EVENT"
STATE_CHANGE_LOG_LVL = "STT CHNG"

logger.level(DATABASE_LOG_LVL, no=33, color="<magenta>")
logger.level(HARDWARE_LOG_LVL, no=34, color="<yellow>")
logger.level(STATE_CHANGE_LOG_LVL, no=34, color="<blue>")

# add a log file destination
logger.add("routine_butler.log")
