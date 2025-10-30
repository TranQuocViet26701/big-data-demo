# 🎯 Big Data Demo: Amazon Recommendation System

A comprehensive demonstration of Big Data architecture using **Hadoop (HDFS)**, **Apache Spark**, and **HBase** to build an Amazon-style product recommendation system.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Demo Workflow](#demo-workflow)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Troubleshooting](#troubleshooting)
- [Technologies](#technologies)

---

## 🎬 Overview

This project demonstrates a complete Big Data pipeline that:

1. **Stores** 10,000 clickstream records in **HDFS** (simulating Amazon user behavior)
2. **Processes** the data using **Apache Spark** to find Top 5 hottest products
3. **Serves** results via **HBase** for instant retrieval (<1ms)
4. **Visualizes** everything in a **Streamlit dashboard**

### 🎯 Learning Objectives

- Understand the role of each Big Data component
- See how HDFS, Spark, and HBase work together
- Learn batch processing vs. real-time serving patterns
- Practice with production-like Big Data architecture

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│              Streamlit Dashboard (Port 8501)                │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Query (< 1ms)
                            │
┌─────────────────────────────────────────────────────────────┐
│                  SERVING LAYER (HBase)                      │
│  • Real-time queries     • NoSQL database                   │
│  • Random access         • Port 16010                       │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Write results
                            │
┌─────────────────────────────────────────────────────────────┐
│             PROCESSING LAYER (Apache Spark)                 │
│  • Batch analytics       • Distributed processing           │
│  • GroupBy/Aggregation   • Port 8080                        │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ Read data
                            │
┌─────────────────────────────────────────────────────────────┐
│              STORAGE LAYER (Hadoop HDFS)                    │
│  • Data Lake             • Distributed storage              │
│  • 10K+ records          • Port 9870                        │
└─────────────────────────────────────────────────────────────┘
```

### Component Roles

| Component | Role | Why We Need It |
|-----------|------|----------------|
| **HDFS** | Data Lake | Stores massive amounts of raw data cheaply and reliably |
| **Spark** | Analytics Engine | Processes large datasets quickly in parallel |
| **HBase** | Serving Layer | Provides instant access to pre-computed results (includes ZooKeeper) |
| **Streamlit** | Dashboard | Visualizes the entire system |

---

## 📦 Prerequisites

Before you begin, ensure you have:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python 3** (version 3.8+)
- **8GB RAM** minimum (recommended: 16GB)
- **10GB free disk space**

### Installation

**macOS:**
```bash
brew install docker docker-compose
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose python3
```

**Windows:**
- Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone or navigate to the project directory
cd big-data-demo

# Make scripts executable
chmod +x scripts/*.sh
chmod +x data/generate_clickstream.py

# Run complete setup (this will take 5-10 minutes)
bash scripts/setup.sh
```

This single command will:
1. ✅ Generate 10,000 clickstream records
2. ✅ Start all Docker services
3. ✅ Initialize HDFS with data
4. ✅ Create HBase tables
5. ✅ Launch the dashboard

### Option 2: Manual Setup

```bash
# 1. Generate clickstream data
cd data
python3 generate_clickstream.py 10000
cd ..

# 2. Start Docker services
docker-compose up -d

# 3. Wait for services to start (30 seconds)
sleep 30

# 4. Initialize HDFS
bash scripts/init-hdfs.sh

# 5. Initialize HBase
bash scripts/init-hbase.sh
```

---

## 🎮 Demo Workflow

Follow these steps to demonstrate the complete Big Data pipeline:

### Bước 1: HDFS - Data Storage (5 minutes)

**Goal:** Show how raw data is stored in HDFS

1. Open HDFS Web UI: http://localhost:9870
2. Navigate to: **Utilities** → **Browse the file system** → `/data`
3. View `clickstream_large.txt`
4. Show file size and block distribution

**Key Points:**
- HDFS automatically splits files into blocks (128MB default)
- Data is replicated for fault tolerance
- Cheap, scalable storage for massive datasets

### Bước 2: Spark - Data Processing (10 minutes)

**Goal:** Demonstrate batch analytics on large datasets

```bash
# Run the Spark job
bash scripts/run-spark-job.sh
```

**OR** use the Streamlit dashboard:
1. Open Dashboard: http://localhost:8501
2. Navigate to **⚡ Spark** page
3. Click **"Run Spark Job"**

**Watch the job:**
1. Open Spark Web UI: http://localhost:8080
2. View job stages and tasks
3. See distributed processing in action

**Key Points:**
- Spark reads 10,000 records from HDFS
- Performs GroupBy and Aggregation
- Finds Top 5 hottest products
- Writes results for HBase

### Bước 3: HBase - Real-Time Serving (5 minutes)

**Goal:** Show instant query response times

**Via Dashboard:**
1. Go to **🗄️ HBase** page in dashboard
2. Click **"Get Top 5 Hot Products"**
3. See results in <1ms

**Via HBase Shell:**
```bash
docker exec -it hbase-master /hbase/bin/hbase shell

# Inside HBase shell:
get 'amazon_recs', 'top_5_hot'
scan 'amazon_recs'
```

**Key Points:**
- HBase provides random access to specific rows
- Response time < 1 millisecond
- Perfect for serving web applications
- This is how Amazon shows recommendations instantly

---

## 📁 Project Structure

```
big-data-demo/
├── README.md                    # This file
├── demo_script.md              # Vietnamese demo script
├── docker-compose.yml          # Docker orchestration
├── .env                        # Environment variables
├── .gitignore                  # Git ignore file
│
├── data/                       # Data generation
│   └── generate_clickstream.py # Generate sample data
│
├── spark/                      # Spark jobs
│   ├── find_recommendations.py # Main analysis job
│   └── requirements.txt        # Python dependencies
│
├── scripts/                    # Automation scripts
│   ├── setup.sh               # Complete setup
│   ├── init-hdfs.sh          # Initialize HDFS
│   ├── init-hbase.sh         # Initialize HBase
│   ├── run-spark-job.sh      # Run Spark job
│   └── sample-queries.sh     # Demo queries
│
├── dashboard/                  # Streamlit dashboard
│   ├── streamlit_app.py       # Main app
│   ├── requirements.txt       # Dashboard dependencies
│   ├── Dockerfile             # Dashboard container
│   └── .streamlit/
│       └── config.toml        # Streamlit config
│
└── config/                     # Configuration files
    └── hbase-site.xml         # HBase configuration
```

---

## 📖 Usage Guide

### Access Web Interfaces

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit Dashboard** | http://localhost:8501 | Main interface |
| **HDFS NameNode UI** | http://localhost:9870 | Browse HDFS files |
| **Spark Master UI** | http://localhost:8080 | View Spark jobs |
| **HBase Master UI** | http://localhost:16010 | Monitor HBase |

### Running Sample Queries

```bash
# Interactive menu
bash scripts/sample-queries.sh

# Or run specific queries
bash scripts/sample-queries.sh hdfs    # HDFS queries
bash scripts/sample-queries.sh hbase   # HBase queries
bash scripts/sample-queries.sh spark   # Spark analysis
bash scripts/sample-queries.sh all     # Run all queries
```

### Viewing Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f spark-master
docker-compose logs -f namenode
docker-compose logs -f hbase-master
docker-compose logs -f dashboard
```

### Stopping/Restarting Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean start)
docker-compose down -v

# Restart specific service
docker-compose restart spark-master

# Start services
docker-compose up -d
```

---

## 🔧 Troubleshooting

### Services Not Starting

**Problem:** Docker containers fail to start

**Solution:**
```bash
# Check Docker is running
docker ps

# Check logs
docker-compose logs

# Restart Docker daemon
# macOS: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Clean start
docker-compose down -v
docker-compose up -d
```

### HDFS Connection Issues

**Problem:** Cannot connect to HDFS

**Solution:**
```bash
# Check namenode is running
docker ps | grep namenode

# Check namenode logs
docker logs namenode

# Restart namenode
docker-compose restart namenode

# Wait for safe mode to exit
docker exec namenode hdfs dfsadmin -safemode wait
```

### Spark Job Fails

**Problem:** Spark job returns errors

**Solution:**
```bash
# Check Spark master is running
docker ps | grep spark-master

# View Spark logs
docker logs spark-master

# Check file exists in HDFS
docker exec namenode hdfs dfs -ls /data/

# Re-upload data if needed
bash scripts/init-hdfs.sh
```

### HBase Not Responding

**Problem:** HBase queries fail

**Solution:**
```bash
# Check HBase is running
docker ps | grep hbase

# Restart HBase
docker-compose restart hbase

# Wait 30 seconds for HBase to initialize
sleep 30

# Reinitialize HBase
bash scripts/init-hbase.sh
```

### Dashboard Not Loading

**Problem:** Streamlit dashboard won't open

**Solution:**
```bash
# Check dashboard container
docker ps | grep dashboard

# Rebuild dashboard
docker-compose up -d --build dashboard

# Check logs
docker logs dashboard

# Access directly
docker exec -it dashboard streamlit run streamlit_app.py
```

### Port Already in Use

**Problem:** Port conflict (e.g., 8501, 9870)

**Solution:**
```bash
# Find process using port
lsof -i :8501  # macOS/Linux
netstat -ano | findstr :8501  # Windows

# Kill the process or change port in docker-compose.yml
# Example: Change 8501:8501 to 8502:8501
```

---

## 🛠️ Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Hadoop** | 3.2.1 | Distributed file system (HDFS) |
| **Apache Spark** | 3.3.0 | Distributed data processing |
| **HBase** | 1.2.6 | NoSQL database (standalone with built-in ZooKeeper) |
| **Streamlit** | 1.28+ | Web dashboard |
| **Python** | 3.10 | Data generation and processing |
| **Docker** | 20.10+ | Containerization |

---

## 📚 Learning Resources

- [Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Apache Spark Guide](https://spark.apache.org/docs/latest/)
- [HBase Guide](https://hbase.apache.org/book.html)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 🎓 Demo Script

For a detailed Vietnamese demo script, see [demo_script.md](demo_script.md)

---

## 📝 License

This project is for educational purposes.

---

## 🙋 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review Docker logs: `docker-compose logs`
3. Ensure all prerequisites are met
4. Try a clean restart: `docker-compose down -v && docker-compose up -d`

---

## 🎉 Conclusion

You now have a working Big Data system that demonstrates:

✅ **HDFS** - Storing large datasets distributed across nodes
✅ **Spark** - Processing data in parallel for analytics
✅ **HBase** - Serving results with millisecond latency
✅ **Real-world architecture** - How Amazon-scale systems work

**Happy Learning! 🚀**
