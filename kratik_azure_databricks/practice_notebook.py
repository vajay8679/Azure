# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, current_date, datediff, floor, lit
from pyspark.sql.types import IntegerType
from datetime import datetime


# COMMAND ----------

spark = SparkSession.builder \
    .appName("GenerateFakeData").getOrCreate()

# COMMAND ----------

file_path = "dbfs:/FileStore/results.json"
# Load the JSON file into DataFrame

df = spark.read.option("multiline",True).json(file_path)



# COMMAND ----------

# Define a function to calculate age from date of birth
def calculate_age(dob):
    if dob is None:
        return None
    today = datetime.today()
    birth_date = datetime.strptime(dob, "%Y-%m-%d")
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

# Register the UDF
age_udf = udf(calculate_age, IntegerType())

# Perform transformations
df_transformed = (
    df.withColumn("name", concat_ws(" ", col("first_name"), col("last_name")))
      .withColumn("age", age_udf(col("birthdate")))
)

# Display the transformed DataFrame
# df_transformed.show()

# COMMAND ----------

output_path = "/dbfs/tmp/transformed_http+_file.json"
df_transformed.write.mode("overwrite").json(output_path)

print("Transformed file saved to:", output_path)