# PySpark Tutorial (Detailed, Beginner-Friendly, with Examples)

Welcome to this complete **PySpark tutorial**, designed for beginners and intermediate learners. This guide explains PySpark concepts in **clear English**, with **many examples** to help you understand how PySpark works and how to use it in real-world applications.

---

## 1. What is PySpark?

PySpark is the **Python API for Apache Spark**, an open-source distributed computing framework.

PySpark is used for:

* Processing **big data** (very large datasets)
* Running operations across **multiple machines** in parallel
* Creating data pipelines for **ETL (Extract, Transform, Load)**
* Performing **machine learning** on large datasets
* Handling **streaming data**

---

## 2. Why Use PySpark?

### Benefits:

* Handles **huge datasets** that don’t fit in memory
* Very fast due to **distributed computing**
* Supports SQL, machine learning (MLlib), streaming, and graph processing
* Integrates well with Hadoop, AWS EMR, Databricks, etc.

---

## 3. Installing PySpark

You can install it using pip:

```bash
pip install pyspark
```

---

## 4. Creating a SparkSession

A SparkSession is the entry point to PySpark.

### Example:

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("FirstApp") \
    .getOrCreate()
```

---

## 5. Creating DataFrames in PySpark

There are 3 main ways to create a DataFrame:

### 5.1 From Python lists

```python
data = [("Alice", 24), ("Bob", 30), ("Charlie", 29)]
df = spark.createDataFrame(data, ["Name", "Age"])
df.show()
```

### 5.2 From CSV

```python
df = spark.read.csv("file.csv", header=True, inferSchema=True)
```

### 5.3 From JSON

```python
df = spark.read.json("data.json")
```

---

## 6. Viewing Data

```python
df.show()        # display table
print(df.count()) # number of rows
df.printSchema()  # column types
```

---

## 7. Selecting Columns

```python
df.select("Name").show()
df.select("Name", "Age").show()
```

---

## 8. Filtering Rows

```python
df.filter(df.Age > 25).show()
df.filter(df.Name == "Alice").show()
```

---

## 9. Adding New Columns

```python
df = df.withColumn("Age_plus_1", df.Age + 1)
df.show()
```

---

## 10. Removing Columns

```python
df = df.drop("Age_plus_1")
```

---

## 11. Renaming Columns

```python
df = df.withColumnRenamed("Age", "Years")
```

---

## 12. Handling Missing Data

### Fill missing values

```python
df.na.fill({"Age": 0}).show()
```

### Drop rows with missing values

```python
df.na.drop().show()
```

---

## 13. GroupBy and Aggregations

```python
df.groupBy("Department").agg({"Salary": "avg"}).show()
```

Common functions:

* `avg`
* `sum`
* `min`
* `max`
* `count`

---

## 14. Joining DataFrames

```python
result = df1.join(df2, df1.id == df2.id, "inner")
result.show()
```

**Join Types**:

* inner
* left
* right
* outer

---

## 15. Sorting Data

```python
df.orderBy("Age").show()
df.orderBy(df.Age.desc()).show()
```

---

## 16. PySpark SQL

You can run SQL queries on DataFrames.

### Register DataFrame as a SQL table:

```python
df.createOrReplaceTempView("people")
```

### Run SQL query:

```python
spark.sql("SELECT Name, Age FROM people WHERE Age > 25").show()
```

---

## 17. Writing Data to Files

### Write CSV

```python
df.write.csv("output_folder", header=True)
```

### Write JSON

```python
df.write.json("output_json")
```

### Write Parquet (most efficient)

```python
df.write.parquet("output_parquet")
```

---

## 18. Working with UDF (User Defined Functions)

You can create custom Python functions and use them in PySpark.

### Example:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def upper_case(name):
    return name.upper()

upper_udf = udf(upper_case, StringType())

df = df.withColumn("NameUpper", upper_udf(df.Name))
df.show()
```

---

## 19. Window Functions

Window functions perform operations across groups of rows.

### Example:

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

window = Window.partitionBy("Department").orderBy(df.Salary.desc())

df.withColumn("rank", row_number().over(window)).show()
```

---

## 20. PySpark MLlib (Machine Learning)

### Example: Linear Regression

```python
from pyspark.ml.regression import LinearRegression

