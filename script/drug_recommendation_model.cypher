// rebuild hypertensin database
// reference: https://stackoverflow.com/questions/23310114/how-to-reset-clear-delete-neo4j-database/23310320#23310320

// :use system;
// create OR replace database hypertension;
// :use hypertension;

MATCH (n)
DETACH DELETE n;

// Drug
MATCH (n:Drug)
DETACH DELETE n;

CREATE CONSTRAINT drug_name_idx IF NOT EXISTS FOR (n:Drug) REQUIRE (n.name) IS UNIQUE;

CREATE CONSTRAINT Condition_name_idx IF NOT EXISTS FOR (n:Condition) REQUIRE (n.name) IS UNIQUE;

CREATE CONSTRAINT drug_rule_rule_no_idx IF NOT EXISTS FOR (n:Drug_Rule) REQUIRE (n.rule_no) IS UNIQUE;

CREATE CONSTRAINT screening_rule_rule_no_idx IF NOT EXISTS FOR (n:Screening_Rule) REQUIRE (n.rule_no) IS UNIQUE;

CREATE CONSTRAINT complication_rule_rule_no_idx IF NOT EXISTS FOR (n:Complication_Rule) REQUIRE (n.rule_no) IS UNIQUE;

CREATE CONSTRAINT contraindication_rule_rule_no_idx IF NOT EXISTS FOR (n:Contraindication_Rule) REQUIRE (n.rule_no) IS UNIQUE;

// unique indices
CREATE CONSTRAINT patient_no_idx IF NOT EXISTS FOR (p:Patient) REQUIRE p.patient_no IS UNIQUE;

CREATE INDEX patient_name_idx IF NOT EXISTS FOR (t:Patient) ON (t.patient_name);

CREATE INDEX patient_phone_idx IF NOT EXISTS FOR (t:Patient) ON (t.patient_phone);

