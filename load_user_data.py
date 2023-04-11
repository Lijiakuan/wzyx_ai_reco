from py2neo import Graph,Node,Relationship
from py2neo.matching import *
from neo4j import AsyncGraphDatabase
import pytz
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from datetime import date, datetime
from bson.codec_options import CodecOptions
import os
import sys
import pathlib
import re
import json
from bson import json_util
from bson.son import SON
import pymongo as mongo
from logger import logger
import time
import asyncio
from dotenv import load_dotenv
load_dotenv() 

# reference: https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-represents-a-number-float-or-int
def convertIntOrFloat(s):
    if s.isdigit():
        return int(s)
    elif s.replace('.','',1).isdigit():
        return float(s)
    else:
        return None

def mongo_utc_to_cypher_cst(dt):
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Shanghai")

    # dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S[{}]".format(tz2))
    return dt_str

def mongo_utc_to_datetime_cst(dt):
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Shanghai")

    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    return dt    

# reference: https://pymongo.readthedocs.io/en/stable/examples/datetimes.html
# 不能跟mongo_utc_to_cypher_cst一起用，timezone不能重复转化，会报错
def timezone_aware_collection(collection):
    return collection.with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=pytz.timezone('Asia/Shanghai')))

# reference: https://stackoverflow.com/questions/2217488/age-from-birthdate-in-python
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class UserDataLoader:
    def __init__(self):
        self.g = Graph(os.getenv("GRAPH_URI"), name=os.getenv("GRAPH_DATABASE"), 
                       auth=(os.getenv("GRAPH_USER"),os.getenv("GRAPH_PASSWORD")))
        self.monconn = mongo.MongoClient(os.getenv("MONGODB_URI"))
        self.mondb = self.monconn[os.getenv("MONGODB_DATABASE")]
        
        # load collection的次序有讲究：blood_pressure和查体需要再检查报告之前，因为要算GFR值
        self.collections = [
            'wzyx_lifestyle_history',
            'wzyx_hzbqpg', # 患者病情评估记录
            'wzyx_past_medical_history',
            'wzyx_present_medical_history',
            'wzyx_baseline_treatment',
            'wzyx_xtjl', # 血糖记录
            'wzyx_family_history',
            'wzyx_cardiovascular_event',
            'blood_pressure_collection',
            'wzyx_thxhdbjl', # 糖化血红蛋白记录
            'wzyx_xzjl', # 血脂记录
            'wzyx_physical_exam',
            'wzyx_prescription_record', # 用药记录
            'wzyx_shjcbg', # 生化检查
            'wzyx_thxhdbjcbg', # 糖化血红蛋白
            'wzyx_xdtjcbg', # 心电图
            'wzyx_bcjcbg', # B超图
            'wzyx_xgjcbg', # X光
            'wzyx_ctjcbg', # CT
            'wzyx_mrijcbg', # MRI
            'wzyx_xgzyjcbg', # 血管造影
            'wzyx_ncgjcbg', # 尿常规
            'wzyx_xcgjcbg', # 血常规
            'wzyx_qtjcbg', # 其他
            'wzyx_dtxyjcbg', # 动态血压
            'wzyx_csxdtjcbg', # 超声心动图
            'wzyx_jdmcsjcbg', # 颈动脉超声
            'wzyx_nbdbjcbg', # 尿白蛋白/肌酐
            'wzyx_ydjcbg', # 眼底
        ]
        
        self.exam_report_collections = {
            'wzyx_shjcbg', # 生化检查
            'wzyx_thxhdbjcbg', # 糖化血红蛋白
            'wzyx_xdtjcbg', # 心电图
            'wzyx_bcjcbg', # B超图
            'wzyx_xgjcbg', # X光
            'wzyx_ctjcbg', # CT
            'wzyx_mrijcbg', # MRI
            'wzyx_xgzyjcbg', # 血管造影
            'wzyx_ncgjcbg', # 尿常规
            'wzyx_xcgjcbg', # 血常规
            'wzyx_qtjcbg', # 其他
            'wzyx_dtxyjcbg', # 动态血压
            'wzyx_csxdtjcbg', # 超声心动图
            'wzyx_jdmcsjcbg', # 颈动脉超声
            'wzyx_nbdbjcbg', # 尿白蛋白/肌酐
            'wzyx_ydjcbg', # 眼底
            }

        self.exam_report_tag_name = {
                'wzyx_shjcbg': '生化检查',
                'wzyx_thxhdbjcbg': '糖化血红蛋白',
                'wzyx_xdtjcbg': '心电图',
                'wzyx_bcjcbg': 'B超图',
                'wzyx_xgjcbg': 'X光',
                'wzyx_ctjcbg': 'CT',
                'wzyx_mrijcbg': 'MRI',
                'wzyx_xgzyjcbg': '血管造影',
                'wzyx_xcgjcbg': '血常规',
                'wzyx_ncgjcbg': '尿常规',
                'wzyx_qtjcbg': '其他',
                'wzyx_dtxyjcbg': '动态血压',
                'wzyx_csxdtjcbg': '超声心动图',
                'wzyx_jdmcsjcbg': '颈动脉超声',
                'wzyx_nbdbjcbg': '尿白蛋白/肌酐',
                'wzyx_ydjcbg': '眼底',
            }
        self.exam_report_date_field = {
                'wzyx_shjcbg': 'shjcbg_01',
                'wzyx_thxhdbjcbg': 'thxhdbjcbg_01',
                'wzyx_xdtjcbg': 'xdtjcbg_01',
                'wzyx_bcjcbg': 'bcjcbg_01',
                'wzyx_xgjcbg': 'xgjcbg_01',
                'wzyx_ctjcbg': 'ctjcbg_01',
                'wzyx_mrijcbg': 'mrijcbg_01',
                'wzyx_xgzyjcbg': 'xgzyjcbg_01',
                'wzyx_xcgjcbg': 'xcgjcbg_01',
                'wzyx_ncgjcbg': 'ncgjcbg_01',
                'wzyx_qtjcbg': 'qtjcbg_01',
                'wzyx_dtxyjcbg': 'dtxyjcbg_01',
                'wzyx_csxdtjcbg': 'csxdtjcbg_01',
                'wzyx_jdmcsjcbg': 'jdmcsjcbg_01',
                'wzyx_nbdbjcbg': 'nbdbjcbg_01',
                'wzyx_ydjcbg': 'ydjcbg_01',
                }
        self.exam_report_image_field = {
                'wzyx_shjcbg': 'shjcbg_02',
                'wzyx_thxhdbjcbg': 'thxhdbjcbg_02',
                'wzyx_xdtjcbg': 'xdtjcbg_02',
                'wzyx_bcjcbg': 'bcjcbg_02',
                'wzyx_xgjcbg': 'xgjcbg_02',
                'wzyx_ctjcbg': 'ctjcbg_02',
                'wzyx_mrijcbg': 'mrijcbg_02',
                'wzyx_xgzyjcbg': 'xgzyjcbg_02',
                'wzyx_xcgjcbg': 'xcgjcbg_02',
                'wzyx_ncgjcbg': 'ncgjcbg_02',
                'wzyx_qtjcbg': 'qtjcbg_02',
                'wzyx_dtxyjcbg': 'dtxyjcbg_02',
                'wzyx_csxdtjcbg': 'csxdtjcbg_02',
                'wzyx_jdmcsjcbg': 'jdmcsjcbg_02',
                'wzyx_nbdbjcbg': 'nbdbjcbg_02',
                'wzyx_ydjcbg': 'ydjcbg_02',
            }
        self.exam_report_prefix_field = {
                'wzyx_shjcbg': ['shjcbg_'],
                'wzyx_thxhdbjcbg': ['thxhdbjcbg_'],
                'wzyx_xdtjcbg': ['xdtjcbg_'],
                'wzyx_bcjcbg': ['bcjcbg_'],
                'wzyx_xgjcbg': ['xgjcbg_'],
                'wzyx_ctjcbg': ['ctjcbg_'],
                'wzyx_mrijcbg': ['mrijcbg_'],
                'wzyx_xgzyjcbg': ['xgzyjcbg_'],
                'wzyx_xcgjcbg': ['xcgjcbg_'],
                'wzyx_ncgjcbg': ['ncgjcbg_'],
                'wzyx_qtjcbg': ['qtjcbg_'],
                'wzyx_dtxyjcbg': ['dtxyjcbg_'],
                'wzyx_csxdtjcbg': ['csxdtjcbg_'],
                'wzyx_jdmcsjcbg': ['jdmcsjcbg_'],
                'wzyx_nbdbjcbg': ['nbdbjcbg_'],
                'wzyx_ydjcbg': ['ydjcbg_'],
            }
        self.exam_report_fields = {
                'shjcbg_CR': {"name": '肌酐/血清肌酐', "value": True, "date": True},
                'shjcbg_7': {"name": '总胆固醇', "value": True, "date": True},
                'shjcbg_08': {"name": '高密度脂蛋白胆固醇', "value": True, "date": True},
                'shjcbg_09': {"name": '低密度脂蛋白胆固醇', "value": True, "date": True}, 
                'shjcbg_10': {"name": '尿酸', "value": True, "date": True},
                'shjcbg_11': {"name": '钾', "value": True, "date": True},
                'shjcbg_12': {"name": '钠', "value": True, "date": True},
                'shjcbg_13': {"name": '氯', "value": True, "date": True},
                'shjcbg_14': {"name": '谷丙转氨酶（ALT）', "value": True, "date": True},
                'shjcbg_15': {"name": '谷草转氨酶（AST）', "value": True, "date": True},
                'ncgjcbg_03': {"name": '尿蛋白', "value": True, "date": True},
                'ncgjcbg_04': {"name": '红细胞', "value": True, "date": True},
                'ncgjcbg_05': {"name": '白细胞', "value": True, "date": True},
                'dtxyjcbg_03': {"name": '全程平均血压:收缩压/mmHg', "value": True, "date": True},
                'dtxyjcbg_04': {"name": '全程平均血压:舒张压/mmHg', "value": True, "date": True},
                'dtxyjcbg_05': {"name": '全程平均血压:心率/次/分钟', "value": True, "date": True},
                'dtxyjcbg_06': {"name": '日间平均血压:收缩压/mmHg', "value": True, "date": True},
                'dtxyjcbg_07': {"name": '日间平均血压:舒张压/mmHg', "value": True, "date": True}, 
                'dtxyjcbg_08': {"name": '日间平均血压:心率/次/分钟', "value": True, "date": True}, 
                'dtxyjcbg_09': {"name": '夜间平均血压:收缩压/mmHg', "value": True, "date": True}, 
                'dtxyjcbg_10': {"name": '夜间平均血压:舒张压/mmHg', "value": True, "date": True}, 
                'dtxyjcbg_11': {"name": '夜间平均血压:心率/次/分钟', "value": True, "date": True}, 
                'csxdtjcbg_03': {"name": '左室肥厚', "value": False, "date": True}, 
                'csxdtjcbg_04': {"name": '左房/左室肥大/扩大', "value": False, "date": True}, 
                'csxdtjcbg_05': {"name": 'LVMI', "value": True, "date": True}, 
                'jdmcsjcbg_03': {"name": '动脉粥样斑块', "value": False, "date": True}, 
                'jdmcsjcbg_04': {"name": '动脉粥样斑块长/mm', "value": True, "date": True}, 
                'jdmcsjcbg_05': {"name": '动脉粥样斑块宽/mm', "value": True, "date": True}, 
                'jdmcsjcbg_06': {"name": '左侧颈动脉IMT', "value": True, "date": True}, 
                'ydjcbg_03': {"name": '出血或渗出', "value": False, "date": True}, 
                'ydjcbg_04': {"name": '视乳头水肿', "value": False, "date": True},         
        }


        self.reflection = {
            '恶心呕吐': ['呕吐'],
            '端坐呼吸伴不能平卧': ['不能平卧'],
            '糖尿病': ['2型糖尿病'],
            '冠心病': ['主动脉疾病或外周血管疾病','动脉粥样硬化','心脏并发症'],
            '脑卒中': ['短暂性脑缺血发作','缺血性脑卒中','脑出血','脑血管并发症'],
            '心绞痛': ['心脏并发症'],
            '心肌梗死': ['心脏并发症'],
            '心力衰竭': ['充血性心力衰竭','心脏并发症'],
            '心律失常': ['快速性心律失常','心房颤动','射血分数减少的心力衰竭（HFrEF）','射血分数保留的心力衰竭（HFpEF）','心脏并发症'],
            '冠状动脉血运重建': ['动脉粥样硬化','主动脉疾病或外周血管疾病','心脏并发症'],
            '外周动脉粥样硬化': ['外周动脉粥样硬化','主动脉疾病或外周血管疾病','动脉粥样硬化'],
            '外周血管病变': ['主动脉疾病或外周血管疾病'],
            '单纯收缩期老年高血压': ['老年单纯收缩期高血压'],
            '糖尿病肾病': ['肾病','慢性肾脏疾病','肾脏并发症'],
            '非糖尿病肾病': ['肾病','慢性肾脏疾病','非糖尿病肾病','肾脏并发症'],
            '慢性肾功能不全': ['肾病','慢性肾脏疾病','肾脏并发症'],
            '肾动脉狭窄': ['肾病','慢性肾脏疾病','双侧肾动脉狭窄','肾脏并发症'],
        }
        self.drug_ingredients = {        
            "1": {"drug_name": "ACEI","record_date": "drug_01_prescription_date"},
            "2": {"drug_name": "ARNI（SPC）","record_date": "drug_02_prescription_date"},
            "3": {"drug_name": "ARB","record_date": "drug_03_prescription_date"},
            "4": {"drug_name": "CCB","record_date": "drug_04_prescription_date"},
            "5": {"drug_name": "α/β受体阻滞剂","record_date": "drug_05_prescription_date"},
            "6": {"drug_name": "β受体阻滞剂","record_date": "drug_06_prescription_date"},
            "7": {"drug_name": "利尿剂","record_date": "drug_07_prescription_date"},
            "8": {"drug_name": "噻嗪类利尿剂","record_date": "drug_08_prescription_date"},
            "9": {"drug_name": "螺内酯","record_date": "drug_09_prescription_date"},
            "10": {"drug_name": "袢利尿剂","record_date": "drug_10_prescription_date"},
            "11": {"drug_name": "二氢吡啶类钙通道阻滞剂","record_date": "drug_11_prescription_date"},
            "12": {"drug_name": "非二氢吡啶类钙通道阻滞剂","record_date": "drug_12_prescription_date"},
        }
        
        self.record_count = 0
        self.latest_bp_time = set()
        self.patient_profile = {}
    
    # 这个method不用了，缺乏完整的脏数据处理
    def load_all_records(self):
        start = time.time()
        last_batch_time = start
        self.get_latest_bp_time()
        
        for collection in self.collections:
            # if not collection in ['blood_pressure_collection']: # collection.endswith("bg"): # not collection in ['wzyx_bcjcbg']: 
            #     # wzyx_physical_exam, wzyx_present_medical_history',wzyx_past_medical_history','wzyx_family_history',"wzyx_lifestyle_history"
            #     continue
            with self.monconn.start_session(causal_consistency=True) as session:
            
                for record in self.mondb[collection].find({"patient_no": "HZ_WZYX_6264"}).sort("_id", mongo.ASCENDING):
                    # if need to extract object id properly, but the json structure would look less readable
                    # record = json.loads(json_util.dumps(record))
                    if "isDeleted" in record and record["isDeleted"] == True:
                        continue
                    if "patient_no" not in record:
                        continue
                    # if collection != 'wzyx_shjcbg':
                    #     continue
                    # if record["patient_no"] != "HZ_WZYX_6264":
                    #     continue
                    base_cypher = '''
                            merge (p:Patient {{patient_no: "{}"}})
                            ON CREATE SET p.node_create_time = datetime()
                            ON MATCH SET p.node_update_time = datetime()
                            '''.format(record['patient_no'])
                    cypher = self._process_single_record(collection, record, base_cypher)                                            
                    if cypher == base_cypher:
                        continue
                    cypher += ';'
                    # print(cypher)
                    try:
                        result = self.g.run(cypher).stats()
                        stats = {}
                        for k in result.keys():
                            if not(isinstance(result[k],int) and int(result[k]) == 0):
                                stats[k] = result[k]
                        # print(stats)
                        self.record_count += 1
                        if self.record_count % 100 == 0:
                            current_time = time.time()
                            logger.info("processed {} records. batch processed in {} seconds".format(self.record_count, int(current_time - last_batch_time)))
                            last_batch_time = current_time
                    except:
                        logger.error("cypher execution error: %s",cypher)
                    
        end = time.time()
        logger.info("Total records processed: {}, in {} seconds".format(self.record_count, int(end - start)))

    async def load_all_records_by_patient_no(self):
        start = time.time()
        processed_patient = set()
        
        for collection in self.collections:
            # if not collection in ['blood_pressure_collection']: # collection.endswith("bg"): # not collection in ['wzyx_bcjcbg']: 
            #     # wzyx_physical_exam, wzyx_present_medical_history',wzyx_past_medical_history','wzyx_family_history',"wzyx_lifestyle_history"
            #     continue
            with self.monconn.start_session(causal_consistency=True) as session:            
                for record in self.mondb[collection].find().sort("_id", mongo.ASCENDING):
                    if "isDeleted" in record and record["isDeleted"] == True:
                        continue
                    if "patient_no" not in record:
                        continue
                    # if collection != 'wzyx_shjcbg':
                    #     continue
                    if record["patient_no"] in processed_patient:
                        continue
                    else:
                        processed_patient.add(record["patient_no"])
                        await self.process_patient_records(record["patient_no"])
   
    
    async def process_patient_records(self, patient_no):
        
        cypher_statements = []
        
        def mongo_query(collection):
            result = []
            if collection == 'blood_pressure_collection':
                blood_pressure_latest = None
                sdp_values = []
                dbp_values = []
                last_3_days = set()
                for record in self.mondb[collection].find({"patient_no": patient_no}).sort("bp_get_time", mongo.DESCENDING):
                    if "isDeleted" in record and record["isDeleted"] == True:
                        continue
                    if blood_pressure_latest is None:
                        blood_pressure_latest = record
                    day_value = mongo_utc_to_datetime_cst(record["bp_get_time"]).strftime('%Y-%m-%d')
                    if len(last_3_days) == 3 and day_value not in last_3_days:
                        break
                    else:
                        sdp_values.append(record["sdp"])
                        dbp_values.append(record["dbp"])
                        last_3_days.add(day_value)
                if blood_pressure_latest is not None:
                    blood_pressure_latest["sdp"] = sum(sdp_values) / len(sdp_values)
                    blood_pressure_latest["dbp"] = sum(dbp_values) / len(dbp_values)
                    blood_pressure_latest["last_3_days"] = list(sorted(last_3_days))
                    result.append(blood_pressure_latest)
                # compatible with load all data
                if blood_pressure_latest:
                    self.latest_bp_time.add((blood_pressure_latest["patient_no"],mongo_utc_to_datetime_cst(blood_pressure_latest["bp_get_time"])))
            elif collection == 'wzyx_prescription_record':
                ingredients = {}
                for record in self.mondb[collection].find({"patient_no": patient_no}).sort("evaluation_time", mongo.DESCENDING):
                    if "isDeleted" in record and record["isDeleted"] == True:
                        continue
                    dates = []
                    if "prescription_date" in record and record["prescription_date"]:
                        dates.append(record["prescription_date"])
                    if "evaluation_time" in record and isinstance(record["evaluation_time"], datetime):
                        dates.append(mongo_utc_to_datetime_cst(record["evaluation_time"]).strftime('%Y-%m-%d'))
                    if "start_time" in record and record["start_time"]:
                        dates.append(record["start_time"])
                    if "effective_date" in record and record["effective_date"]:
                        dates.append(record["effective_date"])
                    three_months_ago = date.today() + relativedelta(months=-3)

                    # exclude those records that are more than 3 months ago
                    if len(dates) > 0 and three_months_ago.strftime('%Y-%m-%d') > max(dates):
                        continue
                    if "drug_ingredients" in record and len(record["drug_ingredients"]) > 0:
                        if "prescription_date" in record:
                            record_time = record["prescription_date"]
                        elif "evaluation_time" in record and isinstance(record["evaluation_time"], datetime):
                            record_time = mongo_utc_to_datetime_cst(record["evaluation_time"]).strftime('%Y-%m-%d')
                        else:
                            record_time = mongo_utc_to_datetime_cst(record["createTime"]).strftime('%Y-%m-%d')
                        for ingredient in record["drug_ingredients"]:
                            if ingredient in ingredients:
                                if record_time > ingredients[ingredient]:
                                    ingredients[ingredient] = record_time
                            else:
                                ingredients[ingredient] = record_time
                             
                    result.append({
                            "patient_no": patient_no,
                            "drug_ingredients": ingredients
                        })

            elif collection in self.exam_report_collections:
                images = set()
                create_time = None
                prev_date = None
                record_date = None
                exam_records = []
                
                for record in self.mondb[collection].find({"patient_no": patient_no}).sort(self.exam_report_date_field[collection], mongo.ASCENDING):
                    if "isDeleted" in record and record["isDeleted"] == True:
                        continue
                    if "createTime" not in record:
                        continue
                    record_date = None
                    
                    # if self.exam_report_date_field[collection] in record and isinstance(record[self.exam_report_date_field[collection]], str):
                    #     try:
                    #         mat=re.match('^(\d{4})-(\d{2})-(\d{2})$', record[self.exam_report_date_field[collection]])
                    #         if mat is not None:
                    #             record_date = record[self.exam_report_date_field[collection]]
                    #         else:
                    #             mat=re.match('^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$', record[self.exam_report_date_field[collection]])
                    #             if mat is not None:
                    #                 record_date = mat.group(1) + '-' + mat.group(2) + '-' + mat.group(3)                                    
                    #     except ValueError:
                    #         pass                        
                    if self.exam_report_date_field[collection] in record and record[self.exam_report_date_field[collection]]:
                        record_date = record[self.exam_report_date_field[collection]].strftime("%Y-%m-%d") if isinstance(record[self.exam_report_date_field[collection]], datetime) \
                            else parse(record[self.exam_report_date_field[collection]]).strftime("%Y-%m-%d")
                        
                    if record_date is None:
                        record_date = mongo_utc_to_datetime_cst(record["createTime"]).strftime('%Y-%m-%d')
                    # assert(record_date is not None)
                    match = False
                    for tmp in exam_records:
                        if tmp[self.exam_report_date_field[collection]] == record_date:
                            match = True
                            if self.exam_report_image_field[collection] in record:
                                for image in record[self.exam_report_image_field[collection]]:
                                    tmp[self.exam_report_image_field[collection]].append(image)
                            for k in record.keys():
                                if any(k.startswith(s) for s in self.exam_report_prefix_field[collection]) and k != self.exam_report_date_field[collection] and k != self.exam_report_image_field[collection]:
                                    if record[k] is not None:
                                        tmp[k] = record[k]
                    if match == False:
                        images = []
                        if self.exam_report_image_field[collection] in record:
                            for image in record[self.exam_report_image_field[collection]]:
                                images.append(image)
                        tmp = {
                            "patient_no": patient_no,
                            "createTime": record["createTime"],
                            self.exam_report_date_field[collection]: record_date,
                            self.exam_report_image_field[collection]: list(images)
                        }
                        for k in record.keys():
                            if any(k.startswith(s) for s in self.exam_report_prefix_field[collection]) and k != self.exam_report_date_field[collection] and k != self.exam_report_image_field[collection]:
                                if record[k] is not None:
                                    tmp[k] = record[k]
                        exam_records.append(tmp)
                # combine individual consolidated records into a single exam report record
                exam_records.sort(key=lambda x: x[self.exam_report_date_field[collection]], reverse=True)
                if len(exam_records) > 0:
                    combined = {"patient_no": exam_records[0]["patient_no"], "latest_exam_date": exam_records[0][self.exam_report_date_field[collection]]}
                    for record in exam_records:
                        for k in record.keys():
                            if k != "patient_no" and k != "createTime" and k != self.exam_report_date_field[collection] and k != self.exam_report_image_field[collection]:
                                if k not in combined and record[k] is not None:
                                    combined[k] = (record[k], record[self.exam_report_date_field[collection]])
                    # only a single combined record is created for exam reports
                    result.append(combined)                
            else:
                if collection in self.mondb.list_collection_names():
                    for record in self.mondb[collection].find({"patient_no": patient_no}).sort("createTime", mongo.DESCENDING):
                        if "isDeleted" in record and record["isDeleted"] == True:
                            continue
                        result.append(record)
                else:
                    logger.warning("collection %s not found", collection)
            return result

        with self.monconn.start_session(causal_consistency=True) as session:
            for collection in self.collections:
                for record in mongo_query(collection):
                    base_cypher = '''
                            merge (p:Patient {{patient_no: "{}"}})
                            ON CREATE SET p.node_create_time = datetime()
                            ON MATCH SET p.node_update_time = datetime()
                            '''.format(patient_no)
                    cypher = self._process_single_record(collection, record, base_cypher)                                            
                    if cypher == base_cypher:
                        continue
                    cypher += ';'
                    cypher_statements.append(cypher)

        async def execute_write_cypher(tx, cypher):
            try:
                await tx.run(cypher)
            except:
                logger.error("cypher execution error: %s",cypher)

        async with AsyncGraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("GRAPH_USER"),os.getenv("GRAPH_PASSWORD"))) as driver:
            async with driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
                try:
                    write_cypher = "match (p:Patient {{patient_no: '{}'}}) detach delete p;".format(patient_no)
                    await session.execute_write(execute_write_cypher, write_cypher)
                    
                    for cypher in cypher_statements:
                        await session.execute_write(execute_write_cypher, cypher)
                    
                    # add no drug condition if no baseline_treatment is entered
                    write_cypher = '''
                        MATCH (p:Patient {{ patient_no: "{}" }})-[r:has_prescription]->(t)
                        with count(r) AS cnt
                        where cnt = 0
                        MATCH (p:Patient {{ patient_no: "{}" }})
                        MATCH (wei:Condition {{name: "未服用降压药物"}})
                        WITH p, wei
                        MERGE (p)-[:has_prescription]->(wei);
                        '''.format(patient_no, patient_no)
                    await session.execute_write(execute_write_cypher, write_cypher)

                except Exception as e:
                    logger.error(e)
                    logger.error("cypher execution error: %s",cypher)
                    
                
  
        result = {"patient_no": patient_no}
        logger.info("processing patient: %s", patient_no)
        
        
        
        return result
    

    def _process_single_record(self, collection, record, base_cypher):
        if collection == 'wzyx_lifestyle_history':
            cypher = self.process_lifestyle_history(record, base_cypher)
        elif collection == 'wzyx_family_history':
            cypher = self.process_family_history(record, base_cypher)
        elif collection == 'wzyx_past_medical_history':
            cypher = self.process_past_medical_history(record, base_cypher)
        elif collection == 'wzyx_present_medical_history':
            cypher = self.process_present_medical_history(record, base_cypher)
        elif collection == 'wzyx_physical_exam':
            cypher = self.process_physical_exam(record, base_cypher)
        elif collection == 'wzyx_baseline_treatment':
            cypher = self.process_baseline_treatment(record, base_cypher)
        elif collection == 'wzyx_xtjl': #血糖记录
            cypher = base_cypher
        elif collection == 'wzyx_xzjl': #血脂记录
            cypher = base_cypher
        elif collection == 'wzyx_thxhdbjl': #好像是糖化血红蛋白记录，没有看到CMDB配置，应该没再用
            cypher = base_cypher
        elif collection == 'wzyx_hzbqpg': #患者病情评估，有病情小结及医生提醒
            cypher = base_cypher
        elif collection == 'wzyx_cardiovascular_event': #心血管事件就是随访
            cypher = self.process_follow_up(record, base_cypher)
        elif collection == 'blood_pressure_collection': #血压数据
            cypher = self.process_blood_pressure_record(record, base_cypher)
        elif collection == 'wzyx_prescription_record': #处方记录
            cypher = self.process_prescription_record(record, base_cypher)            
        else:
            cypher = self.process_exam_report(record, base_cypher, collection)
        return cypher

    def get_latest_bp_time(self):
        
        pipeline = [
            # {"$match": { "patient_name": "张立林" }},   
            { "$sort": { "patient_no": 1, "bp_get_time": -1 } },
            {
            "$group":
                {
                "_id": "$patient_no",
                "last_bp_get_time": { "$first": "$bp_get_time" }
                }
            }
        ]
        with self.monconn.start_session(causal_consistency=True) as session:
            res = timezone_aware_collection(self.mondb["blood_pressure_collection"]).aggregate(pipeline, allowDiskUse=True, session=session )
            for record in res:
                self.latest_bp_time.add((record["_id"],record["last_bp_get_time"]))
            logger.info("get_latest_bp_time is done")
        

    def process_lifestyle_history(self, record, cypher):
        if record["smoke_or_not"] or record["drnk_alcohol"] or record["heavy_taste"] or record["sleep_well"] or record["do_regular_exercise"]:        
            # reset all relationships
            cypher += '''
                        with p
                        optional MATCH (p)-[r:has_lifestyle_history]->(:Lifestyle_History)
                        optional MATCH (p)-[r2:has_lifestyle_history]->(:Condition)
                        DELETE r, r2
                        '''

        if record["smoke_or_not"] == '0':
            cypher += '''
                        with p
                        match (smoke:Lifestyle_History {name: "吸烟_经常吸烟"})
                        match (smoke2:Condition {name: "吸烟"})
                        with p, smoke, smoke2
                        merge (p)-[:has_lifestyle_history]->(smoke)
                        merge (p)-[:has_lifestyle_history]->(smoke2)
                        '''
            if record["daily_cigrette"] and convertIntOrFloat(record["daily_cigrette"]) and convertIntOrFloat(record["daily_cigrette"]) > 0:
                cypher += f'set p.daily_cigarettes = {record["daily_cigrette"]} '
            if record["smoke_year"] and convertIntOrFloat(record["smoke_year"]) and convertIntOrFloat(record["smoke_year"]) > 0:
                cypher += f'set p.smoke_year = {record["smoke_year"]} '
        elif record["smoke_or_not"] == '1':
            cypher += '''
                        with p
                        match (smoke:Lifestyle_History {name: "吸烟_偶尔吸烟"})
                        match (smoke2:Condition {name: "吸烟"})
                        with p, smoke, smoke2
                        merge (p)-[:has_lifestyle_history]->(smoke)
                        merge (p)-[:has_lifestyle_history]->(smoke2)
                        '''
            if record["smoke_year"] and convertIntOrFloat(record["smoke_year"]) and convertIntOrFloat(record["smoke_year"]) > 0:
                cypher += f'set p.smoke_year = {record["smoke_year"]} '
        elif record["smoke_or_not"] == '2':
            cypher += '''
                        with p
                        match (smoke:Lifestyle_History {name: "吸烟_被动吸烟"})
                        match (smoke2:Condition {name: "吸烟"})
                        with p, smoke, smoke2
                        merge (p)-[:has_lifestyle_history]->(smoke)
                        merge (p)-[:has_lifestyle_history]->(smoke2)
                        '''
        elif record["smoke_or_not"] == '3':
            cypher += '''
                        with p
                        match (smoke:Lifestyle_History {name: "吸烟_已戒烟"})
                        with p, smoke
                        merge (p)-[:has_lifestyle_history]->(smoke)
                        '''
