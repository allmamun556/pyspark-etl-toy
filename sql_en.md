Below is a **detailed, beginner-friendly SQL tutorial in English**, including:

✔ Very clear explanations
✔ ASCII diagrams for concepts
✔ Practical examples for each topic
✔ Increasing difficulty levels

This can help you prepare for real SQL interviews or practical work.

---

# 🎓 **SQL Tutorial: From Beginner to Advanced (with ASCII Diagrams & Examples)**

---

# 1️⃣ What is SQL?

**SQL** (Structured Query Language) is a language used to:

* Store data
* Retrieve data
* Update data
* Delete data
* Manage databases

SQL is used everywhere: websites, apps, analytics pipelines, data science systems, and more.

---

# 2️⃣ Database & Table Basics

A **database** contains **tables**, and tables contain rows and columns.

### Example ASCII table:

```
+------------+-----------+-----------+
| id         | name      | salary    |
+------------+-----------+-----------+
| 1          | Alice     | 50000     |
| 2          | Bob       | 60000     |
| 3          | Charlie   | 55000     |
+------------+-----------+-----------+
```

Each column has a **data type**:

* INT → whole numbers
* VARCHAR → text
* DATE → date
* BOOLEAN → true/false

---

# 3️⃣ Creating a Table

```
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    salary INT,
    hire_date DATE
);
```

---

# 4️⃣ Inserting Data

```
INSERT INTO employees (id, name, department, salary, hire_date)
VALUES
(1, 'Alice', 'HR', 50000, '2021-04-01'),
(2, 'Bob', 'Engineering', 60000, '2020-06-15'),
(3, 'Charlie', 'Marketing', 55000, '2019-10-20');
```

---

# 5️⃣ Reading Data (SELECT)

### Basic query:

```
SELECT * FROM employees;
```

### Selecting specific columns:

```
SELECT name, salary FROM employees;
```

### Filtering rows (WHERE):

```
SELECT * 
FROM employees
WHERE salary > 55000;
```

### Using multiple conditions:

```
SELECT * 
FROM employees
WHERE department = 'Engineering' 
  AND salary > 50000;
```

---

# 6️⃣ Sorting (ORDER BY)

```
SELECT *
FROM employees
ORDER BY salary DESC;
```

---

# 7️⃣ Limiting Rows

```
SELECT * FROM employees
ORDER BY salary DESC
LIMIT 2;
```

---

# 8️⃣ Updating Data

```
UPDATE employees
SET salary = 65000
WHERE id = 2;
```

---

# 9️⃣ Deleting Data

```
DELETE FROM employees
WHERE id = 3;
```

---

# 🔟 SQL Functions (SUM, AVG, MIN, MAX)

### Count employees:

```
SELECT COUNT(*) FROM employees;
```

### Average salary:

```
SELECT AVG(salary) FROM employees;
```

### Salary summary per department:

```
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department;
```

### ASCII diagram of GROUP BY:

```
Before grouping:
-------------------------------
HR: salary 50000
HR: salary 52000
Engineering: salary 60000
Engineering: salary 65000
-------------------------------

After GROUP BY department:
-------------------------------
HR → average calculated
Engineering → average calculated
-------------------------------
```

---

# 1️⃣1️⃣ HAVING (like WHERE but for groups)

```
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 55000;
```

---

# 1️⃣2️⃣ JOINs Explained (with ASCII Diagrams)

JOINs combine related data from different tables.

### Example tables:

**employees:**

```
+----+---------+-------------+
| id | name    | department_id |
+----+---------+-------------+
|  1 | Alice   | 1           |
|  2 | Bob     | 2           |
|  3 | Charlie | 1           |
+----+---------+-------------+
```

**departments:**

```
+----+-------------+
| id | dept_name   |
+----+-------------+
| 1  | HR          |
| 2  | Engineering |
| 3  | Finance     |
+----+-------------+
```

---

## ⭐ INNER JOIN

Returns matching rows only.

```
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d
ON e.department_id = d.id;
```

### ASCII DIAGRAM

```
employees          departments
   +---+               +---+
   | 1 |  works with   | 1 |
   | 2 |  ↔            | 2 |
   | 3 |               | 3 |
   +---+               +---+

Result = matches only:
   (1 ↔ 1), (2 ↔ 2), (3 ↔ 1)
```

---

## ⭐ LEFT JOIN

Returns everything from LEFT table + matches from RIGHT.

```
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d
ON e.department_id = d.id;
```

### ASCII Diagram:

```
LEFT JOIN:
+-----------+-------------------+
| employees | departments       |
+-----------+-------------------+
| All rows  | matched or NULL   |
+-----------+-------------------+
```

---

## ⭐ RIGHT JOIN

Returns everything from RIGHT table + matches from LEFT.

```
SELECT e.name, d.dept_name
FROM employees e
RIGHT JOIN departments d
ON e.department_id = d.id;
```

---

## ⭐ FULL OUTER JOIN

Returns all rows from both tables (with NULLs where no match).

```
SELECT *
FROM employees
FULL OUTER JOIN departments
ON employees.department_id = departments.id;
```

---

# 1️⃣3️⃣ Subqueries

### Example: Find employees earning above company average:

```
SELECT name, salary
FROM employees
WHERE salary > (
    SELECT AVG(salary) FROM employees
);
```

---

# 1️⃣4️⃣ SQL Window Functions (Advanced)

### Ranking employees by salary:

```
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees;
```

---

# 1️⃣5️⃣ Practical Exercise Section (with Solutions)

### **Exercise 1:**

Get the highest salary employee.

**Query:**

```
SELECT name, salary
FROM employees
ORDER BY salary DESC
LIMIT 1;
```

---

### **Exercise 2:**

Count employees per department.

```
SELECT department, COUNT(*) AS total
FROM employees
GROUP BY department;
```

---

### **Exercise 3:**

Find employees hired after 2020.

```
SELECT *
FROM employees
WHERE hire_date >= '2020-01-01';
```

---

# 1️⃣6️⃣ Database Architecture ASCII Overview

```
+---------------------+
|     Application     |
| (Python, JS, etc.)  |
+-----------+---------+
            |
            | SQL Query
            v
+-----------+---------+
|    SQL Engine       |
|  (MySQL, Postgres)  |
+-----------+---------+
            |
            v
+---------------------+
|     Table Storage   |
|   (rows & indexes)  |
+---------------------+
```

---

# 🎉 End of Tutorial — Next Steps

I can also prepare:

✔ SQL interview questions + answers
✔ SQL practice tasks with datasets
✔ SQL cheat sheet (1-page summary)
✔ A beginner-to-advanced SQL course structure

Would you like additional exercises or a PDF version?
Here is a **clear, deep, and practical explanation of SQL Window Functions in English**, including ASCII diagrams and plenty of examples.
This is interview-ready and suitable for real production work.

---

# 🎓 **SQL Window Functions – Complete Explanation (with Examples + Diagrams)**

Window Functions allow you to perform calculations **across multiple rows** **without** grouping or losing detail, unlike `GROUP BY`.

They are essential for analytics, data engineering, finance, time-series, ML feature engineering, and reporting.

---

# 1️⃣ What is a Window Function?

A window function performs a calculation across a “window” of rows related to the current row.

General syntax:

```sql
FUNCTION_NAME(...) OVER (
    PARTITION BY column
    ORDER BY column
    ROWS BETWEEN ... 
)
```

---

# 2️⃣ Why Window Functions are Powerful

They allow you to:

✔ Rank rows
✔ Calculate running totals
✔ Compute moving averages
✔ Compare current row with previous/next rows
✔ Calculate percentages
✔ Avoid losing data (unlike GROUP BY)

---

# 3️⃣ Example Table

We will use this table:

```
sales
+------------+---------+--------+
| employee   | month   | amount |
+------------+---------+--------+
| Alice      | Jan     | 1000   |
| Alice      | Feb     | 1500   |
| Alice      | Mar     | 1200   |
| Bob        | Jan     |  800   |
| Bob        | Feb     |  950   |
| Bob        | Mar     | 1100   |
+------------+---------+--------+
```

---

# 4️⃣ PARTITION BY Explained (with ASCII Diagram)

`PARTITION BY` divides the data into groups, but **does NOT collapse** the rows.

Example:

```sql
RANK() OVER (PARTITION BY employee ORDER BY amount DESC)
```

**ASCII Diagram**

```
Window partitions:

Partition 1 (employee = Alice):
    Jan 1000
    Feb 1500
    Mar 1200

Partition 2 (employee = Bob):
    Jan 800
    Feb 950
    Mar 1100
```

Each partition is processed separately.

---

# 5️⃣ ORDER BY in Window Functions

Defines **row order inside the partition**:

```sql
SUM(amount) OVER (PARTITION BY employee ORDER BY month)
```

This is needed for ranking, running totals, moving averages, etc.

---

# 6️⃣ Essential Window Functions (with examples)

---

## ⭐ 1) RANK(), DENSE_RANK(), ROW_NUMBER()

### Example

```sql
SELECT 
    employee,
    month,
    amount,
    RANK() OVER (PARTITION BY employee ORDER BY amount DESC) AS rank_amount
FROM sales;
```

**Output:**

```
+---------+-------+--------+-------------+
|employee |month  |amount  |rank_amount  |
+---------+-------+--------+-------------+
|Alice    |Feb    |1500    |1            |
|Alice    |Mar    |1200    |2            |
|Alice    |Jan    |1000    |3            |
|Bob      |Mar    |1100    |1            |
|Bob      |Feb    |950     |2            |
|Bob      |Jan    |800     |3            |
+---------+-------+--------+-------------+
```

---

## ⭐ 2) Running Total (Cumulative Sum)

```sql
SELECT
    employee,
    month,
    amount,
    SUM(amount) OVER (
        PARTITION BY employee
        ORDER BY month
    ) AS running_total
FROM sales;
```

**Output (for Alice):**

```
Jan: 1000 → total 1000
Feb: 1500 → total 2500
Mar: 1200 → total 3700
```

---

## ⭐ 3) Moving Average (Rolling Window)

```sql
SELECT
    employee,
    month,
    amount,
    AVG(amount) OVER (
        PARTITION BY employee
        ORDER BY month
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS moving_avg
FROM sales;
```

**ASCII Window Diagram**

For Feb:

```
Window:
[ Jan, Feb, Mar ]
```

For Jan:

```
Window:
[ Jan, Feb ]
```

---

## ⭐ 4) LAG() and LEAD()

Used to access previous or next row values.

### Example: Compare this month to previous month

```sql
SELECT
    employee,
    month,
    amount,
    LAG(amount, 1) OVER (
        PARTITION BY employee ORDER BY month
    ) AS previous_month,
    amount - LAG(amount, 1) OVER (
        PARTITION BY employee ORDER BY month
    ) AS diff
FROM sales;
```

**Output example for Alice:**

```
Jan: previous = NULL
Feb: previous = 1000 → diff = 500
Mar: previous = 1500 → diff = -300
```

---

## ⭐ 5) Percent of Total (Useful for BI)

Example: Sales % per employee

```sql
SELECT
    employee,
    amount,
    amount * 100.0 /
        SUM(amount) OVER () AS percent_of_total
FROM sales;
```

Or per employee:

```sql
SELECT
    employee,
    month,
    amount,
    amount * 100.0 /
        SUM(amount) OVER (PARTITION BY employee) AS percent_of_employee_total
FROM sales;
```

---

## ⭐ 6) FIRST_VALUE() and LAST_VALUE()

Example:

```sql
SELECT
    employee,
    month,
    amount,
    FIRST_VALUE(amount) OVER (
        PARTITION BY employee ORDER BY month
    ) AS first_month_sales
FROM sales;
```

For Alice: **1000**

---

# 7️⃣ FULL EXAMPLE: Ranking + Running Totals + Previous Month

```sql
SELECT
    employee,
    month,
    amount,
    ROW_NUMBER() OVER (PARTITION BY employee ORDER BY month) AS row_num,
    SUM(amount) OVER (PARTITION BY employee ORDER BY month) AS cumulative,
    LAG(amount, 1) OVER (PARTITION BY employee ORDER BY month) AS prev_month,
    amount - LAG(amount, 1) OVER (PARTITION BY employee ORDER BY month) AS change_from_prev
FROM sales
ORDER BY employee, month;
```

---

# 8️⃣ Window Frames (ROWS BETWEEN)

### Default frame

```
RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
```

### Common window frames

| Purpose             | Frame                                              |
| ------------------- | -------------------------------------------------- |
| Running Total       | `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` |
| Moving Avg (3 rows) | `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`         |
| Compare neighbors   | `ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING`         |

ASCII illustration:

```
Current row = Feb
Window = Jan, Feb, Mar
```

---

# 9️⃣ When NOT to use Window Functions

❌ Very large tables without proper indexes
❌ When aggregation collapses the view (use GROUP BY instead)
❌ When performance is critical and simpler queries suffice

