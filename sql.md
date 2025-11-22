
# **SQL**

SQL (Structured Query Language) is the standard language for **managing and querying relational databases**.

---

## **1. Introduction to SQL**

* SQL is used to **create, read, update, and delete data** in databases.
* Most relational database systems support SQL (MySQL, PostgreSQL, SQLite, SQL Server, Oracle).

### **Basic SQL Command Categories**

| Category | Description                                                         |
| -------- | ------------------------------------------------------------------- |
| DDL      | Data Definition Language (`CREATE`, `ALTER`, `DROP`)                |
| DML      | Data Manipulation Language (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) |
| DCL      | Data Control Language (`GRANT`, `REVOKE`)                           |
| TCL      | Transaction Control Language (`COMMIT`, `ROLLBACK`)                 |

---

## **2. Creating a Database and Tables**

### **Create Database**

```sql
CREATE DATABASE ecommerce;
```

### **Use Database**

```sql
USE ecommerce;
```

### **Create Table**

```sql
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(50),
    Email VARCHAR(100),
    Country VARCHAR(50)
);

CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    Name VARCHAR(50),
    Category VARCHAR(50),
    Price DECIMAL(10,2)
);

CREATE TABLE Orders (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    OrderDate DATE,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

CREATE TABLE OrderItems (
    OrderItemID INT PRIMARY KEY,
    OrderID INT,
    ProductID INT,
    Quantity INT,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);
```

**Explanation:**

* `VARCHAR(n)` is a string with max length `n`.
* `DECIMAL(10,2)` stores numbers with 2 decimal places.
* `PRIMARY KEY` ensures uniqueness.
* `FOREIGN KEY` creates relationships between tables.

---

## **3. Inserting Data**

```sql
INSERT INTO Customers (CustomerID, Name, Email, Country)
VALUES (1, 'Alice', 'alice@example.com', 'USA'),
       (2, 'Bob', 'bob@example.com', 'UK');

INSERT INTO Products (ProductID, Name, Category, Price)
VALUES (1, 'Laptop', 'Electronics', 1000),
       (2, 'Mouse', 'Accessories', 25),
       (3, 'Keyboard', 'Accessories', 50);

INSERT INTO Orders (OrderID, CustomerID, OrderDate)
VALUES (101, 1, '2025-01-05'),
       (102, 2, '2025-01-06');

INSERT INTO OrderItems (OrderItemID, OrderID, ProductID, Quantity)
VALUES (1, 101, 1, 1),
       (2, 101, 2, 2),
       (3, 102, 2, 1),
       (4, 102, 3, 1);
```

**Explanation:**

* Multiple rows can be inserted using **comma-separated values**.

---

## **4. Basic SELECT Queries**

### **Select all columns**

```sql
SELECT * FROM Customers;
```

### **Select specific columns**

```sql
SELECT Name, Email FROM Customers;
```

### **Filter with WHERE**

```sql
SELECT * FROM Customers
WHERE Country = 'USA';
```

### **Filter with multiple conditions**

```sql
SELECT * FROM OrderItems
WHERE Quantity > 1 AND ProductID = 2;
```

---

## **5. Sorting and Limiting Results**

### **ORDER BY**

```sql
SELECT * FROM Products
ORDER BY Price DESC;
```

### **LIMIT / TOP**

```sql
SELECT * FROM Products
ORDER BY Price DESC
LIMIT 2;  -- Only top 2 products
```

---

## **6. Aggregate Functions**

* `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`

```sql
SELECT COUNT(*) AS TotalCustomers FROM Customers;

SELECT SUM(Price * Quantity) AS TotalSales
FROM OrderItems oi
JOIN Products p ON oi.ProductID = p.ProductID;
```

**Explanation:**

* Aggregates calculate **summary statistics** over a dataset.

---

## **7. GROUP BY and HAVING**

### **Total Sales per Customer**

```sql
SELECT c.Name, SUM(p.Price * oi.Quantity) AS TotalSpent
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
JOIN Products p ON oi.ProductID = p.ProductID
GROUP BY c.Name;
```

### **Filter groups using HAVING**

```sql
SELECT c.Name, SUM(p.Price * oi.Quantity) AS TotalSpent
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
JOIN Products p ON oi.ProductID = p.ProductID
GROUP BY c.Name
HAVING SUM(p.Price * oi.Quantity) > 50;
```

---

## **8. JOINs**

### **INNER JOIN**

```sql
SELECT o.OrderID, c.Name, p.Name AS ProductName, oi.Quantity
FROM Orders o
INNER JOIN Customers c ON o.CustomerID = c.CustomerID
INNER JOIN OrderItems oi ON o.OrderID = oi.OrderID
INNER JOIN Products p ON oi.ProductID = p.ProductID;
```

### **LEFT JOIN**

```sql
SELECT c.Name, o.OrderID
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID;
```

### **RIGHT JOIN**

```sql
SELECT o.OrderID, c.Name
FROM Orders o
RIGHT JOIN Customers c ON o.CustomerID = c.CustomerID;
```

### **FULL OUTER JOIN** (some DBMS only)

```sql
SELECT c.Name, o.OrderID
FROM Customers c
FULL OUTER JOIN Orders o ON c.CustomerID = o.CustomerID;
```

---

## **9. Subqueries**

### **Simple subquery**

```sql
SELECT Name
FROM Customers
WHERE CustomerID IN (SELECT CustomerID FROM Orders);
```

### **Correlated subquery**

```sql
SELECT Name,
       (SELECT SUM(p.Price * oi.Quantity)
        FROM Orders o
        JOIN OrderItems oi ON o.OrderID = oi.OrderID
        JOIN Products p ON oi.ProductID = p.ProductID
        WHERE o.CustomerID = c.CustomerID) AS TotalSpent
FROM Customers c;
```

---

## **10. Modifying Data**

### **UPDATE**

```sql
UPDATE Products
SET Price = Price * 1.10
WHERE Category = 'Accessories';
```

### **DELETE**

```sql
DELETE FROM Customers
WHERE CustomerID = 2;
```

---

## **11. Advanced SQL**

### **CASE Statements**

```sql
SELECT Name,
       CASE
           WHEN CustomerID = 1 THEN 'VIP'
           ELSE 'Regular'
       END AS CustomerType
FROM Customers;
```

### **COALESCE / IFNULL**

```sql
SELECT Name, COALESCE(Email, 'No Email') AS EmailAddress
FROM Customers;
```

### **Window Functions**

```sql
SELECT Name, OrderID,
       SUM(Price * Quantity) OVER(PARTITION BY Name) AS TotalSpent
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
JOIN Products p ON oi.ProductID = p.ProductID;
```

---

## **12. Indexes and Optimization**

```sql
CREATE INDEX idx_customer_name ON Customers(Name);
```

**Explanation:**

* Indexes improve **query performance** on large datasets.

---

## **13. Transactions**

```sql
START TRANSACTION;

UPDATE Products SET Price = Price * 1.10 WHERE Category = 'Electronics';
DELETE FROM Customers WHERE CustomerID = 3;

COMMIT;   -- Save changes
-- or
ROLLBACK; -- Undo changes
```

---

## **14. Best Practices**

1. Always use **JOINs instead of subqueries** for performance.
2. Use **indexes** for large tables on frequently filtered columns.
3. Avoid `SELECT *` in production.
4. Use **transactions** to maintain data integrity.
5. Always back up your database before DDL operations.

---

## **15. Summary**

This tutorial covered:

* Database creation and table design
* Inserting, updating, deleting data
* Querying data with SELECT, WHERE, ORDER BY, GROUP BY
* JOINs, subqueries, and aggregations
* Advanced features: CASE, window functions, transactions, indexes

---

Absolutely! Let’s create a **comprehensive tutorial on SQL window functions**, with detailed explanations, use cases, and examples.

---

# **SQL Window Functions Tutorial**

Window functions are powerful SQL tools used for **performing calculations across a set of table rows related to the current row**, without collapsing the results like aggregate functions. They are also known as **analytic functions**.

---

## **1. What are Window Functions?**

* Unlike aggregate functions (`SUM`, `AVG`) that **group rows**, window functions **maintain the individual rows** while performing calculations over a "window" of related rows.
* Common use cases: **running totals, ranks, moving averages, percentiles**.

---

## **2. Basic Syntax**

```sql
SELECT
    column1,
    column2,
    WINDOW_FUNCTION() OVER (
        [PARTITION BY column]  -- optional
        [ORDER BY column]      -- optional
        [ROWS/RANGE frame]     -- optional
    ) AS alias
FROM table_name;
```

* `PARTITION BY`: divides the dataset into groups (like `GROUP BY` but doesn’t collapse rows).
* `ORDER BY`: defines the order within each partition.
* `ROWS` or `RANGE`: defines the frame/window of rows to consider.

---

## **3. Common Window Functions**

### **a) ROW_NUMBER()**

Assigns a unique number to each row in a partition, ordered by a column.

```sql
SELECT
    CustomerID,
    OrderID,
    OrderDate,
    ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS RowNum
FROM Orders;
```

**Explanation:**

* For each customer (`PARTITION BY CustomerID`), orders are numbered by `OrderDate`.

---

### **b) RANK()**

Assigns a rank to each row within a partition, with **ties sharing the same rank**.

```sql
SELECT
    CustomerID,
    OrderID,
    TotalAmount,
    RANK() OVER (PARTITION BY CustomerID ORDER BY TotalAmount DESC) AS Rank
FROM Orders;
```

**Difference from ROW_NUMBER():**

* ROW_NUMBER() → unique number for every row
* RANK() → tied values get the same rank, and gaps are created

---

### **c) DENSE_RANK()**

Similar to RANK(), but **no gaps in ranking** for ties.

```sql
SELECT
    CustomerID,
    OrderID,
    TotalAmount,
    DENSE_RANK() OVER (PARTITION BY CustomerID ORDER BY TotalAmount DESC) AS DenseRank
FROM Orders;
```

---

### **d) SUM() / AVG() as Window Functions**

Compute running totals or moving averages **without grouping**.

```sql
SELECT
    CustomerID,
    OrderDate,
    TotalAmount,
    SUM(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS RunningTotal,
    AVG(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS RunningAvg
FROM Orders;
```

**Explanation:**

* `SUM()` and `AVG()` act like aggregates but **do not collapse rows**.
* `ORDER BY` defines the order for the cumulative calculation.

---

### **e) LEAD() and LAG()**

Access the **next or previous row's value** in a partition.

```sql
SELECT
    CustomerID,
    OrderDate,
    TotalAmount,
    LAG(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS PrevOrder,
    LEAD(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS NextOrder
FROM Orders;
```

* `LAG()` → value from previous row
* `LEAD()` → value from next row

---

### **f) FIRST_VALUE() and LAST_VALUE()**

Get the **first or last value** in a partition window.

```sql
SELECT
    CustomerID,
    OrderDate,
    TotalAmount,
    FIRST_VALUE(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS FirstOrder,
    LAST_VALUE(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS LastOrder
FROM Orders;
```

**Important:**

* For `LAST_VALUE()`, you often need to specify the window frame, otherwise it may return the current row instead of the last in the partition.

---

## **4. Window Frames**

* By default, window functions operate on **all rows from the start to the current row** (`RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`).
* You can define custom frames:

  ```sql
  ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
  ```

  * Example: moving average over **previous, current, and next row**.

```sql
SELECT
    OrderDate,
    TotalAmount,
    AVG(TotalAmount) OVER (ORDER BY OrderDate ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS MovingAvg
FROM Orders;
```

---

## **5. Practical Example: E-Commerce Orders**

Assume we have the table `Orders`:

| OrderID | CustomerID | OrderDate  | TotalAmount |
| ------- | ---------- | ---------- | ----------- |
| 101     | 1          | 2025-01-01 | 100         |
| 102     | 1          | 2025-01-05 | 200         |
| 103     | 1          | 2025-01-10 | 150         |
| 104     | 2          | 2025-01-03 | 80          |
| 105     | 2          | 2025-01-06 | 120         |

### **Calculate Running Total Per Customer**

```sql
SELECT
    CustomerID,
    OrderID,
    OrderDate,
    TotalAmount,
    SUM(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS RunningTotal
FROM Orders;
```

**Result:**

| CustomerID | OrderID | OrderDate  | TotalAmount | RunningTotal |
| ---------- | ------- | ---------- | ----------- | ------------ |
| 1          | 101     | 2025-01-01 | 100         | 100          |
| 1          | 102     | 2025-01-05 | 200         | 300          |
| 1          | 103     | 2025-01-10 | 150         | 450          |
| 2          | 104     | 2025-01-03 | 80          | 80           |
| 2          | 105     | 2025-01-06 | 120         | 200          |

---

### **Rank Orders by Amount Per Customer**

