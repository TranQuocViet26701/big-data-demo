#!/bin/bash

###############################################################################
# Initialize HDFS - Upload clickstream data
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Initializing HDFS${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if data file exists
if [ ! -f "data/clickstream_large.txt" ]; then
    echo -e "${YELLOW}⚠️  Data file not found. Generating now...${NC}"
    cd data
    python3 generate_clickstream.py 10000
    cd ..
fi

echo -e "${YELLOW}📁 Creating HDFS directory structure...${NC}"
docker exec namenode hdfs dfs -mkdir -p /data

echo -e "${YELLOW}📤 Uploading clickstream data to HDFS...${NC}"
docker exec namenode hdfs dfs -put -f /data/clickstream_large.txt /data/

echo -e "${GREEN}✅ Data uploaded successfully!${NC}\n"

echo -e "${YELLOW}📊 Verifying upload...${NC}"
docker exec namenode hdfs dfs -ls /data/

echo -e "\n${YELLOW}📈 File statistics:${NC}"
docker exec namenode hdfs dfs -du -h /data/clickstream_large.txt

echo -e "\n${GREEN}✅ HDFS initialization complete!${NC}"
echo -e "${BLUE}🌐 View in HDFS Web UI: http://localhost:9870${NC}"
echo -e "${BLUE}   Navigate to: Utilities > Browse the file system > /data${NC}\n"
