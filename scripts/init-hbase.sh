#!/bin/bash

###############################################################################
# Initialize HBase - Create tables for recommendations
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Initializing HBase${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}⏳ Waiting for HBase to be ready...${NC}"
sleep 20

echo -e "${YELLOW}📋 Creating HBase table: amazon_recs${NC}"

# Create table using HBase shell
docker exec hbase /bin/bash -c "echo \"
create 'amazon_recs', 'recommendations', 'metadata'
put 'amazon_recs', 'top_5_hot', 'metadata:status', 'pending'
put 'amazon_recs', 'top_5_hot', 'metadata:last_updated', 'Not yet processed'
list
describe 'amazon_recs'
scan 'amazon_recs'
\" | /opt/hbase/bin/hbase shell"

echo -e "\n${GREEN}✅ HBase initialization complete!${NC}"
echo -e "${BLUE}🌐 View in HBase Web UI: http://localhost:16010${NC}"
echo -e "${BLUE}   Navigate to: Table Details > amazon_recs${NC}\n"

echo -e "${YELLOW}📝 Table Structure:${NC}"
echo -e "   Table Name: amazon_recs"
echo -e "   Row Key: top_5_hot"
echo -e "   Column Families:"
echo -e "     - recommendations: stores product recommendations"
echo -e "     - metadata: stores job metadata"
echo ""