lr = LinearRegression(featuresCol="features", labelCol="label")
model = lr.fit(training_data)
```

---

## 21. PySpark vs Pandas

| Feature   | Pandas          | PySpark             |
| --------- | --------------- | ------------------- |
| Data Size | Small/Medium    | Very Large          |
| Speed     | Slow (big data) | Very fast           |
| Memory    | Single machine  | Distributed cluster |
| Best For  | Analysis        | Big data processing |

---

## 22. Best Practices

* Always use **Parquet** instead of CSV for speed
* Avoid using Python loops; use Spark functions instead
* Cache data only when necessary:

```python
df.cache()
```

* Use Spark UI to monitor jobs

---

## 23. Summary

You learned:

* What PySpark is
* How to install and use SparkSession
* Creating, reading, and writing DataFrames
* Selecting, filtering, grouping, and joining data
* SQL queries
* Window functions
* Machine learning basics with MLlib

---

If you'd like, I can add:

* Practice problems
* Advanced PySpark tutorial
* Coding interview questions for PySpark
* A downloadable PDF version

Just tell me!
# Advanced PySpark Tutorial (Detailed, English, With Examples)

This advanced guide expands on the fundamentals and goes deep into **performance optimization**, **advanced transformations**, **partitioning**, **tuning**, **PySpark SQL internals**, **window functions**, **ML pipelines**, and more.

---

# 1. Spark Architecture (Advanced Understanding)

PySpark runs on top of **Spark**, which has the following key components:

## 1.1 Driver

* Runs the main program.
* Creates the SparkSession.
* Schedules tasks on executors.

## 1.2 Executors

* Run tasks.
* Store cached data.

## 1.3 Cluster Manager

* YARN, Kubernetes, Mesos, or Standalone.

---

# 2. Catalyst Optimizer & Tungsten Engine

Spark uses two powerful components:

## 2.1 Catalyst Optimizer

* Analyzes and optimizes queries.
* Rewrites logical plans.
* Eliminates redundant operations.

## 2.2 Tungsten Execution Engine

* Off-heap memory management
* Code generation ("whole-stage codegen")
* CPU-optimized execution

---

# 3. Understanding Execution Plans

You must understand how Spark executes your code.

### Example:

```python
df.explain()
```

### `explain()` output includes:

* **Parsed logical plan**
* **Analyzed logical plan**
* **Optimized logical plan**
* **Physical plan**

---

# 4. Partitioning (Critical for Performance)

Partitions determine how Spark distributes data.

## 4.1 Check number of partitions:

```python
df.rdd.getNumPartitions()
```

## 4.2 Repartition

Useful for shuffles, large transformations.

```python
df = df.repartition(10)
```

## 4.3 Coalesce

Reduces partitions, avoids shuffle.

```python
df = df.coalesce(2)
```

## When to use?

* **repartition**: Increase partitions or redistribute evenly (shuffle).
* **coalesce**: Reduce partitions efficiently (no shuffle).

---

# 5. Caching & Persistence

Caching can speed up repeated operations but should be used carefully.

## 5.1 Cache

```python
df.cache()
```

## 5.2 Persist with storage levels

```python
from pyspark.storagelevel import StorageLevel

df.persist(StorageLevel.MEMORY_AND_DISK)
```

## 5.3 Unpersist

```python
df.unpersist()
```

---

# 6. Broadcast Variables

Used to avoid large shuffles.

### Example:

```python
from pyspark.sql.functions import broadcast

df.join(broadcast(df_lookup), "id").show()
```

Use broadcast joins when one dataset is small (< 500MB).

---

# 7. Window Functions (Advanced Use)

Window functions perform calculations across a set of rows.

### Example:

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, sum as _sum

window = Window.partitionBy("department").orderBy("salary")

result = df.withColumn("row_num", row_number().over(window))
```

## Common Window Functions

* `row_number()`
* `rank()` / `dense_rank()`
* `lag()` / `lead()`
* `cume_dist()`
* `ntile()`

---

# 8. Complex Aggregations

### Example: Multiple aggregations

```python
from pyspark.sql.functions import sum, avg, max

df.groupBy("category").agg(
    sum("revenue").alias("total_revenue"),
    avg("revenue").alias("avg_revenue"),
    max("revenue").alias("max_revenue")
).show()
```

---

# 9. User Defined Functions (UDF & Pandas UDF)

## 9.1 Regular UDF (slow)

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

def add_five(x):
    return x + 5

add_udf = udf(add_five, IntegerType())