```sql
SELECT
    CustomerID,
    OrderID,
    TotalAmount,
    RANK() OVER (PARTITION BY CustomerID ORDER BY TotalAmount DESC) AS Rank
FROM Orders;
```

---

### **Compare Current Order to Previous Order**

```sql
SELECT
    CustomerID,
    OrderID,
    TotalAmount,
    LAG(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS PrevOrder,
    TotalAmount - LAG(TotalAmount) OVER (PARTITION BY CustomerID ORDER BY OrderDate) AS Difference
FROM Orders;
```

* Shows **how each order compares to the previous order**.

---

## **6. Summary of Common Window Functions**

| Function          | Purpose                         |
| ----------------- | ------------------------------- |
| `ROW_NUMBER()`    | Unique row number per partition |
| `RANK()`          | Rank rows with gaps for ties    |
| `DENSE_RANK()`    | Rank rows without gaps for ties |
| `SUM()` / `AVG()` | Running totals or averages      |
| `LEAD()`          | Access next row’s value         |
| `LAG()`           | Access previous row’s value     |
| `FIRST_VALUE()`   | Get first value in partition    |
| `LAST_VALUE()`    | Get last value in partition     |

---

## **7. Tips for Using Window Functions**

1. **Always specify PARTITION BY** if you want per-group calculations.
2. Use **ORDER BY** inside the window to ensure correct cumulative calculations.
3. Use **ROWS BETWEEN** to define custom frames for moving averages or running totals.
4. Window functions **do not collapse rows**, unlike GROUP BY.

---

If you want, I can also create a **practical E-Commerce SQL report project** where we calculate:

* Customer rankings by spending
* Running totals per customer
* Top-selling products
* Monthly sales using **window functions**

It would be **ready-to-run SQL scripts with sample data and outputs**.

Do you want me to do that next?

Absolutely! Let’s go step by step into **SQL Query Optimization**, covering techniques, examples, and best practices to make your queries faster and more efficient.

---

# **SQL Query Optimization Tutorial**

SQL query optimization is the process of **improving the performance of SQL queries** to reduce execution time, minimize resource usage, and handle large datasets efficiently.

---

## **1. Understanding Query Performance**

Before optimizing, it’s important to know what affects query performance:

* **Table size**: Large tables take longer to scan.
* **Indexes**: Lack of proper indexes can slow queries.
* **Joins**: Complex joins on large datasets can be expensive.
* **Subqueries vs joins**: Some subqueries are less efficient than joins.
* **Functions in WHERE clauses**: Can prevent indexes from being used.
* **Data types**: Mismatched types can lead to table scans.

---

## **2. Use EXPLAIN / EXPLAIN ANALYZE**

* Most databases (MySQL, PostgreSQL, SQL Server) have a command to **analyze query execution plans**.

```sql
EXPLAIN SELECT * FROM Orders WHERE CustomerID = 1;
```

* This shows **how the database executes the query**, which indexes are used, and whether a **full table scan** occurs.

---

## **3. Indexing**

Indexes are like a **table of contents** for your database.

### **Example: Single-column Index**

```sql
CREATE INDEX idx_customer_id ON Orders(CustomerID);
```

* Speeds up queries like:

```sql
SELECT * FROM Orders WHERE CustomerID = 1;
```

### **Example: Composite Index**

```sql
CREATE INDEX idx_customer_date ON Orders(CustomerID, OrderDate);
```

* Speeds up queries filtering on **both columns**:

```sql
SELECT * FROM Orders 
WHERE CustomerID = 1 AND OrderDate >= '2025-01-01';
```

**Tip:** Avoid indexing every column — indexes take **space and slow down inserts/updates**.

---

## **4. Avoid SELECT ***

* Selecting all columns fetches unnecessary data.

```sql
-- Inefficient
SELECT * FROM Orders;

-- Optimized
SELECT OrderID, CustomerID, TotalAmount FROM Orders;
```

---

## **5. Use WHERE clauses efficiently**

* Always filter as early as possible to **reduce rows processed**.

```sql
-- Inefficient: fetch all and then filter
SELECT * FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID;

-- Optimized: filter first
SELECT * FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID
WHERE o.OrderDate >= '2025-01-01';
```

* Avoid functions on columns in WHERE clauses if they prevent index usage:

```sql
-- Inefficient: function prevents index
SELECT * FROM Orders WHERE YEAR(OrderDate) = 2025;

-- Optimized: use range
SELECT * FROM Orders WHERE OrderDate >= '2025-01-01' AND OrderDate < '2026-01-01';
```

---

## **6. Optimize Joins**

* **Use INNER JOIN instead of LEFT JOIN** if you don’t need unmatched rows.
* **Join on indexed columns**.
* **Avoid joining large tables unnecessarily**.

Example:

```sql
-- Inefficient: joining all orders even if not needed
SELECT c.Name, o.OrderID, o.TotalAmount
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID;

-- Optimized: only relevant orders
SELECT c.Name, o.OrderID, o.TotalAmount
FROM Customers c
INNER JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE o.TotalAmount > 100;
```

---

## **7. Use EXISTS instead of IN (for large datasets)**

```sql
-- Slower for large lists
SELECT * FROM Customers WHERE CustomerID IN (SELECT CustomerID FROM Orders);

-- Faster
SELECT * FROM Customers c
WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.CustomerID);
```

* `EXISTS` stops searching after the first match, improving performance.

---

## **8. Limit Rows with LIMIT / TOP**

* Only fetch what you need:

```sql
SELECT * FROM Orders ORDER BY OrderDate DESC LIMIT 10;
```

* Avoid fetching millions of rows if you only need a subset.

---

## **9. Avoid Correlated Subqueries (if possible)**

```sql
-- Inefficient: executes subquery for every row
SELECT Name,
       (SELECT SUM(TotalAmount) 
        FROM Orders o 
        WHERE o.CustomerID = c.CustomerID) AS TotalSpent
FROM Customers c;

-- Optimized: use JOIN + GROUP BY
SELECT c.Name, SUM(o.TotalAmount) AS TotalSpent
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.Name;
```

---

## **10. Use Proper Data Types**

* Use smallest data types that fit the data.
* Avoid varchar/text for numeric values.
* Avoid storing dates as strings.

Example:

```sql
-- Bad
Price VARCHAR(20);

-- Good
Price DECIMAL(10,2);
```

---

## **11. Partitioning and Sharding (Large Databases)**

* **Partitioning:** Split tables by date or key to improve queries.

```sql
-- Example: range partition by year
CREATE TABLE Orders_2025 PARTITION OF Orders
FOR VALUES FROM ('2025-01-01') TO ('2025-12-31');
```

* **Sharding:** Split data across multiple servers for very large datasets.

---

## **12. Caching and Materialized Views**

* **Materialized View:** Precompute and store heavy query results.

```sql
CREATE MATERIALIZED VIEW MonthlySales AS
SELECT CustomerID, SUM(TotalAmount) AS TotalSpent
FROM Orders
GROUP BY CustomerID;
```

* Speeds up **frequent queries**.

---

## **13. Example: Optimizing a Complex Query**

### Original Query (Slow)

```sql
SELECT c.Name, o.OrderID, SUM(oi.Quantity * p.Price) AS Total
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
LEFT JOIN OrderItems oi ON o.OrderID = oi.OrderID
LEFT JOIN Products p ON oi.ProductID = p.ProductID
WHERE YEAR(o.OrderDate) = 2025
GROUP BY c.Name, o.OrderID;
```

### Optimized Version

```sql
SELECT c.Name, o.OrderID, SUM(oi.Quantity * p.Price) AS Total
FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
JOIN Products p ON oi.ProductID = p.ProductID
WHERE o.OrderDate >= '2025-01-01' AND o.OrderDate < '2026-01-01'
GROUP BY c.Name, o.OrderID;
```

**Optimizations Applied:**

1. Replaced `LEFT JOIN` with `JOIN` to remove unnecessary unmatched rows.
2. Avoided `YEAR()` function on column; used a **date range** to allow index usage.
3. Ensured joins are on **indexed columns**.

---

## **14. Summary of Key Optimization Techniques**

| Technique                               | Why It Helps                           |
| --------------------------------------- | -------------------------------------- |
| Use Indexes                             | Speeds up lookups and joins            |
| Avoid SELECT *                          | Reduces I/O and memory usage           |
| Filter early with WHERE                 | Minimizes rows processed               |
| Use JOINs efficiently                   | Reduces unnecessary table scans        |
| Avoid correlated subqueries             | Prevents repeated computations         |
| Use EXISTS instead of IN for large sets | Faster evaluation                      |
| Limit rows fetched                      | Avoids retrieving unnecessary data     |
| Proper data types                       | Reduces storage and improves indexing  |
| Partitioning/Materialized Views         | Improves performance on large datasets |

---

✅ **Next Step:** If you want, I can create a **practical “E-Commerce SQL Optimization Project”** where we:

* Write **slow queries**
* Apply these optimization techniques
* Show **execution times and results**
* Include **indexes, partitions, and window functions**

Do you want me to do that?
Sure! Here’s a **detailed tutorial in English** covering **Databases, Data Warehouses, Data Lakes, Data Mesh, and Data Cubes**.

---

# **Data Management Tutorial: Databases, Data Warehouses, Data Lakes, Data Mesh & Data Cubes**

---

## **1. Databases**

A **database** is a structured storage system for data, managed by a **Database Management System (DBMS)**.

### **Types of Databases:**

1. **Relational Databases (RDBMS)**

   * Data is stored in **tables** with rows and columns.
   * Examples: MySQL, PostgreSQL, Oracle, SQL Server.
   * **Example Table: Customers**

| CustomerID | Name  | Email                                         |
| ---------- | ----- | --------------------------------------------- |
| 1          | Alice | [alice@example.com](mailto:alice@example.com) |
| 2          | Bob   | [bob@example.com](mailto:bob@example.com)     |

2. **NoSQL Databases**

   * Flexible schemas for **key-value, document, graph, or columnar data**.
   * Examples: MongoDB, Cassandra.
   * Advantage: **Scales horizontally** and handles unstructured data.

**Basic Operations:**

* Insert data (`INSERT`)
* Query data (`SELECT`)
* Update data (`UPDATE`)
* Delete data (`DELETE`)

---

## **2. Data Warehouse (DWH)**

A **Data Warehouse** is a centralized storage for **structured enterprise data**, optimized for **reporting and analytics**.

### **Key Features:**

* Data is **extracted, transformed, and loaded (ETL)** from multiple sources.
* Stores **historical data** for analysis, not for daily transactions.
* Uses **Star Schema** or **Snowflake Schema** for modeling.

### **Example Star Schema:**

* **Fact Table:** Sales
* **Dimension Tables:** Customer, Product, Time

```
Fact_Sales
+--------+-----------+--------+-------+
| SaleID | CustomerID| ProdID | Amount|
+--------+-----------+--------+-------+

Dim_Customer
+-----------+------+
| CustomerID| Name |
+-----------+------+
```

**Advantages:**

* Fast queries for **Business Intelligence (BI)**
* Consistent data for reporting

---

## **3. Data Lake**

A **Data Lake** stores **all types of data**, both structured and unstructured, in **raw format**.

### **Key Features:**

* Can handle **massive volumes of data (Big Data)**
* Supports **data science and machine learning**
* Common technologies: Hadoop, Amazon S3, Azure Data Lake

**Example:**

* Store logs, images, JSON files, CSVs, and structured database exports in a single data repository.

**Advantages:**

* Highly flexible, stores data **as-is**
* Ideal for **advanced analytics**
* Can feed **machine learning models** directly

---

## **4. Data Mesh**

**Data Mesh** is a modern **decentralized data architecture** approach.

### **Key Concepts:**

* Treats **data as a product**, with ownership by **domain teams**.
* Each team manages its own **data pipelines, quality, and access**.
* Promotes **scalability, agility, and self-service analytics**.

**Benefits:**

* Reduces bottlenecks from central data teams
* Encourages **domain-driven design**
* Easier to scale with large organizations

---

## **5. Data Cubes**

A **Data Cube** is a **multidimensional representation** of data, often used in OLAP (Online Analytical Processing).

### **Structure:**

* **Dimensions:** Attributes for analysis (e.g., Time, Product, Location)
* **Measures:** Quantitative data (e.g., Sales, Profit)

**Example:**

* A sales cube could have dimensions: `Product`, `Region`, `Month`
* Measure: `Total Sales`

**Operations on Data Cubes:**

* **Roll-up:** Aggregate data along a dimension (e.g., monthly → quarterly sales)
* **Drill-down:** Break down data to more detailed levels
* **Slice:** Select a single dimension value (e.g., sales for Q1)
* **Dice:** Select specific ranges across multiple dimensions

---

## **6. Summary of Key Differences**