# create (n:Lifestyle_History {name: "饮酒_经常饮酒", type: "饮酒", option: "经常饮酒"});
# create (n:Lifestyle_History {name: "饮酒_从来不饮酒", type: "饮酒", option: "从来不饮酒"});
# create (n:Lifestyle_History {name: "饮酒_偶尔饮酒", type: "饮酒", option: "偶尔饮酒"});
# create (n:Lifestyle_History {name: "饮酒_已戒酒", type: "饮酒", option: "已戒酒"});

        if record["drnk_alcohol"] in ["0","1","2","3"]:
            if record["drnk_alcohol"] == "0":
                tag_name = "饮酒_经常饮酒"
            elif record["drnk_alcohol"] == "1":
                tag_name = "饮酒_从来不饮酒"
            elif record["drnk_alcohol"] == "2":
                tag_name = "饮酒_偶尔饮酒"
            elif record["drnk_alcohol"] == "3":
                tag_name = "饮酒_已戒酒"
            cypher += '''
                        with p
                        match (alcohol:Lifestyle_History {{name: "{}"}})
                        with p, alcohol
                        merge (p)-[:has_lifestyle_history]->(alcohol)
                        '''.format(tag_name)

# create (n:Lifestyle_History {name: "口味重_否", type: "口味重", option: "否"});
# create (n:Lifestyle_History {name: "口味重_是", type: "口味重", option: "是"});

        if record["heavy_taste"] in ["0","1"]:
            if record["heavy_taste"] == "0":
                tag_name = "口味重_否"
            elif record["heavy_taste"] == "1":
                tag_name = "口味重_是"

            cypher += '''
                        with p
                        match (taste:Lifestyle_History {{name: "{}"}})
                        with p, taste
                        merge (p)-[:has_lifestyle_history]->(taste)
                        '''.format(tag_name)

        
