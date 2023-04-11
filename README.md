# drug_recommendation

万众益心的基于知识图谱的用药推荐系统

交付时间：2023-01-10

# 运行方法

1. 把.env_production 复制到.env。里面的数据库连接方式做一定的修改
2. 安装并运行 Neo4j 版本 4.x，社区版或企业版都支持
   - settings 配置上加：
     dbms.db.timezone=SYSTEM
     db.temporal.timezone=Asia/Shanghai
3. 安装 Python 3.9. 执行 python3 -m pip install -r requirements.txt 安装依赖
4. 执行 Cypher 脚本，类似这样的 Linux Shell 指令: cypher-shell -f script/drug_recommendation_model.cypher
5. 执行规则导入的 Python 脚本，执行这个脚本要 10 多分钟左右，要等待执行完备：python3 load_drug_condition.py
6. 执行 Python 服务：python3 recommend_drug.py

# Python/Neo4j 服务接口：

- 地址（当然，域名和端口都可以改）：http://localhost:3450/recommend_drug
- 输入：JSON POST: { "patient_no": "WZYX00005493" }
  - 例如：curl -X POST http://8.130.179.199:3450/recommend_drug -H 'Content-Type: application/json' -d '{"patient_no":"HZ000001"}'
- 然后，拿到一个 JSON 回传就是成功了