| Feature            | Database      | Data Warehouse      | Data Lake                 | Data Mesh                 | Data Cube              |
| ------------------ | ------------- | ------------------- | ------------------------- | ------------------------- | ---------------------- |
| Data Type          | Structured    | Structured          | Structured & Unstructured | Structured & Unstructured | Structured             |
| Purpose            | Transactional | Analytics/Reporting | Analytics/ML              | Decentralized Analytics   | OLAP/Multidimensional  |
| Storage            | Tables        | Tables/Schema       | Raw storage (files)       | Domain-owned storage      | Pre-aggregated cubes   |
| Scalability        | Medium        | Medium              | High                      | High                      | Medium                 |
| Query Optimization | Indexes, SQL  | Aggregates, Indexes | Distributed processing    | Domain-specific pipelines | Precomputed aggregates |

---

If you want, I can also create a **practical diagram and example workflow** showing **how data flows from databases → data lake → warehouse → mesh → OLAP cubes**, with **example SQL/Pandas integration**, so it’s very visual and hands-on.

Do you want me to do that next?

Natürlich! Hier ist ein **umfassendes SQL-Tutorial auf Deutsch**, detailliert erklärt, mit Beispielen für Anfänger bis Fortgeschrittene.

---

# **SQL Tutorial – Deutsch**

SQL (Structured Query Language) ist die Standard-Sprache zur **Verwaltung und Abfrage relationaler Datenbanken**.

---

## **1. Einführung in SQL**

* SQL wird verwendet, um **Daten zu erstellen, abzurufen, zu ändern und zu löschen**.
* Die meisten relationalen Datenbanksysteme (MySQL, PostgreSQL, Oracle, SQL Server) unterstützen SQL.

### **Grundlegende SQL-Kategorien**

| Kategorie                          | Befehle                                | Zweck                                   |
| ---------------------------------- | -------------------------------------- | --------------------------------------- |
| DDL (Data Definition Language)     | `CREATE`, `ALTER`, `DROP`              | Tabellen und Datenstrukturen definieren |
| DML (Data Manipulation Language)   | `SELECT`, `INSERT`, `UPDATE`, `DELETE` | Daten manipulieren                      |
| DCL (Data Control Language)        | `GRANT`, `REVOKE`                      | Zugriffsrechte verwalten                |
| TCL (Transaction Control Language) | `COMMIT`, `ROLLBACK`                   | Transaktionen steuern                   |

---

## **2. Datenbank und Tabellen erstellen**

### **Datenbank erstellen**

```sql
CREATE DATABASE ecommerce;
```

### **Datenbank verwenden**

```sql
USE ecommerce;
```

### **Tabelle erstellen**

```sql
CREATE TABLE Kunden (
    KundenID INT PRIMARY KEY,
    Name VARCHAR(50),
    Email VARCHAR(100),
    Land VARCHAR(50)
);

CREATE TABLE Produkte (
    ProduktID INT PRIMARY KEY,
    Name VARCHAR(50),
    Kategorie VARCHAR(50),
    Preis DECIMAL(10,2)
);

CREATE TABLE Bestellungen (
    BestellID INT PRIMARY KEY,
    KundenID INT,
    Bestelldatum DATE,
    FOREIGN KEY (KundenID) REFERENCES Kunden(KundenID)
);

CREATE TABLE BestellPositionen (
    PositionID INT PRIMARY KEY,
    BestellID INT,
    ProduktID INT,
    Menge INT,
    FOREIGN KEY (BestellID) REFERENCES Bestellungen(BestellID),
    FOREIGN KEY (ProduktID) REFERENCES Produkte(ProduktID)
);
```

---

## **3. Daten einfügen**

```sql
INSERT INTO Kunden (KundenID, Name, Email, Land)
VALUES (1, 'Alice', 'alice@example.com', 'Deutschland'),
       (2, 'Bob', 'bob@example.com', 'Österreich');

INSERT INTO Produkte (ProduktID, Name, Kategorie, Preis)
VALUES (1, 'Laptop', 'Elektronik', 1000),
       (2, 'Maus', 'Zubehör', 25),
       (3, 'Tastatur', 'Zubehör', 50);

INSERT INTO Bestellungen (BestellID, KundenID, Bestelldatum)
VALUES (101, 1, '2025-01-05'),
       (102, 2, '2025-01-06');

INSERT INTO BestellPositionen (PositionID, BestellID, ProduktID, Menge)
VALUES (1, 101, 1, 1),
       (2, 101, 2, 2),
       (3, 102, 2, 1),
       (4, 102, 3, 1);
```

---

## **4. Daten abfragen (SELECT)**

### **Alle Spalten auswählen**

```sql
SELECT * FROM Kunden;
```

### **Bestimmte Spalten auswählen**

```sql
SELECT Name, Email FROM Kunden;
```

### **Zeilen filtern (WHERE)**

```sql
SELECT * FROM Kunden
WHERE Land = 'Deutschland';
```

### **Mehrere Bedingungen**

```sql
SELECT * FROM BestellPositionen
WHERE Menge > 1 AND ProduktID = 2;
```

---

## **5. Sortieren und begrenzen**

### **ORDER BY**

```sql
SELECT * FROM Produkte
ORDER BY Preis DESC;
```

### **LIMIT (oder TOP)**

```sql
SELECT * FROM Produkte
ORDER BY Preis DESC
LIMIT 2;
```

---

## **6. Aggregatfunktionen**

* `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()`

```sql
SELECT COUNT(*) AS GesamtKunden FROM Kunden;

SELECT SUM(Preis * Menge) AS GesamtUmsatz
FROM BestellPositionen bp
JOIN Produkte p ON bp.ProduktID = p.ProduktID;
```

---

## **7. GROUP BY und HAVING**

### **Gesamtumsatz pro Kunde**

```sql
SELECT k.Name, SUM(p.Preis * bp.Menge) AS GesamtUmsatz
FROM Kunden k
JOIN Bestellungen b ON k.KundenID = b.KundenID
JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
JOIN Produkte p ON bp.ProduktID = p.ProduktID
GROUP BY k.Name;
```

### **Gruppen filtern (HAVING)**

```sql
SELECT k.Name, SUM(p.Preis * bp.Menge) AS GesamtUmsatz
FROM Kunden k
JOIN Bestellungen b ON k.KundenID = b.KundenID
JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
JOIN Produkte p ON bp.ProduktID = p.ProduktID
GROUP BY k.Name
HAVING SUM(p.Preis * bp.Menge) > 50;
```

---

## **8. JOINs**

### **INNER JOIN**

```sql
SELECT b.BestellID, k.Name, p.Name AS ProduktName, bp.Menge
FROM Bestellungen b
INNER JOIN Kunden k ON b.KundenID = k.KundenID
INNER JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
INNER JOIN Produkte p ON bp.ProduktID = p.ProduktID;
```

### **LEFT JOIN**

```sql
SELECT k.Name, b.BestellID
FROM Kunden k
LEFT JOIN Bestellungen b ON k.KundenID = b.KundenID;
```

---

## **9. Unterabfragen (Subqueries)**

### **Einfache Subquery**

```sql
SELECT Name
FROM Kunden
WHERE KundenID IN (SELECT KundenID FROM Bestellungen);
```

### **Korrelierte Subquery**

```sql
SELECT Name,
       (SELECT SUM(p.Preis * bp.Menge)
        FROM Bestellungen b
        JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
        JOIN Produkte p ON bp.ProduktID = p.ProduktID
        WHERE b.KundenID = k.KundenID) AS GesamtUmsatz
FROM Kunden k;
```

---

## **10. Daten ändern**

### **UPDATE**

```sql
UPDATE Produkte
SET Preis = Preis * 1.10
WHERE Kategorie = 'Zubehör';
```

### **DELETE**

```sql
DELETE FROM Kunden
WHERE KundenID = 2;
```

---

## **11. Erweiterte SQL-Funktionen**

### **CASE Statements**

```sql
SELECT Name,
       CASE
           WHEN KundenID = 1 THEN 'VIP'
           ELSE 'Standard'
       END AS Kundentyp
FROM Kunden;
```

### **COALESCE / IFNULL**

```sql
SELECT Name, COALESCE(Email, 'Keine Email') AS EmailAdresse
FROM Kunden;
```

### **Fensterfunktionen (Window Functions)**

```sql
SELECT Name, BestellID,
       SUM(p.Preis * bp.Menge) OVER(PARTITION BY Name) AS GesamtUmsatz
FROM Kunden k
JOIN Bestellungen b ON k.KundenID = b.KundenID
JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
JOIN Produkte p ON bp.ProduktID = p.ProduktID;
```

---

## **12. Transaktionen**

```sql
START TRANSACTION;

UPDATE Produkte SET Preis = Preis * 1.10 WHERE Kategorie = 'Elektronik';
DELETE FROM Kunden WHERE KundenID = 3;

COMMIT;   -- Änderungen speichern
-- oder
ROLLBACK; -- Änderungen zurücksetzen
```

---

## **13. Indexe für Performance**

```sql
CREATE INDEX idx_kunden_name ON Kunden(Name);
```

* Indexe verbessern **Abfragegeschwindigkeit**, erhöhen aber Speicherbedarf und verlangsamen Inserts/Updates.

---

## **14. Best Practices**

1. **Keine SELECT *** in Produktionsabfragen
2. **Indexe auf häufig gefilterte Spalten**
3. **Joins auf indizierten Spalten**
4. **Filter so früh wie möglich anwenden (WHERE)**
5. **Subqueries vermeiden, wenn JOIN effizienter ist**
6. **Transaktionen verwenden, um Konsistenz zu wahren**

---

## **15. Zusammenfassung**

Dieses Tutorial deckt ab:

* **Grundlagen:** Datenbank, Tabellen, SQL-Befehle
* **Datenabfrage:** SELECT, WHERE, JOIN, GROUP BY, HAVING
* **Datenänderung:** INSERT, UPDATE, DELETE
* **Fortgeschrittene Funktionen:** CASE, COALESCE, Window Functions
* **Performance & Best Practices:** Indexe, Transaktionen, Optimierung

---

Wenn du willst, kann ich auch ein **praktisches E-Commerce SQL Projekt** in Deutsch erstellen, mit **Beispiel-Daten, Abfragen, Analysen, Aggregationen und Window Functions**, das **direkt ausgeführt werden kann**.

Willst du, dass ich das erstelle?

Natürlich! Hier ist ein **detailliertes Tutorial zu SQL Window Functions auf Deutsch** mit Beispielen und Erklärungen.

---

# **SQL Window Functions – Tutorial (Deutsch)**

SQL **Window Functions** (Fensterfunktionen) sind leistungsstarke Funktionen, mit denen Berechnungen über eine **Gruppe von Zeilen** durchgeführt werden, die mit der aktuellen Zeile zusammenhängen, **ohne die Ergebnisse zu aggregieren**.

---

## **1. Grundlagen**

* Im Gegensatz zu Aggregatfunktionen (`SUM()`, `AVG()`), die **Zeilen zusammenfassen**, behalten Fensterfunktionen alle Zeilen bei.
* Häufige Anwendungsfälle: **Rangfolge, kumulative Summen, gleitende Durchschnitte, Vergleich von Zeilen**.

### **Syntax**

```sql
SELECT
    spalte1,
    spalte2,
    WINDOW_FUNCTION() OVER (
        [PARTITION BY spalte]  -- optional: Gruppierung
        [ORDER BY spalte]      -- optional: Reihenfolge innerhalb der Partition
        [ROWS/RANGE frame]     -- optional: Fenstergröße
    ) AS alias
FROM tabelle;
```

---

## **2. Wichtige Fensterfunktionen**

### **a) ROW_NUMBER()**

* Vergibt eine eindeutige Nummer innerhalb jeder Partition.

```sql
SELECT
    KundeID,
    BestellID,
    Bestelldatum,
    ROW_NUMBER() OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS ZeilenNummer
FROM Bestellungen;
```

**Erklärung:**

* Für jeden Kunden (`PARTITION BY KundeID`) werden die Bestellungen nach Datum nummeriert.

---

### **b) RANK()**

* Vergibt Rangwerte, **gleiche Werte erhalten denselben Rang**, Lücken entstehen bei Gleichständen.

```sql
SELECT
    KundeID,
    BestellID,
    SUM(Betrag) AS Gesamtbetrag,
    RANK() OVER (PARTITION BY KundeID ORDER BY SUM(Betrag) DESC) AS Rang
FROM Bestellungen
GROUP BY KundeID, BestellID;
```

---

### **c) DENSE_RANK()**

* Ähnlich wie `RANK()`, aber **keine Lücken bei Gleichständen**.

```sql
SELECT
    KundeID,
    BestellID,
    SUM(Betrag) AS Gesamtbetrag,
    DENSE_RANK() OVER (PARTITION BY KundeID ORDER BY SUM(Betrag) DESC) AS DichteRang
FROM Bestellungen
GROUP BY KundeID, BestellID;
```