newdf = df.withColumn("new", add_udf(df["value"]))
```

## 9.2 Pandas UDF (fast, vectorized)

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("int")
def add_five_pd(series: pd.Series) -> pd.Series:
    return series + 5

newdf = df.withColumn("new", add_five_pd(df["value"]))
```

Pandas UDFs are much faster for large data.

---

# 10. Advanced Joins

### 10.1 Handle different join types

```python
df.join(other, "id", "left_semi").show()
df.join(other, "id", "left_anti").show()
```

### 10.2 Avoid Skew using salting

```python
from pyspark.sql.functions import randint

# Add random salt column
big = big.withColumn("salt", randint(0, 10))
small = small.withColumn("salt", randint(0, 10))

result = big.join(small, ["id", "salt"])
```

---

# 11. File Formats for Big Data

### Best formats:

* **Parquet** → columnar, compressed, optimized for Spark
* **ORC**

### Example:

```python
df.write.mode("overwrite").parquet("output_path")
```

---

# 12. Working with Large Datasets

Use `inferSchema=False` and manually define schema for speed.

### Example:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("name", StringType()),
    StructField("age", IntegerType())
])

df = spark.read.csv("file.csv", schema=schema)
```

---

# 13. Joins vs Broadcast Joins (Performance)

| Join Type          | When to Use                 |
| ------------------ | --------------------------- |
| **Shuffle Join**   | Large tables joining on key |
| **Broadcast Join** | One small table (<500MB)    |

---

# 14. Accumulators

Used for debugging and tracking metrics.

### Example:

```python
acc = spark.sparkContext.accumulator(0)

def add_to_acc(row):
    global acc
    acc += 1

rdd.foreach(add_to_acc)
print(acc.value)
```

---

# 15. ML Pipelines (Advanced)

PySpark MLlib supports end-to-end ML pipelines.

### Example Pipeline:

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml import Pipeline

assembler = VectorAssembler(inputCols=["feature1", "feature2"], outputCol="features")
lr = LinearRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[assembler, lr])
model = pipeline.fit(df)
```

---

# 16. Performance Tuning

## 16.1 Shuffle partitions

```python
spark.conf.set("spark.sql.shuffle.partitions", 300)
```

## 16.2 Broadcast threshold

```python
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "1GB")
```

## 16.3 Avoid wide transformations (like groupBy) without need

## 16.4 Use `explain()` to analyze bottlenecks

---

# 17. Best Practices

* Prefer **Spark SQL functions** over UDFs
* Avoid collecting large data back to driver
* Use **Parquet** instead of CSV
* Repartition before large joins
* Cache wisely and unpersist when done

---

# 18. Summary

This advanced tutorial covered:

* Spark internals
* Execution plans
* Partitioning & performance boosting
* Caching & persistence
* Window functions
* Pandas UDFs
* Salting to fix skewed joins
* ML pipelines
* Best practices for real production systems

If you'd like, I can add:

* Advanced interview questions
* A PySpark + Databricks section
* Real-world project examples
* A PDF version of this tutorial
Nice bundle, let’s do all three in one go 🚀

I’ll structure it like this:

1. **Advanced PySpark interview questions (with answers)**
2. **Real-world end-to-end PySpark project (ETL + ML pipeline)**
3. **Compact but powerful PySpark cheat sheet**

---

## 1️⃣ Advanced PySpark Interview Questions (with Answers)

### Q1. What is the difference between *narrow* and *wide* transformations?

**Answer:**

* **Narrow transformations**: each partition of the parent RDD/DataFrame is used by at most one partition of the child.

  * Examples: `map`, `filter`, `withColumn`, `select`
  * No shuffle.

* **Wide transformations**: data from one partition can end up in many partitions of the child.

  * Examples: `groupBy`, `orderBy`, `repartition`, joins
  * Cause **shuffle** (expensive).

**Why it matters in interviews?**

* Shows you understand performance and shuffles.

---

### Q2. Explain the Spark execution model: job, stage, task.

**Answer:**

* **Job**: triggered by an action (`show`, `count`, `collect`, `write`).
* **Stage**: subdivision of a job, split at shuffle boundaries.
* **Task**: unit of work sent to an executor for a single partition.

**Follow-up interview point:**

* You can mention Spark UI: “Jobs” tab, then “Stages”, then “Tasks”.

---

### Q3. What is the Catalyst Optimizer and Tungsten in Spark?

