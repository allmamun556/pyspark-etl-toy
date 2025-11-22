
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import pandas as pd

# Initialize Spark session
spark = SparkSession.builder \
    .appName("UpgradedToyETL") \
    .getOrCreate()

# Sample data
data1 = [
    ("2025-11-20", "Electronics", "Laptop", 2, 1200.0),
    ("2025-11-21", "Electronics", "Mouse", 5, 20.0),
    ("2025-11-22", "Clothing", "T-shirt", 10, 15.0)
]

data2 = [
    ("2025-11-23", "Clothing", "Jeans", 3, 50.0),
    ("2025-11-24", "Electronics", "Keyboard", 1, 100.0),
    ("2025-11-25", "Clothing", "Hat", -2, 10.0)  # invalid sale
]

# Save CSV files
df1 = pd.DataFrame(data1, columns=["date", "category", "product", "quantity", "price"])
df2 = pd.DataFrame(data2, columns=["date", "category", "product", "quantity", "price"])

df1.to_csv("sales_part1.csv", index=False)
df2.to_csv("sales_part2.csv", index=False)
# Read all CSV files from folder
df = spark.read.option("header", True).option("inferSchema", True).csv("sales_part*.csv")

df.show()
# Register DataFrame as a SQL temporary view
df.createOrReplaceTempView("sales")

# Use Spark SQL for transformations
query = """
SELECT 
    category,
    product,
    date,
    quantity,
    price,
    (quantity * price) AS revenue
FROM sales
WHERE quantity > 0
AND date BETWEEN '2025-11-21' AND '2025-11-24'
"""

df_transformed = spark.sql(query)
df_transformed.show()
agg_query = """
SELECT 
    category,
    SUM(quantity * price) AS total_revenue
FROM sales
WHERE quantity > 0
AND date BETWEEN '2025-11-21' AND '2025-11-24'
GROUP BY category
"""

df_agg = spark.sql(agg_query)
df_agg.show()
# Save transformed data
df_transformed.write.mode("overwrite").csv("upgraded_transformed_sales.csv", header=True)

# Save aggregated data
df_agg.write.mode("overwrite").csv("upgraded_aggregated_sales.csv", header=True)