---

### **d) SUM(), AVG() als Fensterfunktionen**

* Berechnet **kumulative Summen oder gleitende Durchschnitte**.

```sql
SELECT
    KundeID,
    Bestelldatum,
    Betrag,
    SUM(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS LaufendeSumme,
    AVG(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS LaufenderDurchschnitt
FROM Bestellungen;
```

---

### **e) LEAD() und LAG()**

* Zugriff auf **nächste oder vorherige Zeile**.

```sql
SELECT
    KundeID,
    Bestelldatum,
    Betrag,
    LAG(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS VorherigeBestellung,
    LEAD(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS NaechsteBestellung
FROM Bestellungen;
```

* `LAG()` → vorheriger Wert
* `LEAD()` → nächster Wert

---

### **f) FIRST_VALUE() und LAST_VALUE()**

* Holt den **ersten oder letzten Wert** in einer Partition.

```sql
SELECT
    KundeID,
    Bestelldatum,
    Betrag,
    FIRST_VALUE(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS ErsteBestellung,
    LAST_VALUE(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS LetzteBestellung
FROM Bestellungen;
```

**Hinweis:**

* Für `LAST_VALUE()` muss oft der **Fensterbereich** angegeben werden, sonst wird der aktuelle Wert verwendet.

---

## **3. Fensterbereiche (Window Frames)**

* Standard: alle Zeilen **vom Beginn bis zur aktuellen Zeile**
* Definierbar für **gleitende Summen oder Durchschnittswerte**:

```sql
ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
```

Beispiel:

```sql
SELECT
    Bestelldatum,
    Betrag,
    AVG(Betrag) OVER (ORDER BY Bestelldatum ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING) AS GleitenderDurchschnitt
FROM Bestellungen;
```

* Berechnet den Durchschnitt über **die vorherige, aktuelle und nächste Zeile**.

---

## **4. Praktisches Beispiel: E-Commerce**

| BestellID | KundeID | Bestelldatum | Betrag |
| --------- | ------- | ------------ | ------ |
| 101       | 1       | 2025-01-01   | 100    |
| 102       | 1       | 2025-01-05   | 200    |
| 103       | 1       | 2025-01-10   | 150    |
| 104       | 2       | 2025-01-03   | 80     |
| 105       | 2       | 2025-01-06   | 120    |

### **Kumulative Summe pro Kunde**

```sql
SELECT
    KundeID,
    BestellID,
    Betrag,
    SUM(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS LaufendeSumme
FROM Bestellungen;
```

**Ergebnis:**

| KundeID | BestellID | Betrag | LaufendeSumme |
| ------- | --------- | ------ | ------------- |
| 1       | 101       | 100    | 100           |
| 1       | 102       | 200    | 300           |
| 1       | 103       | 150    | 450           |
| 2       | 104       | 80     | 80            |
| 2       | 105       | 120    | 200           |

---

### **Rangfolge pro Kunde**

```sql
SELECT
    KundeID,
    BestellID,
    Betrag,
    RANK() OVER (PARTITION BY KundeID ORDER BY Betrag DESC) AS Rang
FROM Bestellungen;
```

---

### **Vergleich mit vorheriger Bestellung**

```sql
SELECT
    KundeID,
    BestellID,
    Betrag,
    LAG(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS VorherigeBestellung,
    Betrag - LAG(Betrag) OVER (PARTITION BY KundeID ORDER BY Bestelldatum) AS Differenz
FROM Bestellungen;
```

* Zeigt, **wie sich jede Bestellung im Vergleich zur vorherigen verändert**.

---

## **5. Zusammenfassung wichtiger Fensterfunktionen**

| Funktion         | Zweck                              |
| ---------------- | ---------------------------------- |
| `ROW_NUMBER()`   | Eindeutige Nummer pro Partition    |
| `RANK()`         | Rang mit Lücken bei Gleichständen  |
| `DENSE_RANK()`   | Rang ohne Lücken bei Gleichständen |
| `SUM()`, `AVG()` | Kumulative Summe / Durchschnitt    |
| `LEAD()`         | Wert der nächsten Zeile            |
| `LAG()`          | Wert der vorherigen Zeile          |
| `FIRST_VALUE()`  | Erster Wert der Partition          |
| `LAST_VALUE()`   | Letzter Wert der Partition         |

---

### **Tipps**

1. Immer `PARTITION BY` verwenden, wenn Berechnungen **pro Gruppe** nötig sind.
2. `ORDER BY` innerhalb des Fensters definiert die **Reihenfolge für Berechnungen**.
3. `ROWS BETWEEN` definiert **Fenstergröße für kumulative oder gleitende Berechnungen**.
4. Fensterfunktionen **fassen Zeilen nicht zusammen**, im Gegensatz zu `GROUP BY`.

---

Wenn du willst, kann ich auch ein **komplettes praktisches E-Commerce SQL-Projekt in Deutsch** erstellen, bei dem wir **Window Functions, Rankings, kumulative Summen und Analysen** direkt umsetzen.

Willst du, dass ich das erstelle?
Natürlich! Hier ist eine **umfassende Erklärung auf Deutsch** zu **Datenbanken, Data Warehouses, Data Lakes, Delta Lakes, Data Mesh und Data Acquisition**, detailliert und mit Beispielen.

---

# **Datenmanagement und Analytics Tutorial**

---

## **1. Datenbanken**

Eine **Datenbank** ist ein strukturierter Speicher, der es ermöglicht, Daten effizient zu **speichern, abzurufen, zu ändern und zu löschen**.

### **Arten von Datenbanken**

1. **Relationale Datenbanken (RDBMS)**

   * Daten werden in **Tabellen** mit Zeilen und Spalten gespeichert.
   * Beispiele: MySQL, PostgreSQL, SQL Server
   * Unterstützt SQL-Abfragen und garantiert Datenkonsistenz.

2. **NoSQL-Datenbanken**

   * Flexibel, schemafrei, geeignet für **unstrukturierte oder semi-strukturierte Daten**.
   * Beispiele: MongoDB, Cassandra
   * Ideal für horizontale Skalierung und große Datenmengen.

**Wichtige Operationen:**

* `INSERT`, `SELECT`, `UPDATE`, `DELETE`
* Indexe zur **Abfrageoptimierung**

---

## **2. Data Warehouse (DWH)**

Ein **Data Warehouse** ist ein **zentraler Speicher für strukturierte, historische Daten**, optimiert für **Analyse und Reporting**.

### **Merkmale:**

* Daten kommen aus verschiedenen Quellen durch **ETL-Prozesse (Extract, Transform, Load)**
* Verwendung von **Star Schema** oder **Snowflake Schema**
* Optimiert für **leselastige Abfragen**, nicht für Transaktionen

### **Beispiel Star Schema**

* **Faktentabelle:** Sales (z. B. Umsatz)
* **Dimensionstabellen:** Kunde, Produkt, Zeit

```
Fact_Sales
+--------+-----------+--------+-------+
| SaleID | CustomerID| ProdID | Amount|
+--------+-----------+--------+-------+

Dim_Customer
+-----------+------+
| CustomerID| Name |
+-----------+------+
```

**Anwendungsfälle:**

* Business Intelligence (BI)
* Management-Reporting
* Historische Trendanalysen

---

## **3. Data Lake**

Ein **Data Lake** speichert **alle Arten von Daten**, strukturiert und unstrukturiert, **roh**.

### **Merkmale:**

* Kann große Mengen an Daten aufnehmen (Big Data)
* Unterstützt **Data Science, Machine Learning**
* Technologien: Hadoop, Amazon S3, Azure Data Lake

**Beispiel:**

* Log-Dateien, JSON, CSV, Bilder, Datenbankexporte in einem zentralen Speicher.

**Vorteile:**

* Flexible Speicherung
* Ideal für **explorative Analysen** und Machine Learning

---

## **4. Delta Lake**

Ein **Delta Lake** ist eine **erweiterte Form des Data Lakes**, die **ACID-Transaktionen** unterstützt.

### **Merkmale:**

* Bietet **Transaktionssicherheit** und **Versionierung** von Daten
* Unterstützt **Time Travel**, d.h. Zugriff auf historische Datenversionen
* Optimiert für Big Data Analysen

**Beispiel:**

* Änderungen in einem Data Lake können **nachverfolgt und rückgängig gemacht** werden, ohne die gesamte Datenpipeline zu beeinträchtigen.

---

## **5. Data Mesh**

**Data Mesh** ist ein **dezentralisiertes Datenarchitektur-Konzept**.

### **Kernideen:**

* Daten werden als **Produkt** betrachtet
* Verantwortlichkeit liegt bei **Domain-Teams**, nicht einem zentralen Team
* Fördert **Skalierbarkeit, Agilität und Self-Service-Analysen**

**Vorteile:**

* Vermeidet Flaschenhälse bei zentralen Daten-Teams
* Erleichtert das **Management großer Organisationen**
* Bessere Datenqualität durch **Domain-Verantwortung**

---

## **6. Data Cubes / OLAP-Würfel**

Ein **Data Cube** ist eine **mehrdimensionale Darstellung von Daten** für Analysen.

### **Struktur:**

* **Dimensionen:** Attribute wie Zeit, Produkt, Region
* **Maße:** Quantitative Werte wie Umsatz, Gewinn

**Operationen:**

* **Roll-up:** Aggregation auf höherer Ebene (z. B. Monat → Quartal)
* **Drill-down:** Detaillierte Analyse (z. B. Tag → Stunde)
* **Slice:** Auswahl einer Dimension (z. B. nur Q1)
* **Dice:** Auswahl eines bestimmten Bereichs in mehreren Dimensionen

---

## **7. Data Acquisition (Datenakquise)**

**Data Acquisition** beschreibt den Prozess, **Daten aus verschiedenen Quellen zu sammeln** und in Systeme wie Data Lakes oder Warehouses zu laden.

### **Quellen:**

* Datenbanken (SQL, NoSQL)
* APIs (Web Services, SaaS-Plattformen)
* IoT-Geräte / Sensoren
* Logdateien, CSVs, Excel

### **Schritte:**

1. **Extrahieren:** Daten aus verschiedenen Quellen abrufen
2. **Transformieren:** Daten bereinigen, standardisieren, anreichern
3. **Laden (Load):** Daten in Data Warehouse, Data Lake oder Delta Lake speichern

**Tools:** Apache NiFi, Airflow, Talend, Informatica, Databricks

---

## **8. Zusammenfassung**

| Konzept              | Zweck / Verwendung                               |
| -------------------- | ------------------------------------------------ |
| **Datenbank**        | Strukturierte Speicherung, Transaktionen         |
| **Data Warehouse**   | Analysen, Reporting, historische Daten           |
| **Data Lake**        | Speicherung aller Daten, flexibel, Big Data      |
| **Delta Lake**       | Data Lake + ACID-Transaktionen, Versionierung    |
| **Data Mesh**        | Dezentrale Datenarchitektur, Domain Ownership    |
| **Data Cubes**       | Mehrdimensionale Analyse, OLAP                   |
| **Data Acquisition** | Sammeln und Laden von Daten aus diversen Quellen |

---

Wenn du willst, kann ich auch ein **praktisches Beispiel für ein E-Commerce-Datenmodell** erstellen, das **Datenbanken, Data Lake, Delta Lake, Data Mesh und Data Cubes** kombiniert und direkt **mit SQL oder Pandas analysierbar** ist.

Willst du, dass ich das erstelle?
Absolutely! Let’s go step by step. I’ll first explain **SQL GRANT, REVOKE, COMMIT, and ROLLBACK in English**, then provide the **German version**, with practical examples to make it easy to understand.

---

# **SQL Tutorial – Permissions & Transactions**

---

## **1. GRANT – Assigning Privileges**

**Definition:**
`GRANT` is used to **give a user or role specific permissions** on a database object (table, view, schema, or database).

**Common syntax:**

```sql
GRANT privilege ON object TO user;
```

* `privilege`: SELECT, INSERT, UPDATE, DELETE, ALL
* `object`: table, view, database
* `user`: the username or role

**Example:**

```sql
-- Grant SELECT and INSERT privileges on the table Customers to user 'analyst'
GRANT SELECT, INSERT ON Customers TO analyst;
```

**Explanation:**

* The user `analyst` can now **read and insert data** into the Customers table.
* Without `GRANT`, the user would get a “permission denied” error.

---

## **2. REVOKE – Removing Privileges**

**Definition:**
`REVOKE` removes previously granted privileges from a user or role.

**Syntax:**

```sql
REVOKE privilege ON object FROM user;
```

**Example:**

```sql
-- Revoke INSERT privilege from user 'analyst'
REVOKE INSERT ON Customers FROM analyst;
```

**Explanation:**

