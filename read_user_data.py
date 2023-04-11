from neo4j import GraphDatabase
from logger import logger
import os
import sys
import json
import copy
from datetime import date, datetime
from dotenv import load_dotenv
load_dotenv()


# reference: https://stackoverflow.com/questions/2217488/age-from-birthdate-in-python
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

class UserDataReader:
    def __init__(self, patient_no):
        self.patient_no = patient_no
        self.driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("GRAPH_USER"),os.getenv("GRAPH_PASSWORD")))
    def get_one_view(self):

        tag = {
            "Blood_Pressure_Record": "血压记录",
            "Drug": "用药记录",
            "Past_Medical_History": "既往史",
            "Present_Medical_History": "现病史",
            "Physical_Exam": "查体",
            "Lifestyle_History": "生活习惯",
            "Family_History": "家族史",
            "Exam_Report": "检查报告",                        
        }

        result = {
            "基本信息": [],
            "血压记录": [],
            "既往史": [],
            "现病史": [],
            "查体": [],
            "生活习惯": [],
            "家族史": [],
            "检查报告": [],
            "用药记录": [],
        }
        
        def get_first_level_nodes(tx):        
            query = f"""
            MATCH (patient:Patient {{patient_no: '{self.patient_no}'}})
            OPTIONAL MATCH (patient)-->(a)
            WHERE NOT 'Condition' IN labels(a)
            OPTIONAL MATCH (patient)-->(c:Condition)
            WHERE c.type IN ["baseline_treatment", "blood_pressure", "past_medical_history", "present_medical_history",
            "physical_exam", "lifestyle_history", "family_history", "exam_report", "basic_info"]
            WITH patient, a, c
            ORDER BY id(a), id(c)
            RETURN patient, collect(distinct a) AS attributes, collect(distinct c) AS conditions
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            if len(nodes) == 0:
                return {}, [],[]
            else:
                return nodes[0][0], nodes[0][1], nodes[0][2]

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            patient, attributes, conditions = session.execute_read(get_first_level_nodes)
            if "patient_no" in patient:
                result["基本信息"].append("患者编号：" + patient["patient_no"])
            if "patient_name" in patient:
                result["基本信息"].append("患者姓名：" + patient["patient_name"])
            if "patient_phone" in patient:
                result["基本信息"].append("手机号码：" + patient["patient_phone"])
            if "gender" in patient:
                result["基本信息"].append("性别：" + ("男" if patient["gender"] == 1 else "女"))
            if "date_of_birth" in patient:
                result["基本信息"].append("年龄：" + str(calculate_age(patient["date_of_birth"])))
                    
            for n in attributes:
                # ignore the reflection node
                if "reflection" in n:
                    continue
                label, = n.labels # this is how to get the first element of a frozen set
                category = tag[label]
                if label == "Blood_Pressure_Record":
                    if "sdp" in n:
                        result[category].append("平均收缩压："+str(round(n["sdp"])))
                    if "dbp" in n:
                        result[category].append("平均舒张压："+str(round(n["dbp"])))
                    if "hr" in n:
                        result[category].append("平均心率："+str(round(n["hr"])))
                    if "last_3_days" in n and len(n["last_3_days"]) > 0:
                        result[category].append("为以下日期家庭自测血压平均值："+", ".join(n["last_3_days"]))
                    
                else:
                    category = tag[label]
                    row = ""
                    row += n["name"].replace("_",": ")
                    first = True
                    if "properties" in n:
                        for i, value in enumerate(n["properties"]):
                            if value in patient:
                                if first:
                                    row += ": "
                                else:
                                    row += "，"
                                if "property_comments" in n:
                                    if n["property_comments"][i] == n["name"]:
                                        row += str(patient[value])
                                    else:
                                        row += n["property_comments"][i] + ": " + str(patient[value])                
                                first = False
                    result[category].append(row)
            # ignore the condition nodes
            # for n in conditions:
            #     category = condition_type[n["type"]]
            #     result[category].append(n["name"])

 
        return result
    
    def get_exam_recommendation(self):
        result = {
            "病史评估": [],
            "体格检查": [],
            "辅助检验建议": [],
            "可选辅助检查": [],
        }
        def get_examination_nodes(tx):        
            query = f"""
                MATCH (e:Exam_Recommendation {{ name: '高血压评估检查建议' }})-[:requires]->(require_con)
                MATCH (e:Exam_Recommendation {{ name: '高血压评估检查建议' }})-[:recommends]->(recommend_con)
                MATCH (e:Exam_Recommendation {{ name: '高血压评估检查建议' }})-[:suggests]->(suggest_con)
                MATCH (p:Patient {{ patient_no: '{self.patient_no}' }})
                WITH p, collect( DISTINCT require_con) AS require_cons, suggest_con, recommend_con
                WHERE any(x IN require_cons
                WHERE (p)-[*]->(x))
                WITH p, recommend_con, suggest_con
                WHERE NOT exists( (p)-[]->(recommend_con)) AND NOT exists ((p)-[]->(suggest_con))
                WITH recommend_con, suggest_con
                 ORDER BY id(recommend_con), id(suggest_con)
                RETURN collect( DISTINCT recommend_con) AS recommend, collect( DISTINCT suggest_con) AS suggest;
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            return nodes[0][0], nodes[0][1]

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            recommend_exams, suggest_exams = session.execute_read(get_examination_nodes)
            
            for n in recommend_exams:
                if n["type"] == "physical_exam":
                    result["体格检查"].append(n["name"])
                elif n["type"] == "exam_report":
                    result["辅助检验建议"].append(n["name"])
                else:
                    result["病史评估"].append(n["name"])
            for n in suggest_exams:
                result["可选辅助检查"].append(n["name"])
        return result

    def get_transfer(self):
        result = {
            "转诊建议": "无需转诊",
            "转诊原因": [],
        }
        def get_transfer_nodes(tx):        
            query = f"""
                MATCH (rules:Screening_Rule)
                UNWIND rules AS rule
                MATCH (rule)-[*]->(r_condition:Condition)
                WITH rule, collect(r_condition) AS rule_conditions
                MATCH (patient:Patient {{ patient_no: '{self.patient_no}' }})
                WHERE all(x IN rule_conditions
                WHERE (patient)-[*]->(x))
                MATCH (c1:Condition)<-[*]-(rule)-[*]->(rec1:Screening_Recommendation)
                with rec1, c1
                order by id(c1)
                RETURN rec1, collect( DISTINCT c1)
                ORDER BY rec1.name
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            if len(nodes) == 0:
                return False, [],[]
            else:
                return nodes[0][0]["name"] == "急救车转诊", nodes[0][0], nodes[0][1]

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            transfer_status, transfer_recommendation, transfer_reasons = session.execute_read(get_transfer_nodes)
            
            if transfer_status:
                result["转诊建议"] = transfer_recommendation["name"]
                for n in transfer_reasons:
                    result["转诊原因"].append(n["name"])
        return result

    def get_risk(self):
        result = {
            "危险分层": "非高危",
            "血压范围": [],
            "心血管危险因素": [],
            "临床合并症": [],
            "靶器官损害": [],
        }
        def get_risk_nodes(tx):        
            query = f"""
                MATCH (risk:Condition {{ name: "高危" }})
                MATCH (patient:Patient {{ patient_no: '{self.patient_no}' }})
                OPTIONAL MATCH (patient)-->(full_condition_node)<-[:has_full_condition]-(risk)
                OPTIONAL MATCH (patient)-->(additional_condition_node)<-[:has_condition_with_additional_risks]-(risk)
                OPTIONAL MATCH (patient)-->(any_3_cardio_condition_node)<-[:bp130_80_and_any_3_cardio_risks]-(risk)
                OPTIONAL MATCH (patient)-->(any_1_complication_condition_node)<-[:bp130_80_and_any_1_complication_risk]-(risk)
                OPTIONAL MATCH (patient)-->(any_1_target_organ_condition_node)<-[:bp130_80_and_any_1_target_organ_risk]-(risk)
                WITH patient, risk, full_condition_node, additional_condition_node, any_3_cardio_condition_node, any_1_complication_condition_node, any_1_target_organ_condition_node
                ORDER BY id(full_condition_node), id(additional_condition_node), id(any_3_cardio_condition_node), id(any_1_complication_condition_node), id(any_1_target_organ_condition_node)
                WITH patient, risk, count( DISTINCT full_condition_node) AS full_condition_count, collect( DISTINCT full_condition_node) AS full_conditions,
                count( DISTINCT additional_condition_node) AS additional_condition_count, collect( DISTINCT additional_condition_node) AS additional_conditions,
                count( DISTINCT any_3_cardio_condition_node) AS any_3_cardio_condition_count, collect( DISTINCT any_3_cardio_condition_node) AS any_3_cardio_conditions,
                count( DISTINCT any_1_complication_condition_node) AS any_1_complication_condition_count, collect( DISTINCT any_1_complication_condition_node) AS any_1_complication_conditions,
                count( DISTINCT any_1_target_organ_condition_node) AS any_1_target_organ_condition_count, collect( DISTINCT any_1_target_organ_condition_node) AS any_1_target_organ_conditions
                WHERE full_condition_count > 0 OR (
                additional_condition_count > 0 AND (any_3_cardio_condition_count >= 3 OR
                any_1_complication_condition_count >= 1 OR
                any_1_target_organ_condition_count >= 1))
                MERGE (patient)-[:has_hypertension_risk_level]->(risk)
                RETURN full_conditions,
                additional_conditions,
                any_3_cardio_conditions,
                any_1_complication_conditions,
                any_1_target_organ_conditions
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            if len(nodes) == 0:
                return False, [],[],[],[],[]
            else:
                return True, nodes[0][0], nodes[0][1],nodes[0][2], nodes[0][3], nodes[0][4]

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            # 注意这有可能要执行merge，所以是write
            high_risk_status, full_conditions, additional_conditions, any_3_cardio_conditions, any_1_complication_conditions, any_1_target_organ_conditions = session.execute_write(get_risk_nodes)
            
            if high_risk_status:
                result["危险分层"] = "高危"
                for n in full_conditions:
                    result["血压范围"].append(n["name"])
                if len(full_conditions) == 0:
                    for n in additional_conditions:
                        result["血压范围"].append(n["name"])
                for n in any_3_cardio_conditions:
                    result["心血管危险因素"].append(n["name"])
                for n in any_1_complication_conditions:
                    result["临床合并症"].append(n["name"])
                for n in any_1_target_organ_conditions:
                    result["靶器官损害"].append(n["name"])
        return result

    def get_complication(self):
        result = []
        result_record_template = {
            "合并症干预推荐规则编号":"",
            "合并症干预药品推荐":"",
            "合并症干预推荐依据": [],
            "合并症干预推荐文献": "",            
            "合并症干预推荐参考": "",
        }
        def get_complication_nodes(tx):
            query = f"""
                MATCH (rules:Complication_Rule)
                UNWIND rules AS rule
                MATCH (rule)-[*]->(r_condition:Condition)
                WITH rule, r_condition
                ORDER BY id(rule), id(r_condition)
                WITH rule, collect(r_condition) AS rule_conditions
                MATCH (patient:Patient {{ patient_no: '{self.patient_no}' }})
                WHERE all(x IN rule_conditions
                WHERE (patient)-[*]->(x))
                MATCH (rule)-[*]->(drug:Drug)
                RETURN rule, drug, rule_conditions
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            return nodes

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            nodes = session.execute_read(get_complication_nodes)
            for node in nodes:
                result_record = copy.deepcopy(result_record_template)                
                result_record["合并症干预推荐规则编号"] = node[0]["rule_no"]
                result_record["合并症干预药品推荐"] = node[1]["name"]
                for n in node[2]:
                    result_record["合并症干预推荐依据"].append(n["name"])
                # remove all newline characters
                result_record["合并症干预推荐文献"] = node[0]["reference"].replace('\n', ' ').replace('\r', '') if node[0]["reference"] is not None else None
                result_record["合并症干预推荐参考"] = node[0]["reference2"].replace('\n', ' ').replace('\r', '') if node[0]["reference2"] is not None else None
                result.append(result_record)        
        return result

    def get_drug_recommendation(self):
        result = []
        result_record_template = {
            "用药推荐规则编号":"",
            "药成分推荐":[],
            "用药推荐依据": [],
            "用药推荐文献": "",
            "用药禁忌":[],
            "不良反应":[]            
        }
        def get_drug_nodes(tx):

            query = f"""
                MATCH (rules:Drug_Rule)
                UNWIND rules AS rule
                MATCH (rule)-[r*]->(r_condition:Condition)
                WHERE all(x IN r
                WHERE x.type is null OR x.type <> "hypertension_risk_level")
                WITH rule, r_condition
                ORDER BY id(rule), id(r_condition)
                WITH rule, collect(r_condition) AS rule_conditions
                MATCH (patient:Patient {{ patient_no: '{self.patient_no}' }})
                WHERE all(x IN rule_conditions
                WHERE (patient)-[*]->(x))
                MATCH (rule)-[*]->(drug:Drug)
                WITH patient, rule, rule_conditions, drug
                OPTIONAL MATCH (con_condition:Condition)<-[:with_absolute_contraindication|with_relative_contraindication]-(con_rule:Contraindication_Rule)-[:recommend_drug]->(drug)
                OPTIONAL MATCH (con_rule)-[:with_side_effect]->(side_condition:Condition)
                WITH patient, rule, rule_conditions, drug, con_rule, con_condition, side_condition
                ORDER BY id(patient), id(rule), rule_conditions, id(drug), id(con_rule), id(con_condition), id(side_condition)
                WITH patient, rule, rule_conditions, collect( DISTINCT drug) AS drugs, collect( DISTINCT con_rule) AS con_rules, collect( DISTINCT con_condition) AS con_conditions, collect( DISTINCT side_condition) AS side_conditions
                 ORDER BY rule.sort_key asc, rule.rule_no desc
                WHERE none(x IN con_conditions
                WHERE (patient)-[*]->(x))
                RETURN rule, drugs, rule_conditions, con_conditions, side_conditions;
            """
            result = tx.run(query)
            nodes = [record.values() for record in result]
            return nodes

        with self.driver.session(database=os.getenv("GRAPH_DATABASE")) as session:
            nodes = session.execute_read(get_drug_nodes)
            for node in nodes:
                result_record = copy.deepcopy(result_record_template)                
                result_record["用药推荐规则编号"] = node[0]["rule_no"]
                for n in node[1]:
                    result_record["药成分推荐"].append(n["name"])
                for n in node[2]:
                    result_record["用药推荐依据"].append(n["name"])
                # remove all newline characters
                result_record["用药推荐文献"] = node[0]["reference"].replace('\n', ' ').replace('\r', '') if node[0]["reference"] is not None else None
                for n in node[3]:
                    result_record["用药禁忌"].append(n["name"])
                for n in node[4]:
                    result_record["不良反应"].append(n["name"])
                result.append(result_record)        
        return result

    
    def closeConnection(self):
        self.driver.close()
        
