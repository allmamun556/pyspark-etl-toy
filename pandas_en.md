# Pandas Tutorial (Detailed and Beginner-Friendly)

Welcome! This tutorial will guide you through the basics and intermediate features of **pandas**, one of the most powerful Python libraries for data analysis.

---

## 1. Introduction to Pandas

Pandas is a Python library used for data manipulation and analysis. It provides two main data structures:

* **Series**: A one-dimensional labeled array.
* **DataFrame**: A two-dimensional labeled data structure with columns of potentially different types.

---

## 2. Installing Pandas

You can install pandas using pip:

```bash
pip install pandas
```

---

## 3. Importing Pandas

```python
import pandas as pd
```

---

## 4. Pandas Data Structures

### 4.1 Series

A Series is like a list with labels.

```python
s = pd.Series([10, 20, 30])
```

### 4.2 DataFrame

A DataFrame is like a table.

```python
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [24, 30, 29]
}
df = pd.DataFrame(data)
```

---

## 5. Reading and Writing Data

Pandas can read and write many file types.

### 5.1 Reading CSV

```python
df = pd.read_csv('file.csv')
```

### 5.2 Writing CSV

```python
df.to_csv('output.csv', index=False)
```

### 5.3 Reading Excel

```python
df = pd.read_excel('file.xlsx')
```

---

## 6. Exploring Data

These commands help you understand your dataset.

```python
df.head()        # First 5 rows
df.tail()        # Last 5 rows
df.info()        # Column info
df.describe()    # Summary statistics
```

---

## 7. Selecting Data

### 7.1 Selecting Columns

```python
df['Name']
df[['Name', 'Age']]
```

### 7.2 Selecting Rows

```python
df.iloc[0]      # By index
```

### 7.3 Filtering

```python
df[df['Age'] > 25]
```

---

## 8. Modifying Data

### 8.1 Adding Columns

```python
df['Country'] = 'USA'
```

### 8.2 Removing Columns

```python
df = df.drop('Country', axis=1)
```

### 8.3 Renaming Columns

```python
df = df.rename({'Name': 'FullName'}, axis=1)
```

---

## 9. Handling Missing Values

### 9.1 Detecting Missing Values

```python
df.isnull()
```

### 9.2 Filling Missing Values

```python
df.fillna(0)
```

### 9.3 Dropping Missing Rows

```python
df.dropna()
```

---

## 10. Grouping and Aggregation

```python
grouped = df.groupby('Category')['Value'].mean()
```

---

## 11. Merging and Joining

### 11.1 Merge

```python
merged = pd.merge(df1, df2, on='id')
```

### 11.2 Concatenate

```python
result = pd.concat([df1, df2])
```

---

## 12. Sorting Data

```python
df.sort_values('Age')
```

---

## 13. Pivot Tables

```python
pivot = df.pivot_table(values='Value', index='Category', aggfunc='mean')
```

---

## 14. Applying Functions

```python
df['Age_plus_1'] = df['Age'].apply(lambda x: x + 1)
```

---

## 15. Visualization with Pandas

Pandas integrates with matplotlib for simple plots.

```python
df['Age'].plot()
```

---

## 16. Conclusion

You now know the essentials of pandas! If you'd like, I can expand this tutorial with exercises, advanced topics, or real datasets.

---

Let me know what you'd like to add or improve!

Here’s a clear and detailed comparison between **Pandas** and **PySpark**, so you can understand when to use each one:

---

# ✅ **Pandas vs. PySpark — Key Differences**

## **1. Purpose and Use Case**

### **Pandas**

* Designed for **small to medium-sized datasets**.
* Works **on a single machine** (your computer’s RAM).
* Great for **data cleaning, analysis, and exploration**.
* Very easy to use and intuitive.

### **PySpark**

* Python API for **Apache Spark**.
* Designed for **big data (very large datasets)**.
* Works on **distributed systems** (multiple machines / clusters).
* Ideal for **large-scale data processing, ETL pipelines, machine learning on big data**, etc.

---

## **2. Performance**

### **Pandas**

* Fast for small datasets.
* Slows down or crashes if data exceeds your system RAM.

### **PySpark**

* Optimized for **distributed parallel processing**.
* Can process terabytes or petabytes of data.
* Uses **lazy evaluation** for efficiency.