# create (n:Lifestyle_History {name: "睡眠状况_良好", type: "睡眠状况", option: "良好"});
# create (n:Lifestyle_History {name: "睡眠状况_不好", type: "睡眠状况", option: "不好"});
# create (n:Lifestyle_History {name: "睡眠状况_不好_打鼾", type: "睡眠状况_不好_睡眠问题", option: "打鼾"});
# match (head:Lifestyle_History {name: "睡眠状况_不好"}) match (tail:Lifestyle_History {name: "睡眠状况_不好_打鼾"}) with head, tail create (head)-[:multi_select]->(tail);
# create (n:Lifestyle_History {name: "睡眠状况_不好_早醒", type: "睡眠状况_不好_睡眠问题", option: "早醒"});
# match (head:Lifestyle_History {name: "睡眠状况_不好"}) match (tail:Lifestyle_History {name: "睡眠状况_不好_早醒"}) with head, tail create (head)-[:multi_select]->(tail);
# create (n:Lifestyle_History {name: "睡眠状况_不好_入睡困难", type: "睡眠状况_不好_睡眠问题", option: "入睡困难"});
# match (head:Lifestyle_History {name: "睡眠状况_不好"}) match (tail:Lifestyle_History {name: "睡眠状况_不好_入睡困难"}) with head, tail create (head)-[:multi_select]->(tail);
# create (n:Lifestyle_History {name: "睡眠状况_不好_多梦易醒", type: "睡眠状况_不好_睡眠问题", option: "入睡困难"});
# match (head:Lifestyle_History {name: "睡眠状况_不好"}) match (tail:Lifestyle_History {name: "睡眠状况_不好_多梦易醒"}) with head, tail create (head)-[:multi_select]->(tail);

        if record["sleep_well"] in ["0","1"]:
            if record["sleep_well"] == "0":
                tag_name = "睡眠状况_良好"
                cypher += '''
                            with p
                            match (sleep:Lifestyle_History {{name: "{}"}})
                            with p, sleep
                            merge (p)-[:has_lifestyle_history]->(sleep)
                            '''.format(tag_name)
                
            elif record["sleep_well"] == "1":
                tag_name = "睡眠状况_不好"
                cypher += '''
                            with p
                            match (sleep:Lifestyle_History {{name: "{}"}})
                            with p, sleep
                            merge (p)-[:has_lifestyle_history]->(sleep)
                            '''.format(tag_name)
                for i in record["sleep_problem"]:
                    if i == "0":
                        tag_name = "睡眠状况_不好_打鼾"
                    elif i == "1":
                        tag_name = "睡眠状况_不好_早醒"
                    elif i == "2":
                        tag_name = "睡眠状况_不好_入睡困难"
                    elif i == "3":
                        tag_name = "睡眠状况_不好_多梦易醒"
                    cypher += '''
                            with p
                            match (sleep:Lifestyle_History {{name: "{}"}})
                            with p, sleep
                            merge (p)-[:has_lifestyle_history]->(sleep)
                            '''.format(tag_name)
                    
