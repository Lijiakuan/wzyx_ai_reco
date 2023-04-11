// 0. 病历档案

MATCH (patient:Patient { patient_no: 'HZ000001' })
OPTIONAL MATCH (patient)-->(a)
WHERE NOT 'Condition' IN labels(a)
OPTIONAL MATCH (patient)-->(c:Condition)
WHERE c.type IN ["baseline_treatment", "blood_pressure", "past_medical_history", "present_medical_history",
"physical_exam", "lifestyle_history", "family_history", "exam_report", "basic_info"]
WITH patient, a, c
 ORDER BY id(a), id(c)
RETURN patient, collect(a) AS attributes, collect(c) AS conditions

// 1. 检查建议 - 手工建立cypher规则

MATCH (e:Exam_Recommendation { name: "高血压评估检查建议" })-[:requires]->(require_con)
MATCH (e:Exam_Recommendation { name: "高血压评估检查建议" })-[:recommends]->(recommend_con)
MATCH (e:Exam_Recommendation { name: "高血压评估检查建议" })-[:suggests]->(suggest_con)
MATCH (p:Patient { patient_no: "HZ_WZYX_001" })
WITH p, collect( DISTINCT require_con) AS require_cons, suggest_con, recommend_con
WHERE any(x IN require_cons
WHERE (p)-[*]->(x))
WITH p, recommend_con, suggest_con
WHERE NOT exists( (p)-[]->(recommend_con)) AND NOT exists ((p)-[]->(suggest_con))
WITH recommend_con, suggest_con
 ORDER BY id(recommend_con), id(suggest_con)
RETURN collect( DISTINCT recommend_con) AS recommend, collect( DISTINCT suggest_con) AS suggest;

// 2. 转诊筛查 - 程序化Excel导入
MATCH (rules:Screening_Rule)
UNWIND rules AS rule
MATCH (rule)-[*]->(r_condition:Condition)
WITH rule, collect(r_condition) AS rule_conditions
MATCH (patient:Patient { patient_no: "HZ_WZYX_001" })
WHERE all(x IN rule_conditions
WHERE (patient)-[*]->(x))
MATCH (c1:Condition)<-[*]-(rule)-[*]->(rec1:Screening_Recommendation)
WITH rec1, c1
 ORDER BY id(c1)
RETURN rec1, collect( DISTINCT c1)
 ORDER BY rec1.name;

// RETURN rule.rule_no, COLLECT( DISTINCT rec), collect( DISTINCT c);

// 3. 高危分层 - 手工建立cypher规则

//这是给患者打高危标签，这个merge跟后面的query的return可以合并成一个read_write_transaction
MATCH (risk:Condition { name: "高危" })
MATCH (patient { patient_no: "HZ_WZYX_001" })
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
;

// 4. 合并症用药 - 程序化Excel导入
MATCH (rules:Complication_Rule)
UNWIND rules AS rule
MATCH (rule)-[*]->(r_condition:Condition)
WITH rule, r_condition
 ORDER BY id(rule), id(r_condition)
WITH rule, collect(r_condition) AS rule_conditions
MATCH (patient:Patient { patient_no: "HZ_WZYX_001" })
WHERE all(x IN rule_conditions
WHERE (patient)-[*]->(x))
MATCH (rule)-[*]->(drug:Drug)
RETURN rule, drug, rule_conditions;

// 5. 用药规则 - 程序化Excel导入
// 6. 禁忌症 - 程序化Excel导入
MATCH (rules:Drug_Rule)
UNWIND rules AS rule
MATCH (rule)-[r*]->(r_condition:Condition)
WHERE all(x IN r
WHERE x.type is null OR x.type <> "hypertension_risk_level")
WITH rule, r_condition
 ORDER BY id(rule), id(r_condition)
WITH rule, collect(r_condition) AS rule_conditions
MATCH (patient:Patient { patient_no: "HZ_WZYX_001" })
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
RETURN rule, rule_conditions, drugs, con_rules, con_conditions, side_conditions;

// 测试用户信息
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

///////

MATCH p = (r:Drug_Rule { name: "A000.00-AB72" })-[*]->(condition:Condition)
RETURN collect(condition);

//////

MATCH p = (patient:Patient { patient_no: "HZ_WZYX_001" })-[*]->(p_condition:Condition)
WITH collect(p_condition) AS target_conditions
RETURN target_conditions;

// match rules

MATCH (rules:Drug_Rule)
UNWIND rules AS rule
MATCH (rule)-[*]->(r_condition:Condition)
WITH rule, collect(r_condition) AS rule_conditions
MATCH (patient:Patient { patient_no: "HZ_WZYX_001" })
WHERE all(x IN rule_conditions
WHERE (patient)-[*]->(x))
RETURN rule;

MATCH (m:Past_Medical_History { name: "脑卒中" })
create (n:Disease { name: "高血压" })-[:has_diagnosis_factor]->(m);

// delete a particular node by id
// MATCH (n) where id(n) = 1452
// DETACH DELETE n;

// sanity check, should be none:
// MATCH (n) RETURN distinct labels(n), count(*);
// match (n) where labels(n) = [] return (n);

// 给患者添加默认未服用药物标签
MATCH (p:Patient { patient_no: "HZ900003" })-[r:has_baseline_treatment]->(t)
WITH count(r) AS cnt
WHERE cnt = 0
MATCH (p:Patient { patient_no: "HZ900003" })
MATCH (wei)
WHERE (wei:Prescription_Record OR wei:Condition) AND wei.name = "未服用降压药物"
WITH p, wei
MERGE (p)-[:has_baseline_treatment]->(wei);

MATCH (patients:Patient)
UNWIND patients AS p
OPTIONAL MATCH (p)-[r:has_baseline_treatment]->(:Condition)
WITH count(r) AS cnt
WHERE cnt = 0
MATCH (p:Patient { patient_no: "HZ900003" })
MATCH (wei)
WHERE (wei:Prescription_Record OR wei:Condition) AND wei.name = "未服用降压药物"
WITH p, wei
MERGE (p)-[:has_baseline_treatment]->(wei);
