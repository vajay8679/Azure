# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS main_table2 (
# MAGIC     id INT,
# MAGIC     name STRING,
# MAGIC     value STRING,
# MAGIC     prev_name STRING,
# MAGIC     prev_value STRING
# MAGIC )
# MAGIC USING DELTA
# MAGIC

# COMMAND ----------

# Load existing data from the main table
main_df = spark.read.table("databricks_training_rn_ws.default.main_table2")

# Load new data
new_data = spark.read.table("databricks_training_rn_ws.default.new_data")


# COMMAND ----------

from pyspark.sql.functions import col
# Join existing data with new data to find changes
updates = new_data.alias("new").join(main_df.alias("main"), "id", "left_outer") \
    .filter((col("main.id").isNull()) | (col("new.value") != col("main.value")))

updates.show()


# COMMAND ----------

# Prepare updated records
updates_with_prev_values = updates.select(
    col("new.id"),
    col("new.name").alias("name"),
    col("new.value").alias("value"),
    col("main.name").alias("prev_name"),
    col("main.value").alias("prev_value")
)

# Handle cases where there are no previous values
updates_with_prev_values = updates_with_prev_values.fillna({"prev_name": "", "prev_value": ""})


# COMMAND ----------

# Union the updated records with existing records
combined_data = main_df.alias("main").join(updates_with_prev_values.alias("updates"), "id", "left_outer") \
    .select(
        col("updates.id").alias("id"),
        col("updates.name").alias("name"),
        col("updates.value").alias("value"),
        col("updates.prev_name").alias("prev_name"),
        col("updates.prev_value").alias("prev_value")
    )

# Save the combined data back to the main table
combined_data.write.mode("overwrite").format("delta").saveAsTable("databricks_training_rn_ws.default.main_table")