---

# 🔟 Practical Exercises (You can try these)

1. Find the top-selling month per employee
2. Compute cumulative sales per employee
3. Compute a 3-month moving average
4. Calculate month-over-month growth
5. Rank employees by total sales

I can generate queries & solutions if you want!

---

# 🎉 Summary

Window Functions allow:

✔ Analytics
✔ Rankings
✔ Time-series calculations
✔ Cumulative calculations
✔ Row-by-row comparisons
✔ Smooth data analysis without losing rows

They are one of the **most important** SQL topics for advanced work.

---

If you'd like, I can also provide:

📌 A full practice dataset + exercises
📌 A cheat sheet (1 page)
📌 Window Functions interview questions + answers
📌 A comparison of Window vs GROUP BY

Just tell me!
Below is a comprehensive set of **SQL Window Function interview questions with clear, strong answers**, ranging from beginner → intermediate → advanced.
These are perfect for **data science, data engineering, BI, backend, and analytics interviews**.

---

# 🧩 **SQL Window Function Interview Questions + Perfect Answers**

---

# 🔰 **BEGINNER-LEVEL QUESTIONS**

---

### **1. What is a SQL Window Function?**

**Answer:**
A window function performs a calculation across a set of rows related to the current row **without collapsing the result into groups**.
This means every row keeps its detail while still allowing aggregated calculations such as ranking, cumulative sums, moving averages, etc.

---

### **2. What is the difference between GROUP BY and Window Functions?**

**Answer:**

* **GROUP BY** collapses rows → returns one row per group
* **Window Functions** keep all rows → just add new calculated columns

Example:
`SUM()` with GROUP BY → loses row-level detail
`SUM() OVER()` → keeps all rows and adds the sum as a new column

---

### **3. What does PARTITION BY do?**

**Answer:**
`PARTITION BY` divides rows into groups (partitions) on which the window function operates independently.

Example:

```sql
SUM(sales) OVER (PARTITION BY country)
```

→ computes the sum per country, but still returns every row.

---

### **4. What does ORDER BY do in a Window Function?**

**Answer:**
Defines how rows are ordered **within each partition**.
It is required for running totals, ranking, moving averages, etc.

---

# 🟦 **INTERMEDIATE QUESTIONS**

---

### **5. What is the difference between ROW_NUMBER(), RANK(), and DENSE_RANK()?**

**Answer:**

| Function         | Behavior                                   |
| ---------------- | ------------------------------------------ |
| **ROW_NUMBER()** | Always unique sequence (1,2,3…)            |
| **RANK()**       | Gives same rank to ties, but skips numbers |
| **DENSE_RANK()** | Gives same rank to ties, no gaps           |

Example for values: 100, 90, 90, 80

```
ROW_NUMBER → 1,2,3,4
RANK       → 1,2,2,4
DENSE_RANK → 1,2,2,3
```

---

### **6. What is a window frame?**

**Answer:**
A window frame defines **how many rows** the window covers relative to the current row.

Example:

```sql
ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
```

This frame is needed for:

* Moving averages
* Rolling sums
* Cumulative operations with custom frames

---

### **7. What does UNBOUNDED PRECEDING mean?**

**Answer:**
It means the frame starts at the **first row** of the partition.

Used in running totals:

```sql
SUM(amount) OVER (
  PARTITION BY customer
  ORDER BY date
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
)
```

---

### **8. Explain LAG() and LEAD().**

**Answer:**

* **LAG()** accesses a value from a previous row
* **LEAD()** accesses a value from a following row

Example:

```sql
LAG(sales, 1) OVER (ORDER BY month) 
```

→ Previous month’s sales.

---

### **9. What is FIRST_VALUE() and LAST_VALUE()?**

**Answer:**

* **FIRST_VALUE()** returns the first ordered row within the partition
* **LAST_VALUE()** returns the last ordered row (but requires a frame fix)

Correct usage for LAST_VALUE:

```sql
LAST_VALUE(amount) OVER (
  PARTITION BY employee ORDER BY month
  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
)
```

---

# 🟥 **ADVANCED QUESTIONS**

---

### **10. Why can LAST_VALUE() return unexpected results?**

**Answer:**
Because the default window frame ends at the current row, not the final row.
You must manually extend the frame:

```sql
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
```

---

### **11. What is the difference between ROWS and RANGE?**

**Answer:**

* **ROWS** → counts physical rows
* **RANGE** → groups by value equivalence

Example:

For ORDER BY amount:

```
RANGE BETWEEN CURRENT ROW AND 1 FOLLOWING
```

→ includes ALL rows with the same amount value.

This can affect performance and correctness.

---

### **12. How do you calculate a 7-day moving average?**

**Answer:**

```sql
SELECT 
  date,
  value,
  AVG(value) OVER (
    ORDER BY date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS moving_avg
FROM mytable;
```

---

### **13. How do you calculate percent of total using Window Functions?**

**Answer:**

```sql
SELECT
  employee,
  sales,
  sales * 1.0 / SUM(sales) OVER () AS pct_of_total
FROM sales_table;
```

---

### **14. How do Window Functions improve performance compared to self-joins?**

**Answer:**
Many operations like running totals or previous-row comparisons normally require **self-joins**.
Window Functions:

* Reduce complexity
* Avoid repeated scans
* Are optimized by the SQL engine

Thus they are much faster and cleaner.

---

### **15. How would you get the top N rows per group?**

Example: top 2 sales per employee:

```sql
WITH ranked AS (
  SELECT
    employee,
    sale,
    ROW_NUMBER() OVER (
      PARTITION BY employee ORDER BY sale DESC
    ) AS rn
  FROM sales
)
SELECT *
FROM ranked
WHERE rn <= 2;
```

---

# 🧠 **BONUS: PRACTICE QUESTIONS (no answers unless you ask!)**

1. Calculate month-over-month growth per product
2. Find the highest selling month for each employee
3. Compute rolling 30-day revenue
4. Find the top 3 customers by spending in each country
5. Flag transactions that exceed the previous 3-day moving average
6. Calculate customer lifetime value per user (cumulative sum)
7. Compare each sale to the average of the partition
8. Compute cumulative distinct count using window functions

I can generate all answers if needed.

---

# 🎉 Want more?

I can prepare:

✔ A full SQL Window Function cheat sheet
✔ 20 advanced interview exercises with solutions
✔ A full SQL interview preparation pack
✔ Practice datasets for you to run queries on

Just tell me!
Below are **all 8 advanced SQL window function problems**, each with:

✅ A simple example dataset
✅ The correct SQL query
✅ The expected output
✅ Explanation

Everything is written clearly so you can use it for interviews or practice.

---

# 1️⃣ **Calculate month-over-month growth per product**

### Example Table: `sales`

```
+------------+---------+--------+
| product    | month   | amount |
+------------+---------+--------+
| A          | Jan     | 100    |
| A          | Feb     | 150    |
| A          | Mar     | 120    |
| B          | Jan     | 200    |
| B          | Feb     | 220    |
+------------+---------+--------+
```

### SQL Query

```sql
SELECT
    product,
    month,
    amount,
    LAG(amount, 1) OVER (
        PARTITION BY product
        ORDER BY month
    ) AS previous_month_amount,
    amount - LAG(amount, 1) OVER (
        PARTITION BY product
        ORDER BY month
    ) AS month_over_month_growth
FROM sales;
```

### Explanation

`LAG()` retrieves last month’s amount → subtract to get growth.

---

# 2️⃣ **Find the highest-selling month for each employee**

### Example Table: `employee_sales`

```
+----------+--------+--------+
| employee | month  | amount |
+----------+--------+--------+
| Alice    | Jan    | 1000   |
| Alice    | Feb    | 1500   |
| Alice    | Mar    | 1200   |
| Bob      | Jan    | 800    |
| Bob      | Feb    | 950    |
| Bob      | Mar    | 1100   |
+----------+--------+--------+
```

### SQL Query

```sql
WITH ranked AS (
    SELECT
        employee,
        month,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY employee
            ORDER BY amount DESC
        ) AS rn
    FROM employee_sales
)
SELECT employee, month, amount
FROM ranked
WHERE rn = 1;
```

### Explanation

`ROW_NUMBER()` ranks sales per employee → pick rank 1.

---

# 3️⃣ **Compute rolling 30-day revenue**

### Example Table: `daily_revenue`

```
+------------+---------+
| date       | revenue |
+------------+---------+
| 2023-01-01 | 100     |
| 2023-01-02 | 120     |
| ...        | ...     |
```

### SQL Query

```sql
SELECT
    date,
    revenue,
    SUM(revenue) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_30_day_revenue
FROM daily_revenue
ORDER BY date;
```

### Explanation

The window covers **30 days = current row + previous 29 rows**.

---

# 4️⃣ **Find the top 3 customers by spending per country**

### Example Table: `purchases`

```
+----------+----------+---------+--------+
| customer | country  | amount  | date   |
+----------+----------+---------+--------+
| C1       | USA      | 500     | ...    |
| C2       | USA      | 300     | ...    |
| C3       | USA      | 450     | ...    |
| C1       | DE       | 100     | ...    |
+----------+----------+---------+--------+
```

### SQL Query

```sql
WITH ranked AS (
    SELECT
        customer,
        country,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY amount DESC
        ) AS rn
    FROM purchases
)
SELECT *
FROM ranked
WHERE rn <= 3;
```

### Explanation

Rank customers inside each country, filter top 3.

---

# 5️⃣ **Flag transactions that exceed the previous 3-day moving average**

### Example Table: `transactions`

```
+------------+-------------+
| date       | amount      |
+------------+-------------+
| 2023-01-01 | 100         |
| 2023-01-02 | 150         |
| 2023-01-03 | 120         |
| 2023-01-04 | 300         |
+------------+-------------+
```

### SQL Query

```sql
SELECT
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ) AS avg_last_3_days,
    CASE
        WHEN amount > AVG(amount) OVER (
            ORDER BY date
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        ) THEN 'EXCEEDS'
        ELSE 'OK'
    END AS flag
FROM transactions;
```

### Explanation

Window frame:

* Preceding 3 rows
* Up to the row immediately before current

---

# 6️⃣ **Calculate customer lifetime value per user (cumulative sum)**

### Example Table: `orders`

```
+----------+------------+--------+
| customer | date       | amount |
+----------+------------+--------+
| C1       | 2023-01-01 | 100    |
| C1       | 2023-01-05 | 200    |
| C1       | 2023-01-20 | 50     |
| C2       | 2023-01-02 | 300    |
+----------+------------+--------+
```

### SQL Query

```sql
SELECT
    customer,
    date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer
        ORDER BY date
    ) AS lifetime_value
FROM orders;
```

### Explanation

Cumulative sum (`SUM OVER`) per customer.

---

# 7️⃣ **Compare each sale to the average of the partition**

### Example Table: `employee_sales`

```
+----------+--------+--------+
| employee | month  | amount |
+----------+--------+--------+
```

### SQL Query

```sql
SELECT
    employee,
    month,
    amount,
    AVG(amount) OVER (PARTITION BY employee) AS avg_per_employee,
    amount - AVG(amount) OVER (PARTITION BY employee) AS diff_from_avg
FROM employee_sales;
```

### Explanation

Calculate average per employee → subtract.

---

# 8️⃣ **Compute cumulative distinct count using window functions**

⚠️ SQL has **no built-in DISTINCT CUMULATIVE** function,
but we can mimic it using a window function + ROW_NUMBER.

### Example Table: `page_views`

```
+----------+------------+
| user_id  | timestamp  |
+----------+------------+
| U1       | 2023-01-01 |
| U1       | 2023-01-02 |
| U2       | 2023-01-03 |
| U1       | 2023-01-04 |
+----------+------------+
```

We want to count distinct users up to each timestamp.

### SQL Query

```sql
WITH distinct_users AS (
    SELECT
        timestamp,
        user_id,
        ROW_NUMBER() OVER (
            PARTITION BY user_id
            ORDER BY timestamp
        ) AS user_first_seen
    FROM page_views
),
first_visits AS (
    SELECT
        timestamp,
        CASE WHEN user_first_seen = 1 THEN user_id END AS new_user
    FROM distinct_users
)
SELECT
    timestamp,
    COUNT(new_user) OVER (
        ORDER BY timestamp
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_distinct_users
FROM first_visits;
```

### Explanation

1. Identify when each user appears for the **first time**
2. Count cumulative first-time users

---

# 🎉 If you want more:

I can generate:

✔ 20 more advanced SQL window exercises
✔ A complete SQL interview preparation guide
✔ Real datasets + practice queries
✔ A PDF cheat sheet for window functions

Just tell me!
Below are **20 advanced SQL window function exercises** with **full answers + explanations**.
These are perfect for interview prep or mastering real production SQL.

---

# 🧠 **20 Advanced SQL Window Function Exercises (with Answers)**

We assume common table names and structures so every query is runnable.

