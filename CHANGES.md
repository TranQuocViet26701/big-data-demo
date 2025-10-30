# Migration to BDE2020 Ecosystem - Change Log

This document summarizes the migration from mixed Docker images to a unified **bde2020** ecosystem.

## 📋 Summary of Changes

All services now use **bde2020** images for better integration and compatibility.

---

## 🔄 Updated Services

### 1. **Spark Services** (Updated from Bitnami)

**Before:**
```yaml
spark-master:
  image: bitnami/spark:3.3

spark-worker:
  image: bitnami/spark:3.3
```

**After:**
```yaml
spark-master:
  image: bde2020/spark-master:3.3.0-hadoop3.3

spark-worker:
  image: bde2020/spark-worker:3.3.0-hadoop3.3
```

**Benefits:**
- Native Hadoop 3.3 integration
- Consistent with bde2020/hadoop-namenode and bde2020/hadoop-datanode
- Simplified HDFS connectivity via `CORE_CONF_fs_defaultFS`

---

### 2. **HBase Service** (Updated from harisekhon to bde2020)

**Before:**
```yaml
hbase-master:
  image: harisekhon/hbase:1.4
  # Required separate ZooKeeper service
```

**After:**
```yaml
hbase:
  image: bde2020/hbase-standalone:1.0.0-hbase1.2.6
  # Built-in ZooKeeper - no separate service needed
```

**Benefits:**
- Standalone mode with built-in ZooKeeper
- Simplified architecture (removed separate ZooKeeper container)
- Better integration with bde2020 Hadoop HDFS
- Reduced resource usage

---

### 3. **ZooKeeper Service** (Removed)

**Before:**
```yaml
zookeeper:
  image: zookeeper:3.7
  # Separate container for HBase coordination
```

**After:**
- **Removed** - Now built into `bde2020/hbase-standalone`

**Benefits:**
- Reduced container count from 7 to 6 services
- Simplified configuration
- Lower memory footprint

---

## 🗂️ File Changes

### docker-compose.yml
- Updated Spark master and worker to bde2020 images
- Updated HBase to bde2020/hbase-standalone
- Removed standalone ZooKeeper service
- Added `hbase_data` volume
- Updated dashboard environment variables (hbase-master → hbase)

### scripts/run-spark-job.sh
```bash
# Before
docker exec spark-master spark-submit \

# After
docker exec spark-master /spark/bin/spark-submit \
```

### scripts/sample-queries.sh
```bash
# Before
docker exec hbase-master /bin/bash -c "echo 'list' | /hbase/bin/hbase shell"

# After
docker exec hbase /bin/bash -c "echo 'list' | /opt/hbase/bin/hbase shell"
```

### scripts/init-hbase.sh
```bash
# Before
docker exec hbase-master /bin/bash -c "... | /hbase/bin/hbase shell"

# After
docker exec hbase /bin/bash -c "... | /opt/hbase/bin/hbase shell"
```

### .env
```bash
# Updated HBase version and added RegionServer ports
HBASE_VERSION=1.2.6  # was 1.4
HBASE_REGIONSERVER_PORT=16020
HBASE_REGIONSERVER_UI_PORT=16030
HBASE_ZOOKEEPER_PORT=2181  # moved from separate section
```

### README.md
- Updated component table (removed ZooKeeper as separate service)
- Updated troubleshooting section
- Updated technology versions

---

## 📦 Current Architecture

### Service Stack (All BDE2020)

| Service | Image | Version | Purpose |
|---------|-------|---------|---------|
| **namenode** | bde2020/hadoop-namenode | 3.2.1 | HDFS NameNode |
| **datanode** | bde2020/hadoop-datanode | 3.2.1 | HDFS DataNode |
| **spark-master** | bde2020/spark-master | 3.3.0-hadoop3.3 | Spark Master |
| **spark-worker** | bde2020/spark-worker | 3.3.0-hadoop3.3 | Spark Worker |
| **hbase** | bde2020/hbase-standalone | 1.2.6 | HBase + ZooKeeper |
| **dashboard** | Custom (Python 3.10) | - | Streamlit UI |

---

## 🎯 Benefits of Migration

### 1. **Unified Ecosystem**
- All Big Data services use bde2020 images
- Consistent environment variable patterns
- Better inter-service communication

### 2. **Simplified Architecture**
- Reduced from 7 to 6 containers
- HBase includes ZooKeeper (no separate service needed)
- Cleaner dependency graph

### 3. **Better Integration**
- Spark natively supports Hadoop 3.3
- Direct HDFS access without additional configuration
- Consistent network configuration

### 4. **Resource Efficiency**
- Fewer containers = less memory usage
- HBase standalone mode optimized for demos
- Smaller overall footprint

---

## 🔧 Port Mapping (Updated)

| Port | Service | Description |
|------|---------|-------------|
| 9000 | HDFS | NameNode port |
| 9870 | HDFS | NameNode Web UI |
| 9864 | HDFS | DataNode Web UI |
| 7077 | Spark | Master port |
| 8080 | Spark | Master Web UI |
| 8081 | Spark | Worker Web UI |
| 16000 | HBase | Master port |
| 16010 | HBase | Master Web UI |
| 16020 | HBase | RegionServer port |
| 16030 | HBase | RegionServer Web UI |
| 9090 | HBase | Thrift Server |
| 2181 | HBase | ZooKeeper (built-in) |
| 8501 | Dashboard | Streamlit Web UI |

---

## ✅ Testing Checklist

After migration, verify:

- [ ] All containers start successfully: `docker-compose up -d`
- [ ] HDFS Web UI accessible: http://localhost:9870
- [ ] Spark Master UI accessible: http://localhost:8080
- [ ] HBase Master UI accessible: http://localhost:16010
- [ ] Data can be uploaded to HDFS: `bash scripts/init-hdfs.sh`
- [ ] HBase tables can be created: `bash scripts/init-hbase.sh`
- [ ] Spark job runs successfully: `bash scripts/run-spark-job.sh`
- [ ] Dashboard loads: http://localhost:8501
- [ ] Sample queries work: `bash scripts/sample-queries.sh`

---

## 🚀 Migration Complete

The project now uses a fully integrated bde2020 ecosystem for optimal compatibility and performance!

**Date:** 2024-10-26
**Status:** ✅ Complete
