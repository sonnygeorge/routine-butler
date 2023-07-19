import sys

from loguru import logger

DB_LOG_LVL = "DATABASE"
BOX_LOG_LVL = "BOX"
STATE_LOG_LVL = "STATE"
AUDIO_LOG_LVL = "AUDIO"


FORMAT = (
    "\n 🔍 <bg #3d3d3d>{time:HH:mm:ss.SS | MM/DD} | "
    "{function}:{line} | {level.icon}</bg #3d3d3d>\n  "
    "   └── <level>{level}: {message}</level>\n"
)

logger.configure(
    handlers=[
        dict(sink=sys.stderr, format=FORMAT, level=20),
        dict(sink="app.log", rotation="3 days", retention="12 days", level=0),
    ],
    levels=[
        dict(name=DB_LOG_LVL, no=10, color="<magenta><bold>", icon="💾"),
        dict(name=BOX_LOG_LVL, no=10, color="<green><bold>", icon="📦"),
        dict(name=AUDIO_LOG_LVL, no=10, color="<green><bold>", icon="🔉"),
        dict(name=STATE_LOG_LVL, no=40, color="<cyan><bold>", icon="🌐"),
    ],
)