**Answer:**

* **Catalyst Optimizer**:

  * Optimizes logical query plans.
  * Reorders joins, pushes down filters, removes redundant projections, etc.

* **Tungsten**:

  * Memory and execution optimization layer.
  * Off-heap memory management.
  * Whole-stage code generation (JIT-compiled code).

Saying “Catalyst optimizes *what* to do and Tungsten optimizes *how* to do it” is a nice interview phrase.

---

### Q4. When would you use `cache()` vs `persist()`? What storage levels do you know?

**Answer:**

* `cache()` = shortcut for `persist(StorageLevel.MEMORY_ONLY)`.
* `persist()` lets you choose levels:

  * `MEMORY_ONLY`
  * `MEMORY_AND_DISK`
  * `DISK_ONLY`
  * Variants with `_SER` and `_2` (replication).

Use caching when:

* You reuse the **same DataFrame** multiple times.
* The computation to recompute it is expensive.

**Example:**

```python
from pyspark.storagelevel import StorageLevel

df_cached = df.persist(StorageLevel.MEMORY_AND_DISK)
df_cached.count()
df_cached.groupBy("country").count().show()
df_cached.unpersist()
```

---

### Q5. Difference between `repartition()` and `coalesce()`?

**Answer:**

* `repartition(n)`:

  * Can **increase or decrease** partitions.
  * Always **causes a shuffle**.
  * Redistributes data evenly.

* `coalesce(n)`:

  * Only used to **decrease** number of partitions.
  * **Avoids shuffle** (when shrinking).
  * Merges existing partitions.

**Rule of thumb in interviews**:

* “Use `repartition` to *rebalance* data, `coalesce` to *shrink* partitions cheaply.”

---

### Q6. What is a broadcast join and when would you use it?

**Answer:**

Broadcast join = send a **small DataFrame** to all executors so that the large DataFrame doesn’t need to shuffle.

```python
from pyspark.sql.functions import broadcast

result = large_df.join(broadcast(small_df), "id", "inner")
```

Use it when:

* One side is small (typically < 500MB, config-dependent).
* You want to avoid shuffle on the large table.

---

### Q7. How do you handle **data skew** in joins or aggregations?

**Common techniques:**

1. **Salting keys** (for very popular keys):

   ```python
   from pyspark.sql.functions import col, randint

   big = big.withColumn("salt", randint(0, 10))
   small = small.withColumn("salt", randint(0, 10))

   joined = big.join(small, ["id", "salt"])
   ```

2. **Broadcast the small table** (if possible).

3. **Filter hot keys** and process separately.

Interviewers love if you say “skewed keys create very large partitions → long running tasks → job imbalance.”

---

### Q8. Explain window functions with a concrete example.

**Answer:**

Window functions operate over a group of rows, returning a value for each row (like “row_number per group”).

**Example: top 3 employees per department by salary**

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number

win = Window.partitionBy("department").orderBy(col("salary").desc())

df_ranked = df.withColumn("rn", row_number().over(win))
df_ranked.filter("rn <= 3").show()
```

Mention common functions:

* `row_number`, `rank`, `dense_rank`, `lag`, `lead`, `sum().over(win)`.

---

### Q9. Difference between UDF, pandas UDF, and built-in functions?

**Answer:**

* **Built-in Spark SQL functions** (`col`, `when`, `regexp_extract`, etc.):

  * Best performance.
  * Catalyst can optimize them.
* **UDF** (`udf()`):

  * Runs Python code row by row.
  * Slow, limited optimization.
* **Pandas UDF** (`pandas_udf()`):

  * Vectorized.
  * Operation in batches using Pandas.
  * Much faster than normal UDFs.

**Pandas UDF example:**

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

@pandas_udf("double")
def plus_one(s: pd.Series) -> pd.Series:
    return s + 1

df = df.withColumn("value_plus_1", plus_one(df["value"]))
```

---

### Q10. How do you optimize reading a huge CSV in PySpark?

Points to mention:

* **Define schema explicitly** (avoid `inferSchema=True` on big data).
* Use good partitioning (e.g., read from a partitioned folder).
* Use `compression`, `header`, `delimiter` properly.

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
    StructField("age", IntegerType())
])

