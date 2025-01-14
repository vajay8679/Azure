# Databricks notebook source
# MAGIC %sql
# MAGIC -- Create the main table to store the current version of the data
# MAGIC CREATE TABLE IF NOT EXISTS databricks_training_rn_ws.default.main_table (
# MAGIC     id INT,
# MAGIC     name STRING,
# MAGIC     value STRING,
# MAGIC     effective_date DATE
# MAGIC )
# MAGIC USING DELTA;
# MAGIC
# MAGIC -- Create the history table to store historical data
# MAGIC CREATE TABLE IF NOT EXISTS databricks_training_rn_ws.default.history_table (
# MAGIC     id INT,
# MAGIC     name STRING,
# MAGIC     value STRING,
# MAGIC     effective_date DATE,
# MAGIC     end_date DATE
# MAGIC )
# MAGIC USING DELTA;
# MAGIC

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date, lit
from pyspark.sql.types import DateType
from datetime import datetime

# Initialize Spark session
spark = SparkSession.builder.appName("SCD4 Example").getOrCreate()

# Sample data for the main table
main_data = [
    (1, 'ProductA', '2000'),
    (2, 'ProductB', '3000')
]

# Create DataFrame for the main table
main_schema = "id INT, name STRING, value STRING"
main_df = spark.createDataFrame(main_data, main_schema)

# Add the effective_date column
main_df = main_df.withColumn("effective_date", lit(current_date()).cast(DateType()))

# Write data to the main table
main_df.write.format("delta").mode("overwrite").saveAsTable("databricks_training_rn_ws.default.main_table")

# Sample data for the history table
history_data = [
    (1, 'ProductA', '2909', datetime.strptime('2023-01-01', '%Y-%m-%d').date(), datetime.strptime('2023-12-31', '%Y-%m-%d').date()),
    (2, 'ProductB', '3111', datetime.strptime('2023-01-01', '%Y-%m-%d').date(), datetime.strptime('2023-12-31', '%Y-%m-%d').date())
]

# Create DataFrame for the history table
history_schema = "id INT, name STRING, value STRING, effective_date DATE, end_date DATE"
history_df = spark.createDataFrame(history_data, history_schema)

# Write data to the history table
history_df.write.format("delta").mode("overwrite").saveAsTable("databricks_training_rn_ws.default.history_table")

# COMMAND ----------

# Load the existing Delta table into a DataFrame
# delta_table_path = "/databricks_training_rn_ws/default/new_data"
# new_df = spark.read.format("delta").load(delta_table_path)

# Load the Delta table using the table name
new_data = spark.read.table("databricks_training_rn_ws.default.new_data")

new_data = new_data.withColumn("new_effective_date", current_date())

# Show the result
new_data.show()




# COMMAND ----------

# Assuming 'id' is the key and 'effective_date' is the timestamp of the new data
from pyspark.sql.functions import col

# Load the existing data from the main table
main_df = spark.read.table("databricks_training_rn_ws.default.main_table")

# Prefix all columns in new_data with "new."
# Rename multiple columns by chaining withColumnRenamed()
new_data = new_data.withColumnRenamed("name ", "name2").withColumnRenamed("value", "value2")

# Identify changes by comparing main_df and new_data
updates = new_data.join(main_df, "id", "left_outer")
updates.show()
# Identify new records (where main_df has no corresponding id)
new_records = updates.filter(col("name").isNull())
new_records = new_records.drop("name", "value", "effective_date")
new_records.show()
# Identify records that have changed (values differ between main_df and new_data)
changed_records = updates.filter(
    (col("name").isNotNull()) & 
    ((col("value") != col("value2")) | (col("name2") != col("name")))
)
changed_records.show()


# COMMAND ----------

from pyspark.sql.functions import col

# Sample DataFrame with updated columns
history_updates = changed_records.select(
    col("id").cast("integer"),
    col("name").alias("name"),
    col("value").alias("value"),
    col("effective_date"),
    col("new_effective_date").alias("end_date")
)

# Print schema for debugging
history_updates.printSchema()
spark.read.table("databricks_training_rn_ws.default.history_table").printSchema()

# Append data to the history table
history_updates.write.mode("append").option("mergeSchema", "true").format("delta").saveAsTable("databricks_training_rn_ws.default.history_table")


# COMMAND ----------

# Prepare the updated records to be written back to the main table
updated_records = changed_records.select(
    col("id").cast("integer"),
    col("name2").alias("name"),
    col("value2").alias("value"),
    col("new_effective_date")
)

spark.read.table("databricks_training_rn_ws.default.main_table").printSchema()

# Combine new and updated records
upserts = new_records.union(updated_records)
upserts = upserts.withColumn("id", col("id").cast("integer")).withColumn("value2", col("value2").cast("string"))
upserts = upserts.withColumnRenamed("value2","value").withColumnRenamed("new_effective_date","effective_date").withColumnRenamed("name2","name")

upserts.printSchema()

# Overwrite the main table with the new and updated records
upserts.write.mode("overwrite").format("delta").saveAsTable("databricks_training_rn_ws.default.main_table")