---

# 1️⃣ **Running sum of sales per region sorted by date**

### Table: `sales(region, date, amount)`

### Query:

```sql
SELECT
    region,
    date,
    amount,
    SUM(amount) OVER (
        PARTITION BY region
        ORDER BY date
    ) AS running_sum
FROM sales;
```

---

# 2️⃣ **Compute daily difference from previous day’s sales**

```sql
SELECT
    date,
    amount,
    amount - LAG(amount) OVER (ORDER BY date) AS diff_from_previous
FROM sales;
```

---

# 3️⃣ **Find 7-day rolling average of sales**

```sql
SELECT
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_avg_7
FROM sales;
```

---

# 4️⃣ **Rank products by revenue within each category using RANK()**

### Table: `products(category, product, revenue)`

```sql
SELECT
    category,
    product,
    revenue,
    RANK() OVER (
        PARTITION BY category
        ORDER BY revenue DESC
    ) AS revenue_rank
FROM products;
```

---

# 5️⃣ **Get top 5 customers per country by spending**

### Table: `orders(customer, country, amount)`

```sql
WITH ranked AS (
    SELECT
        customer,
        country,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY country
            ORDER BY amount DESC
        ) AS rn
    FROM orders
)
SELECT *
FROM ranked
WHERE rn <= 5;
```

---

# 6️⃣ **Find each order’s percentage of total monthly revenue**

### Table: `orders(order_id, month, amount)`

```sql
SELECT
    order_id,
    month,
    amount,
    amount / SUM(amount) OVER (PARTITION BY month) AS pct_of_month
FROM orders;
```

---

# 7️⃣ **Show customers whose purchase amount is above their personal average**

### Table: `transactions(customer, date, amount)`

```sql
SELECT
    customer,
    date,
    amount,
    AVG(amount) OVER (PARTITION BY customer) AS avg_customer,
    CASE WHEN amount > AVG(amount) OVER (PARTITION BY customer)
         THEN 'ABOVE AVG' ELSE 'BELOW AVG' END AS flag
FROM transactions;
```

---

# 8️⃣ **Find the longest streak of daily sales increases**

```sql
SELECT
    date,
    amount,
    CASE 
        WHEN amount > LAG(amount) OVER (ORDER BY date) THEN 1 
        ELSE 0 
    END AS increase_flag,
    SUM(
        CASE WHEN amount > LAG(amount) OVER (ORDER BY date) THEN 1 ELSE 0 END
    ) OVER (ORDER BY date) AS streak
FROM sales;
```

(This creates streaks; extended version available if you want.)

---

# 9️⃣ **Calculate cumulative average**

```sql
SELECT
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_avg
FROM sales;
```

---

# 🔟 **Calculate total sales over all time (no GROUP BY)**

```sql
SELECT
    date,
    amount,
    SUM(amount) OVER () AS total_sales
FROM sales;
```

---

# 1️⃣1️⃣ **Find highest sale so far for each employee**

### Table: `employee_sales(employee, date, amount)`

```sql
SELECT
    employee,
    date,
    amount,
    MAX(amount) OVER (
        PARTITION BY employee
        ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS max_so_far
FROM employee_sales;
```

---

# 1️⃣2️⃣ **Find employees whose sales fall below their previous 3-month average**

```sql
SELECT
    employee,
    month,
    amount,
    AVG(amount) OVER (
        PARTITION BY employee
        ORDER BY month
        ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ) AS avg_prev_3,
    CASE
        WHEN amount < AVG(amount) OVER (
            PARTITION BY employee
            ORDER BY month
            ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
        ) THEN 'BELOW BASELINE'
        ELSE 'OK'
    END AS status
FROM employee_sales;
```

---

# 1️⃣3️⃣ **Find the first purchase date for each customer**

```sql
SELECT
    customer,
    date,
    FIRST_VALUE(date) OVER (
        PARTITION BY customer
        ORDER BY date
    ) AS first_purchase_date
FROM transactions;
```

---

# 1️⃣4️⃣ **Show customer lifetime value (total cumulative spend)**

```sql
SELECT
    customer,
    date,
    amount,
    SUM(amount) OVER (
        PARTITION BY customer
        ORDER BY date
    ) AS lifetime_value
FROM transactions;
```

---

# 1️⃣5️⃣ **Calculate difference between each sale and the maximum sale in its region**

### Table: `regional_sales(region, amount)`

```sql
SELECT
    region,
    amount,
    MAX(amount) OVER (PARTITION BY region) AS region_max,
    amount - MAX(amount) OVER (PARTITION BY region) AS diff_from_max
FROM regional_sales;
```

---

# 1️⃣6️⃣ **Compute 90-day trailing revenue**

```sql
SELECT
    date,
    amount,
    SUM(amount) OVER (
        ORDER BY date
        RANGE BETWEEN INTERVAL '90 day' PRECEDING AND CURRENT ROW
    ) AS trailing_90
FROM transactions;
```

(*Note: Some SQL engines require ROWS instead of RANGE.*)

---

# 1️⃣7️⃣ **Show each product’s share of total category revenue**

```sql
SELECT
    category,
    product,
    revenue,
    revenue / SUM(revenue) OVER (PARTITION BY category) AS pct_of_category
FROM products;
```

---

# 1️⃣8️⃣ **Rank users by their second purchase date**

```sql
WITH second_purchase AS (
    SELECT
        customer,
        date,
        ROW_NUMBER() OVER (
            PARTITION BY customer
            ORDER BY date
        ) AS rn
    FROM transactions
)
SELECT *
FROM second_purchase
WHERE rn = 2
ORDER BY date;
```

---

# 1️⃣9️⃣ **Cumulative distinct product count per customer**

### Table: `purchases(customer, date, product)`

```sql
WITH first_purchases AS (
    SELECT
        customer,
        date,
        product,
        ROW_NUMBER() OVER (
            PARTITION BY customer, product
            ORDER BY date
        ) AS rn
    FROM purchases
),
new_products AS (
    SELECT
        customer,
        date,
        CASE WHEN rn = 1 THEN 1 ELSE 0 END AS new_product_flag
    FROM first_purchases
)
SELECT
    customer,
    date,
    SUM(new_product_flag) OVER (
        PARTITION BY customer
        ORDER BY date
    ) AS cumulative_distinct_products
FROM new_products;
```

---

# 2️⃣0️⃣ **Find orders that are in the top 10% of values per customer**

```sql
WITH ranked AS (
    SELECT
        customer,
        amount,
        PERCENT_RANK() OVER (
            PARTITION BY customer
            ORDER BY amount
        ) AS pct_rank
    FROM orders
)
SELECT *
FROM ranked
WHERE pct_rank >= 0.90;
```

---

# 🎉 Want more?

I can also provide:

✔ 20 more *expert-level* window function exercises
✔ A cheat sheet (1 page PDF)
✔ A full SQL interview prep kit
✔ A dataset + full practice tasks
✔ Visual diagrams for every window function

Just tell me!
Below is a complete set of **ASCII visual diagrams** for every major SQL window function.
These diagrams help you **see** what each function does inside the OVER() window.

I will cover:

1. `ROW_NUMBER()`
2. `RANK()`
3. `DENSE_RANK()`
4. `LAG()`
5. `LEAD()`
6. `SUM() OVER` (running total)
7. `AVG() OVER` (moving average)
8. `FIRST_VALUE()`
9. `LAST_VALUE()`
10. Window Frames (`ROWS BETWEEN X PRECEDING AND CURRENT ROW`)
11. Partitions vs. Global Window
12. `PERCENT_RANK()`
13. `CUME_DIST()`
14. `NTILE()`

Everything is visual and intuitive.

---

# 🎯 **Sample Dataset Used in All Diagrams**

```
+------+-------+--------+
| Emp  | Month | Amount |
+------+-------+--------+
| A    | Jan   | 100    |
| A    | Feb   | 150    |
| A    | Mar   | 120    |
| B    | Jan   |  80    |
| B    | Feb   | 110    |
| B    | Mar   | 130    |
+------+-------+--------+
```

Partitions are per employee (`PARTITION BY Emp`).

---

# 1️⃣ **ROW_NUMBER()**

Assigns a unique increasing number per partition.

### Diagram:

```
Partition: Emp A
Rows ordered by Month:
Jan  → ROW_NUMBER = 1
Feb  → ROW_NUMBER = 2
Mar  → ROW_NUMBER = 3

Partition: Emp B
Jan  → ROW_NUMBER = 1
Feb  → ROW_NUMBER = 2
Mar  → ROW_NUMBER = 3
```

### Effect:

```
+------+-------+--------+------------+
| Emp  | Month | Amount | ROW_NUMBER |
+------+-------+--------+------------+
| A    | Jan   | 100    | 1          |
| A    | Feb   | 150    | 2          |
| A    | Mar   | 120    | 3          |
| B    | Jan   | 80     | 1          |
| B    | Feb   | 110    | 2          |
| B    | Mar   | 130    | 3          |
+------+-------+--------+------------+
```

---

# 2️⃣ **RANK()**

Ties receive the same rank and **gaps appear**.

### Diagram:

If values were: 100, 150, 150, 120

```
Sorted amounts:
150 → rank 1
150 → rank 1
120 → rank 3
100 → rank 4
```

Gaps after duplicates.

---

# 3️⃣ **DENSE_RANK()**

Ties get the same rank but **no gaps**.

```
150 → 1
150 → 1
120 → 2
100 → 3
```

---

# 4️⃣ **LAG()**

Looks at the **previous row** in the window.

### Diagram (Emp A):

```
Row: Jan → LAG = NULL   (no previous row)
Row: Feb → LAG = 100
Row: Mar → LAG = 150
```

Result:

```
Jan → NULL
Feb → 100
Mar → 150
```

---

# 5️⃣ **LEAD()**

Looks at the **next row**.

### Diagram:

```
Jan → LEAD = 150
Feb → LEAD = 120
Mar → LEAD = NULL
```

---

# 6️⃣ **SUM() OVER (running total)**

Window expands as rows progress.

### Diagram:

```
Row: Jan → SUM = 100
Row: Feb → SUM = 100 + 150 = 250
Row: Mar → SUM = 250 + 120 = 370
```

Visualization:

```
Jan: [100]                        → 100
Feb: [100, 150]                  → 250
Mar: [100, 150, 120]             → 370
```

---

# 7️⃣ **AVG() OVER (moving average)**

Window moves with a frame setting, usually:

```
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
```

### Diagram (window shown as [left, current, right]):

```
Jan → [Jan, Feb]              → AVG(100,150)
Feb → [Jan, Feb, Mar]         → AVG(100,150,120)
Mar → [Feb, Mar]              → AVG(150,120)
```

---

# 8️⃣ **FIRST_VALUE()**

Always returns the **first row in the ordered window**.

### Diagram:

```
Row: Jan → FIRST = 100
Row: Feb → FIRST = 100
Row: Mar → FIRST = 100
```

---

# 9️⃣ **LAST_VALUE()**

⚠️ Must extend the window frame to the end.

```
ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
```

### Diagram:

```
Row: Jan → last = 120
Row: Feb → last = 120
Row: Mar → last = 120
```

---

# 🔟 **Understanding Window Frames**

Window frames define **which rows are included** for a given row.

### Common frames:

#### a) **UNBOUNDED PRECEDING TO CURRENT ROW**

Running sum.

```
Current = Feb
Window = [Jan, Feb]
```

#### b) **2 PRECEDING TO CURRENT ROW**

Rolling window of size 3.

```
Current = Mar
Window = [Jan, Feb, Mar]
```

#### c) **1 PRECEDING TO 1 FOLLOWING**

Moving window of 3 rows:

```
Current = Feb
Window = [Jan, Feb, Mar]
```

ASCII diagram for moving average:

```
        Jan   Feb   Mar   Apr
Window:      [Jan, Feb, Mar]
```

---

# 1️⃣1️⃣ **PARTITION vs GLOBAL WINDOWS**

### WITH PARTITION:

```
PARTITION BY Emp
```

Data splits:

```
Partition A:
Jan, Feb, Mar

Partition B:
Jan, Feb, Mar
```

### WITHOUT PARTITION:

```
OVER ()
```

Everything is one big group:

```
A-Jan
A-Feb
A-Mar
B-Jan
B-Feb
B-Mar
```

---

# 1️⃣2️⃣ **PERCENT_RANK()**

Formula:

```
(rank - 1) / (rows - 1)
```

### Diagram:

```
If 3 rows:

Ranks: 1, 2, 3

PERCENT_RANK:
Row1 → (1-1)/(3-1) = 0.0
Row2 → (2-1)/(3-1) = 0.5
Row3 → (3-1)/(3-1) = 1.0
```

---

# 1️⃣3️⃣ **CUME_DIST()**

Cumulative distribution.

Formula:

```
(rows <= current) / total_rows
```

### Diagram:

```
Sorted rows:
100
120
150

CUME_DIST:
100 → 1/3
120 → 2/3
150 → 3/3
```

---

# 1️⃣4️⃣ **NTILE(n)**

Splits partition into equal buckets.

### Example: `NTILE(3)` with 6 rows:

```
Rows: R1 R2 R3 R4 R5 R6

NTILE(3):
Bucket 1 → R1, R2
Bucket 2 → R3, R4
Bucket 3 → R5, R6
```

Visualization:

```
+----------+---------+
| Row      | NTILE   |
+----------+---------+
| R1       | 1       |
| R2       | 1       |
| R3       | 2       |
| R4       | 2       |
| R5       | 3       |
| R6       | 3       |
+----------+---------+
```

---

# 🎉 **Bonus: Full Visual Cheat Sheet (All in one place)**

```
ROW_NUMBER      → 1,2,3,4
RANK            → 1,2,2,4
DENSE_RANK      → 1,2,2,3
LAG             → previous value
LEAD            → next value
SUM OVER        → running total: [prev..current]
AVG OVER        → rolling average: sliding window
FIRST_VALUE     → first row in ordered window
LAST_VALUE      → last row (requires full frame)
NTILE           → evenly distributes rows into buckets
PERCENT_RANK    → rank position in [0,1]
CUME_DIST       → cumulative probability
PARTITION BY    → splits rows into independent windows
ROWS BETWEEN    → controls window frame size
```

---

If you want, I can also create:

✔ A **PDF cheat sheet** for download
✔ Animated step-by-step diagrams for each window function
✔ 30 more exercises with solutions
✔ A full mock SQL interview

Just tell me!
Below are **30 new advanced SQL Window Function exercises with full solutions + explanations**.
These are excellent for **data science, engineering, BI, analytics, and SQL-heavy interviews**.

I’m continuing from the previous 20, so these go deeper into **real-world complexity**.

---

# 🧠 **30 NEW ADVANCED WINDOW FUNCTION EXERCISES (WITH SOLUTIONS)**

Assume sample tables like:

* `sales(emp, date, amount)`
* `transactions(user_id, ts, amount)`
* `orders(id, customer, country, amount, order_date)`
* `products(category, product, price)`
* `events(user_id, event_time, event_type)`

---

# 1️⃣ **Find each employee's best and worst month**

```sql
SELECT
    emp,
    date,
    amount,
    FIRST_VALUE(amount) OVER (PARTITION BY emp ORDER BY amount DESC) AS best_month_value,
    FIRST_VALUE(amount) OVER (PARTITION BY emp ORDER BY amount ASC) AS worst_month_value
FROM sales;
```

---

# 2️⃣ **Detect revenue drops greater than 20% month-over-month**

```sql
SELECT
    date,
    amount,
    LAG(amount) OVER (ORDER BY date) AS prev,
    CASE WHEN amount < 0.8 * LAG(amount) OVER (ORDER BY date)
         THEN 'DROP >20%' ELSE 'OK' END AS status
FROM sales;
```

---

# 3️⃣ **Find 2nd highest sale per department**

```sql
WITH ranked AS (
    SELECT *,
           DENSE_RANK() OVER (
               PARTITION BY department ORDER BY amount DESC
           ) AS rnk
    FROM sales
)
SELECT *
FROM ranked
WHERE rnk = 2;
```

---

# 4️⃣ **Compute each user’s average transaction size over their last 5 transactions**

```sql
SELECT
    user_id,
    ts,
    amount,
    AVG(amount) OVER (
        PARTITION BY user_id
        ORDER BY ts
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS moving_avg_5
FROM transactions;
```

---

# 5️⃣ **Calculate the time difference from the previous transaction per user**

```sql
SELECT
    user_id,
    ts,
    amount,
    ts - LAG(ts) OVER (PARTITION BY user_id ORDER BY ts) AS time_since_last
FROM transactions;
```

---

# 6️⃣ **Identify users inactive for more than 30 days**

```sql
SELECT
    user_id,
    ts,
    CASE 
        WHEN ts - LAG(ts) OVER (PARTITION BY user_id ORDER BY ts) > INTERVAL '30 DAY'
        THEN 'INACTIVE 30+'
        ELSE 'ACTIVE'
    END AS status
FROM transactions;
```

---

# 7️⃣ **Find each customer’s first purchase amount and compare against current purchase**

```sql
SELECT
    customer,
    order_date,
    amount,
    FIRST_VALUE(amount) OVER (
        PARTITION BY customer ORDER BY order_date
    ) AS first_purchase,
    amount - FIRST_VALUE(amount) OVER (
        PARTITION BY customer ORDER BY order_date
    ) AS difference
FROM orders;
```

---

# 8️⃣ **Calculate median sale per employee using window function**

```sql
SELECT DISTINCT
    emp,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount)
        OVER (PARTITION BY emp) AS median_amount
FROM sales;
```

---

# 9️⃣ **Find top 10% transactions per day**

```sql
WITH ranked AS (
    SELECT *,
           PERCENT_RANK() OVER (
               PARTITION BY date ORDER BY amount
           ) AS pr
    FROM sales
)
SELECT *
FROM ranked
WHERE pr >= 0.9;
```

---

# 🔟 **Compute each sale’s rank across entire company (no partition)**

```sql
SELECT
    emp,
    date,
    amount,
    RANK() OVER (ORDER BY amount DESC) AS company_rank
FROM sales;
```

---

# 1️⃣1️⃣ **Show rolling average excluding current row**

```sql
SELECT
    emp,
    date,
    amount,
    AVG(amount) OVER (
        PARTITION BY emp
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ) AS prev_3_avg
FROM sales;
```

---

# 1️⃣2️⃣ **Find sessions where event_type changes from last event**

```sql
SELECT
    user_id,
    event_time,
    event_type,
    LAG(event_type) OVER (PARTITION BY user_id ORDER BY event_time) AS prev_event,
    CASE WHEN event_type != LAG(event_type) OVER (PARTITION BY user_id ORDER BY event_time)
         THEN 1 ELSE 0 END AS type_changed
FROM events;
```

---

# 1️⃣3️⃣ **Rank product prices within the whole catalog**

```sql
SELECT
    product,
    price,
    NTILE(4) OVER (ORDER BY price) AS price_quartile
FROM products;
```

---

# 1️⃣4️⃣ **Find daily cumulative number of new users (distinct)**

```sql
WITH first_seen AS (
    SELECT
        user_id,
        MIN(ts) AS first_seen_date
    FROM events
    GROUP BY user_id
)
SELECT
    first_seen_date,
    COUNT(*) OVER (ORDER BY first_seen_date) AS cumulative_new_users
FROM first_seen;
```

---

# 1️⃣5️⃣ **Compute the difference between this sale and the max sale in its category**

```sql
SELECT
    category,
    product,
    price,
    MAX(price) OVER (PARTITION BY category) AS cat_max,
    price - MAX(price) OVER (PARTITION BY category) AS diff_from_max
FROM products;
```

---

# 1️⃣6️⃣ **Label events that occur within 5 minutes of previous event (per user)**

```sql
SELECT
    user_id,
    event_time,
    event_type,
    CASE 
        WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time)
              <= INTERVAL '5 MINUTE'
        THEN 'WITHIN 5 MINUTES'
        ELSE 'NEW'
    END AS event_tag
FROM events;
```

---

# 1️⃣7️⃣ **Calculate year-over-year growth per product**

```sql
SELECT
    product,
    year,
    amount,
    amount - LAG(amount) OVER (PARTITION BY product ORDER BY year) AS yoy_growth
FROM product_year_sales;
```

---

# 1️⃣8️⃣ **Show cumulative minimum value**

```sql
SELECT
    emp,
    date,
    amount,
    MIN(amount) OVER (
        PARTITION BY emp ORDER BY date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_min
FROM sales;
```

---

# 1️⃣9️⃣ **Compute a weighted moving average**

```sql
SELECT
    date,
    amount,
    SUM(amount * weight) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) /
    SUM(weight) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS weighted_moving_avg
FROM weighted_sales;
```

---

# 2️⃣0️⃣ **Find each user’s 3rd transaction**

```sql
WITH numbered AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY user_id ORDER BY ts
           ) AS rn
    FROM transactions
)
SELECT *
FROM numbered
WHERE rn = 3;
```

---

# 2️⃣1️⃣ **Identify customers who increased purchase amount 3 times in a row**

```sql
WITH diffs AS (
    SELECT
        customer,
        amount,
        CASE WHEN amount > LAG(amount) OVER (PARTITION BY customer ORDER BY order_date)
             THEN 1 ELSE 0 END AS increased_flag
    FROM orders
),
streaks AS (
    SELECT *,
           SUM(increased_flag) OVER (
               PARTITION BY customer ORDER BY amount
               ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
           ) AS streak_3
    FROM diffs
)
SELECT *
FROM streaks
WHERE streak_3 = 3;
```

---

# 2️⃣2️⃣ **Calculate the difference from the median per category**

```sql
SELECT
    category,
    product,
    price,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)
        OVER (PARTITION BY category) AS median_price,
    price - PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)
        OVER (PARTITION BY category) AS diff_from_median
FROM products;
```

---

# 2️⃣3️⃣ **Find customers whose last purchase is their highest**

```sql
WITH ordered AS (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY customer ORDER BY order_date DESC) AS rn_last,
        MAX(amount) OVER (PARTITION BY customer) AS max_amt
    FROM orders
)
SELECT customer
FROM ordered
WHERE rn_last = 1
  AND amount = max_amt;
```

---

# 2️⃣4️⃣ **Find the top sale per hour (sliding)**

```sql
SELECT
    ts,
    amount,
    MAX(amount) OVER (
        ORDER BY ts
        RANGE BETWEEN INTERVAL '1 HOUR' PRECEDING 
              AND CURRENT ROW
    ) AS max_last_hour
FROM transactions;
```

---

# 2️⃣5️⃣ **Identify products whose price increased for 4 consecutive updates**

```sql
WITH diffs AS (
    SELECT
        product,
        price,
        price - LAG(price) OVER (PARTITION BY product ORDER BY update_time) AS diff
    FROM price_updates
)
SELECT *
FROM (
    SELECT *,
           SUM(CASE WHEN diff > 0 THEN 1 ELSE 0 END)
           OVER (PARTITION BY product ORDER BY update_time
                 ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS streak
    FROM diffs
) t
WHERE streak = 4;
```

---

# 2️⃣6️⃣ **Calculate total sales in the same quarter**

```sql
SELECT
    emp,
    quarter,
    amount,
    SUM(amount) OVER (
        PARTITION BY emp, quarter
    ) AS quarterly_total
FROM quarterly_sales;
```

---

# 2️⃣7️⃣ **Find employees performing above team moving average**

```sql
WITH avg_table AS (
    SELECT
        emp,
        amount,
        AVG(amount) OVER (PARTITION BY team) AS team_avg
    FROM employee_sales
)
SELECT *
FROM avg_table
WHERE amount > team_avg;
```

---

# 2️⃣8️⃣ **Cluster repeated values into groups**

```sql
SELECT
    *,
    SUM(CASE WHEN amount != LAG(amount) OVER (ORDER BY date)
             THEN 1 ELSE 0 END)
        OVER (ORDER BY date) AS change_group
FROM sales;
```

Creates a "group id" every time the amount changes.

---

# 2️⃣9️⃣ **Compute cumulative revenue per product category**

```sql
SELECT
    category,
    date,
    amount,
    SUM(amount) OVER (
        PARTITION BY category ORDER BY date
    ) AS cum_revenue
FROM category_sales;
```

---

# 3️⃣0️⃣ **Find the highest 3-day rolling sum**

```sql
SELECT
    date,
    SUM(amount) OVER (
        ORDER BY date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS sum_3d
FROM sales;
```

---

# 🎉 Want even more?

I can generate:

✔ 50 more expert-level SQL window exercises
✔ A downloadable PDF of all exercises
✔ Full datasets for practice
✔ A mock SQL interview with scoring
✔ A visualization guide for window frames

Just tell me!
Below is a **clear, detailed, and practical guide on SQL query optimization** written in English, with **real explanations, diagrams, and before/after examples**.
This is the level expected in **data engineer, backend, analyst, and data scientist interviews**.

---

# 🚀 **How to Optimize SQL Queries (Complete Guide + Examples)**

SQL query optimization means improving:

* **Speed / performance**
* **Memory usage**
* **Disk I/O**
* **CPU load**
* **Query cost**
* **Response time**

We optimize SQL by improving:
**indexes, joins, filtering, query structure, execution plans, and table design.**

Let’s dive step by step.

---

# 1️⃣ **Use Proper Indexing**

Indexes work like book indexes:
instead of scanning entire tables, the database jumps directly to needed rows.

### ❌ Slow Query (Full Table Scan)

```sql
SELECT * 
FROM customers
WHERE email = 'user@example.com';
```

### ✔️ Optimized Query (Using Index)