df = spark.read.csv(
    "s3://bucket/path/",
    header=True,
    schema=schema,
    mode="DROPMALFORMED"
)
```

---

### Q11. How do you inspect and understand a physical plan?

```python
df.explain(True)
```

Things to mention:

* Look for:

  * `BroadcastHashJoin` vs `ShuffledHashJoin` vs `SortMergeJoin`
  * `WholeStageCodegen`
  * Where shuffles occur (`Exchange` nodes).

In an interview, say: “I use `explain(True)` + Spark UI to diagnose performance problems.”

---

### Q12. How do you deal with **too many small files** in Spark?

* Repartition or coalesce before writing:

  ```python
  df.repartition(10).write.parquet("path")
  ```
* Use `coalesce(1)` only for small, final outputs (like exporting).
* Talk about small files issue in HDFS/S3 and NameNode / metadata overhead.

---

### Q13. How do you design an idempotent ETL in PySpark?

Key points:

* Write to a **new path** or partition (e.g. `dt=2025-11-24`) each run.
* Use **overwrite dynamic partitions** or swap directories using metadata.
* Avoid `append` without partition filters.
* Use checkpointing for streaming.

---

You can turn each of these into a 3–5 min spoken answer in an interview.

---

## 2️⃣ Real-World End-to-End PySpark Project (ETL + ML Pipeline)

Let’s design a realistic project:

> **Use case:** Predict customer churn for a subscription service using daily usage logs.

### 2.1 Architecture Overview

* **Data source:**

  * Raw usage logs in **CSV/JSON** in a data lake (e.g., S3 / HDFS)
  * Customer info in another table.
* **Steps:**

  1. **Extract**: Read raw logs + customer table.
  2. **Transform**: Clean data, aggregate to customer-level features.
  3. **Load**: Write cleaned features as Parquet.
  4. **Model**: Train an ML model (binary classification: churn / not churn).
  5. **Serve results**: Save predictions for BI / dashboards.

---

### 2.2 Data Assumptions

* `events` (usage logs):

  * `customer_id`, `event_time`, `event_type`, `minutes_watched`, `device_type`
* `customers`:

  * `customer_id`, `signup_date`, `country`, `churned` (label: 0/1)

---

### 2.3 ETL + Feature Engineering (PySpark code sketch)

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, countDistinct, sum as _sum, max as _max, min as _min, datediff, to_date

spark = SparkSession.builder.appName("ChurnETL").getOrCreate()

# 1. Read data
events = spark.read.json("s3://datalake/raw/events/")
customers = spark.read.parquet("s3://datalake/raw/customers/")

# 2. Basic cleaning
events = events.dropna(subset=["customer_id", "event_time"])

# Convert event_time to date
events = events.withColumn("event_date", to_date(col("event_time")))

# 3. Aggregate usage per customer
usage_agg = (
    events.groupBy("customer_id")
    .agg(
        countDistinct("event_date").alias("active_days"),
        _sum("minutes_watched").alias("total_minutes"),
        countDistinct("device_type").alias("num_devices")
    )
)

# 4. Join with customer info
data = customers.join(usage_agg, "customer_id", "left")

# 5. Create additional features
data = data.withColumn(
    "days_since_signup",
    datediff(_max(col("event_date")).over(), col("signup_date"))  # or use a constant reference date
)

# 6. Handle missing
data = data.fillna({"total_minutes": 0, "active_days": 0, "num_devices": 0})

# 7. Save cleaned features
data.write.mode("overwrite").parquet("s3://datalake/curated/customer_churn_features/")
```

In reality, you might:

* Partition by date / country.
* Use incremental loads (only yesterday’s data, etc.).

---

### 2.4 ML Pipeline for Churn Prediction

```python
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator

# Read curated features
df = spark.read.parquet("s3://datalake/curated/customer_churn_features/")

# Select features + label
feature_cols = ["active_days", "total_minutes", "num_devices"]
cat_cols = ["country"]

# Index categorical column
country_indexer = StringIndexer(inputCol="country", outputCol="country_idx", handleInvalid="keep")

all_features = feature_cols + ["country_idx"]

assembler = VectorAssembler(inputCols=all_features, outputCol="features")

rf = RandomForestClassifier(featuresCol="features", labelCol="churned")

pipeline = Pipeline(stages=[country_indexer, assembler, rf])

# Train-test split
train, test = df.randomSplit([0.8, 0.2], seed=42)

model = pipeline.fit(train)

preds = model.transform(test)

evaluator = BinaryClassificationEvaluator(labelCol="churned", metricName="areaUnderROC")

auc = evaluator.evaluate(preds)
print("AUC:", auc)

# Save model
model.write().overwrite().save("s3://models/churn_rf_model/")
```