create (n:Drug { name: "ACEI", properties: ["drug_01_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "ARNI（SPC）", properties: ["drug_02_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "ARB", properties: ["drug_03_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "CCB", properties: ["drug_04_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "α/β受体阻滞剂", properties: ["drug_05_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "β受体阻滞剂", properties: ["drug_06_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "利尿剂", properties: ["drug_07_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "噻嗪类利尿剂", properties: ["drug_08_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "螺内酯", properties: ["drug_09_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "袢利尿剂", properties: ["drug_10_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "二氢吡啶类钙通道阻滞剂", properties: ["drug_11_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "非二氢吡啶类钙通道阻滞剂", properties: ["drug_12_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "阿司匹林75~100mg，每日1次", properties: ["drug_13_prescription_date"], property_comments: ["处方日期"] });

create (n:Drug { name: "他汀类降脂药", properties: ["drug_14_prescription_date"], property_comments: ["处方日期"] });

// Drug_Product

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '阿利沙坦酯片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '阿替洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '氨氯地平贝那普利片(II)'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '氨氯地平贝那普利片(II)'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '奥美沙坦酯片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '贝那普利氢氯噻嗪'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '贝那普利氢氯噻嗪'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '苯磺酸氨氯地平胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '苯磺酸氨氯地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '比索洛尔氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '比索洛尔氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '厄贝沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '非洛地平缓释胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '非洛地平缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '非洛地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '非诺地平缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '福辛普利钠片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '复方卡托普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '复方卡托普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '富马酸比索洛尔胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '富马酸比索洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '琥珀酸美托洛尔缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '酒石酸美托洛尔缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '酒石酸美托洛尔胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'β受体阻滞剂' }) create (dp:Drug_Product { name: '酒石酸美托洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '卡托普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'α/β受体阻滞剂' }) create (dp:Drug_Product { name: '卡维地洛胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '坎地沙坦西酯片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '坎地沙坦酯分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '坎地沙坦酯胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '坎地沙坦酯片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '拉西地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '赖诺普利氢氯噻嗪'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '赖诺普利氢氯噻嗪'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '雷米普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '螺内酯' }) create (dp:Drug_Product { name: '螺内酯片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '氯沙坦钾胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '氯沙坦钾片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '氯沙坦钾氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '氯沙坦钾氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '马来酸氨氯地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '马来酸依那普利分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '马来酸依那普利胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '马来酸依那普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '马来酸左氨氯地平分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '马来酸左旋氨氯地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '尼群地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '尼群地平软胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '尼群洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: ' ' }) create (dp:Drug_Product { name: '尼群洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '培哚普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '培哚普利吲达帕胺片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '培哚普利吲达帕胺片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARNI（SPC）' }) create (dp:Drug_Product { name: '沙库巴曲缬沙坦钠片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '替米沙坦胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '替米沙坦片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '替米沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '替米沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '西尼地平胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '西尼地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '硝苯地平缓释胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '硝苯地平缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '硝苯地平缓释片(Ⅱ)'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '硝苯地平控释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦氨氯地平'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '缬沙坦氨氯地平'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦氨氯地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '缬沙坦氨氯地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦分散片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦氢氯噻嗪胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '缬沙坦氢氯噻嗪胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ARB' }) create (dp:Drug_Product { name: '缬沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '缬沙坦氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'α/β受体阻滞剂' }) create (dp:Drug_Product { name: '盐酸阿罗洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '盐酸贝那普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '盐酸贝尼地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'α/β受体阻滞剂' }) create (dp:Drug_Product { name: '盐酸拉贝洛尔片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'CCB' }) create (dp:Drug_Product { name: '盐酸乐卡地平片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '盐酸咪达普利片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: 'ACEI' }) create (dp:Drug_Product { name: '依那普利氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '依那普利氢氯噻嗪片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '吲达帕胺缓释胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '吲达帕胺缓释片'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '吲达帕胺胶囊'})-[:has_drug_ingredient]->(d);

MATCH (d:Drug { name: '噻嗪类利尿剂' }) create (dp:Drug_Product { name: '吲达帕胺片'})-[:has_drug_ingredient]->(d);

// Prescription_Record and Condition

MATCH (n:Prescription_Record)
DETACH DELETE n;

MATCH (n:Condition)
WHERE n.type = "baseline_treatment"
DETACH DELETE n;

CREATE CONSTRAINT baseline_treatment_name_idx IF NOT EXISTS FOR (n:Prescription_Record) REQUIRE (n.name) IS UNIQUE;

MATCH (drug:Drug { name: "ACEI" }) create (:Prescription_Record {name: "服用ACEI"})-[:take_drug]->(drug), (:Condition {name: "服用ACEI", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "ARB" }) create (:Prescription_Record {name: "服用ARB", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用ARB", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "ARNI（SPC）" }) create (:Prescription_Record {name: "服用ARNI（SPC）", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用ARNI（SPC）", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "CCB" }) create (:Prescription_Record {name: "服用CCB", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用CCB", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "α/β受体阻滞剂" }) create (:Prescription_Record {name: "服用α/β受体阻滞剂", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用α/β受体阻滞剂", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "β受体阻滞剂" }) create (:Prescription_Record {name: "服用β受体阻滞剂", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用β受体阻滞剂", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "利尿剂" }) create (:Prescription_Record {name: "服用利尿剂", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用利尿剂", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "噻嗪类利尿剂" }) create (:Prescription_Record {name: "服用噻嗪类利尿剂", type: "baseline_treatment"})-[:take_drug]->(drug), (:Condition {name: "服用噻嗪类利尿剂", type: "baseline_treatment"})-[:take_drug]->(drug);

MATCH (drug:Drug { name: "螺内酯" }) create (:Prescription_Record { name: "服用螺内酯", type: "baseline_treatment" })-[:take_drug]->(drug), (:Condition { name: "服用螺内酯", type: "baseline_treatment" })-[:take_drug]->(drug);

MATCH (drug:Drug { name: "袢利尿剂" }) create (:Prescription_Record { name: "服用袢利尿剂", type: "baseline_treatment" })-[:take_drug]->(drug), (:Condition { name: "服用袢利尿剂", type: "baseline_treatment" })-[:take_drug]->(drug);

MATCH (drug:Drug { name: "ACEI" }) create (:Condition {name: "服用非ACEI类药物", type: "baseline_treatment"})-[:take_drug_but_not]->(drug);

MATCH (drug:Drug { name: "ARB" }) create (:Condition {name: "服用非ARB类药物", type: "baseline_treatment"})-[:take_drug_but_not]->(drug);

MATCH (drug:Drug { name: "CCB" }) create (:Condition {name: "服用非CCB类药物", type: "baseline_treatment"})-[:take_drug_but_not]->(drug);

MATCH (drug:Drug { name: "ARNI（SPC）" }) create (:Condition {name: "服用非ARNI类药物", type: "baseline_treatment"})-[:take_drug_but_not]->(drug);

MATCH (d1:Drug { name: "ACEI" })
MATCH (d2:Drug { name: "ARB" })
create (n:Condition { name: "服用非ACEI/ARB类药物", type: "baseline_treatment" }),
(n)-[:take_drug_but_not]->(d1),
(n)-[:take_drug_but_not]->(d2);

MATCH (drug:Drug { name: "α/β受体阻滞剂" }) create (n:Condition {name: "服用非α/β受体阻滞剂类药物", type: "baseline_treatment"})-[r:take_drug_but_not]->(drug);

MATCH (drug:Drug { name: "β受体阻滞剂" }) create (n:Condition {name: "服用非β受体阻滞剂类药物", type: "baseline_treatment"})-[r:take_drug_but_not]->(drug);

MATCH (drug1:Drug { name: "利尿剂" })
MATCH (drug2:Drug { name: "噻嗪类利尿剂" })
MATCH (drug3:Drug { name: "袢利尿剂" })
create (:Condition { name: "服用利尿剂类药物", type: "baseline_treatment" }),
(n)-[:take_drug]->(drug1),
(n)-[:take_drug]->(drug2),
(n)-[:take_drug]->(drug3);

MATCH (drug1:Drug { name: "利尿剂" })
MATCH (drug2:Drug { name: "噻嗪类利尿剂" })
MATCH (drug3:Drug { name: "袢利尿剂" })
create (:Condition { name: "未服用利尿剂类药物", type: "baseline_treatment" }),
(n)-[:not_take_drug]->(drug1),
(n)-[:not_take_drug]->(drug2),
(n)-[:not_take_drug]->(drug3);

MATCH (drug1:Drug { name: "利尿剂" })
MATCH (drug2:Drug { name: "噻嗪类利尿剂" })
MATCH (drug3:Drug { name: "袢利尿剂" })
create (:Condition { name: "服用非利尿剂类药物", type: "baseline_treatment" }),
(n)-[:take_drug_but_not]->(drug1),
(n)-[:take_drug_but_not]->(drug2),
(n)-[:take_drug_but_not]->(drug3);

MATCH (drug:Drug { name: "噻嗪类利尿剂" }) create (n:Condition {name: "服用非噻嗪类利尿剂类药物", type: "baseline_treatment"})-[r:take_drug_but_not]->(drug);

create (n:Condition { name:"坚持服用3种降压药物", type: "baseline_treatment", measure: "正在服用种类", times: 3 } );

create (n:Condition { name:"坚持服用2种降压药物", type: "baseline_treatment", measure: "正在服用种类", times: 2 } );

create (n:Condition { name:"坚持服用1种降压药物", type: "baseline_treatment", measure: "正在服用种类", times: 1 } );

create (:Condition { name:"未服用降压药物", type: "baseline_treatment", measure: "正在服用种类", times: 0 } );

create (n:Condition { name:"服用降压药物", type: "baseline_treatment" } );

create (n:Condition { name:"并发症无处理条件", type: "baseline_treatment" } );

// 血压数据
// blood pressure value range
MATCH (n:Condition)
WHERE n.type = "blood_pressure"
DETACH DELETE n;

create (n:Condition { name: "收缩压>=130mmHg", type: "blood_pressure", measure: "sbp", operand: ">=", value: 130 });

create (n:Condition { name: "收缩压>=140mmHg", type: "blood_pressure", measure: "sbp", operand: ">=", value: 140 });

create (n:Condition { name: "收缩压>=160mmHg", type: "blood_pressure", measure: "sbp", operand: ">=", value: 160 });

create (n:Condition { name: "收缩压>=180mmHg", type: "blood_pressure", measure: "sbp", operand: ">=", value: 180 });

create (n:Condition { name: "收缩压<90mmHg", type: "blood_pressure", measure: "sbp", operand: "<", value: 90 });

create (n:Condition { name: "收缩压<140mmHg", type: "blood_pressure", measure: "sbp", operand: "<", value: 140 });

create (n:Condition { name: "收缩压<160mmHg", type: "blood_pressure", measure: "sbp", operand: "<", value: 160 });

create (n:Condition { name: "舒张压>=80mmHg", type: "blood_pressure", measure: "dbp", operand: ">=", value: 80 });

create (n:Condition { name: "舒张压>=90mmHg", type: "blood_pressure", measure: "dbp", operand: ">=", value: 90 });

create (n:Condition { name: "舒张压>=100mmHg", type: "blood_pressure", measure: "dbp", operand: ">=", value: 100 });

create (n:Condition { name: "舒张压>=110mmHg", type: "blood_pressure", measure: "dbp", operand: ">=", value: 110 });

create (n:Condition { name: "舒张压<60mmHg", type: "blood_pressure", measure: "dbp", operand: "<", value: 60 });

create (n:Condition { name: "舒张压<90mmHg", type: "blood_pressure", measure: "dbp", operand: "<", value: 90 });

create (n:Condition { name: "舒张压<100mmHg", type: "blood_pressure", measure: "dbp", operand: "<", value: 100 });

create (n:Condition { name: "收缩压>=140mmHg和/或舒张压>=90mmHg", type: "blood_pressure" });

create (n:Condition { name: "收缩压=130-139mmHg和/或舒张压=80-89mmHg", type: "blood_pressure" });

create (n:Condition { name: "收缩压<150mmHg和舒张压<90mmHg", type: "blood_pressure" });

create (n:Condition { name: "双上肢收缩压差异>20mmHg", type: "blood_pressure" });

// 既往史

MATCH (n:Past_Medical_History)
DETACH DELETE n;

MATCH (n)
WHERE n:Condition AND n.type = "past_medical_history"
DETACH DELETE n;

CREATE CONSTRAINT past_medical_history_name_idx IF NOT EXISTS FOR (n:Past_Medical_History) REQUIRE n.name IS UNIQUE;

create (n:Past_Medical_History { name: "高血压" }), (c:Condition {name: "高血压", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "难治性高血压" }), (c:Condition {name: "难治性高血压", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "糖尿病" }), (c:Condition {name: "糖尿病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "2型糖尿病", reflection: true }), (c:Condition {name: "2型糖尿病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "高血脂" }), (c:Condition {name: "高血脂", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "冠心病" }), (c:Condition {name: "冠心病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "肾病", reflection: true }), (c:Condition {name: "肾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "慢性肾脏病", reflection: true }), (c:Condition {name: "慢性肾脏病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "肾功能异常" }), (c:Condition {name: "肾功能异常", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "慢性肾脏疾病", reflection: true }), (c:Condition {name: "慢性肾脏疾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "糖尿病肾病" }), (c:Condition {name: "糖尿病肾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "非糖尿病肾病", reflection: true }), (c:Condition {name: "非糖尿病肾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "高血压处理后仍无法控制" }), (c:Condition {name: "高血压处理后仍无法控制", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "老年单纯收缩期高血压", reflection: true }), (c:Condition {name: "老年单纯收缩期高血压", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "其他系统疾病", properties: ["other_systemic_diseases"], property_comments: ["其他系统疾病"] })
, (c:Condition { name: "其他系统疾病", type: "past_medical_history" }), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "代谢综合征" }), (c:Condition {name: "代谢综合征", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "蛋白尿" }), (c:Condition {name: "蛋白尿", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "微量蛋白尿" }), (c:Condition {name: "微量蛋白尿", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "血尿" }), (c:Condition {name: "血尿", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "快速心律失常", reflection: true }), (c:Condition {name: "快速心律失常", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "脑卒中" }), (c:Condition {name: "脑卒中", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "动脉粥样硬化", reflection: true }), (c:Condition {name: "动脉粥样硬化", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "外周动脉粥样硬化", reflection: true }), (c:Condition {name: "外周动脉粥样硬化", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "颈动脉粥样硬化" }), (c:Condition {name: "颈动脉粥样硬化", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "外周动脉疾病" }), (c:Condition {name: "外周动脉疾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心肌梗死" }), (c:Condition {name: "心肌梗死", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心绞痛" }), (c:Condition {name: "心绞痛", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心力衰竭" }), (c:Condition {name: "心力衰竭", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "充血性心力衰竭" }), (c:Condition {name: "充血性心力衰竭", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心房颤动", reflection: true }), (c:Condition {name: "心房颤动", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心动过缓" }), (c:Condition {name: "心动过缓", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "心脏并发症", reflection: true }), (c:Condition {name: "心脏并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "左心室肥厚" }), (c:Condition {name: "左心室肥厚", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "左房扩大" }), (c:Condition {name: "左房扩大", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "房室传导阻滞" }), (c:Condition {name: "房室传导阻滞", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "二度房室传导阻滞" }), (c:Condition {name: "二度房室传导阻滞", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "三度房室传导阻滞" }), (c:Condition {name: "三度房室传导阻滞", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "脑出血", reflection: true }), (c:Condition {name: "脑出血", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "缺血性脑卒中", reflection: true }), (c:Condition {name: "缺血性脑卒中", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "短暂性脑缺血发作", reflection: true }), (c:Condition {name: "短暂性脑缺血发作", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "主动脉疾病或外周血管疾病", relfection: true }), (c:Condition {name: "主动脉疾病或外周血管疾病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "视网膜病变" }), (c:Condition {name: "视网膜病变", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "射血分数保留的心力衰竭（HFpEF）", reflection: true }), (c:Condition {name: "射血分数保留的心力衰竭（HFpEF）", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "射血分数减少的心力衰竭（HFrEF）", reflection: true }), (c:Condition {name: "射血分数减少的心力衰竭（HFrEF）", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "新发心脏并发症" }), (c:Condition {name: "新发心脏并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "新发脑血管并发症" }), (c:Condition {name: "新发脑血管并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "新发肾脏并发症" }), (c:Condition {name: "新发肾脏并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "脑血管并发症", reflection: true }), (c:Condition {name: "脑血管并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "肾脏并发症", reflection: true }), (c:Condition {name: "肾脏并发症", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "双侧肾动脉狭窄", reflection: true }), (c:Condition {name: "双侧肾动脉狭窄", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "哮喘" }), (c:Condition {name: "哮喘", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "慢性阻塞性肺病" }), (c:Condition {name: "慢性阻塞性肺病", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "支气管痉挛" }), (c:Condition {name: "支气管痉挛", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "痛风" }), (c:Condition {name: "痛风", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

create (n:Past_Medical_History { name: "血管神经性水肿" }), (c:Condition {name: "血管神经性水肿", type: "past_medical_history"}), (c)-[r:has_past_medical_history]->(n);

// 现病史
MATCH (n:Present_Medical_History)
DETACH DELETE n;

MATCH (n)
WHERE n:Condition AND n.type = "present_medical_history"
DETACH DELETE n;

CREATE CONSTRAINT present_medical_history_name_idx IF NOT EXISTS FOR (n:Present_Medical_History) REQUIRE n.name IS UNIQUE;

create (present:Present_Medical_History { name: "现病史填写时间", properties: ["present_medical_history_record_time"], property_comments: ["现病史填写时间"] });

create (present:Present_Medical_History { name: "发病时间", properties: ["present_medical_history_onset_time"], property_comments: ["发病时间"] });

create (present:Present_Medical_History { name: "发病年龄", properties: ["present_medical_history_onset_age"], property_comments: ["发病年龄"] });

create (present:Present_Medical_History { name: "发病时长", properties: ["present_medical_history_disease_duration"], property_comments: ["发病时长"] });

create (present:Present_Medical_History { name: "日常血压水平：高压（mmHg）", properties: ["present_medical_history_bp_level_high"], property_comments: ["日常血压水平：高压（mmHg）"] });

create (present:Present_Medical_History { name: "日常血压水平：低压（mmHg）", properties: ["present_medical_history_bp_level_low"], property_comments: ["日常血压水平：低压（mmHg）"] });

create (present:Present_Medical_History { name: "日常血压水平：心率（次/分钟）", properties: ["present_medical_history_bp_level_pulse"], property_comments: ["日常血压水平：心率（次/分钟）"] });

create (present:Present_Medical_History { name: "头痛" }), (c:Condition {name: "头痛", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "头晕" }), (c:Condition {name: "头晕", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "心慌" }), (c:Condition {name: "心慌", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "胸闷" }), (c:Condition {name: "胸闷", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "胸痛持续时间>=10min" }), (c:Condition {name: "胸痛持续时间>=10min", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "气短" }), (c:Condition {name: "气短", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "失眠" }), (c:Condition {name: "失眠", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "手脚麻木" }), (c:Condition {name: "手脚麻木", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "呕吐", reflection: true }), (c:Condition {name: "呕吐", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "恶心呕吐" }), (c:Condition {name: "恶心呕吐", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "其他", properties: ["present_medical_history_other"], property_comments: ["其他"] }), (c:Condition {name: "其他", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "咳嗽" }), (c:Condition {name: "咳嗽", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "水肿" }), (c:Condition {name: "水肿", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "下肢水肿" }), (c:Condition {name: "下肢水肿", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "晕厥" }), (c:Condition {name: "晕厥", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "伴头痛" }), (c:Condition {name: "伴头痛", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "多汗" }), (c:Condition {name: "多汗", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "大汗" }), (c:Condition {name: "大汗", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "意识淡漠" }), (c:Condition {name: "意识淡漠", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "意识丧失" }), (c:Condition {name: "意识丧失", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "意识模糊" }), (c:Condition {name: "意识模糊", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "全身严重过敏反应" }), (c:Condition {name: "全身严重过敏反应", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "服用降压药不良反应" }), (c:Condition {name: "服用降压药不良反应", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "呼吸困难" }), (c:Condition {name: "呼吸困难", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "端坐呼吸伴不能平卧" }), (c:Condition {name: "端坐呼吸伴不能平卧", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "不能平卧", reflection: true }), (c:Condition {name: "不能平卧", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "突发言语障碍" }), (c:Condition {name: "突发言语障碍", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "持续性胸背部剧烈疼痛" }), (c:Condition {name: "持续性胸背部剧烈疼痛", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "剧烈头痛" }), (c:Condition {name: "剧烈头痛", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "肢体瘫痪" }), (c:Condition {name: "肢体瘫痪", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "阵发性血压升高" }), (c:Condition {name: "阵发性血压升高", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

create (present:Present_Medical_History { name: "血压明显波动" }), (c:Condition {name: "血压明显波动", type: "present_medical_history"}), (c)-[r:has_present_medical_history]->(n);

MATCH (drug:Drug { name: "ACEI" })
MATCH (present:Present_Medical_History { name: "咳嗽" })
create (con:Condition { name: "ACEI引起的咳嗽", type: "present_medical_history" }),
(con)-[r:caused_by]->(drug),
(con)-[r2:has_present_medical_history]->(present);

// 体查
MATCH (n:Physical_Exam)
DETACH DELETE n;

MATCH (n:Condition)
WHERE n.type = "physical_exam"
DETACH DELETE n;

CREATE CONSTRAINT physical_exam_idx IF NOT EXISTS FOR (n:Physical_Exam) REQUIRE n.name IS UNIQUE;

create (n:Physical_Exam { name: "身高（厘米）", properties: ["height_cm"], property_comments: ["身高（厘米）"] }), (c:Condition {name: "身高（厘米）", type: "physical_exam"}), (c)-[r:has_physical_exam]->(n);

create (n:Physical_Exam { name: "体重（千克）", properties: ["weight_kg"], property_comments: ["体重（千克）"] }), (c:Condition {name: "体重（千克）", type: "physical_exam"}), (c)-[r:has_physical_exam]->(n);

create (n:Physical_Exam { name: "心率（次/分钟）", properties: ["heart_pulse_rate"], property_comments: ["心率（次/分钟）"] }), (c:Condition {name: "心率（次/分钟）", type: "physical_exam"}), (c)-[r:has_physical_exam]->(n);

create (n:Physical_Exam { name: "BMI", properties: ["bmi"], property_comments: ["BMI"] });

create (n:Physical_Exam { name: "腰围（厘米）", properties: ["waist_cm"], property_comments: ["腰围（厘米）"] }), (c:Condition {name: "腰围（厘米）", type: "physical_exam"}), (c)-[r:has_physical_exam]->(n);

create (n:Condition { name: "心率>100次/分", type:"physical_exam", measure: "heart_pulse_rate", operand: ">", value: 100 });

create (n:Condition { name: "心率>80次/分", type:"physical_exam", measure: "heart_pulse_rate", operand: ">", value: 80 });

create (n:Condition { name: "心率<60次/分", type:"physical_exam", measure: "heart_pulse_rate", operand: "<", value: 60 });

create (n:Condition { name: "BMI>=28", type:"physical_exam", measure: "bmi", operand: ">=", value: 28 });

// 个人史
MATCH (n:Lifestyle_History)
DETACH DELETE n;

MATCH (n)
WHERE n:Condition AND n.type = "lifestyle_history"
DETACH DELETE n;

CREATE CONSTRAINT lifestyle_history_name_idx IF NOT EXISTS FOR (n:Lifestyle_History) REQUIRE n.name IS UNIQUE;

MERGE (n:Lifestyle_History { name: "吸烟_经常吸烟", type: "吸烟", option: "经常吸烟", properties: ["daily_cigarettes", "smoke_year"], property_comments: ["每日吸烟支", "吸烟_经常吸烟_吸烟年"] });

MERGE (n:Lifestyle_History { name: "吸烟_偶尔吸烟", type: "吸烟", option: "偶尔吸烟", properties: ["smoke_year"], property_comments: ["吸烟年"] });

create (n:Lifestyle_History { name: "吸烟_被动吸烟", type: "吸烟", option: "被动吸烟" });

create (n:Lifestyle_History { name: "吸烟_已戒烟", type: "吸烟", option: "已戒烟" });

create (n:Lifestyle_History { name: "吸烟_从未吸烟", type: "吸烟", option: "从未吸烟" });

create (con:Condition { name: "吸烟", type: "lifestyle_history" })
WITH con
MATCH (n:Lifestyle_History)
WHERE n.name IN ["吸烟_经常吸烟", "吸烟_偶尔吸烟", "吸烟_被动吸烟"]
UNWIND n AS element
create (con)-[r2:has_lifestyle_history]->(element);

create (n:Lifestyle_History { name: "饮酒_经常饮酒", type: "饮酒", option: "经常饮酒" });

create (n:Lifestyle_History { name: "饮酒_从来不饮酒", type: "饮酒", option: "从来不饮酒" });

create (n:Lifestyle_History { name: "饮酒_偶尔饮酒", type: "饮酒", option: "偶尔饮酒" });

create (n:Lifestyle_History { name: "饮酒_已戒酒", type: "饮酒", option: "已戒酒" });

create (n:Lifestyle_History { name: "口味重_否", type: "口味重", option: "否" });

create (n:Lifestyle_History { name: "口味重_是", type: "口味重", option: "是" });

create (n:Lifestyle_History { name: "睡眠状况_良好", type: "睡眠状况", option: "良好" });

create (n:Lifestyle_History { name: "睡眠状况_不好", type: "睡眠状况", option: "不好" });

create (n:Lifestyle_History { name: "睡眠状况_不好_打鼾", type: "睡眠状况_不好_睡眠问题", option: "打鼾" });

MATCH (head:Lifestyle_History { name: "睡眠状况_不好" })
MATCH (tail:Lifestyle_History { name: "睡眠状况_不好_打鼾" })
WITH head, tail create (head)-[:multi_select]->(tail);

create (n:Lifestyle_History { name: "睡眠状况_不好_早醒", type: "睡眠状况_不好_睡眠问题", option: "早醒" });

MATCH (head:Lifestyle_History { name: "睡眠状况_不好" })
MATCH (tail:Lifestyle_History { name: "睡眠状况_不好_早醒" })
WITH head, tail create (head)-[:multi_select]->(tail);

create (n:Lifestyle_History { name: "睡眠状况_不好_入睡困难", type: "睡眠状况_不好_睡眠问题", option: "入睡困难" });

MATCH (head:Lifestyle_History { name: "睡眠状况_不好" })
MATCH (tail:Lifestyle_History { name: "睡眠状况_不好_入睡困难" })
WITH head, tail create (head)-[:multi_select]->(tail);

create (n:Lifestyle_History { name: "睡眠状况_不好_多梦易醒", type: "睡眠状况_不好_睡眠问题", option: "入睡困难" });

MATCH (head:Lifestyle_History { name: "睡眠状况_不好" })
MATCH (tail:Lifestyle_History { name: "睡眠状况_不好_多梦易醒" })
WITH head, tail create (head)-[:multi_select]->(tail);

create (n:Lifestyle_History { name: "经常锻炼_是", type: "经常锻炼", option: "是" });

create (n:Lifestyle_History { name: "经常锻炼_否", type: "经常锻炼", option: "否" });

create (n:Lifestyle_History { name: "妊娠", type: "特殊时期", option: "妊娠" }), (c:Condition {name: "妊娠", type: "lifestyle_history"}), (c)-[r:has_lifestyle_history]->(n);

create (n:Lifestyle_History { name: "哺乳期", type: "特殊时期", option: "哺乳期" }), (c:Condition {name: "哺乳期", type: "lifestyle_history"}), (c)-[r:has_lifestyle_history]->(n);

create (n:Lifestyle_History { name: "备孕", type: "特殊时期", option: "备孕" }), (c:Condition {name: "备孕", type: "lifestyle_history"}), (c)-[r:has_lifestyle_history]->(n);

// 家族史
MATCH (n:Family_History)
DETACH DELETE n;

MATCH (n)
WHERE n:Condition AND n.type = "family_history"
DETACH DELETE n;

CREATE CONSTRAINT family_history_name_idx IF NOT EXISTS FOR (n:Family_History) REQUIRE n.name IS UNIQUE;

create (n:Family_History { name: "高血压家族史" }),
(c:Condition { name: "高血压家族史", type: "family_history" }), (c)-[:has_family_history]->(n);

create (n:Family_History { name: "糖尿病家族史" }),
(c:Condition { name: "糖尿病家族史", type: "family_history" }), (c)-[:has_family_history]->(n);

create (n:Family_History { name: "血脂异常家族史" }),
(c:Condition { name: "血脂异常家族史", type: "family_history" }), (c)-[:has_family_history]->(n);

create (n:Family_History { name: "早发心血管病家族史" }),
(c:Condition { name: "早发心血管病家族史", type: "family_history" }), (c)-[:has_family_history]->(n);

// 检查报告

MATCH (n:Exam_Report)
DETACH DELETE n;

MATCH (n)
WHERE n:Condition AND n.type = "exam_report"
DETACH DELETE n;

create (n:Exam_Report { name: '肌酐/血清肌酐', exam: "生化检查", properties: ['shjcbg_CR_value', 'shjcbg_CR_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '总胆固醇', exam: "生化检查", properties: ['shjcbg_7_value', 'shjcbg_7_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '高密度脂蛋白胆固醇', exam: "生化检查", properties: ['shjcbg_08_value', 'shjcbg_08_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '低密度脂蛋白胆固醇', exam: "生化检查", properties: ['shjcbg_09_value', 'shjcbg_09_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '尿酸', exam: "生化检查", properties: ['shjcbg_10_value', 'shjcbg_10_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '钾', exam: "生化检查", properties: ['shjcbg_11_value', 'shjcbg_11_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '钠', exam: "生化检查", properties: ['shjcbg_12_value', 'shjcbg_12_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '氯', exam: "生化检查", properties: ['shjcbg_13_value', 'shjcbg_13_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '谷丙转氨酶（ALT）', exam: "生化检查", properties: ['shjcbg_14_value', 'shjcbg_14_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name: '谷草转氨酶（AST）', exam: "生化检查", properties: ['shjcbg_15_value', 'shjcbg_15_date'], property_comments: ["值", "检查日期"] });

create (n:Exam_Report { name:'尿蛋白', exam: '尿常规', properties: ['ncgjcbg_03_value', 'ncgjcbg_03_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'红细胞', exam: '尿常规', properties: ['ncgjcbg_04_value', 'ncgjcbg_04_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'白细胞', exam: '尿常规', properties: ['ncgjcbg_05_value', 'ncgjcbg_05_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'全程平均血压:收缩压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_03_value', 'dtxyjcbg_03_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'全程平均血压:舒张压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_04_value', 'dtxyjcbg_04_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'全程平均血压:心率/次/分钟', exam: '动态血压', properties: ['dtxyjcbg_05_value', 'dtxyjcbg_05_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'日间平均血压:收缩压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_06_value', 'dtxyjcbg_06_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'日间平均血压:舒张压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_07_value', 'dtxyjcbg_07_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'日间平均血压:心率/次/分钟', exam: '动态血压', properties: ['dtxyjcbg_08_value', 'dtxyjcbg_08_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'夜间平均血压:收缩压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_09_value', 'dtxyjcbg_09_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'夜间平均血压:舒张压/mmHg', exam: '动态血压', properties: ['dtxyjcbg_10_value', 'dtxyjcbg_10_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'夜间平均血压:心率/次/分钟', exam: '动态血压', properties: ['dtxyjcbg_11_value', 'dtxyjcbg_11_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'左室肥厚', exam: '超声心动图', properties: ['csxdtjcbg_03_date'], property_comments: ['检查日期'] });

create (n:Exam_Report { name:'左房/左室肥大/扩大', exam: '超声心动图', properties: ['csxdtjcbg_04_date'], property_comments: ['检查日期'] });

create (n:Exam_Report { name:'LVMI', exam: '超声心动图', properties: ['csxdtjcbg_05_value', 'csxdtjcbg_05_date'], property_comments: ["值", '检查日期'] });

create (n:Exam_Report { name:'动脉粥样斑块', exam: '颈动脉超声', properties: ['jdmcsjcbg_03_date'], property_comments: ['检查日期'] });

create (n:Exam_Report { name:'动脉粥样斑块长/mm', exam: '颈动脉超声', properties: ['jdmcsjcbg_04_value', 'jdmcsjcbg_04_date'], property_comments: ['值', '检查日期'] });

create (n:Exam_Report { name:'动脉粥样斑块宽/mm', exam: '颈动脉超声', properties: ['jdmcsjcbg_05_value', 'jdmcsjcbg_05_date'], property_comments: ['值', '检查日期'] });

create (n:Exam_Report { name:'左侧颈动脉IMT', exam: '颈动脉超声', properties: ['jdmcsjcbg_06_value', 'jdmcsjcbg_06_date'], property_comments: ['值', '检查日期'] });

create (n:Exam_Report { name:'出血或渗出', exam: '眼底', properties: ['ydjcbg_03_date'], property_comments: ['检查日期'] });

create (n:Exam_Report { name:'视乳头水肿', exam: '眼底', properties: ['ydjcbg_04_date'], property_comments: ['检查日期'] });

create (n:Condition { name: "微量蛋白尿>=30mg/24h", type: "exam_report", measure: "微量蛋白尿mg/24h", operand: ">", value: 30 });

create (n:Condition { name: "eGFR<60ml/min/1.73m2", type: "exam_report", measure: "eGFR", operand: "<", value: 60 });

create (n:Condition { name: "肾功能不全：eGFR<30ml/min/1.73m2", type: "exam_report", measure: "eGFR", operand: "<", value: 30 });

create (n:Condition { name: "严重肾功能不全：肌酐>3mg/dl（265umol/L）", type: "exam_report", measure: "肌酐", operand: ">", value: 3 });

create (n:Condition { name: "白蛋白/肌酐>=30mg/g", type: "exam_report", measure: "白蛋白/肌酐", operand: ">=", value: 30 });

create (n:Condition { name: "（LDL-C）>=4.9mmol/L", type: "exam_report", measure: "LDL-C", operand: ">=", value: 4.9 });

create (n:Condition { name: "（LDL-C）>=3.4mmol/L", type: "exam_report", measure: "LDL-C", operand: ">=", value: 3.4 });

create (n:Condition { name: "（LDL-C）>=2.6mmol/L", type: "exam_report", measure: "LDL-C", operand: ">=", value: 2.6 });

create (n:Condition { name: "（LDL-C）>=1.8mmol/L", type: "exam_report", measure: "LDL-C", operand: ">=", value: 1.8 });

create (n:Condition { name: "（HDL-C）<1.04mmol/L", type: "exam_report", measure: "HDL-C", operand: "<", value: 1.04 });

create (n:Condition { name: "总胆固醇（TC）>=7.2mmol/L", type: "exam_report", measure: "总胆固醇（TC）", operand: ">=", value: 7.2 });

create (n:Condition { name: "空腹血糖异常（6.1-6.9mmol/L）", type: "exam_report", measure: "空腹血糖", operand: "between", value1: 6.1 , value2: 6.9 });

create (n:Condition { name: "臂踝脉搏波速度>=18m/s", type: "exam_report", measure: "空腹血糖", operand: ">=", value: 18 });

create (n:Condition { name: "颈股脉搏波速度>10m/s", type: "exam_report", measure: "空腹血糖", operand: ">", value: 10 });

create (n:Condition { name: "踝/臂指数<=0.9", type: "exam_report", measure: "踝/臂指数", operand: "<=", value: 0.9 });

create (n:Condition { name: "电解质异常(血钾<3.5mmol/L)", type: "exam_report", measure: "血钾", operand: "<", value: 3.5 });

create (n:Condition { name: "电解质异常(血钾>5.5mmol/L)", type: "exam_report", measure: "血钾", operand: ">", value: 5.5 });

create (n:Condition { name: "心电图示至少两个导联ST段抬高", type: "exam_report" });

create (n:Condition { name: "血常规", type: "exam_report" });

create (n:Condition { name: "尿常规", type: "exam_report" });

create (n:Condition { name: "生化检查", type: "exam_report" });

create (n:Condition { name: "心电图", type: "exam_report" });

create (n:Condition { name: "动态血压监测", type: "exam_report" });

create (n:Condition { name: "超声心动图", type: "exam_report" });

create (n:Condition { name: "颈动脉超声", type: "exam_report" });

create (n:Condition { name: "尿白蛋白/肌酐", type: "exam_report" });

create (n:Condition { name: "X光", type: "exam_report" });

create (n:Condition { name: "眼底", type: "exam_report" });

// Community Server doesn't support
// CREATE CONSTRAINT blood_pressure_record_patient_no_bp_get_time_idx IF NOT EXISTS ON (m:Blood_Pressure_Record) ASSERT (m.patient_no, m.bp_get_time) IS NODE KEY;

// 基本信息

MATCH (n:Basic_Info)
DETACH DELETE n;

MATCH (n:Condition)
WHERE n.type = "basic_info"
DETACH DELETE n;

CREATE CONSTRAINT basic_info_name_idx IF NOT EXISTS FOR (n:Basic_Info) REQUIRE n.name IS UNIQUE;

create (n:Condition { name: "男>=45岁", type: "basic_info" });

create (n:Condition { name: "女>=55岁", type: "basic_info" });

create (n:Condition { name: "年龄>=40岁", type: "basic_info" });

create (n:Condition { name: "年龄<30岁", type: "basic_info" });

//初诊转诊

MATCH (n:Condition)
WHERE n.type = "screening"
DETACH DELETE n;

create (n:Condition { name: "初诊", type:"screening" });

create (n:Condition { name: "随诊", type:"screening" });

MATCH (n:Screening_Recommendation)
DETACH DELETE n;

CREATE CONSTRAINT screening_recommendation_name_idx IF NOT EXISTS FOR (n:Screening_Recommendation) REQUIRE (n.name) IS UNIQUE;

create (n:Screening_Recommendation { name: "转诊" });

create (n:Screening_Recommendation { name: "急救车转诊" });

//危险分层

MATCH (n:Condition)
WHERE n.type = "hypertension_risk_level"
DETACH DELETE n;

create (n:Condition { name: "高危", type:"hypertension_risk_level" });

MATCH (n:Condition { name: "高危", type:"hypertension_risk_level" })
MATCH (n2:Condition { name: "收缩压>=140mmHg和/或舒张压>=90mmHg", type: "blood_pressure" })
WITH n, n2
create (n)-[:has_full_condition { type:"hypertension_risk_level" }]->(n2);

MATCH (n:Condition { name: "高危", type:"hypertension_risk_level" })
MATCH (n2:Condition { name: "收缩压=130-139mmHg和/或舒张压=80-89mmHg", type: "blood_pressure" })
WITH n, n2
create (n)-[:has_condition_with_additional_risks { type:"hypertension_risk_level" }]->(n2);

MATCH (n:Condition { name: "高危" })
WITH n
MATCH (req:Condition)
WHERE req.name IN ["男>=45岁", "女>=55岁", "吸烟", "（HDL-C）<1.04mmol/L", "（LDL-C）>=3.4mmol/L", "空腹血糖异常（6.1-6.9mmol/L）", "BMI>=28"]
UNWIND req AS element
create (n)-[:bp130_80_and_any_3_cardio_risks { type:"hypertension_risk_level" }]->(element);

MATCH (n:Condition { name: "高危" })
WITH n
MATCH (req:Condition)
WHERE req.name IN ["左心室肥厚", "左房扩大", "颈动脉粥样硬化", "臂踝脉搏波速度>=18m/s", "颈股脉搏波速度>10m/s", "踝/臂指数<=0.9" ]
UNWIND req AS element
create (n)-[:bp130_80_and_any_1_target_organ_risk { type:"hypertension_risk_level" }]->(element);

MATCH (n:Condition { name: "高危" })
WITH n
MATCH (req:Condition)
WHERE req.name IN ["脑出血", "缺血性脑卒中", "短暂性脑缺血发作",
"冠心病", "心力衰竭", "心房颤动",
"（LDL-C）>=4.9mmol/L", "总胆固醇（TC）>=7.2mmol/L",
"肾病", "微量蛋白尿>=30mg/24h", "eGFR<60ml/min/1.73m2", "白蛋白/肌酐>=30mg/g",
"糖尿病",
"主动脉疾病或外周血管疾病",
"视网膜病变"]
UNWIND req AS element
create (n)-[:bp130_80_and_any_1_complication_risk { type:"hypertension_risk_level" }]->(element);

MATCH (n:Exam_Recommendation { name: "高血压评估检查建议" })
DETACH DELETE n;

CREATE CONSTRAINT exam_recommendation_name_idx IF NOT EXISTS FOR (n:Exam_Recommendation) REQUIRE (n.name) IS UNIQUE;

create (n:Exam_Recommendation { name: "高血压评估检查建议" })
WITH n
MATCH (req:Condition)
WHERE req.name IN [
"高血压",
"收缩压>=140mmHg",
"舒张压>=90mmHg"
]
UNWIND req AS element
create (n)-[:requires]->(element);

MATCH (n:Exam_Recommendation { name: "高血压评估检查建议" })
WITH n
MATCH (req1:Condition)
WHERE req1.name IN [
"糖尿病",
"脑卒中",
"冠心病",
"心力衰竭",
"心房颤动",
"肾病",
"外周动脉粥样硬化",
"高血压家族史",
"糖尿病家族史",
"血脂异常家族史",
"早发心血管病家族史",
"吸烟",
"心率",
"身高",
"体重",
"腰围",
"下肢水肿",
"血常规",
"尿常规",
"生化检查",
"心电图"
]
UNWIND req1 AS element
create (n)-[:recommends]->(element);

MATCH (n:Exam_Recommendation { name: "高血压评估检查建议" })
WITH n
MATCH (req2:Condition)
WHERE req2.name IN [
"动态血压监测",
"超声心动图",
"颈动脉超声",
"尿白蛋白/肌酐",
"X光",
"眼底"
]
UNWIND req2 AS element
create (n)-[:suggests]->(element);