```sql
CREATE INDEX idx_customers_email ON customers(email);

SELECT * 
FROM customers
WHERE email = 'user@example.com';
```

### Why it’s faster:

* Without index → DB checks ALL rows (full table scan)
* With index → DB jumps directly to matching row
* Huge difference on millions of rows

### ASCII Visualization:

```
Table Scan (slow):
[Row1] → [Row2] → [Row3] → ... → [RowN]

Index Lookup (fast):
email_index → row_pointer → return results
```

---

# 2️⃣ **Only SELECT the columns you need**

### ❌ Bad

```sql
SELECT * FROM orders;
```

### ✔️ Good

```sql
SELECT order_id, customer_id, total_amount 
FROM orders;
```

### Why it’s faster:

* Reduces memory
* Reduces network bandwidth
* Improves execution plan

---

# 3️⃣ **Filter Early (WHERE before JOIN)**

Filtering small tables is fast.
Filtering huge tables *after* JOIN is expensive.

### ❌ Bad

```sql
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE c.country = 'Germany';
```

### ✔️ Good

```sql
SELECT *
FROM (
  SELECT * 
  FROM customers 
  WHERE country = 'Germany'
) c
JOIN orders o ON o.customer_id = c.id;
```

### Explanation:

* Filter customers first → fewer rows
* Joining fewer rows = faster

---

# 4️⃣ **Use the RIGHT JOIN strategy**

### ⭐ Prefer INNER JOIN over LEFT JOIN

when possible.

### ❌ Slow

```sql
SELECT *
FROM big_table t1
LEFT JOIN small_table t2
ON t1.id = t2.id;
```

### ✔️ Faster

If you don’t need rows without matches:

```sql
SELECT *
FROM big_table t1
INNER JOIN small_table t2
ON t1.id = t2.id;
```

INNER JOIN allows:

* Better optimization
* Less memory usage

---

# 5️⃣ **Avoid functions on indexed columns**

This breaks indexes.

### ❌ Slow

```sql
SELECT *
FROM users
WHERE LOWER(email) = 'user@example.com';
```

### ✔️ Fast

```sql
SELECT *
FROM users
WHERE email = 'user@example.com';
```

Or create a functional index:

```sql
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

---

# 6️⃣ **Use JOIN instead of subqueries where possible**

### ❌ Slow Correlated Subquery

```sql
SELECT
    customer_id,
    (SELECT SUM(amount) FROM orders o WHERE o.customer_id = c.id)
FROM customers c;
```

### ✔️ Fast JOIN

```sql
SELECT c.id, SUM(o.amount)
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id;
```

Why?

* Subqueries run **many times**
* JOIN runs **once**

---

# 7️⃣ **Use EXISTS instead of IN for large datasets**

### ❌ Slow

```sql
SELECT *
FROM products
WHERE id IN (SELECT product_id FROM sales);
```

### ✔️ Better

```sql
SELECT *
FROM products p
WHERE EXISTS (
    SELECT 1
    FROM sales s
    WHERE s.product_id = p.id
);
```

`EXISTS` stops scanning as soon as it finds a match → faster.

---

# 8️⃣ **Limit rows returned**

### ❌ Slow

```sql
SELECT * FROM logs ORDER BY created_at DESC;
```

### ✔️ Fast

```sql
SELECT * FROM logs 
ORDER BY created_at DESC 
LIMIT 100;
```

Why?

* Sorting millions of rows is expensive
* Returning only top results reduces everything

---

# 9️⃣ **Use proper ORDER BY indexing**

Sorting is expensive.

### ❌ Slow

```sql
SELECT * FROM orders ORDER BY created_at;
```

### ✔️ Fast

```sql
CREATE INDEX idx_orders_created_at ON orders(created_at);

SELECT * FROM orders ORDER BY created_at;
```

---

# 🔟 **Analyze Query Execution Plan**

Use:

```sql
EXPLAIN SELECT ...
```

or

```sql
EXPLAIN ANALYZE SELECT ...
```

This shows:

* Index usage
* JOIN strategy
* Table scans
* Query cost

Example plan output (simplified):

```
Seq Scan on orders  (cost=0.00..15000.00 rows=500000)
```

If you see **Seq Scan**, try:

* Adding indexes
* Filtering earlier

---

# 1️⃣1️⃣ **Avoid SELECT DISTINCT when possible**

DISTINCT forces a **sort** → expensive.

### ❌ Slow

```sql
SELECT DISTINCT customer_id FROM orders;
```

### ✔️ Faster alternative

If table already enforces uniqueness or you only need existence:

```sql
SELECT customer_id 
FROM orders
GROUP BY customer_id;
```

Or even better:

```sql
SELECT customer_id FROM customers;
```

---

# 1️⃣2️⃣ **Avoid wildcard leading (breaks index)**

### ❌ NO INDEX

```sql
WHERE name LIKE '%john'
```

### ✔️ INDEX OK

```sql
WHERE name LIKE 'john%'
```

---

# ⚡ FULL WORKED EXAMPLE: 5× SPEED IMPROVEMENT

### ❌ Original Query (Slow, 12 seconds)

```sql
SELECT *
FROM orders o
WHERE LOWER(customer_email) = 'test@gmail.com'
  AND order_date >= '2024-01-01'
ORDER BY order_date DESC;
```

### Problems:

* Function on indexed column
* `SELECT *`
* No ORDER BY index
* No filtered subquery

---

### ✔️ Optimized Query (Fast, 1.5 seconds)

1. Fix index usage
2. Select needed columns
3. Add index
4. Filter first

```sql
CREATE INDEX idx_orders_email ON orders(customer_email);
CREATE INDEX idx_orders_date ON orders(order_date DESC);

SELECT order_id, amount, order_date
FROM orders
WHERE customer_email = 'test@gmail.com'
  AND order_date >= '2024-01-01'
ORDER BY order_date DESC
LIMIT 1000;
```

### Result improvements:

* CPU ↓
* Memory ↓
* Disk I/O ↓
* Runtime ↓ from 12s → 1.5s

---

# 🎓 Summary of Optimization Techniques (Checklist)

### ✔ Use indexes smartly

### ✔ Avoid functions on indexed columns

### ✔ SELECT only needed columns

### ✔ Filter early

### ✔ Replace subqueries with JOINs

### ✔ Use EXISTS over IN

### ✔ Limit results

### ✔ Use JOIN > correlated subquery

### ✔ Avoid SELECT *

### ✔ Add ORDER BY indexes

### ✔ Analyze EXPLAIN plans

### ✔ Avoid leading wildcards

### ✔ Use proper data types

---

# 🎉 Want more?

I can give you:

🔥 20 SQL performance optimization interview questions + answers
🔥 A cheat-sheet PDF for query optimization
🔥 Slow SQL examples + optimized versions
🔥 Real-world scenario (ecommerce, finance, IoT) optimization tasks
🔥 Index design guide

Just tell me!
Below is a **comprehensive, clear, and practical tutorial** covering:

✔ Database Indexing
✔ CTEs (Common Table Expressions) & WITH queries
✔ Databases (OLTP)
✔ Data Warehouses (OLAP)
✔ Data Lakes
✔ Use cases
✔ Examples
✔ ASCII diagrams

This is written for **beginner → advanced** learners and perfect for interviews and real-world work.

---

# 📘 **1. Database Indexing — Complete Guide**

## 🔍 What is a Database Index?

A **database index** is like the index of a book—it helps the database find rows **fast** without scanning the entire table.

### Without index (slow):

```
Full Table Scan:
[Row1] -> [Row2] -> [Row3] -> ... -> [RowN]
```

### With index (fast):

```
Index (sorted like a tree)
   ↓
Pointer to exact row
```

Indexes typically use a **balanced B-tree** structure.

---

## 🎯 Why Indexes Improve Performance

Indexes improve queries using:

* `WHERE`
* `JOIN`
* `ORDER BY`
* `GROUP BY`

---

## 🧱 Types of Indexes

### 1️⃣ **B-Tree Index**

Most common. Best for:

* equality (`=`)
* range queries (`>`, `<`, `BETWEEN`)

### Example:

```sql
CREATE INDEX idx_users_email ON users(email);
```

---

### 2️⃣ **Hash Index**

Best for equality only.

---

### 3️⃣ **Composite Index**

Index on multiple columns.

```sql
CREATE INDEX idx_orders_customer_date
    ON orders(customer_id, order_date);
```

Use when queries filter on **both columns**.

---

### 4️⃣ **Unique Index**

Ensures no duplicate values.

```sql
CREATE UNIQUE INDEX idx_users_username
    ON users(username);
```

---

## ⚠️ When NOT to use indexes

* On small tables (overkill)
* On columns with low diversity (e.g., gender “M/F”)
* On columns heavily updated (indexes increase write cost)

---

## 📝 Example Query Optimization with Index

### ❌ Slow:

```sql
SELECT * FROM orders WHERE customer_id = 123;
```

### ✔️ Fast:

```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);

SELECT * FROM orders WHERE customer_id = 123;
```

---

# 📘 **2. CTE (Common Table Expression) / WITH Clause**

A **CTE** is a temporary result set used within a query.

### Syntax:

```sql
WITH cte_name AS (
    SELECT ...
)
SELECT *
FROM cte_name
WHERE ...
```

---

## 🎯 Benefits of CTEs

✔ Makes complex queries readable
✔ Allows reuse of a subquery
✔ Helps with recursive structures (hierarchies, trees)

---

## 📝 Example 1: Simple CTE

```sql
WITH german_customers AS (
    SELECT id, name
    FROM customers
    WHERE country = 'Germany'
)
SELECT *
FROM german_customers;
```

---

## 📝 Example 2: Recursive CTE (hierarchy)

Imagine an org chart:

```
CEO
 └── Manager
       └── Employee
```

### Query:

```sql
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL  -- CEO

    UNION ALL

    SELECT e.id, e.name, e.manager_id, org.level + 1
    FROM employees e
    JOIN org ON e.manager_id = org.id
)
SELECT * FROM org;
```

---

# 📘 **3. Databases (OLTP)**

A **database** is designed for **Online Transaction Processing (OLTP)**.
These systems are optimized for:

* Fast inserts
* Fast updates
* Real-time operations
* Transaction safety (ACID)

### Used by:

* Websites
* Mobile apps
* Banking systems
* E-commerce platforms

---

## 🧱 Characteristics

```
Small transactions
Immediate consistency
Normalized schema
Row-level storage
```

### Example Schema:

```
customers
orders
order_items
products
```

---

## 📝 Example Query

```sql
INSERT INTO orders (customer_id, amount)
VALUES (101, 49.99);
```

---

# 📘 **4. Data Warehouse (OLAP)**

A **Data Warehouse** is optimized for **Online Analytical Processing (OLAP)**.

Used for:

* Reporting
* BI dashboards
* Aggregated analytics
* Trend analysis

Databases: **Snowflake, Redshift, BigQuery, Synapse**

---

## ⚙️ Characteristics

```
Large read-heavy queries
Historical data
Aggregated facts
Denormalized schema (Star Schema)
Columnar storage (fast scans)
```

---

## ⭐ Star Schema Diagram

```
           customers
               |
products -- fact_sales -- dates
               |
           stores
```

---

## 📝 Example Warehouse Query

```sql
SELECT
    product_id,
    SUM(sales_amount) AS total_sales
FROM fact_sales
WHERE sales_date BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY product_id
ORDER BY total_sales DESC;
```

---

# 📘 **5. Data Lake**

A **Data Lake** is a large storage system for **raw data**.

Formats supported:

* CSV
* JSON
* Parquet
* Images
* Video
* Sensor logs
* IoT data

Examples:

* **AWS S3**
* **Azure Data Lake Storage**
* **Google Cloud Storage**

---

## 🧱 Data Lake Characteristics

```
Stores raw, unprocessed files
Schema-on-read
Huge amounts of data
Cheap storage
```

---

## ✔ Best for:

* Machine learning
* IoT sensor data
* Clickstream logs
* Unstructured data

---

## 📝 Example Workflow

```
IoT Sensor → S3 (data lake) → ETL → Redshift (data warehouse) → BI Dashboard
```

---

# 📘 **6. Differences Between Database, Data Warehouse & Data Lake**

| Feature   | Database (OLTP) | Data Warehouse (OLAP) | Data Lake       |
| --------- | --------------- | --------------------- | --------------- |
| Purpose   | Transactions    | Analytics             | Raw storage     |
| Latency   | ms              | seconds               | high            |
| Schema    | Schema-on-write | Star schema           | Schema-on-read  |
| Data Type | Structured      | Structured            | All types       |
| Users     | Apps            | Analysts              | Data scientists |
| Storage   | Expensive       | Medium                | Cheap           |

---

# 📘 **7. Real Use Cases**

---

## 🧪 Use Case 1: E-Commerce Platform

### Database

Stores:

* Customers
* Orders
* Payments

### Data Warehouse

* Daily sales reports
* Customer churn
* Product profitability

### Data Lake

* Clickstream (user browsing)
* Heatmaps
* Raw JSON logs

---

## 🧪 Use Case 2: IoT Predictive Maintenance

### Database

* Device registration
* Alerts

### Data Lake

* Raw high-frequency sensor data (Kafka → S3)

### Data Warehouse

* Aggregated hourly averages
* Model features for ML

---

## 🧪 Use Case 3: Banking

### Database

* Transfers
* Accounts
* ATM transactions

### Data Warehouse

* Fraud detection patterns
* Risk scoring
* Customer 360

### Data Lake

* Raw logs
* Historical archives

---

# 📘 **8. How They Work Together (Modern Architecture)**

```
          RAW DATA
     (Sensors, APIs, Logs)
                |
                v
        +------------------+
        |   DATA LAKE (S3) |
        +------------------+
                |
     ETL / ELT  v
        +-------------------------+
        |  DATA WAREHOUSE (OLAP)  |
        +-------------------------+
                |
                v
       Dashboards / ML Models
