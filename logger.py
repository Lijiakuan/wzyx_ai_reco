import os
import sys
from dotenv import load_dotenv
load_dotenv() 
import logging
import datetime
import re
from logging.handlers import TimedRotatingFileHandler

# reference: https://towardsdatascience.com/python-logging-saving-logs-to-a-file-sending-logs-to-an-api-75ec5964943f

logFileFormatter = logging.Formatter(
    fmt=f"%(asctime)s %(levelname)s %(process)d (%(relativeCreated)d) %(pathname)s %(funcName)s L%(lineno)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
fileHandler = logging.FileHandler(filename=os.path.join(os.environ.get("LOG_DIR","./log"),"recommend_drug_{}.log".format(datetime.date.today().strftime('%Y-%m-%d'))))
# cur_time_plus = datetime.datetime.now() + datetime.timedelta(seconds=10)
# fileHandler = TimedRotatingFileHandler(os.path.join(os.environ.get("LOG_DIR","./log"),"recommend_drug"), when="midnight", interval=1, backupCount=0)
# fileHandler.namer = lambda name: name + ".log"
# fileHandler.suffix = '%Y-%m-%d.log'
# fileHandler.extMatch = re.compile(r"^\d{4}-\d{3}-\d{2}.log$")

# fileHandler.doRollover()
fileHandler.setFormatter(logFileFormatter)
fileHandler.setLevel(level=os.environ.get("LOGLEVEL", "INFO"))
consoleHandler = logging.StreamHandler(stream=sys.stdout)
consoleHandler.setFormatter(logFileFormatter)
consoleHandler.setLevel(level=os.environ.get("LOGLEVEL", "INFO"))

logger = logging.getLogger(__name__)
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)
logger.setLevel(level=os.environ.get("LOGLEVEL", "INFO"))