# create (n:Lifestyle_History {name: "经常锻炼_是", type: "经常锻炼", option: "是"});
# create (n:Lifestyle_History {name: "经常锻炼_否", type: "经常锻炼", option: "否"});

        if record["do_regular_exercise"] in ["0","1"]:
            if record["do_regular_exercise"] == "0":
                tag_name = "经常锻炼_是"
            elif record["do_regular_exercise"] == "1":
                tag_name = "经常锻炼_否"

            cypher += '''
                        with p
                        match (exercise:Lifestyle_History {{name: "{}"}})
                        with p, exercise
                        merge (p)-[:has_lifestyle_history]->(exercise)
                        '''.format(tag_name)

        return cypher
        
# create (n:Family_History {name: "高血压"});
# create (n:Family_History {name: "糖尿病"});
# create (n:Family_History {name: "血脂异常"});
# create (n:Family_History {name: "早发心血管病"});

    def process_family_history(self, record, cypher):
        with_record = False
        tag_name = {"hypertension":"高血压家族史", "diabetes":"糖尿病家族史", "dyslipidemia":"血脂异常家族史", "premature_cardiovascular_disease":"早发心血管病家族史"}

        for attribute in ["hypertension", "diabetes", "dyslipidemia", "premature_cardiovascular_disease"]:
            if with_record == False:
                # reset all relationships
                cypher += '''
                            with p
                            optional MATCH (p)-[r:has_family_history]->(:Family_History)
                            optional MATCH (p)-[r2:has_family_history]->(:Condition)
                            DELETE r, r2
                            '''
                with_record = True
                        
            if record[attribute] == "1":
                cypher += '''
                            with p
                            match (f:Family_History {{name: "{}"}})
                            match (dr:Condition {{name: "{}"}})
                            with p, f, dr
                            merge (p)-[:has_family_history]->(f)
                            merge (p)-[:has_family_history]->(dr)
                            '''.format(tag_name[attribute],tag_name[attribute])
        return cypher
    

