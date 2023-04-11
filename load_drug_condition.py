from py2neo import Graph,Node,Relationship
from py2neo.matching import *
import os
import sys
import pathlib
import pandas as pd
import time
from logger import logger
from dotenv import load_dotenv
load_dotenv()

class DrugCondition:
    def __init__(self):
        self.g = Graph(os.getenv("GRAPH_URI"), name=os.getenv("GRAPH_DATABASE"), 
                       auth=(os.getenv("GRAPH_USER"),os.getenv("GRAPH_PASSWORD")))

        self.current_row_count = 2 # 从第2行开始处理
    
    def load_drug_recommendation(self):
        self.g.run("match (n:Drug_Rule) detach delete n")
        read_filename = os.path.join(pathlib.Path(__file__).parent.resolve(),'script','mdnov原发性用药规则.xlsx')
        excel_data_df = pd.read_excel(read_filename, sheet_name='综合用药规则_5')
        # convert all nan values to None, reference: https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb
        excel_data_df1 = excel_data_df.where(pd.notnull(excel_data_df), None)
        records = excel_data_df1.to_dict(orient = 'records')
        for record in records:
            self.process_drug_record(record)

    def load_prescreen(self):
        self.g.run("match (n:Screening_Rule) detach delete n")
        read_filename = os.path.join(pathlib.Path(__file__).parent.resolve(),'script','mdnov原发性用药规则.xlsx')
        excel_data_df = pd.read_excel(read_filename, sheet_name='前期筛查_2')
        # convert all nan values to None, reference: https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb
        excel_data_df1 = excel_data_df.where(pd.notnull(excel_data_df), None)
        records = excel_data_df1.to_dict(orient = 'records')
        for record in records:
            self.process_prescreen_record(record)

    def load_complication(self):
        self.g.run("match (n:Complication_Rule) detach delete n")
        read_filename = os.path.join(pathlib.Path(__file__).parent.resolve(),'script','mdnov原发性用药规则.xlsx')
        excel_data_df = pd.read_excel(read_filename, sheet_name='高血压合并症综合干预用药推荐_4')
        # convert all nan values to None, reference: https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb
        excel_data_df1 = excel_data_df.where(pd.notnull(excel_data_df), None)
        records = excel_data_df1.to_dict(orient = 'records')
        for record in records:
            self.process_complication_record(record)

    def load_contraindication(self):
        self.g.run("match (n:Contraindication_Rule) detach delete n")
        read_filename = os.path.join(pathlib.Path(__file__).parent.resolve(),'script','mdnov原发性用药规则.xlsx')
        excel_data_df = pd.read_excel(read_filename, sheet_name='药品禁忌症_6')
        # convert all nan values to None, reference: https://stackoverflow.com/questions/14162723/replacing-pandas-or-numpy-nan-with-a-none-to-use-with-mysqldb
        excel_data_df1 = excel_data_df.where(pd.notnull(excel_data_df), None)
        records = excel_data_df1.to_dict(orient = 'records')
        for record in records:
            if record["编号"] is None:
                break
            else:
                self.process_contraindication_record(record)
    
    def process_drug_record(self, record):
        drug_nodes = []
        condition_nodes = []
                
        nodes = NodeMatcher(self.g)
        if record["药品种类一"]:
            drug_match = nodes.match("Drug", name=record["药品种类一"])
            if len(drug_match) != 1:
                print("药品种类一不存在:",record["药品种类一"])
            else:
                drug_nodes.append(drug_match.first())
        if record["药品种类二"]:
            drug_match = nodes.match("Drug", name=record["药品种类二"])
            if len(drug_match) != 1:
                print("药品种类二不存在:",record["药品种类二"])
            else:
                drug_nodes.append(drug_match.first())
        if record["药品种类三"]:
            drug_match = nodes.match("Drug", name=record["药品种类三"])
            if len(drug_match) != 1:
                print("药品种类三不存在:",record["药品种类三"])
            else:
                drug_nodes.append(drug_match.first())
        if record["药品种类四"]:
            drug_match = nodes.match("Drug", name=record["药品种类四"])
            if len(drug_match) != 1:
                print("药品种类四不存在:",record["药品种类四"])
            else:
                drug_nodes.append(drug_match.first())

        if record["用药依据（危险分层）"] == '高危':
            condition_match = nodes.match("Condition", name="高危")
            if len(condition_match) != 1:
                print("用药依据（危险分层）:",record["用药依据（危险分层）"])
            else:
                drug_nodes.append(condition_match.first())
                    
        taking_drug = False
        for n in range(1,7):
            condition_name = record["用药依据"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue
            elif condition_name == '坚持服用':
                assert taking_drug == False
                taking_drug = True
                continue
            elif taking_drug:
                condition_name = "坚持服用" + condition_name
                taking_drug = False
            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，用药依据{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                condition_nodes.append(condition_match.first())

        reference_grade = {
            "1A": 1,
            "1B": 2,
            "1C": 3,
            "2A": 4,
            "2B": 5,
            "2C": 6,
        }
        sort_key = 10
        if record["参考文献1"]:
            for grade in reference_grade:
                if grade in record["参考文献1"]:
                    sort_key = reference_grade[grade]
                    break
            
        self.current_row_count += 1
        recommendation = Node("Drug_Rule",rule_no=record["编号"],disease=record["病种"],reference=record["参考文献1"], sort_key=sort_key)
        self.g.create(recommendation)
        for drug in drug_nodes:
            self.g.create(Relationship(recommendation,"recommend_drug",drug))
        for condition in condition_nodes:
            self.g.create(Relationship(recommendation,"with_condition",condition))
                        
    def process_prescreen_record(self, record):
        condition_nodes = []
                
        nodes = NodeMatcher(self.g)

        if record["就诊"]:
            condition_match = nodes.match("Condition", name=record["就诊"])
            if len(condition_match) != 1:
                print("就诊：",record["就诊"])
            else:
                condition_nodes.append(condition_match.first())
                    
        for n in range(1,6):
            condition_name = record["转诊条件"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，转诊条件{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                condition_nodes.append(condition_match.first())
        
        self.current_row_count += 1
        recommendation = Node("Screening_Rule",rule_no=record["编号"],reference=record["参考文献1"])
        self.g.create(recommendation)
        for condition in condition_nodes:
            self.g.create(Relationship(recommendation,"with_condition",condition))
        outcome = nodes.match("Screening_Recommendation", name=record["处理"]).first()
        self.g.create(Relationship(recommendation,"with_outcome",outcome))
            
    def process_complication_record(self, record):
        drug_nodes = []
        condition_nodes = []
                
        nodes = NodeMatcher(self.g)
        if record["用药推荐"]:
            drug_match = nodes.match("Drug", name=record["用药推荐"])
            if len(drug_match) != 1:
                print("用药推荐不存在: ",record["用药推荐"])
            else:
                drug_nodes.append(drug_match.first())
                    
        for n in range(1,6):
            condition_name = record["用药条件"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，用药条件{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                condition_nodes.append(condition_match.first())
        
        self.current_row_count += 1
        recommendation = Node("Complication_Rule",rule_no=record["编号"],reference=record["参考文献1"], reference2=record["参考文献2"])
        self.g.create(recommendation)
        for drug in drug_nodes:
            self.g.create(Relationship(recommendation,"recommend_drug",drug))
        for condition in condition_nodes:
            self.g.create(Relationship(recommendation,"with_condition",condition))
        
    def process_contraindication_record(self, record):
        drug_nodes = []
        absolute_nodes = []
        relative_nodes = []
        side_nodes = []

        nodes = NodeMatcher(self.g)
                    
        if record["药品类型/名称"]:
            condition_match = nodes.match("Drug", name=record["药品类型/名称"])
            if len(condition_match) != 1:
                print("药品类型/名称: ",record["药品类型/名称"])
            else:
                drug_nodes.append(condition_match.first())

        for n in range(1,4):
            condition_name = record["绝对禁忌"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，绝对禁忌{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                absolute_nodes.append(condition_match.first())
        
        for n in range(1,3):
            condition_name = record["相对禁忌"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，相对禁忌{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                relative_nodes.append(condition_match.first())

        for n in range(1,3):
            condition_name = record["不良反应"+str(n)] 
            if condition_name is None or condition_name.strip() == "":
                continue            
            condition_match = nodes.match("Condition", name=condition_name)
            if len(condition_match) != 1:
                print("第{}行，不良反应{}不存在: {}".format(self.current_row_count, n, condition_name))
                # sys.exit()
            else:
                side_nodes.append(condition_match.first())


        self.current_row_count += 1
        recommendation = Node("Contraindication_Rule",rule_no=record["编号"])
        self.g.create(recommendation)
        for drug in drug_nodes:
            self.g.create(Relationship(recommendation,"recommend_drug",drug))
        for condition in absolute_nodes:
            self.g.create(Relationship(recommendation,"with_absolute_contraindication",condition))
        for condition in relative_nodes:
            self.g.create(Relationship(recommendation,"with_relative_contraindication",condition))
        for condition in side_nodes:
            self.g.create(Relationship(recommendation,"with_side_effect",condition))


if __name__ == '__main__':
    handler = DrugCondition()
    original_start = time.time()

    start = original_start
    handler.load_drug_recommendation()
    logger.info("load_drug_recommendation: %s seconds", round(time.time() - start))

    start = time.time()
    handler.load_prescreen()
    logger.info("load_prescreen: %s seconds", round(time.time() - start))

    start = time.time()
    handler.load_complication()
    logger.info("load_complication: %s seconds", round(time.time() - start))

    start = time.time()
    handler.load_contraindication()
    logger.info("load_contraindication: %s seconds", round(time.time() - start))

    logger.info("total processing time: %s seconds", round(time.time() - original_start))
    
    