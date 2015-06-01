import logging
from logging.config import fileConfig

fileConfig('logging.conf')
logger = logging.getLogger("err")
logger2 = logging.getLogger("report")
logger.error("whattttt")
logger2.error("aaa")
