#!/usr/bin/env python3
"""
HBase Table Setup Script
Creates and configures HBase tables for the recommendation system
"""

import sys
import happybase
from hbase_connector import HBaseConnector


def setup_recommendations_table(hbase_host='hbase', hbase_port=9090):
    """
    Create the recommendations table with appropriate schema

    Table Schema:
    - Table: recommendations
    - Column Family: info
    - Columns: product_name, category, total_interactions, purchases,
               clicks, views, avg_price, hot_score
    - Row Key: product_id
    """
    print("=" * 80)
    print("🔧 HBase Table Setup - Recommendations System")
    print("=" * 80)

    try:
        # Connect to HBase
        print(f"\n📡 Connecting to HBase at {hbase_host}:{hbase_port}...")
        connection = happybase.Connection(host=hbase_host, port=hbase_port, timeout=10000)

        # List existing tables
        existing_tables = [t.decode() for t in connection.tables()]
        print(f"\n📋 Existing tables: {existing_tables if existing_tables else 'None'}")

        # Create recommendations table
        table_name = 'recommendations'
        print(f"\n🏗️  Creating table '{table_name}'...")

        if table_name.encode() in connection.tables():
            print(f"⚠️  Table '{table_name}' already exists")

            # Ask if user wants to recreate
            response = input("Do you want to delete and recreate it? (yes/no): ").strip().lower()

            if response == 'yes':
                print(f"🗑️  Disabling and deleting table '{table_name}'...")
                connection.delete_table(table_name, disable=True)
                print(f"✅ Table '{table_name}' deleted")
            else:
                print("ℹ️  Keeping existing table")
                connection.close()
                return

        # Create table with column family
        column_families = {
            'info': dict(max_versions=1)  # Store only latest version
        }

        connection.create_table(table_name, column_families)
        print(f"✅ Table '{table_name}' created successfully!")

        # Verify table creation
        print(f"\n✓ Table Details:")
        print(f"  - Name: {table_name}")
        print(f"  - Column Families: info")
        print(f"  - Row Key: product_id")
        print(f"  - Columns: product_name, category, total_interactions, purchases,")
        print(f"            clicks, views, avg_price, hot_score")

        # Insert sample data for testing
        print(f"\n📝 Inserting sample data for testing...")
        table = connection.table(table_name)

        sample_data = {
            b'info:product_name': b'Sample Product',
            b'info:category': b'Electronics',
            b'info:total_interactions': b'100',
            b'info:purchases': b'10',
            b'info:clicks': b'30',
            b'info:views': b'60',
            b'info:avg_price': b'99.99',
            b'info:hot_score': b'250'
        }

        table.put(b'SAMPLE_001', sample_data)
        print(f"✅ Sample data inserted")

        # Read back to verify
        print(f"\n🔍 Verifying data...")
        row = table.row(b'SAMPLE_001')

        if row:
            print(f"✅ Data verification successful!")
            print(f"   Sample row:")
            for key, value in row.items():
                print(f"     {key.decode()}: {value.decode()}")
        else:
            print(f"⚠️  Could not verify sample data")

        # Clean up sample data
        table.delete(b'SAMPLE_001')
        print(f"\n🧹 Sample data cleaned up")

        connection.close()

        print("\n" + "=" * 80)
        print("✅ HBase table setup completed successfully!")
        print("=" * 80)
        print(f"\n📋 Summary:")
        print(f"   Table Name: {table_name}")
        print(f"   Status: Ready for use")
        print(f"   Connection: {hbase_host}:{hbase_port}")
        print(f"\n🎯 You can now run your Spark job to populate this table!")

    except happybase.thrift.ttypes.IOError as e:
        print(f"\n❌ HBase IO Error: {str(e)}")
        print("   Make sure HBase Thrift server is running on port 9090")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def list_tables(hbase_host='hbase', hbase_port=9090):
    """List all tables in HBase"""
    try:
        connection = happybase.Connection(host=hbase_host, port=hbase_port, timeout=10000)
        tables = [t.decode() for t in connection.tables()]

        print("\n📋 HBase Tables:")
        if tables:
            for idx, table_name in enumerate(tables, 1):
                print(f"   {idx}. {table_name}")
        else:
            print("   No tables found")

        connection.close()

    except Exception as e:
        print(f"❌ Error listing tables: {str(e)}")


def main():
    """Main function"""
    print("\n🚀 HBase Setup Utility")
    print("=" * 80)

    # Parse command line arguments
    hbase_host = sys.argv[1] if len(sys.argv) > 1 else 'hbase'
    hbase_port = int(sys.argv[2]) if len(sys.argv) > 2 else 9090

    print(f"Target: {hbase_host}:{hbase_port}")

    # Setup tables
    setup_recommendations_table(hbase_host, hbase_port)

    # List all tables
    list_tables(hbase_host, hbase_port)


if __name__ == "__main__":
    main()