```

---

# 🎉 Final Summary

## **Database Indexing**

* Makes queries fast
* B-Tree, Composite, Unique
* Avoid indexing low-quality columns

## **CTEs**

* Improve readability
* Allow recursion
* Used for hierarchical data

## **Databases (OLTP)**

* Real-time operations
* Normalized
* ACID transactions

## **Data Warehouse (OLAP)**

* Analytics
* Columnar storage
* Star schema

## **Data Lake**

* Raw data storage
* Cheap and scalable
* Schema-on-read

---

If you'd like, I can also provide:

✔ 50 interview questions on: indexing, CTEs, databases, data warehouses, lakes
✔ A visual cheat sheet for all concepts
✔ A complete data-engineering roadmap
✔ ETL vs ELT explanations with diagrams

Just tell me!
Below is a **clear, detailed, and practical tutorial** covering:

✔ **OLTP (Online Transaction Processing)**
✔ **OLAP (Online Analytical Processing)**
✔ **Data Cube (a.k.a. OLAP Cube)**
✔ **Data Mesh**

This tutorial includes explanations, diagrams, differences, use cases, and examples.

---

# 📘 **1. OLTP (Online Transaction Processing)**

## 🔍 **What is OLTP?**

OLTP systems handle **real-time transactions** used by operational applications such as:

* e-commerce checkout
* banking systems
* mobile apps
* reservation systems
* POS systems

OLTP databases are designed to be:

✔ Fast for inserts/updates
✔ Highly consistent (ACID)
✔ Normalized (to reduce data duplication)
✔ Scalable for thousands or millions of small transactions

---

## 🧱 OLTP Characteristics

```
Small transactions
High concurrency
Immediate consistency
Normalized schema (3NF)
Row-level storage
High number of read/writes
```

---

## 📝 Example OLTP System

### 💳 Banking Example

```
customers
accounts
transactions
```

### Query example:

```sql
INSERT INTO transactions (account_id, amount, type)
VALUES (101, -50.00, 'withdrawal');
```

Focus: **Write speed** + **data integrity**.

---

# 📘 **2. OLAP (Online Analytical Processing)**

## 🔍 What is OLAP?

OLAP systems handle **large-scale analytical queries**, not real-time transactions.

Used for:

* BI dashboards
* reports
* trend analysis
* forecasting
* aggregated analytics

OLAP systems are optimized for:

✔ Complex queries
✔ Aggregations (SUM, AVG, COUNT)
✔ Large datasets (TBs, PBs)
✔ Columnar storage (fast scans)
✔ Historical data

---

## 🧱 OLAP Characteristics

```
Long complex queries
Read-heavy
Aggregated facts
Denormalized schema (Star or Snowflake)
Columnar storage
Batch updates
```

---

## 📝 Example OLAP Query

```sql
SELECT
    product_id,
    SUM(quantity) AS total_sold
FROM fact_sales
WHERE date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY product_id
ORDER BY total_sold DESC;
```

Focus: **Query speed over huge datasets**, not realtime updates.

---

# 📊 **3. OLTP vs OLAP — Key Differences**

| Feature | OLTP             | OLAP                       |
| ------- | ---------------- | -------------------------- |
| Purpose | Transactions     | Analytics                  |
| Users   | Apps/Customers   | Analysts/Decision-makers   |
| Queries | Small, simple    | Large, complex             |
| Schema  | Normalized (3NF) | Denormalized (Star Schema) |
| Data    | Current          | Historical                 |
| Storage | Row-based        | Column-based               |
| Example | Banking          | BI Dashboard               |

---

# 🏛 ASCII Diagram

```
                +----------------+
                |   OLTP         |
                |  (live data)   |
                +----------------+
                         |
                  ETL / ELT Jobs
                         |
                +----------------+
                |     OLAP       |
                | (historical)   |
                +----------------+
```

---

# 📘 **4. Data Cube (OLAP Cube)**

A **Data Cube** is a multi-dimensional OLAP structure used for **fast slicing, dicing, and aggregations**.

Think of it as a 3D cube of data:

```
          +-------------+
          |             |
  Time →  |   CUBE      |  ← Product
          |             |
          +-------------+
         ↑
     Region
```

It supports:

✔ Slice (filter one dimension)
✔ Dice (filter multiple dimensions)
✔ Roll-up (group higher level)
✔ Drill-down (go from year → month → day)

---

## 📝 Example: Sales Cube

Dimensions:

* Time: Year → Month → Day
* Product: Category → Product
* Geography: Country → Region

Measure:

* sales_amount
* quantity

### Query example (MOLAP/DOLAP concept):

"Total sales for Electronics in Germany by month"

```
Cube[Product='Electronics', Country='Germany', Time='Month']
```

In SQL (simulated):

```sql
SELECT
    month,
    SUM(sales_amount)
FROM fact_sales
JOIN dim_product USING (product_id)
JOIN dim_region USING (region_id)
WHERE category = 'Electronics'
  AND country = 'Germany'
GROUP BY month;
```

---

# 📘 **5. Data Mesh (Modern Architecture)**

## 🔍 What is Data Mesh?

**Data Mesh** is a modern decentralized data architecture.

Instead of:

❌ One big central data team
❌ One monolithic data warehouse/lake

We have:

✔ Domain-oriented data ownership
✔ Each team manages their own “data product”
✔ Self-service platforms
✔ Federated governance

---

## 🧱 Data Mesh Principles

1️⃣ **Domain Ownership**
Teams (Finance, Sales, Marketing) own their data.

2️⃣ **Data as a Product**
Each domain provides production-grade data (quality, SLAs).

3️⃣ **Self-Service Platform**
Central tools (auth, metadata, pipelines) are shared.

4️⃣ **Federated Governance**
Each team follows shared standards (security, metadata, formats).

---

## ASCII Diagram: Data Mesh

```
          +------------+       +------------+
          | Finance    |       | Marketing  |
          | Data       |       | Data       |
          +------------+       +------------+
                \               /
                 \             /
             +---------------------+
             |   Self-Service      |
             |   Data Platform     |
             +---------------------+
                 /             \
                /               \
         +------------+      +------------+
         | Sales Data |      | Ops Data   |
         +------------+      +------------+
```

---

## 🧪 Use Cases for Data Mesh

### 🔥 Best for:

* Large organizations
* Multi-domain enterprises
* High-speed analytics needs
* Decentralized teams
* Multiple independent business units

### Example:

In a company:

* Finance team owns **billing data**
* Marketing team owns **ad campaign data**
* Sales team owns **CRM data**
* Each publishes a high-quality data product
* Analysts combine them across domains

---

# 📘 **6. How OLTP, OLAP, Data Cube, and Data Mesh fit together**

```
                     +----------------+
User Actions  --->   |     OLTP       |
                     |  (operational) |
                     +----------------+
                            |
                            | ETL / ELT
                            v
                     +----------------+
                     |    OLAP        |
                     | (warehouse)    |
                     +----------------+
                            |
                   Cube / Materialized Views
                            |
                            v
                     +----------------+
                     | BI Dashboards  |
                     +----------------+
                            |
                       Data Mesh Layer
                            |
   +--------------+   +------------+   +-------------+
   | Finance Data |   | Sales Data |   | Ops Data    |
   +--------------+   +------------+   +-------------+
```

---

# 🎉 FINAL SUMMARY

## **OLTP**

* Transactional
* Real-time
* Normalized
* Used by apps

## **OLAP**

* Analytical
* Long-running complex queries
* Denormalized
* Used by analysts

## **Data Cube**

* Multi-dimensional
* Supports slicing/dicing
* Very fast aggregations

## **Data Mesh**

* Decentralized data ownership
* Each team produces “data products”
* Strong governance + autonomy

---

# 🔧 Want next?

I can create:

✔ Hands-on SQL examples for OLTP vs OLAP
✔ Example star schemas + fact tables
✔ A Data Mesh implementation plan
✔ 50 interview questions on all topics
✔ Visual cheat sheets (PDF-ready)

Just tell me!
Below is a **clear, detailed, beginner-friendly → advanced tutorial** explaining:

✔ **Star Schema**
✔ **Snowflake Schema**
✔ Differences
✔ Advantages / disadvantages
✔ Use cases
✔ Real examples
✔ ASCII diagrams (visual!)

Perfect for interviews (Data Engineer, Analyst, BI, Data Scientist), and for real-world understanding of data warehousing.

---

# 🌟 **1. What is a Star Schema?**

A **Star Schema** is a type of data warehouse schema designed specifically for **fast analytical queries**.

It consists of:

### ✔ 1 Fact Table

* Stores **measurable numeric data**
* Example: sales amount, quantity, revenue

### ✔ Multiple Dimension Tables

* Store **descriptions** of business entities
* Example: customer, product, date

---

## ⭐ **Star Schema Diagram (ASCII)**

```
                 +-------------------+
                 |   dim_customer    |
                 +---------+---------+
                           |
+-------------+   +--------+--------+    +--------------+
| dim_product |---|   fact_sales   |----|  dim_date     |
+-------------+   +--------+--------+    +--------------+
                           |
                 +---------+---------+
                 |   dim_store      |
                 +------------------+
```

It looks like a **star**, with the fact table in the center and dimensions around it.

---

# 📦 **2. Components of a Star Schema**

### 1️⃣ **Fact Table**

Contains:

| Column      | Type   | Meaning                     |
| ----------- | ------ | --------------------------- |
| product_id  | FK     | Links to product dimension  |
| customer_id | FK     | Links to customer dimension |
| date_id     | FK     | Links to date dimension     |
| revenue     | metric | Main measure                |
| quantity    | metric | Quantity sold               |

Example:

```
fact_sales:
product_id | customer_id | date_id | store_id | revenue | quantity
```

---

### 2️⃣ **Dimension Tables**

Contain descriptive attributes.

#### Example: Product dimension

```
dim_product:
product_id | product_name | category | brand | color | size
```

#### Example: Customer dimension

```
dim_customer:
customer_id | name | gender | age_group | country | city
```

#### Example: Date dimension

```
dim_date:
date_id | date | month | year | quarter | week_number
```

---

# 📊 **3. Example of a Full Star Schema**

### `fact_sales` table (center):

```
product_id | customer_id | date_id | store_id | revenue | units
---------------------------------------------------------------
1001       | 501         | 20230101| 10       | 30.50   | 1
1002       | 502         | 20230101| 12       | 90.00   | 3
```

### `dim_product` table:

```
product_id | name         | category | brand
----------------------------------------------
1001       | T-Shirt      | Apparel  | Nike
1002       | Running Shoe | Footwear | Adidas
```

### `dim_customer`:

```
customer_id | name       | country | gender
---------------------------------------------
501         | John Doe   | Germany | M
502         | Anna Smith | France  | F
```

---

# 💡 **Use Cases of Star Schema**

* Business Intelligence (BI)
* Reporting systems
* Dashboards (Power BI, Tableau)
* Ad-hoc analytics
* Summaries, aggregates, trends
* Data warehouses (Snowflake, BigQuery, Redshift, Synapse)

---

# 🧊 **4. What is a Snowflake Schema?**

A **Snowflake Schema** is an extension of the star schema where **dimension tables are normalized** into multiple related tables.

This reduces data redundancy but adds complexity.

---

## ❄️ **Snowflake Schema Diagram (ASCII)**

```
                         +---------------------+
                         |    dim_country      |
                         +----------+----------+
                                    |
+-------------+            +--------+---------+           +--------------+
| dim_product |------------|    dim_customer  |-----------|  dim_gender  |
+-------------+            +--------+---------+           +--------------+
                                    |
                          +---------+---------+
                          |    fact_sales     |
                          +-------------------+
