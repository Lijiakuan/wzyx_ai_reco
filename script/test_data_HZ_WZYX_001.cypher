MATCH (n:Patient)
WHERE n.patient_no = "HZ_WZYX_001"
DETACH DELETE n;

MATCH (b1:Condition { name: "收缩压>=140mmHg", measure: "sbp", operand: ">=", value: 140 })
MATCH (b2:Condition { name: "收缩压<160mmHg", measure: "sbp", operand: "<", value: 160 })
MATCH (b3:Condition { name: "舒张压<90mmHg" })
MATCH (b4:Condition { name: "收缩压=130-139mmHg和/或舒张压=80-89mmHg" })
MATCH (b5:Condition { name: "收缩压<150mmHg和舒张压<90mmHg" })
MATCH (past1:Condition { name: "糖尿病" })
MATCH (past2:Condition { name: "脑卒中" })
MATCH (past3:Condition { name: "高血压" })
MATCH (past4:Condition { name: "蛋白尿" })
MATCH (past5:Condition { name: "冠心病" })
MATCH (past6:Condition { name: "痛风" })
MATCH (no_drug:Condition { name:"未服用降压药物" })
MATCH (exam_report1:Condition { name: "心电图" })
MATCH (exam_report2:Condition { name: "X光" })
MATCH (exam_report3:Condition { name: "（LDL-C）>=3.4mmol/L" })
MATCH (present1:Condition { name: "意识丧失" })
MATCH (present2:Condition { name: "意识淡漠" })
//MATCH (lifestyle1:Condition { name: "妊娠" })
MATCH (phyiscal_exam1:Condition { name: "心率>100次/分" })
MATCH (phyiscal_exam2:Condition { name: "BMI>=28" })
MATCH (screening1:Condition { name: "初诊" })
MATCH (basic1:Condition { name: "女>=55岁" })

MERGE (p:Patient { patient_no: "HZ_WZYX_001" })
MERGE (p)-[:has_blood_pressure_range]->(b1)
MERGE (p)-[:has_blood_pressure_range]->(b2)
MERGE (p)-[:has_blood_pressure_range]->(b3)
MERGE (p)-[:has_blood_pressure_range]->(b4)
MERGE (p)-[:has_blood_pressure_range]->(b5)
MERGE (p)-[:has_past_medical_history]->(past1)
MERGE (p)-[:has_past_medical_history]->(past2)
MERGE (p)-[:has_past_medical_history]->(past3)
MERGE (p)-[:has_past_medical_history]->(past4)
MERGE (p)-[:has_past_medical_history]->(past5)
MERGE (p)-[:has_past_medical_history]->(past6)
MERGE (p)-[:has_baseline_treatment]->(no_drug)
MERGE (p)-[:has_exam_report]->(exam_report1)
MERGE (p)-[:has_exam_report]->(exam_report2)
MERGE (p)-[:has_exam_report]->(exam_report3)
MERGE (p)-[:has_present_medical_history]->(present1)
MERGE (p)-[:has_present_medical_history]->(present2)
//MERGE (p)-[:has_lifestyle_history]->(lifestyle1)
MERGE (p)-[:has_phyiscal_exam]->(phyiscal_exam1)
MERGE (p)-[:has_phyiscal_exam]->(phyiscal_exam2)
MERGE (p)-[:has_screening]->(screening1)
MERGE (p)-[:has_basic_info]->(basic1)
;
