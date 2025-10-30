#!/bin/bash
###############################################################################
# Spark-HBase Job Runner
# Installs dependencies and runs Spark job with HBase integration
###############################################################################

set -e  # Exit on error

echo "=========================================================================="
echo "🚀 Spark-HBase Job Runner"
echo "=========================================================================="

# Configuration
SPARK_MASTER="${SPARK_MASTER:-spark://spark-master:7077}"
HDFS_PATH="${HDFS_PATH:-hdfs://namenode:9000/data/clickstream_large.txt}"
HBASE_HOST="${HBASE_HOST:-hbase}"
HBASE_PORT="${HBASE_PORT:-9090}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo ""
echo "📋 Configuration:"
echo "   Spark Master: $SPARK_MASTER"
echo "   HDFS Path: $HDFS_PATH"
echo "   HBase Host: $HBASE_HOST"
echo "   HBase Port: $HBASE_PORT"
echo ""

# Step 1: Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -q -r "$SCRIPT_DIR/requirements.txt"
    echo "✅ Dependencies installed"
else
    echo "⚠️  requirements.txt not found, installing manually..."
    pip install -q happybase thrift
    echo "✅ Dependencies installed"
fi

# Step 2: Check HBase connectivity
echo ""
echo "🔍 Checking HBase connectivity..."
python3 <<EOF
import sys
try:
    import happybase
    conn = happybase.Connection('$HBASE_HOST', port=$HBASE_PORT, timeout=5000)
    tables = conn.tables()
    print(f"✅ Successfully connected to HBase at $HBASE_HOST:$HBASE_PORT")
    print(f"   Available tables: {[t.decode() for t in tables]}")
    conn.close()
except Exception as e:
    print(f"❌ Failed to connect to HBase: {str(e)}")
    print("   Make sure HBase container is running and Thrift server is accessible")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  HBase connectivity check failed!"
    echo "   You can still continue, but the job may fail during HBase write"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 3: Setup HBase tables (optional)
echo ""
read -p "Do you want to setup/verify HBase tables? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Setting up HBase tables..."
    python3 "$SCRIPT_DIR/setup_hbase_tables.py" "$HBASE_HOST" "$HBASE_PORT"
fi

# Step 4: Run Spark job
echo ""
echo "=========================================================================="
echo "🚀 Submitting Spark job..."
echo "=========================================================================="
echo ""

spark-submit \
    --master "$SPARK_MASTER" \
    --conf spark.executor.memory=1g \
    --conf spark.executor.cores=2 \
    --conf spark.driver.memory=1g \
    --py-files "$SCRIPT_DIR/hbase_connector.py" \
    "$SCRIPT_DIR/find_recommendations.py" \
    "$HDFS_PATH"

EXIT_CODE=$?

echo ""
echo "=========================================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Spark job completed successfully!"
    echo "=========================================================================="
    echo ""
    echo "📊 You can now query the recommendations from HBase:"
    echo "   docker exec -it hbase hbase shell"
    echo "   > scan 'recommendations', {LIMIT => 10}"
    echo ""
else
    echo "❌ Spark job failed with exit code $EXIT_CODE"
    echo "=========================================================================="
    exit $EXIT_CODE
fi