```

Notice:

* `dim_customer` is split into `dim_country`, `dim_gender`, etc.
* This looks like a **snowflake pattern**—more branches.

---

# 📘 **5. Differences Between Star Schema vs Snowflake Schema**

| Feature           | Star Schema   | Snowflake Schema                            |
| ----------------- | ------------- | ------------------------------------------- |
| Normalization     | Denormalized  | Normalized                                  |
| Query Performance | Faster        | Slower                                      |
| Storage           | More space    | Less space                                  |
| Number of Joins   | Fewer joins   | Many joins                                  |
| Complexity        | Simple        | More complex                                |
| Use Case          | BI dashboards | Large enterprises needing clean master data |

---

# ✔ Example: Difference Illustrated

### **Star Schema — denormalized dim_customer**

```
dim_customer:
customer_id | name | country | country_region | gender | segment
```

### **Snowflake Schema — normalized dim_customer**

```
dim_customer:
customer_id | name | country_id | gender_id | segment_id

dim_country:
country_id  | country_name | region

dim_gender:
gender_id   | gender
```

---

# ⚙️ Example Query Difference

### ⭐ Star Schema Query

```sql
SELECT 
    c.country,
    SUM(f.revenue)
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
GROUP BY c.country;
```

Only **1 join** needed.

---

### ❄️ Snowflake Schema Query

```sql
SELECT 
    co.country_name,
    SUM(f.revenue)
FROM fact_sales f
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_country co ON c.country_id = co.country_id
GROUP BY co.country_name;
```

Requires **multiple joins**.

---

# 🧠 **6. When to Use Star vs Snowflake**

## ⭐ Use Star Schema When:

* You need **fast query performance**
* BI dashboards (Looker, Power BI, Tableau)
* Simpler data model preferred
* Read-heavy workloads
* Denormalization is acceptable

## ❄️ Use Snowflake Schema When:

* You need a **clean, normalized** structure
* You want to reduce data redundancy
* Many dimensions share lookup tables
* Very large enterprise with master data management (MDM)
* Storage cost matters

---

# 🧪 Real Business Use Cases

### 🎉 Retail Company

* **Star**: For fast sales dashboards
* **Snowflake**: For master data (product hierarchy, location hierarchy)

### 🏥 Healthcare

* **Star**: Patient visits fact + dimensions
* **Snowflake**: Detailed provider → department → hospital structures

### 📦 Logistics

* **Star**: Shipment metrics
* **Snowflake**: Detailed geographic hierarchies (country → region → city)

---

# 🎓 Final Summary

## ⭐ Star Schema

* Simpler
* Denormalized
* Fast
* Great for BI

## ❄️ Snowflake Schema

* Complex
* Normalized
* More joins
* Good for large enterprises

---

# 🎉 Want more?

I can also create:

✔ A tutorial on **fact tables vs dimension tables**
✔ A full **end-to-end star schema design** for e-commerce
✔ 30 interview questions about star & snowflake
✔ A cheat sheet PDF for all warehousing concepts
✔ A tutorial on **data vault modeling**

Just tell me!
Below is a **clear, complete, and practical tutorial** on **Data Normalization** in English — with explanations, rules, examples, diagrams, and use cases.
This will help you in **data engineering, databases, interviews, and real projects**.

---

# 📘 **Data Normalization – Complete Tutorial (Beginner → Advanced)**

---

# 🌟 **1. What is Data Normalization?**

**Data normalization** is the process of organizing data in a relational database to:

✔ Reduce redundancy (duplicate data)
✔ Improve data integrity
✔ Make updates/inserts faster and cleaner
✔ Avoid anomalies (insertion, deletion, update anomalies)

Normalization transforms messy tables into **structured, well-organized tables**.

---

# 🧠 **Why Normalize Data?**

Because unstructured or redundant data causes:

❌ Update anomalies
❌ Inconsistent data
❌ Wasted storage
❌ Slow queries
❌ Poor integrity

Normalization fixes these problems by splitting tables into smaller, meaningful structures.

---

# 🧱 **2. Normalization Forms (NF)**

There are several levels of normalization:

1. **1NF – First Normal Form**
2. **2NF – Second Normal Form**
3. **3NF – Third Normal Form**
4. **BCNF – Boyce-Codd Normal Form** *(advanced)*

Most companies normalize data up to **3NF**.

---

# 📌 **Before Normalization (Bad Table Example)**

Consider this table:

```
+-----------+------------+---------------------------+----------------+
| order_id  | customer   | products                  | address        |
+-----------+------------+---------------------------+----------------+
| 1001      | John Smith | Shoes, T-Shirt            | Berlin, DE     |
| 1002      | John Smith | Jacket                    | Berlin, DE     |
| 1003      | Anna Brown | Shoes, Hat, T-Shirt       | Paris, FR      |
+-----------+------------+---------------------------+----------------+
```

Problems:

* Products stored as comma-separated list → ❌ not atomic
* Customer information duplicated
* Address repeated
* Hard to update/change customer data

Normalization fixes all that.

---

# 🥇 **3. 1NF – First Normal Form**

**Rules:**

1. Each column has atomic (indivisible) values
2. No repeating groups
3. Rows must be unique

### ❌ Bad (not atomic):

```
Products: "Shoes, T-Shirt"
```

### ✔ Good (atomic):

```
Products: 1 row per product
```

### 1NF Solution:

Split products into separate rows:

```
+-----------+------------+----------+
| order_id  | customer   | product  |
+-----------+------------+----------+
| 1001      | John       | Shoes    |
| 1001      | John       | T-Shirt  |
| 1002      | John       | Jacket   |
| 1003      | Anna       | Shoes    |
...
```

---

# 🥈 **4. 2NF – Second Normal Form**

**Rule:**
A table is in 2NF if it is in 1NF AND
**every non-key column depends on the whole primary key** (no partial dependency).

This applies when a table has a **composite key** (two columns as primary key).

### Example Problem:

```
(order_id, product) → customer_name
```

But **customer_name** does not depend on *product*.
It only depends on *order_id*.
This violates 2NF.

### 2NF Fix:

Split customer data into its own table:

**orders table**

```
order_id | customer_id | order_date
```

**order_items table**

```
order_id | product_id | quantity
```

**customers table**

```
customer_id | name | address
```

---

# 🥉 **5. 3NF – Third Normal Form**

**Rule:**
A table is in 3NF if it is in 2NF AND
**no non-key attribute depends on another non-key attribute**
(avoid transitive dependency).

### Example Problem:

```
customers table:
customer_id | name | city | country | country_code
```

Here:

```
country_code depends on country → transitive dependency
```

### 3NF Fix:

Split country information into a separate table.

**customers**

```
customer_id | name | city | country_id
```

**countries**

```
country_id | country_name | country_code
```

---

# 🧠 **6. BCNF – Boyce-Codd Normal Form** *(advanced)*

BCNF is stricter than 3NF.

Rule:
**For every functional dependency A → B, A must be a superkey.**

Used when:

* Multiple candidate keys exist
* Complex constraints

Most databases stop at **3NF**, unless advanced correctness is needed.

---

# 📊 **7. Full Normalization Example**

### Raw Table:

```
order_id | customer | address        | product     | price
------------------------------------------------------------
1001     | John     | Berlin, DE     | Shoes       | 50
1001     | John     | Berlin, DE     | T-Shirt     | 20
1002     | Anna     | Paris, FR      | Coat        | 100
```

---

### Final Normalized Schema:

**customers**

```
customer_id | name | address
1           | John | Berlin, DE
2           | Anna | Paris, FR
```

**orders**

```
order_id | customer_id | order_date
1001     | 1           | 2024-02-01
1002     | 2           | 2024-02-03
```

**products**

```
product_id | name     | price
1          | Shoes    | 50
2          | T-Shirt  | 20
3          | Coat     | 100
```

**order_items**

```
order_id | product_id | quantity
1001     | 1          | 1
1001     | 2          | 1
1002     | 3          | 1
```

---

# 🌟 **8. Benefits of Normalization**

### ✔ No duplicate data

### ✔ Easier updates

### ✔ Less storage

### ✔ Prevents anomalies

### ✔ Clear, logical structure

### ✔ Consistent data integrity

### ✔ Faster writes

---

# ⚠️ **9. When NOT to Normalize Too Much**

Highly normalized structures may cause:

* Too many joins
* Slower analytical queries

That’s why **data warehouses use denormalization** (star schemas).

Use:

### Normalization → for OLTP

### Denormalization → for OLAP

---

# 🧪 **10. Real-Life Use Cases**

### ✔ Banking systems

Need strong normalization to avoid incorrect balances.

### ✔ E-commerce

Customer data normalized; product catalog normalized.

### ✔ Healthcare

Patient records must not be duplicated → normalization ensures safety.

### ✔ Applications with heavy writes

Normalization speeds up inserts and updates.

---

# 🎉 **Final Summary**

Normalization is the process of structuring your relational database to:

* Reduce redundancy
* Improve data consistency
* Organize data logically
* Prevent anomalies

**1NF**: Atomic values
**2NF**: No partial dependency
**3NF**: No transitive dependency
**BCNF**: Every determinant must be a key

Used heavily in **OLTP databases**.

---

If you'd like, I can also provide:

✔ SQL examples to normalize a raw dataset step-by-step
✔ 20 interview questions about normalization
✔ Real-world normalization case studies
✔ Cheat sheet PDF for database design

Just tell me!
Below is a **clear, complete, and industry-grade tutorial** covering:

---

# ✅ **1. Fact Tables vs Dimension Tables — Full Tutorial (with diagrams & examples)**

# ✅ **2. Data Vault Modeling — Full Tutorial (with diagrams, rules, examples)**

These explanations match the depth required for **data engineering, BI, data warehousing, analytics, and architecture interviews**.

---

# 🧱 **PART 1 — FACT TABLES vs DIMENSION TABLES (TUTORIAL)**

Data warehouses (OLAP systems) typically use **star schema** or **snowflake schema**.
Both require understanding two key table types:

👉 **Fact Tables**
👉 **Dimension Tables**

---

# ⭐ **What Are Fact Tables?**

A **fact table** stores *measurable business metrics* (facts) and *foreign keys* referencing dimensions.

### Facts are:

* Numeric
* Additive (usually)
* Quantitative

Examples:

* Revenue
* Quantity sold
* Clicks
* Sessions
* Page views
* Temperature reading

---

## 📘 Fact Table Characteristics

| Property              | Description                                   |
| --------------------- | --------------------------------------------- |
| Contains metrics      | e.g., revenue, profit, units sold             |
| Granularity           | level of detail (e.g., 1 row per transaction) |
| Foreign Keys          | references to dimension tables                |
| VERY large            | can have billions of rows                     |
| Supports aggregations | SUM, AVG, COUNT                               |

---

## ⭐ **Fact Table Example: fact_sales**

```
+------------+-------------+----------+--------+----------+
| date_id    | product_id  | store_id | units  | revenue  |
+------------+-------------+----------+--------+----------+
| 20230101   | 1001        | 10       | 3      | 90.00    |
| 20230101   | 1002        | 12       | 1      | 50.00    |
| 20230102   | 1003        | 11       | 2      | 40.00    |
+------------+-------------+----------+--------+----------+
```

* **Metrics:** units, revenue
* **Foreign keys:** date_id, product_id, store_id

---

# ⭐ **What Are Dimension Tables?**

A **dimension table** stores descriptive attributes that give context to facts.

Examples:

* Product details
* Customer information
* City, region, country
* Time attributes
* Salesperson information

---

## 📘 Dimension Table Characteristics

| Property                         | Description               |
| -------------------------------- | ------------------------- |
| Contains text attributes         | name, category, country   |
| Slowly Changing Dimensions (SCD) | handles changes over time |
| Used for slicing and dicing      | GROUP BY                  |
| Much smaller than fact tables    |                           |

---

## ⭐ Example: dim_product

```
+------------+--------------+-----------+--------+
| product_id | product_name | category  | brand  |
+------------+--------------+-----------+--------+
| 1001       | T-Shirt      | Apparel   | Nike   |
| 1002       | Shoe         | Footwear  | Adidas |
```

---

## ⭐ Example: dim_date

```
+---------+------------+--------+-------+--------+
| date_id | date       | month  | year  | quarter|
+---------+------------+--------+-------+--------+
|20230101 |2023-01-01  | January| 2023  | Q1     |
```

---

# ⭐ ASCII Diagram — Fact vs Dimensions

```
               +-------------------+
               |   dim_customer    |
               +---------+---------+
                         |
+-------------+  +-------+--------+   +--------------+
| dim_product |--|   FACT_SALES   |---|  dim_date    |
+-------------+  +-------+--------+   +--------------+
                         |
                   +-----+------+
                   |  dim_store |
                   +------------+