---

## **3. Memory Usage**

### **Pandas**

* Loads all data into RAM.
* Limited by hardware.

### **PySpark**

* Data is distributed across cluster nodes.
* Handles datasets too large for a single machine.

---

## **4. Execution Model**

### **Pandas**

* **Eager execution**: operations run immediately.

### **PySpark**

* **Lazy execution**: operations are planned first and executed only when needed.
* Allows complex optimization.

---

## **5. Syntax and Learning Curve**

### **Pandas**

* More intuitive and Pythonic.
* Easier for beginners.

### **PySpark**

* More complex syntax.
* Requires understanding of distributed computing concepts.

---

## **6. Deployment**

### **Pandas**

* Suitable for notebooks, small apps, personal projects.

### **PySpark**

* Used in production big data environments (Hadoop, Databricks, AWS EMR, etc.).

---

## **7. Typical Use Cases**

### **Use Pandas when:**

* Dataset fits in memory.
* You’re exploring or cleaning data.
* Doing small to mid-size ML experiments.

### **Use PySpark when:**

* Dataset is **huge** (GBs to TBs+).
* You need distributed processing.
* Running ETL jobs on a data lake or cluster.

---

# ✔️ **Simple Comparison Table**

| Feature     | Pandas             | PySpark                              |
| ----------- | ------------------ | ------------------------------------ |
| Data Size   | Small–Medium       | Very Large (Big Data)                |
| Memory      | In-RAM             | Distributed                          |
| Execution   | Eager              | Lazy                                 |
| Speed       | Fast (small data)  | Fast (big data)                      |
| Ease of Use | Easy               | Moderate                             |
| Best For    | Analysis, modeling | Large-scale ETL, big data processing |

---

# ✔️ Example Code Difference

### **Pandas**

```python
import pandas as pd

df = pd.read_csv("data.csv")
df.groupby("category")["sales"].sum()
```

### **PySpark**

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("App").getOrCreate()
df = spark.read.csv("data.csv", header=True, inferSchema=True)