* After this, `analyst` can no longer insert new rows but can still select if SELECT was granted.

**Practical Use:**

* If a temporary analyst or contractor should only access data for a limited period, you can **grant privileges temporarily** and revoke later.

---

## **3. COMMIT – Saving Changes**

**Definition:**
`COMMIT` is used in **transactions** to make all changes **permanent**.

**Transactions:**

* A transaction is a group of SQL statements executed as a single unit.
* Until `COMMIT` is issued, changes are not permanent and can be undone.

**Syntax:**

```sql
COMMIT;
```

**Example:**

```sql
BEGIN TRANSACTION;

INSERT INTO Customers (CustomerID, Name, Email) VALUES (3, 'Charlie', 'charlie@example.com');
UPDATE Products SET Price = Price * 1.1 WHERE Category = 'Electronics';

COMMIT;
```

**Explanation:**

* Both the INSERT and UPDATE statements will be **permanently saved**.
* If the database crashes **before COMMIT**, changes are not saved.

---

## **4. ROLLBACK – Undo Changes**

**Definition:**
`ROLLBACK` undoes all changes in the current transaction **since the last COMMIT**.

**Syntax:**

```sql
ROLLBACK;
```

**Example:**

```sql
BEGIN TRANSACTION;

INSERT INTO Customers (CustomerID, Name, Email) VALUES (4, 'David', 'david@example.com');
UPDATE Products SET Price = Price * 0.9 WHERE Category = 'Accessories';

ROLLBACK;
```

**Explanation:**

* No changes are saved to the database.
* Useful if a mistake occurs in a transaction or validation fails.

---

## **5. Practical Scenario Combining GRANT, REVOKE, COMMIT, and ROLLBACK**

1. Create users:

```sql
CREATE USER analyst IDENTIFIED BY 'password';
```

2. Grant privileges:

```sql
GRANT SELECT, INSERT ON Customers TO analyst;
```

3. Analyst tries a transaction:

```sql
BEGIN TRANSACTION;
INSERT INTO Customers (CustomerID, Name, Email) VALUES (5, 'Eva', 'eva@example.com');
-- Suppose they make a mistake:
ROLLBACK;  -- undo the insert
```

4. Revoke privileges after task completion:

```sql
REVOKE INSERT ON Customers FROM analyst;
```

**Key Takeaways:**

* `GRANT` & `REVOKE` → control access rights.
* `COMMIT` → permanently save changes.
* `ROLLBACK` → undo mistakes.

---

# **SQL Tutorial – Deutsch**

---

## **1. GRANT – Berechtigungen vergeben**

**Definition:**
`GRANT` wird verwendet, um **einem Benutzer oder einer Rolle spezifische Rechte** auf Datenbankobjekte zu geben.

**Syntax:**

```sql
GRANT privilege ON object TO user;
```

**Beispiel:**

```sql
-- SELECT- und INSERT-Rechte auf Tabelle Customers an 'analyst' vergeben
GRANT SELECT, INSERT ON Customers TO analyst;
```

**Erklärung:**

* `analyst` kann nun **lesen und einfügen**.
* Ohne GRANT: Zugriff wird verweigert.

---

## **2. REVOKE – Berechtigungen entziehen**

**Definition:**
`REVOKE` entfernt zuvor gewährte Rechte.

**Syntax:**

```sql
REVOKE privilege ON object FROM user;
```

**Beispiel:**

```sql
-- INSERT-Recht entziehen
REVOKE INSERT ON Customers FROM analyst;
```

**Erklärung:**

* `analyst` darf nicht mehr einfügen, SELECT bleibt möglich.

---

## **3. COMMIT – Änderungen speichern**

**Definition:**
`COMMIT` speichert alle Änderungen einer **Transaktion dauerhaft**.

**Beispiel:**

```sql
BEGIN TRANSACTION;

INSERT INTO Customers (CustomerID, Name, Email) VALUES (3, 'Charlie', 'charlie@example.com');
UPDATE Products SET Price = Price * 1.1 WHERE Category = 'Electronics';

COMMIT;
```

**Erklärung:**

* Beide Anweisungen werden **dauerhaft gespeichert**.
* Vor COMMIT können Änderungen noch zurückgenommen werden.

---

## **4. ROLLBACK – Änderungen zurücknehmen**

**Definition:**
`ROLLBACK` macht alle Änderungen der aktuellen Transaktion seit dem letzten COMMIT **rückgängig**.

**Beispiel:**

```sql
BEGIN TRANSACTION;

INSERT INTO Customers (CustomerID, Name, Email) VALUES (4, 'David', 'david@example.com');
UPDATE Products SET Price = Price * 0.9 WHERE Category = 'Accessories';

ROLLBACK;
```

**Erklärung:**

* Änderungen werden **nicht gespeichert**.
* Ideal bei Fehlern oder falschen Eingaben.

---

## **5. Praktisches Szenario**

1. Benutzer erstellen:

```sql
CREATE USER analyst IDENTIFIED BY 'password';
```

2. Rechte vergeben:

```sql
GRANT SELECT, INSERT ON Customers TO analyst;
```

3. Benutzer führt Transaktion aus:

```sql
BEGIN TRANSACTION;
INSERT INTO Customers (CustomerID, Name, Email) VALUES (5, 'Eva', 'eva@example.com');
-- Fehler erkannt:
ROLLBACK;  -- alles rückgängig
```

4. Rechte wieder entziehen:

```sql
REVOKE INSERT ON Customers FROM analyst;
```

**Zusammenfassung:**

* **GRANT/REVOKE:** Zugriffsrechte steuern
* **COMMIT:** Änderungen dauerhaft speichern
* **ROLLBACK:** Änderungen rückgängig machen

---

Absolutely! Let’s go **step by step**. I’ll first explain **SQL Indexes and Query Optimization in English**, then provide the **German version**. I’ll include **practical examples** to clarify concepts.

---

# **SQL Indexes and Query Optimization**

---

## **1. SQL Indexes – English Version**

**Definition:**
An **index** in SQL is a database object that **improves the speed of data retrieval** from a table, similar to an index in a book. It does not store actual data but references the data's location in the table.

### **Types of Indexes:**

1. **Primary Index (Primary Key)**

   * Automatically created on primary keys.
   * Ensures uniqueness and fast lookup.

2. **Unique Index**

   * Prevents duplicate values in a column.

3. **Non-Unique Index**

   * Speeds up queries on columns that are frequently searched or filtered.

4. **Composite Index**

   * Index on multiple columns. Useful for queries that filter by more than one column.

### **Syntax to Create an Index**

```sql
-- Single column index
CREATE INDEX idx_customer_name ON Customers(Name);

-- Composite index
CREATE INDEX idx_customer_name_email ON Customers(Name, Email);
```

### **How Indexes Work**

* When a query uses a **WHERE**, **JOIN**, or **ORDER BY**, the database can **use the index** to locate rows faster instead of scanning the entire table (full table scan).
* Indexes improve **read operations** but slightly **slow down inserts, updates, and deletes** because the index must also be updated.

---

## **2. Query Optimization**

**Definition:**
Query optimization is the process by which the database **decides the most efficient way to execute a query**.

### **Key Concepts:**

1. **Execution Plan**

   * The database generates a plan showing how it will retrieve data (using indexes, joins, scans).
   * Use `EXPLAIN` (MySQL/PostgreSQL) or `EXPLAIN PLAN` (Oracle) to see the plan.

2. **Selectivity**

   * Indexes work best on columns with **high selectivity** (many unique values).
   * Low selectivity (few distinct values) may not benefit much.

3. **Covering Index**

   * An index that contains all columns needed by the query.
   * Database can answer the query **without accessing the table**.

4. **Query Rewrite**

   * Database optimizer may **rewrite queries** for better performance, e.g., join order, subquery flattening.

---

### **Practical Example**

```sql
-- Table Customers
SELECT * FROM Customers WHERE Name = 'Alice';

-- Without index: full table scan
-- With index on Name: direct lookup via idx_customer_name

-- Check execution plan
EXPLAIN SELECT * FROM Customers WHERE Name = 'Alice';
```

**Best Practices:**

* Index columns used in **WHERE**, **JOIN**, **ORDER BY**, **GROUP BY**.
* Avoid too many indexes on write-heavy tables.
* Monitor execution plans for slow queries.

---

## **3. Summary – English**

| Concept         | Purpose                                           |
| --------------- | ------------------------------------------------- |
| Index           | Speed up retrieval (like a book index)            |
| Primary Key     | Unique and automatically indexed                  |
| Unique Index    | Prevent duplicates                                |
| Composite Index | Optimizes queries on multiple columns             |
| Execution Plan  | Shows how the database executes a query           |
| Query Optimizer | Determines the fastest method for query execution |

---

# **SQL Indexes und Optimierung – Deutsch Version**

---

## **1. SQL-Indexe – Deutsch**

**Definition:**
Ein **Index** ist ein Datenbankobjekt, das **die Geschwindigkeit von Abfragen verbessert**, ähnlich einem Index in einem Buch.

* Speichert keine Daten selbst, sondern verweist auf die Position der Daten in der Tabelle.

### **Arten von Indexen:**

1. **Primärindex (Primary Key)**

   * Wird automatisch für Primärschlüssel erstellt.
   * Sorgt für Einzigartigkeit und schnellen Zugriff.

2. **Unique Index**

   * Verhindert doppelte Werte in einer Spalte.

3. **Non-Unique Index**

   * Beschleunigt Abfragen auf häufig gefilterten Spalten.

4. **Composite Index (Mehrspaltenindex)**

   * Index auf mehreren Spalten, nützlich bei Abfragen mit mehreren Filterbedingungen.

### **Syntax**

```sql
-- Einzelspalten-Index
CREATE INDEX idx_customer_name ON Customers(Name);

-- Mehrspalten-Index
CREATE INDEX idx_customer_name_email ON Customers(Name, Email);
```

### **Funktionsweise**

* Bei **WHERE**, **JOIN** oder **ORDER BY** kann die Datenbank **den Index verwenden**, um direkt auf die relevanten Zeilen zuzugreifen, statt die ganze Tabelle zu durchsuchen.
* Indexe verbessern **Lesegeschwindigkeit**, verlangsamen aber **INSERT, UPDATE, DELETE**, da der Index ebenfalls aktualisiert werden muss.

---

## **2. Abfrageoptimierung (Query Optimization)**

**Definition:**
Die Abfrageoptimierung ist der Prozess, bei dem die Datenbank **den effizientesten Weg zur Ausführung einer Abfrage bestimmt**.

### **Wichtige Konzepte:**

1. **Execution Plan (Ausführungsplan)**

   * Zeigt, wie die Datenbank die Abfrage ausführt (Index, Join, Scan).
   * `EXPLAIN` (MySQL/PostgreSQL) oder `EXPLAIN PLAN` (Oracle) verwenden.

2. **Selectivity (Selektivität)**

   * Indexe wirken am besten auf Spalten mit **hoher Selektivität** (viele verschiedene Werte).
   * Bei wenigen verschiedenen Werten weniger effektiv.

3. **Covering Index**

   * Ein Index, der **alle Spalten enthält, die für die Abfrage benötigt werden**.
   * Die Datenbank kann die Abfrage direkt aus dem Index beantworten.

4. **Query Rewrite**

   * Optimierer kann die Abfrage **umschreiben**, z. B. Join-Reihenfolge oder Subquery-Vereinfachung.

---

### **Praktisches Beispiel**

```sql
-- Tabelle Customers
SELECT * FROM Customers WHERE Name = 'Alice';

-- Ohne Index: vollständiger Tabellenscan
-- Mit Index auf Name: direkte Suche über idx_customer_name

-- Ausführungsplan prüfen
EXPLAIN SELECT * FROM Customers WHERE Name = 'Alice';
```

**Best Practices:**

* Indexiere Spalten, die in **WHERE**, **JOIN**, **ORDER BY**, **GROUP BY** verwendet werden.
* Vermeide zu viele Indexe auf schreibintensiven Tabellen.
* Prüfe langsame Abfragen mit dem **Execution Plan**.

---

## **3. Zusammenfassung – Deutsch**

| Konzept         | Zweck                                                 |
| --------------- | ----------------------------------------------------- |
| Index           | Beschleunigt Abfragen (wie Buchindex)                 |
| Primary Key     | Eindeutig, automatisch indexiert                      |
| Unique Index    | Verhindert Duplikate                                  |
| Composite Index | Optimiert Abfragen mit mehreren Spalten               |
| Execution Plan  | Zeigt, wie die Datenbank eine Abfrage ausführt        |
| Query Optimizer | Findet den schnellsten Weg zur Ausführung der Abfrage |

---


Absolutely! Let’s dive into **SQL Window Functions** with **practical examples and data** to make it clear. I’ll first explain the concept, then show examples you can run directly.

---