```

---

# ⭐ **Key Differences Table**

| Feature   | Fact Table                    | Dimension Table            |
| --------- | ----------------------------- | -------------------------- |
| Content   | Metrics                       | Attributes                 |
| Size      | VERY large                    | Small                      |
| Keys      | Foreign keys                  | Primary key                |
| Usage     | Aggregation                   | Filtering, grouping        |
| Structure | Numeric-heavy                 | Text-heavy                 |
| History   | Snapshot or transaction level | Slowly Changing Dimensions |

---

# 🎉 Summary for Facts vs Dimensions

✔ Fact tables = **numbers**
✔ Dimension tables = **textual descriptions**
✔ Fact tables use FK → dimension PK
✔ Dimensions help slice, dice, group, and filter data

---

# 🧱 **PART 2 — DATA VAULT MODELING (FULL TUTORIAL)**

Data Vault Modeling is a **modern data warehousing approach** designed for:

✔ Scalability
✔ Auditability
✔ Historical tracking
✔ Flexibility
✔ Decentralized data ingestion

Invented by Dan Linstedt, used widely in large enterprises.

---

# 🧊 **What Is Data Vault Modeling?**

Data Vault is a modeling technique with **3 core components**:

1. **Hubs**
2. **Links**
3. **Satellites**

Each plays a unique role in storing raw enterprise data.

---

# 🧱 1. HUBS

A **Hub** stores:

* Business keys (unique identifiers)
* Surrogate key
* Metadata (load date, source system)

### Example: HUB_CUSTOMER

```
+------------------+------------------+--------------+
| customer_key     | customer_id_bk   | load_date    |
+------------------+------------------+--------------+
| 1001             | CUST_4455        | 2024-01-01   |
```

* **customer_id_bk** = business key (from source system)
* **customer_key** = surrogate hash key (created by warehouse)
* No descriptive attributes → go into satellites

---

# 🔗 2. LINKS

Links store **relationships between hubs** (many-to-many allowed).

### Example Link: LINK_ORDER_CUSTOMER

```
+----------------+-----------------+----------------+
| order_key      | customer_key     | load_date     |
+----------------+-----------------+----------------+
```

A customer can have many orders → central linking table.

---

# 🛰️ 3. SATELLITES

Satellites store:

* Descriptive attributes (name, address, brand, etc.)
* Historical versions (SCD Type 2)
* Hash differences to detect changes

### Example Satellite: SAT_CUSTOMER_DETAILS

```
+----------------+------------+------------+----------------+
| customer_key   | name       | address    | effective_from |
+----------------+------------+------------+----------------+
| 1001           | John Doe   | Berlin     | 2024-01-01     |
| 1001           | John Doe   | Hamburg    | 2024-05-01     |
```

Every change creates a **new row** (historical tracking).

---

# ❄️ ASCII Diagram — Data Vault Model

```
              +------------------+
              |     HUB_USER     |
              +--------+---------+
                       |
                       |
               +-------+-------+
               |    LINK       |
               | USER_PRODUCT  |
               +-------+-------+
                       |
              +--------+---------+
              |    HUB_PRODUCT   |
              +--------+---------+

   +-------------------+   +----------------------+
   | SAT_USER_DETAILS  |   | SAT_PRODUCT_DETAILS  |
   +-------------------+   +----------------------+
```

---

# 🔥 **Why Data Vault?**

Because it solves problems with traditional warehouses:

| Issue                   | Traditional DWH | Data Vault                |
| ----------------------- | --------------- | ------------------------- |
| Changing business rules | Breaks model    | Easy to add new hubs/sats |
| Source system changes   | Hard            | Simple (new satellite)    |
| Auditing                | Weak            | Strong audit fields       |
| Scalability             | Moderate        | Excellent                 |
| Loading                 | Batch           | Parallel loads            |

---

# 🎯 **Data Vault Use Cases**

### 🚀 Ideal for:

* Large enterprises
* Multiple source systems
* Constantly changing business rules
* Highly scalable data lakes
* Regulatory environments (banks, insurance)

### 💼 Examples:

* Tracking customer changes over time
* Merging multiple CRM systems
* Storing IoT sensor data + metadata
* Layer between raw zone → business vault → data marts

---

# ⚙️ **Data Vault Layers**

1. **Raw Vault**

   * Raw ingestion
   * Exact copy of source keys

2. **Business Vault**

   * Business logic
   * Derived satellites
   * KPIs, rules, conforming dimensions

3. **Information Marts**

   * Final BI-ready tables (typically **star schemas**)

### Diagram:

```
Source Systems → Raw Vault → Business Vault → Data Marts (Star Schema) → BI Tools
```

---

# 🧠 **Example — Building a Customer Data Vault**

### Step 1: Hubs

```
HUB_CUSTOMER
HUB_ORDER
```

### Step 2: Link

```
LINK_ORDER_CUSTOMER
```

### Step 3: Satellites

```
SAT_CUSTOMER_DETAILS
SAT_ORDER_DETAILS
```

### Step 4: Business Vault

* Derived facts (e.g., total sales)
* Cleansed dimensions

### Step 5: BI Star Schema

* fact_sales
* dim_customer
* dim_product

This layered architecture is extremely flexible and scalable.

---

# 🎉 FINAL SUMMARY

## ⭐ **Fact Tables**

* Store numeric metrics
* Huge tables
* Used for aggregations

## ⭐ **Dimension Tables**

* Store descriptive info
* Smaller tables
* Used for filtering and grouping

## 🧱 **Data Vault**

* Hubs = business keys
* Links = relationships
* Satellites = historical attributes
* Highly scalable, auditable, flexible

## 🧱 Data Vault Architecture

```
Raw Vault → Business Vault → Star Schema → BI Reports
```

---

# 🚀 Want More?

I can also create:

✔ A full **Data Vault → Star Schema** transformation example
✔ 30 Data Vault interview questions
✔ SQL examples for building hubs, links, and satellites
✔ An end-to-end retail data warehouse design
✔ A PDF cheat sheet for Fact/Dimension + Data Vault

Just tell me!
Below is a **complete, clear, industry-grade data modeling solution** for the 4 use cases you mentioned:

✔ **Banking Systems**
✔ **E-commerce**
✔ **Healthcare**
✔ **High-Write Applications**

Each section includes:

* Business requirements
* OLTP-optimized **normalized data model**
* Entity descriptions
* ASCII ERD diagrams
* Notes on constraints & best practices
* Optional OLAP extension where relevant

This is the level of detail expected from **data architects, data engineers, and senior data modelers.**

---

# 🏦 **1. BANKING SYSTEM – STRONGLY NORMALIZED MODEL (3NF)**

## 📌 Why normalization is critical in banking:

* Prevent double-spending
* Ensure accurate balances
* Track every transaction immutably
* Prevent duplicate accounts
* Legal audit requirements
* High consistency (ACID)

---

## 🧱 **Banking OLTP Entities**

### 1. **Customer**

Stores personal information.

```
customer_id (PK)
first_name
last_name
date_of_birth
national_id
address_id (FK)
created_at
```

---

### 2. **Address**

Separate table to avoid duplication.

```
address_id (PK)
street
city
postal_code
country
```

---

### 3. **Account**

Every customer can have multiple accounts.

```
account_id (PK)
customer_id (FK)
account_type (Savings/Checking)
currency
opened_date
status (Active/Closed/Frozen)
```

---

### 4. **Transaction**

Immutable; never update balances directly.

```
transaction_id (PK)
account_id (FK)
transaction_type (Deposit/Withdrawal/Transfer)
amount
timestamp
related_account_id (FK)   -- for transfers
balance_after_transaction
```

---

### 5. **Card (optional)**

```
card_id (PK)
account_id (FK)
card_number (unique)
expiration_date
status
```

---

## 🧩 ASCII ERD — Banking Model

```
CUSTOMER --< ACCOUNT --< TRANSACTION
    |                     |
    +-- ADDRESS           +-- related_account (transfer)
```

```
+-----------+      +-----------+       +---------------+
| CUSTOMER  |      | ACCOUNT   |       | TRANSACTION   |
+-----------+      +-----------+       +---------------+
|customer_id|1   * |account_id |1   *  |transaction_id |
+-----------+------|customer_id|--------|account_id     |
                   |type       |        |amount         |
                   +-----------+        +---------------+
```

---

# 🛒 **2. E-COMMERCE DATA MODEL (Normalized OLTP Core)**

## 📌 Why normalization is important:

* Accurate orders & inventory
* Fast order creation
* Avoid duplicated product data
* Maintain clean customer records

---

## 🧱 **E-Commerce Entities**

### 1. Product

```
product_id (PK)
name
brand_id (FK)
category_id (FK)
price
description
created_at
```

---

### 2. Category

```
category_id (PK)
category_name
parent_category_id (FK nullable)
```

---

### 3. Brand

```
brand_id (PK)
brand_name
country_of_origin
```

---

### 4. Customer

```
customer_id (PK)
first_name
last_name
email (unique)
address_id (FK)
created_at
```

---

### 5. Order

```
order_id (PK)
customer_id (FK)
order_date
status
total_amount
```

---

### 6. Order Item

```
order_item_id (PK)
order_id (FK)
product_id (FK)
quantity
unit_price
```

---

### 7. Inventory

```
product_id (PK)
stock_quantity
warehouse_location
```

---

## 🧩 ASCII ERD — E-Commerce

```
 CUSTOMER --< ORDER --< ORDER_ITEM >-- PRODUCT --< INVENTORY
                                         |
                                         +-- CATEGORY
                                         |
                                         +-- BRAND
```

---

# 🏥 **3. HEALTHCARE DATA MODEL (Highly Normalized & Secure)**

## 📌 Why normalization is essential:

* Patient safety
* Avoid duplicated patient records
* Accurate medical history
* Compliance (HIPAA, GDPR)
* Avoid conflicting clinical data

---

## 🧱 **Healthcare Entities**

### 1. Patient

```
patient_id (PK)
first_name
last_name
date_of_birth
gender
national_id
address_id (FK)
```

---

### 2. Address

```
address_id
street
city
postal_code
country
```

---

### 3. Encounter / Visit

```
encounter_id (PK)
patient_id (FK)
visit_date
visit_type (Inpatient/Outpatient/ER)
doctor_id (FK)
department_id (FK)
```

---

### 4. Doctor

```
doctor_id
name
specialization_id (FK)
```

---

### 5. Specialization

```
specialization_id
specialization_name
```

---

### 6. Diagnosis

```
diagnosis_id (PK)
encounter_id (FK)
icd_code
description
```

---

### 7. Medication

```
med_id (PK)
name
dosage_form
strength
```

---

### 8. Prescription

```
prescription_id (PK)
encounter_id (FK)
med_id (FK)
dosage
frequency
duration
```

---

## 🧩 ASCII ERD — Healthcare

```
PATIENT --< ENCOUNTER --< DIAGNOSIS
              |
              +-- PRESCRIPTION >-- MEDICATION
              |
              +-- DOCTOR --< SPECIALIZATION
```

---

# ⚡ **4. HIGH-WRITE SYSTEM MODEL (Log / Event System)**

*(example: clickstream, IoT telemetry, logs)*

## 📌 Why normalization?

* Avoid duplication of static metadata
* Reduce write amplification
* Improve write throughput
* Streamlined ingestion

---

## 🧱 **High-Write Data Model**

### 1. Device / User

```
device_id (PK)
device_type
user_agent
os_version
```

---

### 2. Event Type

```
event_type_id (PK)
event_name
category
```

---

### 3. Event Log (HIGH VOLUME)

```
event_id (PK)
device_id (FK)
event_type_id (FK)
timestamp
metadata_json (semi-structured)
```

*Why JSON?*
Some fields vary—metadata should not break normalization.

---

### 4. Session (Optional)

```
session_id
device_id (FK)
start_time
end_time
```

---

## 🧩 ASCII ERD — High Write System

```
DEVICE --< SESSION --< EVENT_LOG >-- EVENT_TYPE
```

Logs stay clean & normalized.

---

# 🔥 BONUS — OLAP Extensions (for Analytics)

After OLTP → you will denormalize for analytics.

### Fact tables:

* fact_transactions
* fact_orders
* fact_patient_visits
* fact_events

### Dimensions:

* dim_patient
* dim_product
* dim_device
* dim_date

---

# 🎉 FINAL SUMMARY

Below is what we achieved:

| Use Case        | Requirements                      | Modeling Results                          |
| --------------- | --------------------------------- | ----------------------------------------- |
| Banking         | accuracy, ACID, anti-fraud        | 3NF: customers, accounts, transactions    |
| E-commerce      | fast orders, no dupes             | product, brand, category, order items     |
| Healthcare      | safety, compliance                | patient, encounter, diagnosis, medication |
| High-write apps | fast writes, metadata flexibility | normalized events, devices, event types   |

---

# 🚀 Would you like the next step?

I can also produce:

✔ ER diagrams in PNG/SVG
✔ SQL CREATE TABLE scripts for each model
✔ Data Vault versions of all 4 use cases
✔ Star Schema versions for analytics
✔ Data Engineering architecture for each
✔ 50 interview questions on data modeling

Just tell me!
