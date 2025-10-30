# Spark-HBase Integration Guide

This guide explains how to feed data from Apache Spark into HBase for real-time serving.

## Architecture Overview

```
HDFS (Raw Data) → Spark (Processing) → HBase (Real-time Storage)
```

### Data Flow:
1. **HDFS**: Stores large clickstream datasets
2. **Spark**: Processes data in parallel, computes recommendations
3. **HBase**: Stores results for instant querying

## Files Created

| File | Purpose |
|------|---------|
| `hbase_connector.py` | Python wrapper for HBase operations using happybase |
| `setup_hbase_tables.py` | Script to create/configure HBase tables |
| `find_recommendations.py` | **Modified** - Now writes to HBase instead of CSV |
| `run_with_hbase.sh` | Convenient script to run Spark job with HBase |
| `requirements.txt` | Python dependencies (happybase, thrift) |

## Prerequisites

### 1. Install Dependencies in Spark Container

```bash
# Install build tools (required for happybase)
docker exec spark-master apk add --no-cache gcc g++ musl-dev python3-dev

# Install Python libraries
docker exec spark-master pip3 install happybase thrift
```

### 2. Ensure HBase is Running

```bash
# Check HBase status
docker-compose ps hbase

# Restart HBase if needed
docker-compose restart hbase

# Verify Thrift server is accessible
docker exec spark-master python3 -c "
import happybase
conn = happybase.Connection('hbase', port=9090, timeout=10000)
print('✅ Connected!', conn.tables())
conn.close()
"
```

## Usage

### Method 1: Using the Convenience Script (Recommended)

```bash
# Enter spark-master container
docker exec -it spark-master bash

# Run the script
cd /opt/spark-apps
bash run_with_hbase.sh
```

The script will:
- ✅ Install dependencies automatically
- ✅ Check HBase connectivity
- ✅ Offer to setup tables
- ✅ Submit Spark job
- ✅ Display results

### Method 2: Manual Setup

#### Step 1: Create HBase Tables

```bash
# Enter spark-master container
docker exec -it spark-master bash

# Run table setup
cd /opt/spark-apps
python3 setup_hbase_tables.py hbase 9090
```

This creates the `recommendations` table with:
- **Column Family**: `info`
- **Columns**: product_name, category, purchases, clicks, views, hot_score, etc.
- **Row Key**: product_id

#### Step 2: Run Spark Job

```bash
# Submit Spark job
spark-submit \
  --master spark://spark-master:7077 \
  --py-files /opt/spark-apps/hbase_connector.py \
  /opt/spark-apps/find_recommendations.py \
  hdfs://namenode:9000/data/clickstream_large.txt
```

#### Step 3: Query Results from HBase

```bash
# Enter HBase shell
docker exec -it hbase hbase shell

# Scan recommendations table
scan 'recommendations', {LIMIT => 10}

# Get specific product
get 'recommendations', 'PROD_001'

# Count records
count 'recommendations'

# Exit
exit
```

## HBase Data Model

### Table: `recommendations`

| Row Key | Column Family | Column | Example Value |
|---------|---------------|--------|---------------|
| PROD_001 | info | product_name | "Wireless Mouse" |
| PROD_001 | info | category | "Electronics" |
| PROD_001 | info | purchases | "150" |
| PROD_001 | info | clicks | "450" |
| PROD_001 | info | views | "1200" |
| PROD_001 | info | hot_score | "3600" |
| PROD_001 | info | total_interactions | "1800" |
| PROD_001 | info | avg_price | "29.99" |

## Code Examples

### Reading from HBase (Python)

```python
from hbase_connector import HBaseConnector

# Create connector
connector = HBaseConnector(host='hbase', port=9090, table_name='recommendations')

# Read top 5 products
rows = connector.read_table(limit=5)

for row in rows:
    print(f"Product: {row['product_name']}")
    print(f"Hot Score: {row['hot_score']}")
    print(f"Purchases: {row['purchases']}")
    print("---")
```

### Writing DataFrame to HBase

```python
from pyspark.sql import SparkSession
from hbase_connector import dataframe_to_hbase

# Create Spark session
spark = SparkSession.builder.appName("test").getOrCreate()

# Create sample DataFrame
data = [
    ("PROD_001", "Product A", "Category A", 100, 50.0),
    ("PROD_002", "Product B", "Category B", 200, 75.0)
]
columns = ["product_id", "product_name", "category", "purchases", "hot_score"]
df = spark.createDataFrame(data, columns)

# Write to HBase
dataframe_to_hbase(
    df,
    table_name='recommendations',
    row_key_field='product_id',
    hbase_host='hbase',
    hbase_port=9090
)
```

## Troubleshooting

### Issue: "Connection timeout" or "Cannot connect to HBase"

**Solution:**
```bash
# Restart HBase
docker-compose restart hbase

# Wait 20 seconds for services to start
sleep 20

# Test connection
docker exec spark-master python3 -c "
import happybase
conn = happybase.Connection('hbase', port=9090, timeout=10000)
print(conn.tables())
"
```

### Issue: "happybase module not found"

**Solution:**
```bash
# Install in spark-master
docker exec spark-master apk add gcc g++ musl-dev python3-dev
docker exec spark-master pip3 install happybase thrift
```

### Issue: "Table does not exist"

**Solution:**
```bash
# Create table manually
docker exec spark-master python3 /opt/spark-apps/setup_hbase_tables.py hbase 9090
```

### Issue: "KeeperException: NoNode for /hbase/master"

**Solution:**
```bash
# HBase may not be fully initialized, restart it
docker-compose restart hbase
sleep 30
```

## Performance Tips

1. **Batch Writes**: The connector uses `foreachPartition()` for efficient batch writes
2. **Partitioning**: Increase DataFrame partitions for better parallelism:
   ```python
   df = df.repartition(10)  # 10 partitions
   dataframe_to_hbase(df, ...)
   ```
3. **Connection Pooling**: Each partition creates its own HBase connection
4. **Row Key Design**: Use product_id as row key for fast lookups

## Configuration

### HBase Connection Settings

Default settings in `hbase_connector.py`:
```python
host='hbase'           # HBase Thrift server hostname
port=9090              # Thrift server port
timeout=10000          # Connection timeout (ms)
table_name='recommendations'  # Target table
```

### Spark Submit Options

```bash
spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.executor.memory=1g \
  --conf spark.executor.cores=2 \
  --conf spark.driver.memory=1g \
  --py-files /opt/spark-apps/hbase_connector.py \
  /opt/spark-apps/find_recommendations.py
```

## Production Considerations

1. **Error Handling**: The code includes fallback to HDFS if HBase writes fail
2. **Backup**: Set `save_backup=True` to keep CSV/JSON backups
3. **Monitoring**: Check Spark Web UI (http://localhost:8080) for job progress
4. **HBase Web UI**: Monitor at http://localhost:16010

## Next Steps

1. ✅ Data is now in HBase for real-time access
2. Build a REST API to serve recommendations
3. Create a dashboard to visualize results
4. Set up scheduled Spark jobs for regular updates

## Additional Resources

- **Spark Documentation**: https://spark.apache.org/docs/latest/
- **HBase Documentation**: https://hbase.apache.org/book.html
- **Happybase Documentation**: https://happybase.readthedocs.io/
- **Thrift Protocol**: https://thrift.apache.org/

---

**Generated with Spark-HBase Integration** 🚀