# match (n:Past_Medical_History) detach delete n;
# create (n:Past_Medical_History {name: "高血压"});
# create (n:Past_Medical_History {name: "糖尿病"});
# create (n:Past_Medical_History {name: "高血脂"});
# create (n:Past_Medical_History {name: "冠心病"});
# create (n:Past_Medical_History {name: "其他系统疾病", properties: ["other_systemic_diseases"], property_comments: ["既往史_其他系统疾病"]});

    def process_past_medical_history(self, record, cypher):

        # reset all relationships
        cypher += '''
                    with p
                    optional MATCH (p)-[r:has_past_medical_history]->(:Past_Medical_History)
                    optional MATCH (p)-[r2:has_past_medical_history]->(:Condition)
                    DELETE r, r2
                    remove p.other_systemic_diseases
                '''

        tag_name = {"have_high_bp_history":"高血压", "have_diabetes_history":"糖尿病", "have_hyperlipidemia_history":"高血脂", 
                        "have_chd_history":"冠心病", "have_stroke_history":"脑卒中", 
                        "hyperuricemia": "血尿","gout_attack": "痛风","gout_attack": "代谢综合征",
                        "have_other_systemic_disease_history":"其他系统疾病"}
        
        def set_node(cypher, name):
            cypher += '''
                        with p
                        match (f:Past_Medical_History {{name: "{}"}})
                        match (d:Condition {{name: "{}"}})
                        with p, f, d
                        merge (p)-[:has_past_medical_history]->(f)
                        merge (p)-[:has_past_medical_history]->(d)
                        '''.format(name, name)
            if name in self.reflection:
                for ref in self.reflection[name]:
                    cypher += '''
                                with p
                                match (f:Past_Medical_History {{name: "{}"}})
                                match (d:Condition {{name: "{}"}})
                                with p, f, d
                                merge (p)-[:has_past_medical_history]->(f)
                                merge (p)-[:has_past_medical_history]->(d)
                                '''.format(ref, ref)
            return cypher
                    
        for attribute in ["have_high_bp_history", "have_diabetes_history", "have_hyperlipidemia_history", 
                          "have_chd_history", "have_stroke_history", "have_other_systemic_disease_history"]:
            
            if record[attribute] == "1":
                cypher = set_node(cypher, tag_name[attribute])
                if attribute == "have_other_systemic_disease_history" and record["other_system_disease_input"] != "":
                    cypher += '''
                                with p
                                set p.other_systemic_diseases = "{}"
                                '''.format(record["other_system_disease_input"])

        if "other_cardiovascular_disease_10" in record:
            tag_name = {"1": "心绞痛", "2": "心肌梗死", "3": "心力衰竭", "4": "快速心律失常", "6": "外周动脉粥样硬化"}
            for id in record["other_cardiovascular_disease_10"]:
                if id in tag_name.keys():
                    cypher = set_node(cypher, tag_name[id])

        if "ophthalmic_diseases" in record:
            tag_name = {"1": "视网膜病变" }
            for id in record["ophthalmic_diseases"]:
                if id in tag_name.keys():
                    cypher = set_node(cypher, tag_name[id])

        if "urinary_system_disease" in record:
            tag_name = {"1": "糖尿病肾病","2": "非糖尿病肾病", "3": "慢性肾脏病", "4": "双侧肾动脉狭窄" }
            for id in record["urinary_system_disease"]:
                if id in tag_name.keys():
                    cypher = set_node(cypher, tag_name[id])

        if "respiratory_disease" in record:
            tag_name = {"1": "哮喘","2":"慢性阻塞性肺病" }
            for id in record["respiratory_disease"]:
                if id in tag_name.keys():
                    cypher = set_node(cypher, tag_name[id])
            
        return cypher