# **SQL Window Functions Tutorial**

---

## **1. What Are Window Functions?**

**Definition:**
Window Functions in SQL perform calculations **across a set of rows related to the current row**, while **keeping all rows** in the result. Unlike aggregate functions (`SUM`, `AVG`) that collapse rows, window functions **do not group rows**.

**Use Cases:**

* Ranking rows (`ROW_NUMBER`, `RANK`)
* Cumulative totals (`SUM`, `AVG`)
* Comparing rows (`LAG`, `LEAD`)
* First or last value in a group (`FIRST_VALUE`, `LAST_VALUE`)

**Syntax:**

```sql
FUNCTION_NAME() OVER (
    [PARTITION BY column]  -- groups rows
    [ORDER BY column]      -- defines order in the window
    [ROWS BETWEEN ...]     -- defines window frame (optional)
)
```

---

## **2. Sample Data**

Let’s use an **E-Commerce Orders table**:

| OrderID | Customer | Product  | Quantity | Price | OrderDate  |
| ------- | -------- | -------- | -------- | ----- | ---------- |
| 101     | Alice    | Laptop   | 1        | 1000  | 2025-01-01 |
| 102     | Alice    | Mouse    | 2        | 25    | 2025-01-05 |
| 103     | Alice    | Keyboard | 1        | 50    | 2025-01-10 |
| 104     | Bob      | Laptop   | 1        | 1000  | 2025-01-03 |
| 105     | Bob      | Mouse    | 1        | 25    | 2025-01-06 |

---

## **3. ROW_NUMBER() – Number rows in a group**

```sql
SELECT 
    Customer,
    OrderID,
    Product,
    ROW_NUMBER() OVER (PARTITION BY Customer ORDER BY OrderDate) AS RowNum
FROM Orders;
```

**Result:**

| Customer | OrderID | Product  | RowNum |
| -------- | ------- | -------- | ------ |
| Alice    | 101     | Laptop   | 1      |
| Alice    | 102     | Mouse    | 2      |
| Alice    | 103     | Keyboard | 3      |
| Bob      | 104     | Laptop   | 1      |
| Bob      | 105     | Mouse    | 2      |

**Explanation:**

* Each customer’s orders are numbered by date.

---

## **4. RANK() – Ranking rows with gaps**

```sql
SELECT
    Customer,
    OrderID,
    Price,
    RANK() OVER (PARTITION BY Customer ORDER BY Price DESC) AS RankPrice
FROM Orders;
```

**Result:**

| Customer | OrderID | Price | RankPrice |
| -------- | ------- | ----- | --------- |
| Alice    | 101     | 1000  | 1         |
| Alice    | 103     | 50    | 2         |
| Alice    | 102     | 25    | 3         |
| Bob      | 104     | 1000  | 1         |
| Bob      | 105     | 25    | 2         |

* Ties share the same rank, gaps appear in the numbering.

---

## **5. DENSE_RANK() – Ranking rows without gaps**

```sql
SELECT
    Customer,
    OrderID,
    Price,
    DENSE_RANK() OVER (PARTITION BY Customer ORDER BY Price DESC) AS DenseRank
FROM Orders;
```

* Works like `RANK()`, but no gaps in rank numbers.

---

## **6. SUM() as a window function – cumulative total**

```sql
SELECT
    Customer,
    OrderID,
    Price,
    SUM(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS CumulativeTotal
FROM Orders;
```

**Result:**

| Customer | OrderID | Price | CumulativeTotal |
| -------- | ------- | ----- | --------------- |
| Alice    | 101     | 1000  | 1000            |
| Alice    | 102     | 25    | 1025            |
| Alice    | 103     | 50    | 1075            |
| Bob      | 104     | 1000  | 1000            |
| Bob      | 105     | 25    | 1025            |

---

## **7. LAG() and LEAD() – Compare previous/next row**

```sql
SELECT
    Customer,
    OrderID,
    Price,
    LAG(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS PreviousPrice,
    LEAD(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS NextPrice
FROM Orders;
```

**Explanation:**

* `LAG()` → value of previous row
* `LEAD()` → value of next row
* Useful to calculate differences or trends.

---

## **8. FIRST_VALUE() and LAST_VALUE() – First and last in a group**

```sql
SELECT
    Customer,
    OrderID,
    Price,
    FIRST_VALUE(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS FirstOrderPrice,
    LAST_VALUE(Price) OVER (PARTITION BY Customer ORDER BY OrderDate 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS LastOrderPrice
FROM Orders;
```

* `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING` ensures LAST_VALUE() considers the full partition.

---

## **9. Practical Use Case**

**Goal:** Find each customer’s cumulative spending and previous order price.

```sql
SELECT
    Customer,
    OrderID,
    Price,
    SUM(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS CumulativeTotal,
    LAG(Price) OVER (PARTITION BY Customer ORDER BY OrderDate) AS PreviousOrderPrice
FROM Orders;
```

**Result:**

| Customer | OrderID | Price | CumulativeTotal | PreviousOrderPrice |
| -------- | ------- | ----- | --------------- | ------------------ |
| Alice    | 101     | 1000  | 1000            | NULL               |
| Alice    | 102     | 25    | 1025            | 1000               |
| Alice    | 103     | 50    | 1075            | 25                 |
| Bob      | 104     | 1000  | 1000            | NULL               |
| Bob      | 105     | 25    | 1025            | 1000               |

---

## ✅ **Key Points**

* Window functions **do not collapse rows**.
* Use `PARTITION BY` to define the group.
* Use `ORDER BY` to define sequence inside the window.
* Useful for **ranking, cumulative metrics, comparisons, first/last values**.

---
Absolutely — here is a **complete, detailed SQL tutorial** covering:

* **WITH (CTE)**
* **CASE expressions**
* **COALESCE**
* **SQL Functions (built-in + user-defined)**
* **Full examples with explanation**
* **Industry-style use cases**

Written **clearly, step-by-step**, for real understanding.

---

# ✅ **SQL Tutorial: WITH (CTE), CASE, COALESCE, and SQL Functions**

---

# **1. WITH (CTE) — Common Table Expressions**

A **CTE** is a temporary *named result set* you reference inside a query.

### ✔ Why Use CTEs?

* Makes complex queries readable
* Allows you to reference data **multiple times**
* Allows **recursive queries**
* Replaces nested subqueries

---

## **1.1 Basic CTE Example**

### **Problem:**

Find customers who spent more than **$1000 total**.

### **Data (Orders):**

| OrderID | Customer | Amount |
| ------- | -------- | ------ |
| 1       | Alice    | 500    |
| 2       | Alice    | 700    |
| 3       | Bob      | 200    |
| 4       | Bob      | 300    |

---

### **CTE Query**

```sql
WITH CustomerTotals AS (
    SELECT 
        Customer,
        SUM(Amount) AS TotalSpent
    FROM Orders
    GROUP BY Customer
)
SELECT *
FROM CustomerTotals
WHERE TotalSpent > 1000;
```

### **Explanation:**

* The CTE (`CustomerTotals`) calculates total spending per customer.
* The outer query filters results.

---

## **1.2 Multiple CTEs**

```sql
WITH Sales AS (
    SELECT Customer, SUM(Amount) AS TotalSales
    FROM Orders
    GROUP BY Customer
),
HighValue AS (
    SELECT Customer, TotalSales
    FROM Sales
    WHERE TotalSales > 1000
)
SELECT * FROM HighValue;
```

---

## **1.3 Recursive CTE Example**

Used for hierarchical data.

### Example: Generate numbers 1 to 5

```sql
WITH RECURSIVE Numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM Numbers
    WHERE n < 5
)
SELECT * FROM Numbers;
```

---

# **2. CASE Expression**

`CASE` is SQL’s version of **if/else logic**.

---

## **2.1 Simple CASE Example**

```sql
SELECT 
   Customer,
   Amount,
   CASE 
       WHEN Amount > 500 THEN 'High'
       WHEN Amount > 200 THEN 'Medium'
       ELSE 'Low'
   END AS OrderCategory
FROM Orders;
```

### Result:

| Customer | Amount | OrderCategory |
| -------- | ------ | ------------- |
| Alice    | 700    | High          |
| Bob      | 200    | Low           |

---

## **2.2 CASE with Aggregates**

Calculate revenue by category:

```sql
SELECT
    SUM(CASE WHEN Amount > 500 THEN Amount END) AS HighOrders,
    SUM(CASE WHEN Amount BETWEEN 200 AND 500 THEN Amount END) AS MediumOrders,
    SUM(CASE WHEN Amount < 200 THEN Amount END) AS LowOrders
FROM Orders;
```

---

## **2.3 CASE inside ORDER BY**

Sort customers by importance:

```sql
SELECT Customer, TotalSpent
FROM CustomerTotals
ORDER BY 
  CASE 
     WHEN TotalSpent > 5000 THEN 1
     WHEN TotalSpent > 2000 THEN 2
     ELSE 3
  END;
```

---

# **3. COALESCE — Replace NULLs**

`COALESCE(a, b, c...)` returns the **first non-null** value.

---

## **3.1 Basic Example**

```sql
SELECT 
    Customer,
    COALESCE(PhoneNumber, 'No Phone Provided') AS CleanPhone
FROM Customers;
```

---

## **3.2 With Calculations**

```sql
SELECT
    Price * COALESCE(Quantity, 1) AS Total
FROM Items;
```

### Explanation:

If `Quantity` is NULL → use **1**.

---

## **3.3 Multiple COALESCE Levels**

```sql
SELECT 
    COALESCE(HomePhone, WorkPhone, MobilePhone, 'No Contact') AS BestContact
FROM Users;
```

---

# **4. SQL Functions**

SQL has **built-in functions** + **user-defined functions (UDFs)**.

---

# **4.1 Built-in SQL Functions**

---

## **String Functions**

```sql
SELECT 
   UPPER(CustomerName),
   LOWER(CustomerName),
   CONCAT(FirstName, ' ', LastName) AS FullName,
   LENGTH(CustomerName)
FROM Customers;
```

---

## **Date Functions**

```sql
SELECT 
    OrderID,
    OrderDate,
    YEAR(OrderDate) AS OrderYear,
    MONTH(OrderDate) AS OrderMonth,
    DATEADD(day, 7, OrderDate) AS DeliveryDate
FROM Orders;
```

---

## **Math Functions**

```sql
SELECT 
   Price,
   ROUND(Price, 2),
   CEILING(Price),
   FLOOR(Price)
FROM Products;
```

---

# **4.2 User-Defined Functions (UDF)**

---

## **4.2.1 Scalar Function (returns 1 value)**

### Example: Tax calculation

```sql
CREATE FUNCTION CalculateTax (@amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN @amount * 0.15
END;
```

**Use it:**

```sql
SELECT 
    Amount,
    dbo.CalculateTax(Amount) AS Tax
FROM Orders;
```

---

## **4.2.2 Table-Valued Function**

```sql
CREATE FUNCTION OrdersAboveAmount (@minAmount DECIMAL(10,2))
RETURNS TABLE
AS
RETURN (
    SELECT * FROM Orders WHERE Amount > @minAmount
);
```

**Use it:**

```sql
SELECT * FROM dbo.OrdersAboveAmount(500);
```

---

# **5. Combined Example — Using CTE + CASE + COALESCE + Function**

### **Goal:**

Create a customer spending report that:

* Calculates total sales (CTE)
* Categorizes customers (CASE)
* Replaces missing phone numbers (COALESCE)
* Adds a tax calculation (UDF)

---

## **Step 1 — Create UDF**

```sql
CREATE FUNCTION AddTax (@amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN @amount * 1.15;
END;
```

---

## **Step 2 — CTE**

```sql
WITH CustSales AS (
    SELECT 
        Customer,
        SUM(Amount) AS TotalSpent
    FROM Orders
    GROUP BY Customer
)
SELECT 
    c.Customer,
    COALESCE(c.Phone, 'No Phone') AS Phone,
    s.TotalSpent,
    dbo.AddTax(s.TotalSpent) AS TotalWithTax,
    CASE
        WHEN s.TotalSpent > 5000 THEN 'VIP'
        WHEN s.TotalSpent > 2000 THEN 'Gold'
        WHEN s.TotalSpent > 1000 THEN 'Silver'
        ELSE 'Bronze'
    END AS Category
FROM Customers c
JOIN CustSales s ON c.Customer = s.Customer;
```

---

# 🎉 **Summary Table**

| Feature       | Purpose                    | Example                      |
| ------------- | -------------------------- | ---------------------------- |
| **CTE**       | Create reusable temp table | `WITH x AS (...) SELECT ...` |
| **CASE**      | Conditional logic          | `CASE WHEN...`               |
| **COALESCE**  | Replace NULLs              | `COALESCE(x, 'default')`     |
| **Functions** | Custom logic               | `CREATE FUNCTION ...`        |

