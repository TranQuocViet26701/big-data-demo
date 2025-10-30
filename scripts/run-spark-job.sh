#!/bin/bash

###############################################################################
# Run Spark Job - Analyze clickstream and generate recommendations
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running Spark Job${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}🚀 Submitting Spark job to cluster...${NC}\n"

# Submit Spark job
docker exec spark-master /spark/bin/spark-submit \
    --master spark://spark-master:7077 \
    --deploy-mode client \
    --conf spark.driver.memory=1g \
    --conf spark.executor.memory=1g \
    --conf spark.executor.cores=2 \
    /opt/spark-apps/find_recommendations.py

echo -e "\n${GREEN}✅ Spark job completed!${NC}\n"

echo -e "${YELLOW}📊 Viewing results...${NC}"
echo -e "${BLUE}Results have been saved to: /data/recommendations_output${NC}\n"

# Display results
echo -e "${YELLOW}📁 Output files:${NC}"
docker exec namenode hdfs dfs -ls -R /data/recommendations_output || true

echo -e "\n${YELLOW}📈 Sample results (JSON format):${NC}"
docker exec namenode hdfs dfs -cat /data/recommendations_output/top_5_products_json/*.json 2>/dev/null | head -20 || echo "Files not yet created"

echo -e "\n${GREEN}✅ Job execution complete!${NC}"
echo -e "${BLUE}🌐 View job details in Spark Web UI: http://localhost:8080${NC}"
echo -e "${BLUE}🌐 View results in Dashboard: http://localhost:8501${NC}\n"

echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "   1. Check Spark Web UI for job statistics"
echo -e "   2. View recommendations in the Streamlit dashboard"
echo -e "   3. Run sample queries: bash scripts/sample-queries.sh"
echo ""
