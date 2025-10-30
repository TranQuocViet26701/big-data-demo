#!/bin/bash

###############################################################################
# Sample Queries - Demonstrate HDFS, Spark, and HBase interactions
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

# HDFS Queries
hdfs_queries() {
    print_header "📁 HDFS Sample Queries"

    echo -e "${YELLOW}1. List all files in /data directory:${NC}"
    docker exec namenode hdfs dfs -ls /data/
    echo ""

    echo -e "${YELLOW}2. Show file statistics:${NC}"
    docker exec namenode hdfs dfs -du -h /data/
    echo ""

    echo -e "${YELLOW}3. View first 10 lines of clickstream data:${NC}"
    docker exec namenode hdfs dfs -cat /data/clickstream_large.txt | head -10
    echo ""

    echo -e "${YELLOW}4. Count total lines in clickstream:${NC}"
    docker exec namenode hdfs dfs -cat /data/clickstream_large.txt | wc -l
    echo ""

    echo -e "${YELLOW}5. Get file system statistics:${NC}"
    docker exec namenode hdfs dfsadmin -report
    echo ""
}

# HBase Queries
hbase_queries() {
    print_header "🗄️  HBase Sample Queries"

    echo -e "${YELLOW}1. List all tables:${NC}"
    docker exec hbase /bin/bash -c "echo 'list' | /opt/hbase/bin/hbase shell -n"
    echo ""

    echo -e "${YELLOW}2. Describe amazon_recs table:${NC}"
    docker exec hbase /bin/bash -c "echo \"describe 'amazon_recs'\" | /opt/hbase/bin/hbase shell -n"
    echo ""

    echo -e "${YELLOW}3. Scan all data in amazon_recs:${NC}"
    docker exec hbase /bin/bash -c "echo \"scan 'amazon_recs'\" | /opt/hbase/bin/hbase shell -n"
    echo ""

    echo -e "${YELLOW}4. Get Top 5 recommendations (key query from demo):${NC}"
    docker exec hbase /bin/bash -c "echo \"get 'amazon_recs', 'top_5_hot'\" | /opt/hbase/bin/hbase shell -n"
    echo ""

    echo -e "${YELLOW}5. Count rows in table:${NC}"
    docker exec hbase /bin/bash -c "echo \"count 'amazon_recs'\" | /opt/hbase/bin/hbase shell -n"
    echo ""
}

# Spark Queries (Interactive)
spark_queries() {
    print_header "⚡ Spark Sample Queries"

    echo -e "${YELLOW}Running interactive Spark analysis...${NC}\n"

    docker exec spark-master /spark/bin/spark-submit \
        --master spark://spark-master:7077 \
        --deploy-mode client \
        /opt/spark-apps/find_recommendations.py

    echo -e "${GREEN}✅ Spark analysis complete!${NC}\n"
}

# Data Analysis Queries
analysis_queries() {
    print_header "📊 Quick Data Analysis"

    echo -e "${YELLOW}1. Top 5 most purchased products (from HDFS):${NC}"
    docker exec namenode hdfs dfs -cat /data/clickstream_large.txt | \
        grep "purchase" | \
        cut -d',' -f5 | \
        sort | uniq -c | \
        sort -rn | \
        head -5
    echo ""

    echo -e "${YELLOW}2. Action distribution:${NC}"
    docker exec namenode hdfs dfs -cat /data/clickstream_large.txt | \
        tail -n +2 | \
        cut -d',' -f7 | \
        sort | uniq -c | \
        sort -rn
    echo ""

    echo -e "${YELLOW}3. Category distribution:${NC}"
    docker exec namenode hdfs dfs -cat /data/clickstream_large.txt | \
        tail -n +2 | \
        cut -d',' -f6 | \
        sort | uniq -c | \
        sort -rn
    echo ""
}

# Main menu
show_menu() {
    print_header "🔍 Big Data Demo - Sample Queries"

    echo "Select query type to run:"
    echo ""
    echo "  1) HDFS Queries"
    echo "  2) HBase Queries"
    echo "  3) Spark Analysis"
    echo "  4) Quick Data Analysis"
    echo "  5) Run All"
    echo "  6) Exit"
    echo ""
    read -p "Enter your choice [1-6]: " choice

    case $choice in
        1) hdfs_queries ;;
        2) hbase_queries ;;
        3) spark_queries ;;
        4) analysis_queries ;;
        5)
            hdfs_queries
            hbase_queries
            analysis_queries
            ;;
        6) exit 0 ;;
        *) echo -e "${RED}Invalid choice${NC}" ;;
    esac

    echo -e "\n${GREEN}Press Enter to return to menu...${NC}"
    read
    show_menu
}

# Run menu if no arguments, otherwise run specific query
if [ $# -eq 0 ]; then
    show_menu
else
    case $1 in
        hdfs) hdfs_queries ;;
        hbase) hbase_queries ;;
        spark) spark_queries ;;
        analysis) analysis_queries ;;
        all)
            hdfs_queries
            hbase_queries
            analysis_queries
            ;;
        *) echo -e "${RED}Unknown option: $1${NC}"
           echo "Usage: $0 [hdfs|hbase|spark|analysis|all]"
           exit 1
           ;;
    esac
fi