# create (present:Present_Medical_History {name: "头痛", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "头晕", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "心慌", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "胸闷", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "气短", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "失眠", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "手脚麻木", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "恶心呕吐", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});
# create (present:Present_Medical_History {name: "其他", properties: ["present_medical_history_time", "present_medical_history_other"], property_comments: ["现病史_填写时间", "现病史_其他"]});
# create (present:Present_Medical_History {name: "咳嗽", properties: ["present_medical_history_time"], property_comments: ["现病史_填写时间"]});

    def process_present_medical_history(self, record, cypher):
        def set_node(cypher, name):
            cypher += '''
                        with p
                        match (f:Present_Medical_History {{name: "{}"}})
                        match (d:Condition {{name: "{}"}})
                        with p, f, d
                        merge (p)-[:has_present_medical_history]->(f)
                        merge (p)-[:has_present_medical_history]->(d)
                        '''.format(name, name)
            if name in self.reflection:
                for ref in self.reflection[name]:
                    cypher += '''
                            with p
                            match (f:Present_Medical_History {{name: "{}"}})
                            match (d:Condition {{name: "{}"}})
                            with p, f, d
                            merge (p)-[:has_present_medical_history]->(f)
                            merge (p)-[:has_present_medical_history]->(d)
                                '''.format(ref, ref)
            return cypher

        # reset all relationships
        if "present_symptoms" in record or "present_record_time" in record:
            cypher += '''
                        with p
                        optional MATCH (p)-[r:has_present_medical_history]->(:Present_Medical_History)
                        optional MATCH (p)-[r2:has_present_medical_history]->(:Condition)
                        DELETE r, r2
                        remove p.present_medical_history_time, p.present_medical_history_other
                        '''
        if "present_symptoms" in record:
            tag_name = {"0": "头痛", "1": "头晕", "2": "心慌", "3": "胸闷", "4": "气短", "5": "失眠", "6": "手脚麻木", "7": "恶心呕吐", "8": "其他"}
            for id in record["present_symptoms"]:                
                cypher = set_node(cypher, tag_name[id])
                if tag_name[id] == "其他" and record["present_symptom_others"] != "":
                    cypher += '''
                                with p
                                set p.present_medical_history_other = "{}"
                                '''.format(record["present_symptom_others"])
        if "present_syndrome_cd" in record:
            tag_name = {"1": "意识淡漠", "2": "意识丧失", "3": "意识模糊" }
            for id in record["present_syndrome_cd"]:                
                cypher = set_node(cypher, tag_name[id])
        if "present_syndrome_acutesymptom" in record:
            tag_name = {"1": "意识障碍", "2": "言语障碍", "3": "突发言语障碍", "4": "肢体瘫痪", "6": "大汗", "7": "多汗", 
                        "8": "呼吸困难", "9": "持续性胸背部剧烈撕裂样疼痛", "10":"胸闷、胸痛持续时间≥10 min", "11":"端坐呼吸伴不能平卧","12":"全身严重过敏反应",
                        "13": "阵发性血压升高","14": "血压明显波动"}
            node_names = []
            for id in record["present_syndrome_acutesymptom"]:      
                if id == "1":
                    continue # 没有“意识障碍”的字段
                elif id == "10":
                    node_names.append("胸闷")
                    node_names.append("胸痛持续时间>=10min")
                else:
                    node_names.append(tag_name[id])
            for name in node_names:
                cypher = set_node(cypher, name)
        
        if "present_record_time" in record and record["present_record_time"]:
            cypher += '''
                        with p
                        set p.present_medical_history_record_time = Date("{}")
                        with p
                        match (f:Present_Medical_History {{name: "现病史填写时间"}})
                        with p, f
                        merge (p)-[:has_present_medical_history]->(f)
                        '''.format(record["present_record_time"])
        if "onset_time" in record and record["onset_time"]:
            cypher += '''
                        with p
                        set p.present_medical_history_onset_time = "{}"
                        with p
                        match (f:Present_Medical_History {{name: "发病时间"}})
                        with p, f
                        merge (p)-[:has_present_medical_history]->(f)
                        '''.format(record["onset_time"])
        tag_name = {"onset_age":"发病年龄", "disease_duration":"发病时长", 
                    "bp_level_high":"日常血压水平：高压（mmHg）", "bp_level_low":"日常血压水平：低压（mmHg）",
                    "bp_level_pulse":"日常血压水平：心率（次/分钟）"}
        for key in ["onset_age","disease_duration","bp_level_high", "bp_level_low","bp_level_pulse"]:
            if key in record and record[key]:
                cypher += '''
                            with p
                            set p.present_medical_history_{} = {}
                            with p
                            match (f:Present_Medical_History {{name: "{}"}})
                            with p, f
                            merge (p)-[:has_present_medical_history]->(f)
                            '''.format(key, record[key], tag_name[key])

        return cypher