---

If you want, I can also create:

✅ A **German version**
✅ An **SQL practice workbook**
✅ A **database schema** to test all examples

Would you like any of these?

Gerne! Hier ist das **komplette SQL-Tutorial über WITH (CTE), CASE, COALESCE und SQL-Funktionen – vollständig ins Deutsche übersetzt**, mit ausführlichen Erklärungen und praktischen Beispielen.

---

# 🇩🇪 **SQL-Tutorial: WITH (CTE), CASE, COALESCE und SQL-Funktionen**

Dieses Tutorial behandelt:

* **WITH (Common Table Expressions / CTEs)**
* **CASE-Ausdrücke**
* **COALESCE zum Umgang mit NULL**
* **SQL-Funktionen (eingebaute + benutzerdefinierte Funktionen)**
* **Vollständige Praxisbeispiele**

---

# **1. WITH (CTE) – Common Table Expressions**

Eine **CTE** ist ein *benannter temporärer Ergebnissatz*, den man in einer Abfrage wie eine Tabelle verwenden kann.

### ✔ Vorteile einer CTE:

* Macht komplexe Queries viel lesbarer
* Kann mehrfach verwendet werden
* Unterstützt **rekursive Abfragen**
* Ersetzt verschachtelte Subqueries

---

## **1.1 Einfaches CTE Beispiel**

### 📌 Aufgabe:

Finde Kunden, die insgesamt **mehr als 1000 €** ausgegeben haben.

### Beispieldaten (Orders):

| OrderID | Customer | Amount |
| ------- | -------- | ------ |
| 1       | Alice    | 500    |
| 2       | Alice    | 700    |
| 3       | Bob      | 200    |
| 4       | Bob      | 300    |

---

### **CTE-Abfrage**

```sql
WITH CustomerTotals AS (
    SELECT 
        Customer,
        SUM(Amount) AS TotalSpent
    FROM Orders
    GROUP BY Customer
)
SELECT *
FROM CustomerTotals
WHERE TotalSpent > 1000;
```

🔍 **Erklärung:**

* Die CTE `CustomerTotals` berechnet zunächst die Gesamtausgaben pro Kunde.
* Die Hauptabfrage filtert Kunden über 1000 €.

---

## **1.2 Mehrere CTEs**

```sql
WITH Sales AS (
    SELECT Customer, SUM(Amount) AS TotalSales
    FROM Orders
    GROUP BY Customer
),
HighValue AS (
    SELECT Customer, TotalSales
    FROM Sales
    WHERE TotalSales > 1000
)
SELECT * FROM HighValue;
```

---

## **1.3 Rekursive CTE (Beispiel)**

Beispiel: Zahlen von 1 bis 5 generieren.

```sql
WITH RECURSIVE Numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM Numbers
    WHERE n < 5
)
SELECT * FROM Numbers;
```

---

# **2. CASE-Ausdruck**

`CASE` ist SQLs Version von **IF/ELSE**-Logik.

---

## **2.1 Einfaches CASE Beispiel**

```sql
SELECT 
   Customer,
   Amount,
   CASE 
       WHEN Amount > 500 THEN 'High'
       WHEN Amount > 200 THEN 'Medium'
       ELSE 'Low'
   END AS OrderCategory
FROM Orders;
```

### Ergebnis:

| Customer | Amount | OrderCategory |
| -------- | ------ | ------------- |
| Alice    | 700    | High          |
| Bob      | 200    | Low           |

---

## **2.2 CASE mit Aggregationen**

```sql
SELECT
    SUM(CASE WHEN Amount > 500 THEN Amount END) AS HighOrders,
    SUM(CASE WHEN Amount BETWEEN 200 AND 500 THEN Amount END) AS MediumOrders,
    SUM(CASE WHEN Amount < 200 THEN Amount END) AS LowOrders
FROM Orders;
```

---

## **2.3 CASE in ORDER BY**

Kunden nach Wichtigkeit sortieren:

```sql
SELECT Customer, TotalSpent
FROM CustomerTotals
ORDER BY 
  CASE 
     WHEN TotalSpent > 5000 THEN 1
     WHEN TotalSpent > 2000 THEN 2
     ELSE 3
  END;
```

---

# **3. COALESCE – Umgang mit NULL-Werten**

`COALESCE(a, b, c...)` gibt **den ersten Nicht-NULL Wert** zurück.

---

## **3.1 Einfaches Beispiel**

```sql
SELECT 
    Customer,
    COALESCE(PhoneNumber, 'Keine Telefonnummer') AS CleanPhone
FROM Customers;
```

---

## **3.2 Beispiel in Berechnungen**

```sql
SELECT
    Price * COALESCE(Quantity, 1) AS Total
FROM Items;
```

Erklärung:
Wenn `Quantity` NULL ist → verwende **1**.

---

## **3.3 Mehrstufiges COALESCE**

```sql
SELECT 
    COALESCE(HomePhone, WorkPhone, MobilePhone, 'Keine Kontaktdaten') AS BestContact
FROM Users;
```

---

# **4. SQL-Funktionen**

---

# **4.1 Eingebaute SQL-Funktionen**

---

## **String-Funktionen**

```sql
SELECT 
   UPPER(CustomerName),
   LOWER(CustomerName),
   CONCAT(FirstName, ' ', LastName) AS FullName,
   LENGTH(CustomerName)
FROM Customers;
```

---

## **Datums-Funktionen**

```sql
SELECT 
    OrderID,
    OrderDate,
    YEAR(OrderDate) AS OrderYear,
    MONTH(OrderDate) AS OrderMonth,
    DATEADD(day, 7, OrderDate) AS DeliveryDate
FROM Orders;
```

---

## **Mathematische Funktionen**

```sql
SELECT 
   Price,
   ROUND(Price, 2),
   CEILING(Price),
   FLOOR(Price)
FROM Products;
```

---

# **4.2 Benutzerdefinierte SQL-Funktionen (UDFs)**

---

## **4.2.1 Skalarfunktion (gibt einen einzelnen Wert zurück)**

Beispiel: Steuerberechnung

```sql
CREATE FUNCTION CalculateTax (@amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN @amount * 0.15
END;
```

**Verwendung:**

```sql
SELECT 
    Amount,
    dbo.CalculateTax(Amount) AS Tax
FROM Orders;
```

---

## **4.2.2 Table-Valued Function**

```sql
CREATE FUNCTION OrdersAboveAmount (@minAmount DECIMAL(10,2))
RETURNS TABLE
AS
RETURN (
    SELECT * FROM Orders WHERE Amount > @minAmount
);
```

**Verwendung:**

```sql
SELECT * FROM dbo.OrdersAboveAmount(500);
```

---

# **5. Kombiniertes Beispiel: CTE + CASE + COALESCE + Funktion**

Ziel: Erstelle einen Kundenreport mit:

* Gesamtausgaben (CTE)
* Kundenkategorisierung (CASE)
* Ersatz von NULL-Telefonnummern (COALESCE)
* Steuerfunktion (UDF)

---

## **Schritt 1 – UDF erstellen**

```sql
CREATE FUNCTION AddTax (@amount DECIMAL(10,2))
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN @amount * 1.15;
END;
```

---

## **Schritt 2 – CTE nutzen**

```sql
WITH CustSales AS (
    SELECT 
        Customer,
        SUM(Amount) AS TotalSpent
    FROM Orders
    GROUP BY Customer
)
SELECT 
    c.Customer,
    COALESCE(c.Phone, 'Keine Nummer') AS Phone,
    s.TotalSpent,
    dbo.AddTax(s.TotalSpent) AS TotalMitSteuer,
    CASE
        WHEN s.TotalSpent > 5000 THEN 'VIP'
        WHEN s.TotalSpent > 2000 THEN 'Gold'
        WHEN s.TotalSpent > 1000 THEN 'Silber'
        ELSE 'Bronze'
    END AS Kategorie
FROM Customers c
JOIN CustSales s ON c.Customer = s.Customer;
```

---

# 🎉 **Zusammenfassung**

| SQL-Feature    | Zweck                                | Beispiel                 |
| -------------- | ------------------------------------ | ------------------------ |
| **CTE (WITH)** | Temporäre Tabelle zur Strukturierung | `WITH t AS (...)`        |
| **CASE**       | Bedingungen                          | `CASE WHEN ...`          |
| **COALESCE**   | NULL ersetzen                        | `COALESCE(x, 'default')` |
| **Funktionen** | Wiederverwendbare Logik              | `CREATE FUNCTION ...`    |

---


Below is a **complete, detailed tutorial** on **SQL Database Schema Design** and **SQL Views**, written in clear English, with real-world examples.

This is a **professional-level** guide suitable for beginners, intermediates, and advanced learners.

---

# ⭐ **SQL Database Schema Design & SQL Views — Complete Tutorial**

---

# **1. What Is a Database Schema?**

A **database schema** defines the structure of a database.
It describes:

* **tables**
* **columns**
* **data types**
* **primary keys**
* **foreign keys**
* **relationships**
* **constraints**
* **indexes**

Think of the schema as the **blueprint** of your database.

---

# **2. Core Concepts in Schema Design**

---

## **2.1 Tables**

A table stores data in rows and columns.

Example:

```sql
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Email VARCHAR(150),
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## **2.2 Data Types**

Choose types carefully:

| Type       | Example    |
| ---------- | ---------- |
| INT        | 1, 2, 3    |
| VARCHAR(n) | “John Doe” |
| DATE       | 2025-01-01 |
| DECIMAL    | 10.99      |
| BOOLEAN    | TRUE/FALSE |

Proper data types improve performance and reduce storage.

---

## **2.3 Keys**

### **Primary Key (PK)**

Uniquely identifies each row.

```sql
CustomerID INT PRIMARY KEY
```

### **Foreign Key (FK)**

Links a row to another table.

```sql
CustomerID INT REFERENCES Customers(CustomerID)
```

### **Composite Key**

Two or more columns form the key.

```sql
PRIMARY KEY (OrderID, ProductID)
```

---

## **2.4 Constraints**

Constraints enforce rules.

| Constraint  | Purpose                |
| ----------- | ---------------------- |
| PRIMARY KEY | Unique row             |
| FOREIGN KEY | Relationship integrity |
| UNIQUE      | No duplicates          |
| NOT NULL    | Must have value        |
| CHECK       | Apply conditions       |

Example:

```sql
CHECK (Quantity > 0)
```

---

## **2.5 Relationships**

### **1-to-1**

One row in Table A ↔ one row in Table B

### **1-to-Many** (most common)

One Customer → many Orders

### **Many-to-Many**

Solved by **junction table**
Example: products in orders → OrderItems table

---

# **3. Normalization**

Normalization is the process of organizing data to reduce duplication.

---

## **3.1 First Normal Form (1NF)**

* No repeating groups
* Atomic values only

Bad:

| Customer | PhoneNumbers |
| -------- | ------------ |
| Alice    | 123, 456     |

Good:

| Customer | Phone |
| -------- | ----- |
| Alice    | 123   |
| Alice    | 456   |

---

## **3.2 Second Normal Form (2NF)**

* In 1NF
* All non-key attributes depend on the whole key

---

## **3.3 Third Normal Form (3NF)**

* In 2NF
* No transitive dependencies

Bad:

```
Orders(OrderID, CustomerID, CustomerName)
```

Good:

```
Customers(CustomerID, CustomerName)
Orders(OrderID, CustomerID)
```

---

# **4. Example: Full E-Commerce Database Schema**

Below is a clean, normalized schema.

---

## **4.1 Customers**

```sql
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(100),
    LastName VARCHAR(100),
    Email VARCHAR(150) UNIQUE,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## **4.2 Products**

```sql
CREATE TABLE Products (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    ProductName VARCHAR(200),
    Category VARCHAR(100),
    Price DECIMAL(10,2),
    Stock INT CHECK(Stock >= 0)
);
```

---

## **4.3 Orders**

```sql
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT,
    OrderDate DATE,
    Status VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);
```

---

## **4.4 OrderItems** (Many-to-Many)

```sql
CREATE TABLE OrderItems (
    OrderID INT,
    ProductID INT,
    Quantity INT CHECK (Quantity > 0),
    Price DECIMAL(10,2),
    PRIMARY KEY (OrderID, ProductID),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);
```

---

## **4.5 Payments**

```sql
CREATE TABLE Payments (
    PaymentID INT PRIMARY KEY AUTO_INCREMENT,
    OrderID INT,
    Amount DECIMAL(10,2),
    PaymentDate DATETIME,
    PaymentMethod VARCHAR(100),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);
```

---

# **5. SQL Views**

A **View** is a saved SELECT query that behaves like a virtual table.

### ✔ Uses of Views:

* Simplify complex queries
* Provide controlled access to data
* Improve readability
* Encapsulate logic
* Mask sensitive data