df.groupBy("category").sum("sales").show()
```

---

# 🔍 Final Summary

* **Pandas = small data, easy, local processing.**
* **PySpark = big data, distributed, scalable processing.**

If you want, I can also create:
✅ A side-by-side cheat sheet
✅ A decision flowchart “Pandas or PySpark?”
✅ Examples using the same dataset in both tools

Just tell me!
Below is a **detailed list of real interview questions on Pandas**, written in English, with **clear explanations and code examples**. These questions are commonly asked in data analyst, data engineer, and data scientist interviews.

---

# ✅ **Pandas Interview Questions (Beginner → Advanced)**

Includes **explanations + code examples**.

---

# 📘 **1. What is Pandas, and why is it used?**

### **Answer:**

Pandas is a Python library for **data manipulation, cleaning, and analysis**.
It provides two main data structures:

* **Series** (1-D labeled data)
* **DataFrame** (2-D tabular data)

### **Example:**

```python
import pandas as pd
df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'Age': [24, 30]})
```

---

# 📘 **2. What is the difference between a Series and a DataFrame?**

### **Answer:**

| Series               | DataFrame                 |
| -------------------- | ------------------------- |
| 1-dimensional        | 2-dimensional             |
| Like a single column | Table with rows + columns |
| Has one axis         | Has two axes              |

### **Example:**

```python
s = pd.Series([1,2,3])
df = pd.DataFrame({'col1':[1,2,3], 'col2':[4,5,6]})
```

---

# 📘 **3. How do you read a CSV file in Pandas?**

### **Answer:**

```python
df = pd.read_csv("file.csv")
```

---

# 📘 **4. How to check the first and last rows of a DataFrame?**

### **Example:**

```python
df.head()    # first 5 rows
df.tail()    # last 5 rows
```

---

# 📘 **5. How do you select a single column and multiple columns?**

### **Example:**

```python
df['Age']               # single column
df[['Name','Age']]      # multiple columns
```

---

# 📘 **6. Difference between .iloc and .loc?**

### **Answer:**

| Feature    | loc       | iloc         |
| ---------- | --------- | ------------ |
| Selects by | label     | index number |
| Example    | df.loc[2] | df.iloc[2]   |

### **Example:**

```python
df.loc[2]      # row with index label 2
df.iloc[2]     # third row
```

---

# 📘 **7. How do you filter rows in Pandas?**

### **Example:**

```python
df[df['Age'] > 25]
```

---

# 📘 **8. How do you handle missing values?**

### **Detect missing**

```python
df.isnull().sum()
```

### **Fill missing**

```python
df.fillna(0)
```

### **Remove missing rows**

```python
df.dropna()
```

---

# 📘 **9. What is the difference between apply(), map(), and applymap()?**

### **Answer:**

| Function       | Works On            | Description                    |
| -------------- | ------------------- | ------------------------------ |
| **map()**      | Series              | Applies function to each value |
| **apply()**    | Series or DataFrame | Row/column-wise                |
| **applymap()** | DataFrame           | Every element                  |

### **Example:**

```python
df['Age'].map(lambda x: x + 1)
df.apply(lambda col: col.max())
df.applymap(lambda x: x*2)
```

---

# 📘 **10. How do you remove a column in Pandas?**

### **Example:**

```python
df = df.drop('Age', axis=1)
```

---

# 📘 **11. What is groupby(), and why is it used?**

### **Answer:**

`groupby()` groups data by one or more columns and applies an aggregate function.

### **Example:**

```python
df.groupby('Department')['Salary'].mean()
```

---

# 📘 **12. How do you merge two DataFrames?**

### **Example:**

```python
pd.merge(df1, df2, on='id', how='inner')
```

**Types of merge:**

* **inner**
* **left**
* **right**
* **outer**

---

# 📘 **13. What is the difference between merge(), join(), and concat()?**

### **Answer:**

| Function     | Purpose                              |
| ------------ | ------------------------------------ |
| **merge()**  | SQL-style joins using columns        |
| **join()**   | Join using DataFrame index           |
| **concat()** | Stack DataFrames vertical/horizontal |

### **Examples:**

```python
pd.concat([df1, df2], axis=0)   # vertical stack
df1.join(df2)                   # index-based join
```

---

# 📘 **14. How do you sort data in Pandas?**

### **Example:**

```python
df.sort_values('Age')
df.sort_values(['Age','Salary'], ascending=[True, False])
```

---

# 📘 **15. How do you reset the index?**

### **Example:**

```python
df.reset_index(drop=True)
```

---

# 📘 **16. What is a pivot table?**

### **Example:**

```python
df.pivot_table(values='Sales', index='Region', aggfunc='sum')
```

---

# 📘 **17. How do you find duplicates?**

### **Example:**

```python
df.duplicated()
df.drop_duplicates()
```

---

# 📘 **18. How do you convert data types in Pandas?**

### **Example:**

```python
df['Age'] = df['Age'].astype(int)
```

---

# 📘 **19. How do you read a large file in chunks?**

(Asked in many interviews!)

### **Example:**

```python
for chunk in pd.read_csv("big.csv", chunksize=50000):
    print(chunk.shape)
```

---

# 📘 **20. What is vectorization in Pandas? Why is it important?**

### **Answer:**

Vectorization means using Pandas’ internal optimized C operations instead of Python loops.

### **Example (slow):**

```python
df['Age_plus_1'] = df['Age'].apply(lambda x: x+1)
```

### **Vectorized (fast):**

```python
df['Age_plus_1'] = df['Age'] + 1
```

---

# 📘 **21. How do you find correlation between columns?**

### **Example:**

```python
df.corr()
```

---

# 📘 **22. How do you perform one-hot encoding in Pandas?**

### **Example:**

```python
pd.get_dummies(df, columns=['City'])
```

---

# 📘 **23. How do you combine text columns?**

### **Example:**

```python
df['FullName'] = df['First'] + " " + df['Last']
```

---

# 📘 **24. How do you set a column as an index?**

### **Example:**

```python
df.set_index('ID', inplace=True)
```

---

# 📘 **25. How do you convert a DataFrame to a NumPy array?**

### **Example:**

```python
df.values
```

---

# 🎯 **Want More? I Can Provide:**

✅ 50+ more advanced Pandas interview questions
✅ Scenario-based questions (very common in real interviews)
✅ A PDF version of all questions
✅ Coding challenges using Pandas
✅ A mock interview

Just tell me what you want!