# create (n:Physical_Exam {name: "身高", properties: ["height_cm"], property_comments: ["体查_身高"]});
# create (n:Physical_Exam {name: "体重", properties: ["weight_kg"], property_comments: ["体查_体重"]});
# create (n:Physical_Exam {name: "心率", properties: ["heart_pulse_rate"], property_comments: ["体查_心率"]});
# create (n:Physical_Exam {name: "BMI", properties: ["bmi"], property_comments: ["BMI"]});

    def process_physical_exam(self, record, cypher):
        if record["height_cm"] or record["weight_kg"] or record["heart_pulse_rate"]:
            cypher += '''
                        with p
                        optional MATCH (p)-[r:has_physical_exam]->(:Physical_Exam)
                        optional MATCH (p)-[r2:has_physical_exam]->(:Condition)
                        DELETE r, r2
                        remove p.height_cm, p.weight_kg, p.bmi, p.heart_pulse_rate
                        '''
        if record["height_cm"]:
            cypher += '''
                        with p
                        match (e:Physical_Exam {{name: "身高（厘米）"}})
                        match (d:Condition {{name: "身高（厘米）"}})
                        with p, e, d
                        merge (p)-[:has_physical_exam]->(e)
                        merge (p)-[:has_physical_exam]->(d)
                        with p
                        set p.height_cm = {}
                        '''.format(record["height_cm"])
        if record["weight_kg"]:
            cypher += '''
                        with p
                        match (e:Physical_Exam {{name: "体重（千克）"}})
                        match (d:Condition {{name: "体重（千克）"}})
                        with p, e, d
                        merge (p)-[:has_physical_exam]->(e)
                        merge (p)-[:has_physical_exam]->(d)
                        with p
                        set p.weight_kg = {}
                        '''.format(record["weight_kg"])
            self.patient_profile[record["patient_no"]] = {"gender": record["weight_kg"]}
                        
        if record["height_cm"] and record["height_cm"] > 0 and \
            record["weight_kg"] and record["weight_kg"] > 0:
            bmi = round(record["weight_kg"] / ((record["height_cm"] / 100.0) ** 2),2)
            cypher += '''
                        with p
                        match (e:Physical_Exam {{name: "BMI"}})
                        with p, e
                        merge (p)-[:has_physical_exam]->(e)
                        with p
                        set p.bmi = {}
                        '''.format(bmi)
            if bmi >= 28.0:
                cypher += '''
                            with p
                            match (d:Condition {name: "BMI>=28"})
                            with p, d
                            merge (p)-[:has_physical_exam]->(d)
                            '''
                
        if "heart_pulse_rate" in record and record["heart_pulse_rate"]:
            cypher += '''
                        with p
                        match (e:Physical_Exam {{name: "心率（次/分钟）"}})
                        match (d:Condition {{name: "心率（次/分钟）"}})
                        with p, e, d
                        merge (p)-[:has_physical_exam]->(e)
                        merge (p)-[:has_physical_exam]->(d)
                        with p
                        set p.heart_pulse_rate = {}
                        '''.format(record["heart_pulse_rate"])
            if isinstance(record["heart_pulse_rate"], int) and record["heart_pulse_rate"] > 80:
                cypher += '''
                            with p
                            match (d:Condition {name: "心率>80次/分"})
                            with p, d
                            merge (p)-[:has_physical_exam]->(d)
                            '''
                            
        return cypher

    def process_exam_report(self, record, cypher, collection):
        
        data_conditions = ["血常规","尿常规", "生化检查", "心电图","动态血压监测","超声心动图","颈动脉超声","尿白蛋白/肌酐",
                           "X光", "眼底"]
                
        def set_node(cypher, name):
            cypher += '''
                        with p
                        match (da:Condition {{name: "{}"}})
                        merge (p)-[:has_exam_report]->(da)
                        '''.format(name)
            return cypher

        for key in record.keys():
            if key in ["patient_no","latest_exam_date","createTime"]:
                continue
            if key in self.exam_report_fields.keys():
                cypher += '''
                            with p
                            match (e:Exam_Report {{name: "{}"}})
                            merge (p)-[:has_exam_report]->(e)
                        '''.format(self.exam_report_fields[key]["name"])
                if self.exam_report_fields[key]["value"] or record[key][0] == "1":
                    cypher += '''
                                with p
                                set p.{} = {}                            
                            '''.format(key + "_value", record[key][0])
                    
                    if self.exam_report_fields[key]["date"]:
                        cypher += '''
                                    with p
                                    set p.{} = "{}"                            
                                '''.format(key + "_date", record[key][1])
                    
                if (self.exam_report_fields[key]["name"] == '尿蛋白' and record[key][0] >= 30):
                    cypher = set_node(cypher, "微量蛋白尿>=30mg/24h")
                if (self.exam_report_fields[key]["name"] == '肌酐/血清肌酐'):
                    if record[key][0] > 3:
                        cypher = set_node(cypher, "严重肾功能不全：肌酐>3mg/dl（265umol/L）")
                    GFR = None
                    if record["patient_no"] in self.patient_profile and \
                        "gender" in self.patient_profile[record["patient_no"]] and \
                        "age" in self.patient_profile[record["patient_no"]] and \
                        "weight_kg" in self.patient_profile[record["patient_no"]]:
                        if self.patient_profile[record["patient_no"]]["gender"] == 1:
                           # 男性Ccr（内生肌酐清除率）=(140-年龄)*体重(kg)/72*血肌酐浓度（mg/dl），GFR≈Ccr
                            GFR = (140 - self.patient_profile[record["patient_no"]]["age"]) * \
                                self.patient_profile[record["patient_no"]]["weight_kg"] / 72 * record[key][0]
                        else:
                            # 女性Ccr（内生肌酐清除率）=(140-年龄)*体重(kg)/85*血肌酐浓度（mg/dl），GFR≈Ccr			
                            GFR = (140 - self.patient_profile[record["patient_no"]]["age"]) * \
                                self.patient_profile[record["patient_no"]]["weight_kg"] / 85 * record[key][0]
                    if GFR is not None:
                        if GFR < 60.0:
                            cypher = set_node(cypher, "eGFR<60ml/min/1.73m2")
                        if GFR < 30.0:
                            cypher = set_node(cypher, "肾功能不全：eGFR<30ml/min/1.73m2")
                if (self.exam_report_fields[key]["name"] == '低密度脂蛋白胆固醇'):
                    if record[key][0] >= 4.9:
                        cypher = set_node(cypher, "（LDL-C）>=4.9mmol/L")
                    if record[key][0] >= 3.4:
                        cypher = set_node(cypher, "（LDL-C）>=3.4mmol/L")
                    if record[key][0] >= 2.6:
                        cypher = set_node(cypher, "（LDL-C）>=2.6mmol/L")
                    if record[key][0] >= 1.8:
                        cypher = set_node(cypher, "（LDL-C）>=1.8mmol/L")
                if (self.exam_report_fields[key]["name"] == '高密度脂蛋白胆固醇'):
                    if record[key][0] < 1.04:
                        cypher = set_node(cypher, "（HDL-C）<1.04mmol/L")
                if (self.exam_report_fields[key]["name"] == '总胆固醇'):
                    if record[key][0] >= 7.2:
                        cypher = set_node(cypher, "总胆固醇（TC）>=7.2mmol/L")
                if (self.exam_report_fields[key]["name"] == '钾'):
                    if record[key][0] < 3.5:
                        cypher = set_node(cypher, "电解质异常(血钾<3.5mmol/L)")
                    if record[key][0] > 5.5:
                        cypher = set_node(cypher, "电解质异常(血钾>5.5mmol/L)")

                # not yet handled:
                # "白蛋白/肌酐>=30mg/g"                        
                # "空腹血糖异常（6.1-6.9mmol/L）"
                # "臂踝脉搏波速度>=18m/s"
                # "颈股脉搏波速度>10m/s"
                # "踝/臂指数<=0.9"
                # "心电图示至少两个导联ST段抬高"

        if self.exam_report_tag_name[collection] in data_conditions:
            cypher += '''
                        with p
                        match (da:Condition {{name: "{}"}})
                        merge (p)-[:has_exam_report]->(da)
                        '''.format(self.exam_report_tag_name[collection])
        return cypher

    def process_blood_pressure_record(self, record, cypher):
        if (record["patient_no"],mongo_utc_to_datetime_cst(record["bp_get_time"])) in self.latest_bp_time:

            cypher += '''
                        with p
                        optional MATCH (b:Blood_Pressure_Record) 
                        where b.patient_no = "{}"
                        detach delete b            
                        with p
                        merge (b:Blood_Pressure_Record {{patient_no: "{}"}})
                        on create set b.bp_get_time = datetime("{}"),
                        p.patient_name = "{}", p.patient_phone = "{}", 
                        p.doctor_no = "{}", p.doctor_name = "{}", p.hospital_name = "{}",
                        b.last_3_days = {},
                        b.sdp = {}, b.dbp = {}, b.hr = {}, b.node_create_time = datetime("{}"),
                        b.imei = "{}"
                        with p, b
                        merge (p)-[:has_blood_pressure]->(b)
                        '''.format(
                                record["patient_no"],
                                record["patient_no"],
                                mongo_utc_to_cypher_cst(record["bp_get_time"]),
                                record["patient_name"],record["patient_phone_no"],
                                record["doctor_no"] if "doctor_no" in record else "",
                                record["doctor_name"] if "doctor_name" in record else "",
                                record["hospital_name"] if "hospital_name" in record else "",
                                json.dumps(record["last_3_days"]) if "last_3_days" in record else "[]",
                                record["sdp"], record["dbp"], record["hr"], mongo_utc_to_cypher_cst(record["createTime"]),
                                record["device_serial_no"] if "device_serial_no" in record else "人工输入")

            if record["patient_birthday"]:
                cypher += '''
                            with p
                            set p.date_of_birth = date("{}")
                            '''.format(record["patient_birthday"])
            if record["patient_gender"] in ["0","1"]:
                cypher += '''
                            with p
                            set p.gender = {}
                            '''.format(record["patient_gender"])
                
            cypher += '''
                        with p
                        optional MATCH (p)-[r:has_blood_pressure_range]->(:Condition)
                        delete r                        
                    '''
            if record["patient_birthday"] and record["patient_gender"] in ["0","1"]:                
                birthday = datetime.strptime(record["patient_birthday"], "%Y-%m-%d").date()
                if record["patient_gender"] == "0" and calculate_age(birthday) >= 45:
                    cypher += '''
                            with p
                            match (e:Condition {name: "男>=45岁"})
                            with p, e
                            merge (p)-[:has_basic_info]->(e)
                            '''
                if record["patient_gender"] == "1" and calculate_age(birthday) >= 55:
                    cypher += '''
                            with p
                            match (e:Condition {name: "女>=55岁"})
                            with p, e
                            merge (p)-[:has_basic_info]->(e)
                            '''
                self.patient_profile[record["patient_no"]] = {"gender": record["patient_gender"], "age": calculate_age(birthday)}
                    
            if record["sdp"] >= 130:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压>=130mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''

            if record["sdp"] >= 140:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压>=140mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["sdp"] >= 160:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压>=160mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["sdp"] < 140:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压<140mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["sdp"] < 160:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压<160mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["dbp"] >= 80:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "舒张压>=80mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["dbp"] >= 90:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "舒张压>=90mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["dbp"] >= 100:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "舒张压>=100mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["dbp"] < 90:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "舒张压<90mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''
            if record["dbp"] < 100:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "舒张压<100mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''

            if record["sdp"] >= 140 or record["dbp"] >= 90:
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压>=140mmHg和/或舒张压>=90mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''

            if ((record["sdp"] >= 130 and record["sdp"] <= 139 and record["dbp"] <= 90) or 
                (record["sdp"] <= 130 and record["dbp"] >= 80 and record["dbp"] <= 89)):
                cypher += '''
                            with p
                            match (bpr:Condition {name: "收缩压=130-139mmHg和/或舒张压=80-89mmHg"})
                            merge (p)-[:has_blood_pressure_range]->(bpr)
                        '''

        return cypher

    def process_prescription_record(self, record, cypher):
        tags = []
        additional_tags = []

        def set_drug_node(cypher, name, record_date_field, record_date):
            cypher += '''
                        with p
                        match (d:Drug {{name: "{}"}})
                        merge (p)-[:has_prescription]->(d)
                        with p
                        set p.{} = "{}"
                        '''.format(name, record_date_field, record_date)
            return cypher
        def set_condition_node(cypher, name):
            cypher += '''
                        with p
                        match (da:Condition {{name: "{}"}})
                        merge (p)-[:has_prescription]->(da)
                        '''.format(name)
            return cypher
        
        for key in record["drug_ingredients"].keys():
            if key in self.drug_ingredients.keys():
                tags.append("服用"+self.drug_ingredients[key]["drug_name"])
        if len(tags) > 1 and "服用ACEI" not in tags:
            additional_tags.append("服用非ACEI类药物")
        if len(tags) > 1 and "服用ARB" not in tags:
            additional_tags.append("服用非ARB类药物")
        if len(tags) > 1 and "服用CCB" not in tags:
            additional_tags.append("服用非CCB类药物")
        if len(tags) > 1 and "服用ARNI（SPC）" not in tags:
            additional_tags.append("服用非ARNI类药物")
        if len(tags) > 2 and not ("服用ACEI" in tags or "服用ARB" in tags):
            additional_tags.append("服用非ACEI/ARB类药物")
        if len(tags) > 1 and "服用α/β受体阻滞剂" not in tags:
            additional_tags.append("服用非α/β受体阻滞剂类药物")
        if len(tags) > 1 and "服用β受体阻滞剂" not in tags:
            additional_tags.append("服用非β受体阻滞剂类药物")

        if len(tags) > 0:
            with_diuretic_drug = False
            without_diuretic_drug = True
            for tag in tags:
                if "利尿剂" in tag:
                    with_diuretic_drug = True
                    without_diuretic_drug = False
            if with_diuretic_drug:
                additional_tags.append("服用利尿剂类药物")
            if with_diuretic_drug == False:
                additional_tags.append("未服用利尿剂类药物")
            if len(tags) > 1 and without_diuretic_drug:
                additional_tags.append("服用非利尿剂类药物")
            if len(tags) > 1 and "服用噻嗪类利尿剂" not in tags:
                additional_tags.append("服用非噻嗪类利尿剂类药物")
        
        if len(tags) == 3:
            additional_tags.append("坚持服用3种降压药物")
        if len(tags) == 2:
            additional_tags.append("坚持服用2种降压药物")
        if len(tags) == 1:
            additional_tags.append("坚持服用1种降压药物")
        if len(tags) > 0:
            additional_tags.append("服用降压药物")
            
        for key in record["drug_ingredients"].keys():
            cypher = set_drug_node(cypher, self.drug_ingredients[key]["drug_name"], self.drug_ingredients[key]["record_date"], record["drug_ingredients"][key])            
        for tag in tags:
            cypher = set_condition_node(cypher, tag)
        for tag in additional_tags:
            cypher = set_condition_node(cypher, tag)        

        return cypher
    
    def process_follow_up(self, record, cypher):
        return cypher

    def process_baseline_treatment(self, record, cypher):
        return cypher


async def main():
    handler = UserDataLoader()
    await handler.load_all_records_by_patient_no()
if __name__ == '__main__':
    asyncio.run(main())