Views **do not store data** (except materialized views).

---

# **6. Creating SQL Views**

---

## **6.1 Simple View**

```sql
CREATE VIEW CustomerList AS
SELECT
    CustomerID,
    CONCAT(FirstName, ' ', LastName) AS FullName,
    Email
FROM Customers;
```

Use it like a table:

```sql
SELECT * FROM CustomerList;
```

---

## **6.2 View with JOINs**

```sql
CREATE VIEW OrderSummary AS
SELECT 
    o.OrderID,
    c.FirstName,
    c.LastName,
    o.OrderDate,
    SUM(oi.Quantity * oi.Price) AS TotalAmount
FROM Orders o
JOIN Customers c ON o.CustomerID = c.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
GROUP BY o.OrderID, c.FirstName, c.LastName, o.OrderDate;
```

Query it:

```sql
SELECT * FROM OrderSummary WHERE TotalAmount > 100;
```

---

## **6.3 View With Filter Logic**

Useful for applications:

```sql
CREATE VIEW ActiveOrders AS
SELECT *
FROM Orders
WHERE Status = 'Active';
```

---

## **6.4 View for Security (Masking Data)**

```sql
CREATE VIEW PublicCustomers AS
SELECT
    CustomerID,
    CONCAT(LEFT(Email, 3), '***') AS MaskedEmail
FROM Customers;
```

---

# **7. Materialized Views (If Supported)**

Materialized views **store the data**, unlike regular views.

Used for:

* heavy aggregations
* expensive joins
* analytics workloads

Example (Oracle/Postgres):

```sql
CREATE MATERIALIZED VIEW SalesSummary AS
SELECT 
    ProductID,
    SUM(Quantity) AS TotalQty
FROM OrderItems
GROUP BY ProductID;
```

---

# **8. Schema Design Best Practices**

---

## **8.1 Use normalization to avoid duplication**

But…

## **8.2 Know when to denormalize**

For performance in analytical systems:

* add summary tables
* aggregate data
* caching

---

## **8.3 Use proper data types**

Avoid:

* VARCHAR(2000) for phone numbers
* Storing dates as VARCHAR
* Storing numeric values as text

---

## **8.4 Always define primary keys**

Either:

* auto-increment integers
* UUIDs

---

## **8.5 Use foreign keys**

Prevents orphan data.

---

## **8.6 Index important columns**

Index columns used in:

* WHERE
* JOIN
* ORDER BY
* GROUP BY

---

## **8.7 Add CHECK constraints**

Prevent invalid data at the database level.

---

## **8.8 Use naming conventions**

Examples:

* `tbl_Customers`
* `dimCustomer` (data warehouse)
* `OrderItems` instead of `oi`

---

# **9. Putting It All Together — Practical Example**

### **Goal:**

Create a report showing each customer’s total spending.

---

## **Step 1 — Create View**

```sql
CREATE VIEW CustomerSales AS
SELECT
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS Customer,
    SUM(oi.Quantity * oi.Price) AS TotalSpent
FROM Customers c
JOIN Orders o ON c.CustomerID = o.CustomerID
JOIN OrderItems oi ON o.OrderID = oi.OrderID
GROUP BY c.CustomerID, c.FirstName, c.LastName;
```

---

## **Step 2 — Query the view**

```sql
SELECT *
FROM CustomerSales
WHERE TotalSpent > 500;
```

---

# 🎉 **You now have a complete understanding of:**

✔ How to design SQL database schemas
✔ Best practices for table structure
✔ Primary & foreign keys
✔ Normalization
✔ SQL Views (simple, join-based, filtered, secure)
✔ Materialized views
✔ Real-world e-commerce schema

---
Natürlich — hier ist das **komplette Tutorial über SQL-Datenbankschemata & SQL-Views in deutscher Sprache**, vollständig übersetzt und leicht verständlich, mit Praxisbeispielen.

---

# 🇩🇪 **SQL-Datenbankschema-Design & SQL-Views — Vollständiges Tutorial**

---

# **1. Was ist ein Datenbankschema?**

Ein **Datenbankschema** beschreibt die **Struktur** einer Datenbank.
Es definiert:

* Tabellen
* Spalten
* Datentypen
* Primärschlüssel
* Fremdschlüssel
* Beziehungen
* Einschränkungen (Constraints)
* Indexe

Das Schema ist der **Bauplan** deiner Datenbank.

---

# **2. Zentrale Konzepte im Schema-Design**

---

## **2.1 Tabellen**

Eine Tabelle speichert Daten in Zeilen und Spalten.

Beispiel:

```sql
CREATE TABLE Kunden (
    KundeID INT PRIMARY KEY,
    Vorname VARCHAR(100),
    Nachname VARCHAR(100),
    Email VARCHAR(150),
    ErstelltAm DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## **2.2 Datentypen**

Wähle passende Datentypen:

| Typ        | Beispiel         |
| ---------- | ---------------- |
| INT        | 1, 2, 3          |
| VARCHAR(n) | „Max Mustermann“ |
| DATE       | 2025-01-01       |
| DECIMAL    | 10.99            |
| BOOLEAN    | TRUE/FALSE       |

Gute Datentypen = bessere Performance + weniger Speicher.

---

## **2.3 Schlüssel**

### **Primärschlüssel (PK)**

Eindeutiger Bezeichner einer Zeile.

```sql
KundeID INT PRIMARY KEY
```

### **Fremdschlüssel (FK)**

Verknüpft Tabellen miteinander.

```sql
KundeID INT REFERENCES Kunden(KundeID)
```

### **Zusammengesetzter Schlüssel**

```sql
PRIMARY KEY (BestellID, ProduktID)
```

---

## **2.4 Constraints (Einschränkungen)**

| Constraint  | Beschreibung                  |
| ----------- | ----------------------------- |
| PRIMARY KEY | eindeutiger Schlüssel         |
| FOREIGN KEY | referenzielle Integrität      |
| UNIQUE      | keine Duplikate               |
| NOT NULL    | Wert erforderlich             |
| CHECK       | Bedingung muss erfüllt werden |

Beispiel:

```sql
CHECK (Menge > 0)
```

---

## **2.5 Beziehungen zwischen Tabellen**

### **1:1**

Ein Kunde ↔ ein Kundenprofil

### **1:N (häufigste)**

Ein Kundenkonto → viele Bestellungen

### **N:M**

Wird über eine **Zwischentabelle** gelöst
Beispiel: Bestellungen enthalten viele Produkte
Zwischentabelle: **BestellPositionen**

---

# **3. Normalisierung**

Ziel: Datenredundanz vermeiden.

---

## **3.1 Erste Normalform (1NF)**

* keine wiederholenden Gruppen
* atomare Werte

Schlecht:

| Kunde | Telefonnummern |
| ----- | -------------- |
| Max   | 123, 456       |

Gut:

| Kunde | Telefonnummer |
| ----- | ------------- |
| Max   | 123           |
| Max   | 456           |

---

## **3.2 Zweite Normalform (2NF)**

* 1NF erfüllt
* Attribute hängen vom vollständigen Primärschlüssel ab

---

## **3.3 Dritte Normalform (3NF)**

* keine transitiven Abhängigkeiten

Schlecht:

```
Bestellung(BestellID, KundeID, KundenName)
```

Gut:

```
Kunden(KundeID, KundenName)
Bestellung(BestellID, KundeID)
```

---

# **4. Beispiel: E-Commerce-Datenbankschema**

---

## **4.1 Kunden**

```sql
CREATE TABLE Kunden (
    KundeID INT PRIMARY KEY AUTO_INCREMENT,
    Vorname VARCHAR(100),
    Nachname VARCHAR(100),
    Email VARCHAR(150) UNIQUE,
    ErstelltAm DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## **4.2 Produkte**

```sql
CREATE TABLE Produkte (
    ProduktID INT PRIMARY KEY AUTO_INCREMENT,
    ProduktName VARCHAR(200),
    Kategorie VARCHAR(100),
    Preis DECIMAL(10,2),
    Bestand INT CHECK(Bestand >= 0)
);
```

---

## **4.3 Bestellungen**

```sql
CREATE TABLE Bestellungen (
    BestellID INT PRIMARY KEY AUTO_INCREMENT,
    KundeID INT,
    Bestelldatum DATE,
    Status VARCHAR(50),
    FOREIGN KEY (KundeID) REFERENCES Kunden(KundeID)
);
```

---

## **4.4 BestellPositionen** (N:M)

```sql
CREATE TABLE BestellPositionen (
    BestellID INT,
    ProduktID INT,
    Menge INT CHECK (Menge > 0),
    Preis DECIMAL(10,2),
    PRIMARY KEY (BestellID, ProduktID),
    FOREIGN KEY (BestellID) REFERENCES Bestellungen(BestellID),
    FOREIGN KEY (ProduktID) REFERENCES Produkte(ProduktID)
);
```

---

## **4.5 Zahlungen**

```sql
CREATE TABLE Zahlungen (
    ZahlungID INT PRIMARY KEY AUTO_INCREMENT,
    BestellID INT,
    Betrag DECIMAL(10,2),
    Zahlungsdatum DATETIME,
    Zahlungsmethode VARCHAR(100),
    FOREIGN KEY (BestellID) REFERENCES Bestellungen(BestellID)
);
```

---

# **5. SQL Views (Sichten)**

Eine **View** ist eine gespeicherte SELECT-Abfrage, die wie eine virtuelle Tabelle wirkt.

### Vorteile:

✔ vereinfacht komplexe Abfragen
✔ Sicherheitslayer (z.B. Datenmaskierung)
✔ konsistente Reports
✔ weniger Duplikation

Views speichern **keine Daten**, außer *materialisierte Views*.

---

# **6. Views erstellen**

---

## **6.1 Einfache View**

```sql
CREATE VIEW KundenListe AS
SELECT
    KundeID,
    CONCAT(Vorname, ' ', Nachname) AS Vollname,
    Email
FROM Kunden;
```

Aufruf:

```sql
SELECT * FROM KundenListe;
```

---

## **6.2 View mit JOIN**

```sql
CREATE VIEW BestellÜbersicht AS
SELECT
    b.BestellID,
    k.Vorname,
    k.Nachname,
    b.Bestelldatum,
    SUM(bp.Menge * bp.Preis) AS Gesamtbetrag
FROM Bestellungen b
JOIN Kunden k ON b.KundeID = k.KundeID
JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
GROUP BY b.BestellID, k.Vorname, k.Nachname, b.Bestelldatum;
```

---

## **6.3 View zur Filterung**

```sql
CREATE VIEW AktiveBestellungen AS
SELECT *
FROM Bestellungen
WHERE Status = 'Aktiv';
```

---

## **6.4 View für Datensicherheit**

```sql
CREATE VIEW KundenÖffentlich AS
SELECT
    KundeID,
    CONCAT(LEFT(Email, 3), '***') AS MaskierteEmail
FROM Kunden;
```

---

# **7. Materialisierte Views (sofern DB unterstützt)**

Materialisierte Views speichern das Ergebnis auf der Festplatte.

Beispiel (Postgres):

```sql
CREATE MATERIALIZED VIEW VerkaufsStatistik AS
SELECT
    ProduktID,
    SUM(Menge) AS GesamtMenge
FROM BestellPositionen
GROUP BY ProduktID;
```

---

# **8. Best Practices im Schema-Design**

✔ Normalisieren — aber
✔ für Analytik auch manchmal denormalisieren
✔ Immer PRIMARY KEY definieren
✔ FOREIGN KEYs nutzen
✔ sinnvolle Datentypen wählen
✔ Indexe auf häufig verwendete Spalten
✔ CHECK Constraints nutzen
✔ konsistente Namenskonventionen

---

# **9. Komplettes Praxisbeispiel**

## Aufgabe

Erstelle einen Kunden-Umsatzreport.

---

### **View erstellen**

```sql
CREATE VIEW KundenUmsatz AS
SELECT
    k.KundeID,
    CONCAT(k.Vorname, ' ', k.Nachname) AS Kunde,
    SUM(bp.Menge * bp.Preis) AS GesamtUmsatz
FROM Kunden k
JOIN Bestellungen b ON k.KundeID = b.KundeID
JOIN BestellPositionen bp ON b.BestellID = bp.BestellID
GROUP BY k.KundeID, k.Vorname, k.Nachname;
```

### **View abfragen**

```sql
SELECT *
FROM KundenUmsatz
WHERE GesamtUmsatz > 500;
```

---

# 🎉 **Du hast jetzt gelernt:**

✔ Datenbankschemas erstellen
✔ Tabellen, Schlüssel & Beziehungen modellieren
✔ Normalformen verstehen
✔ E-Commerce-Schema aufbauen
✔ SQL-Views erstellen
✔ materialisierte Views nutzen
✔ Best Practices im Datenbankdesign

---



