#!/usr/bin/env python3
"""
HBase Connector Module for PySpark
Provides utilities to write Spark DataFrames to HBase using Thrift
"""

import happybase
from typing import Iterator, Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HBaseConnector:
    """
    Wrapper class for HBase operations via Thrift
    """

    def __init__(self, host='hbase', port=9090, table_name='recommendations'):
        """
        Initialize HBase connection parameters

        Args:
            host: HBase Thrift server hostname
            port: HBase Thrift server port (default 9090)
            table_name: Target HBase table name
        """
        self.host = host
        self.port = port
        self.table_name = table_name

    def get_connection(self):
        """
        Create and return HBase connection

        Returns:
            happybase.Connection: HBase connection object
        """
        try:
            connection = happybase.Connection(
                host=self.host,
                port=self.port,
                timeout=10000,
                autoconnect=True
            )
            logger.info(f"✅ Connected to HBase at {self.host}:{self.port}")
            return connection
        except Exception as e:
            logger.error(f"❌ Failed to connect to HBase: {str(e)}")
            raise

    def create_table_if_not_exists(self, column_families=['info']):
        """
        Create HBase table if it doesn't exist

        Args:
            column_families: List of column family names
        """
        connection = self.get_connection()

        try:
            if self.table_name.encode() in connection.tables():
                logger.info(f"ℹ️  Table '{self.table_name}' already exists")
            else:
                families = {cf: dict() for cf in column_families}
                connection.create_table(self.table_name, families)
                logger.info(f"✅ Created table '{self.table_name}' with families: {column_families}")
        except Exception as e:
            logger.error(f"❌ Error creating table: {str(e)}")
            raise
        finally:
            connection.close()

    def write_batch(self, rows: List[Dict], row_key_field='product_id', column_family='info'):
        """
        Write a batch of rows to HBase

        Args:
            rows: List of dictionaries representing rows
            row_key_field: Field to use as HBase row key
            column_family: Column family to write to
        """
        connection = self.get_connection()

        try:
            table = connection.table(self.table_name)
            batch = table.batch()

            write_count = 0
            for row in rows:
                if row_key_field not in row:
                    logger.warning(f"⚠️  Skipping row without key field '{row_key_field}'")
                    continue

                # Create row key
                row_key = str(row[row_key_field])

                # Prepare columns (exclude row key from data)
                columns = {}
                for key, value in row.items():
                    if key != row_key_field and value is not None:
                        # Convert all values to strings for HBase
                        col_name = f"{column_family}:{key}".encode()
                        col_value = str(value).encode()
                        columns[col_name] = col_value

                # Write to batch
                batch.put(row_key.encode(), columns)
                write_count += 1

            # Send batch
            batch.send()
            logger.info(f"✅ Successfully wrote {write_count} rows to HBase table '{self.table_name}'")

        except Exception as e:
            logger.error(f"❌ Error writing batch to HBase: {str(e)}")
            raise
        finally:
            connection.close()

    def read_table(self, limit=None):
        """
        Read rows from HBase table

        Args:
            limit: Maximum number of rows to read (None for all)

        Returns:
            List of dictionaries representing rows
        """
        connection = self.get_connection()

        try:
            table = connection.table(self.table_name)
            rows = []

            count = 0
            for key, data in table.scan():
                row = {'row_key': key.decode()}

                # Decode columns
                for col_name, col_value in data.items():
                    col_name_decoded = col_name.decode().split(':', 1)[1]  # Remove column family prefix
                    row[col_name_decoded] = col_value.decode()

                rows.append(row)
                count += 1

                if limit and count >= limit:
                    break

            logger.info(f"✅ Read {len(rows)} rows from HBase table '{self.table_name}'")
            return rows

        except Exception as e:
            logger.error(f"❌ Error reading from HBase: {str(e)}")
            raise
        finally:
            connection.close()

    def delete_table(self):
        """
        Delete the HBase table (use with caution!)
        """
        connection = self.get_connection()

        try:
            if self.table_name.encode() in connection.tables():
                connection.delete_table(self.table_name, disable=True)
                logger.info(f"✅ Deleted table '{self.table_name}'")
            else:
                logger.warning(f"⚠️  Table '{self.table_name}' does not exist")
        except Exception as e:
            logger.error(f"❌ Error deleting table: {str(e)}")
            raise
        finally:
            connection.close()


def write_partition_to_hbase(partition_iter: Iterator, hbase_host='hbase', hbase_port=9090,
                              table_name='recommendations', row_key_field='product_id'):
    """
    Function to write a partition of DataFrame to HBase
    Used with DataFrame.foreachPartition()

    Args:
        partition_iter: Iterator over partition rows
        hbase_host: HBase Thrift server hostname
        hbase_port: HBase Thrift server port
        table_name: Target HBase table name
        row_key_field: Field to use as row key
    """
    # Convert iterator to list (required for batch processing)
    rows = list(partition_iter)

    if not rows:
        logger.info("ℹ️  Empty partition, skipping...")
        return

    # Write this partition to HBase
    connector = HBaseConnector(host=hbase_host, port=hbase_port, table_name=table_name)

    # Convert Row objects to dictionaries
    rows_dict = [row.asDict() for row in rows]

    try:
        connector.write_batch(rows_dict, row_key_field=row_key_field)
    except Exception as e:
        logger.error(f"❌ Failed to write partition: {str(e)}")
        raise


def dataframe_to_hbase(df, table_name='recommendations', row_key_field='product_id',
                        hbase_host='hbase', hbase_port=9090):
    """
    Write Spark DataFrame to HBase using foreachPartition for efficiency

    Args:
        df: Spark DataFrame to write
        table_name: Target HBase table name
        row_key_field: Field to use as HBase row key
        hbase_host: HBase Thrift server hostname
        hbase_port: HBase Thrift server port
    """
    logger.info(f"📤 Writing DataFrame to HBase table '{table_name}'...")

    # Use foreachPartition for efficient batch writes
    df.foreachPartition(
        lambda partition: write_partition_to_hbase(
            partition,
            hbase_host=hbase_host,
            hbase_port=hbase_port,
            table_name=table_name,
            row_key_field=row_key_field
        )
    )

    logger.info(f"✅ DataFrame written to HBase table '{table_name}'")


if __name__ == "__main__":
    # Test connectivity
    print("Testing HBase connection...")
    try:
        connector = HBaseConnector(host='localhost', port=9090)
        connection = connector.get_connection()
        print(f"✅ Successfully connected to HBase")
        print(f"📋 Available tables: {connection.tables()}")
        connection.close()
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