**In an interview**, you can describe:

* How often this pipeline runs (daily batch).
* Where logs arrive (Kafka → raw → silver → gold layers).
* How you monitor performance (Spark UI, logs, metrics).
* How you ensure idempotency (partitioning by date & overwrite).

---

## 3️⃣ PySpark Cheat Sheet (Practical Commands)

### 3.1 Setup

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MyApp").getOrCreate()
```

---

### 3.2 Reading Data

```python
df_csv = spark.read.csv("path/file.csv", header=True, inferSchema=True)
df_json = spark.read.json("path/file.json")
df_parquet = spark.read.parquet("path/folder/")
```

With schema:

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType())
])

df = spark.read.csv("path", header=True, schema=schema)
```

---

### 3.3 Basic Data Inspection

```python
df.printSchema()
df.show(5)
df.count()
df.columns
df.describe().show()
```

---

### 3.4 Selecting & Filtering

```python
from pyspark.sql.functions import col

df.select("col1", "col2").show()
df.select(col("age") + 1).show()
df.filter(col("age") > 30).show()
df.where("age > 30 AND country = 'US'").show()
```

---

### 3.5 Column Operations

```python
from pyspark.sql.functions import when, lit

df = df.withColumn("age_plus_1", col("age") + 1)

df = df.withColumn(
    "age_bucket",
    when(col("age") < 18, "child")
    .when(col("age") < 65, "adult")
    .otherwise("senior")
)

df = df.drop("unneeded_column")
df = df.withColumnRenamed("old_name", "new_name")
```

---

### 3.6 Handling Nulls

```python
df.na.fill({"age": 0, "country": "unknown"})
df.na.drop(subset=["age"])
df.na.replace(["US", "United States"], "USA", "country")
```

---

### 3.7 Aggregations & GroupBy

```python
from pyspark.sql.functions import sum, avg, max, min, countDistinct

df.groupBy("country").agg(
    countDistinct("user_id").alias("unique_users"),
    sum("revenue").alias("total_revenue"),
    avg("revenue").alias("avg_revenue")
).show()
```

---

### 3.8 Joins

```python
# default is inner
df1.join(df2, "id").show()

df1.join(df2, "id", "left").show()
df1.join(df2, ["id", "country"], "outer").show()

from pyspark.sql.functions import broadcast
df1.join(broadcast(df2), "id", "inner").show()
```

---

### 3.9 Window Functions

```python
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number, rank, lag

w = Window.partitionBy("group_col").orderBy(col("metric").desc())

df = df.withColumn("rn", row_number().over(w))
df = df.withColumn("prev_metric", lag("metric", 1).over(w))
```

---

### 3.10 Repartition / Coalesce

```python
df.rdd.getNumPartitions()

df_repart = df.repartition(20)   # shuffle
df_small  = df.coalesce(2)       # shrink, no shuffle
```

---

### 3.11 Cache / Persist

```python
from pyspark.storagelevel import StorageLevel

df_cached = df.persist(StorageLevel.MEMORY_AND_DISK)
df_cached.count()
df_cached.unpersist()
```

---

### 3.12 UDF & Pandas UDF

```python
from pyspark.sql.functions import udf, pandas_udf
from pyspark.sql.types import IntegerType
import pandas as pd

# Regular UDF
@udf(IntegerType())
def plus_one(x):
    return x + 1

df = df.withColumn("x1", plus_one(col("x")))

# Pandas UDF
@pandas_udf("int")
def plus_one_pd(s: pd.Series) -> pd.Series:
    return s + 1

df = df.withColumn("x1", plus_one_pd(col("x")))
```

---

### 3.13 Writing Data

```python
df.write.mode("overwrite").parquet("path/out_parquet")
df.write.mode("append").json("path/out_json")
df.write.mode("overwrite").option("header", True).csv("path/out_csv")
```

---

### 3.14 Useful Configs

```python
spark.conf.set("spark.sql.shuffle.partitions", 200)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "1GB")
```

---

If you like, next I can:

* Turn all of this into a **PDF-style text** you could paste into a document.
* Create **PySpark practice exercises** (with solutions).
* Simulate a **mock PySpark interview** where I ask you questions and you answer.
