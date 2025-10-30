#!/usr/bin/env python3
"""
Amazon Product Recommendations - Spark Job
Analyzes clickstream data from HDFS to find top products and write to HBase

This job demonstrates:
1. Reading large datasets from HDFS
2. Distributed data processing with Spark
3. Writing results to HBase for real-time serving
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, avg, sum as spark_sum
import sys
import time
from hbase_connector import dataframe_to_hbase, HBaseConnector


def create_spark_session(app_name="Amazon-Recommendations"):
    """Create and configure Spark session"""
    print("🚀 Creating Spark Session...")

    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")

    print(f"✅ Spark Session created: {spark.version}")
    return spark


def read_clickstream_from_hdfs(spark, hdfs_path="hdfs://namenode:9000/data/clickstream_large.txt"):
    """Read clickstream data from HDFS"""
    print(f"\n📖 Reading data from HDFS: {hdfs_path}")

    start_time = time.time()

    df = spark.read.csv(
        hdfs_path,
        header=True,
        inferSchema=True
    )

    record_count = df.count()
    elapsed_time = time.time() - start_time

    print(f"✅ Read {record_count:,} records in {elapsed_time:.2f} seconds")
    print(f"📊 Schema:")
    df.printSchema()

    return df


def analyze_top_products(df):
    """Analyze clickstream to find top products"""
    print("\n🔍 Analyzing top products...")

    # Calculate metrics per product
    product_stats = df.groupBy("product_id", "product_name", "category") \
        .agg(
            count("*").alias("total_interactions"),
            spark_sum((col("action") == "purchase").cast("int")).alias("purchases"),
            spark_sum((col("action") == "click").cast("int")).alias("clicks"),
            spark_sum((col("action") == "view").cast("int")).alias("views"),
            avg("price").alias("avg_price")
        ) \
        .orderBy(desc("total_interactions"))

    # Calculate hot score (weighted: purchase=10, click=3, view=1)
    product_stats = product_stats.withColumn(
        "hot_score",
        (col("purchases") * 10) + (col("clicks") * 3) + col("views")
    )

    # Get top 10
    top_products = product_stats.orderBy(desc("hot_score")).limit(10)

    print("\n🏆 Top 10 Hot Products:")
    print("=" * 100)
    top_products.show(truncate=False)

    return top_products


def analyze_top_categories(df):
    """Analyze top categories by sales"""
    print("\n📊 Analyzing top categories...")

    category_stats = df.groupBy("category") \
        .agg(
            count("*").alias("total_interactions"),
            spark_sum((col("action") == "purchase").cast("int")).alias("purchases"),
            avg("price").alias("avg_price")
        ) \
        .orderBy(desc("purchases"))

    print("\n🏷️  Category Performance:")
    print("=" * 80)
    category_stats.show(truncate=False)

    return category_stats


def analyze_user_behavior(df):
    """Analyze user behavior patterns"""
    print("\n👥 Analyzing user behavior...")

    user_stats = df.groupBy("user_id") \
        .agg(
            count("*").alias("total_actions"),
            spark_sum((col("action") == "purchase").cast("int")).alias("purchases"),
            spark_sum((col("action") == "view").cast("int")).alias("views")
        ) \
        .orderBy(desc("purchases"))

    print("\n👤 Top 10 Buyers:")
    print("=" * 60)
    user_stats.show(10, truncate=False)

    # Calculate conversion metrics
    action_distribution = df.groupBy("action").count().orderBy(desc("count"))

    print("\n📈 Action Distribution:")
    print("=" * 40)
    action_distribution.show(truncate=False)

    return user_stats, action_distribution


def save_to_hbase(top_products, hbase_host='hbase', hbase_port=9090,
                  table_name='recommendations', save_backup=True):
    """
    Save recommendations to HBase for real-time serving

    Args:
        top_products: Spark DataFrame with product recommendations
        hbase_host: HBase Thrift server hostname
        hbase_port: HBase Thrift server port
        table_name: HBase table name
        save_backup: Whether to save backup files to HDFS
    """
    print(f"\n💾 Saving recommendations to HBase table '{table_name}'...")

    # Get top products for display
    top_10 = top_products.limit(10)

    print("\n🎯 Top 10 Products to Save:")
    print("=" * 100)
    top_10.show(truncate=False)

    # Ensure table exists
    try:
        connector = HBaseConnector(host=hbase_host, port=hbase_port, table_name=table_name)
        connector.create_table_if_not_exists(column_families=['info'])
        print(f"✅ HBase table '{table_name}' is ready")
    except Exception as e:
        print(f"⚠️  Warning: Could not verify/create table: {str(e)}")
        print("   Continuing with write attempt...")

    # Write DataFrame to HBase
    try:
        print(f"\n📤 Writing {top_products.count()} products to HBase...")

        dataframe_to_hbase(
            top_products,
            table_name=table_name,
            row_key_field='product_id',
            hbase_host=hbase_host,
            hbase_port=hbase_port
        )

        print(f"✅ Successfully wrote recommendations to HBase!")

    except Exception as e:
        print(f"❌ Error writing to HBase: {str(e)}")
        print("   Falling back to file-based storage...")
        save_backup = True

    # Optional: Save backup to HDFS
    if save_backup:
        print(f"\n💾 Saving backup to HDFS...")
        output_path = "/data/recommendations_output"

        top_products.coalesce(1).write.mode("overwrite").csv(
            output_path + "/recommendations_csv",
            header=True
        )

        top_products.coalesce(1).write.mode("overwrite").json(
            output_path + "/recommendations_json"
        )

        print(f"✅ Backup saved to {output_path}")

    # Display HBase format
    recommendations = top_10.collect()

    print("\n📝 HBase Storage Format:")
    print(f"   Table: {table_name}")
    print(f"   Column Family: info")
    print("-" * 80)

    for idx, row in enumerate(recommendations[:5], 1):
        print(f"  Row Key: {row['product_id']}")
        print(f"    info:product_name     => {row['product_name']}")
        print(f"    info:category         => {row['category']}")
        print(f"    info:hot_score        => {row['hot_score']}")
        print(f"    info:purchases        => {row['purchases']}")
        print(f"    info:total_interactions => {row['total_interactions']}")
        print()


def main():
    """Main execution function"""
    print("=" * 100)
    print("🎯 AMAZON PRODUCT RECOMMENDATIONS - SPARK JOB")
    print("=" * 100)

    start_time = time.time()

    # Get HDFS path from argument or use default
    hdfs_path = sys.argv[1] if len(sys.argv) > 1 else "hdfs://localhost:9000/big-data-demo/clickstream_large.txt"

    # Step 1: Create Spark Session
    spark = create_spark_session()

    try:
        # Step 2: Read data from HDFS
        df = read_clickstream_from_hdfs(spark, hdfs_path)

        # Step 3: Analyze top products
        top_products = analyze_top_products(df)

        # Step 4: Analyze categories
        top_categories = analyze_top_categories(df)

        # Step 5: Analyze user behavior
        user_stats, action_dist = analyze_user_behavior(df)

        # Step 6: Save results to HBase
        save_to_hbase(top_products, hbase_host='localhost', hbase_port=9090)

        # Summary
        total_time = time.time() - start_time
        print("\n" + "=" * 100)
        print(f"✅ JOB COMPLETED SUCCESSFULLY in {total_time:.2f} seconds")
        print("=" * 100)

        print("\n📌 Key Takeaways:")
        print("   1. ✅ HDFS: Successfully read large dataset from distributed storage")
        print("   2. ✅ Spark: Processed data in parallel using distributed computing")
        print("   3. ✅ HBase: Stored recommendations in HBase for real-time serving")
        print("\n🎯 Data Pipeline Complete: HDFS → Spark → HBase")

    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        spark.stop()
        print("\n👋 Spark Session closed")


if __name__ == "__main__":
    main()
