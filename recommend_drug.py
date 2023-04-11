#!/usr/bin/env python
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import time
import uvicorn
import os
import sys
sys.path.append(".")
sys.path.append("..")
from logger import logger

from datetime import datetime, date, timedelta

from dotenv import load_dotenv
load_dotenv() 

from load_user_data import UserDataLoader
from read_user_data import UserDataReader
from logger import logger

start_day = date.today()
app = FastAPI()

# reference: https://fastapi.tiangolo.com/tutorial/body/
class Input(BaseModel):
    patient_no: str
    test_data: Union[bool, None] = False

@app.post("/recommend_drug/")
async def recommend_drug(input: Input):
    patient_no = input.patient_no
    test_data = input.test_data
    result = {
        "病历档案":{},
        "检查建议":{},
        "前期筛查":{},
        "危险分层":{},
        "合并症干预":[],        
        "药成分方案":[],
        "log": {"patient_no": patient_no, "test_data": test_data},
    }    
    # reference a hack to rotate log file. TimedRotatingFileHandler doesn't work properly in multi-process environment
    # https://stackoverflow.com/questions/13839554/how-to-change-filehandle-with-python-logging-on-the-fly-with-different-classes-a
    global start_day
    cur_day = date.today()
    if cur_day > start_day:
        logger.handlers[0].setStream( open(os.path.join(os.environ.get("LOG_DIR","./log"),"recommend_drug_{}.log".format(cur_day.strftime('%Y-%m-%d'))), 'a') )
        start_day = cur_day
        logger.info("new log file date: %s",cur_day)

    start = time.time()
    if not test_data:
        writer = UserDataLoader()
        write_result = await writer.process_patient_records(patient_no)
        result["log"]["write_result"] = write_result
    reader = UserDataReader(patient_no)
    if not test_data:
        personal = reader.get_one_view()
        result["病历档案"] = personal
    personal = reader.get_exam_recommendation()
    result["检查建议"] = personal
    transfer = reader.get_transfer()
    result["前期筛查"] = transfer
    risk = reader.get_risk()
    result["危险分层"] = risk
    complication = reader.get_complication()
    result["合并症干预"] = complication
    drug = reader.get_drug_recommendation()
    result["药成分方案"] = drug
    end = time.time()

    logger.info("processing_seconds: {}".format(int(end - start)))
    result["log"]["processing_seconds"] = int(end - start)
    logger.info(result)
    return result

if __name__ == "__main__":
    # os.system("cls" if os.name == "nt" else "clear")
    worker_no = int(os.getenv("PYTHON_WORKER_NO"))
    uvicorn.run("recommend_drug:app", workers=worker_no, host="0.0.0.0", port=int(os.getenv("PYTHON_PORT")))


