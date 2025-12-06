import pandas as pd
import duckdb

df = pd.DataFrame({
    'product': ['A','A','B','B'],
    'amount': [10,20,15,25]
})



result = duckdb.query("""
    SELECT
        product,
        amount,
        ROW_NUMBER() OVER (PARTITION BY product ORDER BY amount) AS row_num,
        LAG(amount) OVER (PARTITION BY product ORDER BY amount) AS lag_val,
        LEAD(amount) OVER (PARTITION BY product ORDER BY amount) AS lead_val,
        SUM(amount) OVER (PARTITION BY product) AS total_per_product,
        DeNSE_RANK() OVER (PARTITION BY product ORDER BY amount) AS dense_rank_val
    FROM df
""").to_df()

#print(result)


result= duckdb.query("""
    SELECT
        product,
        max(amount) AS max_amount,
        min(amount) AS min_amount,
        avg(amount) AS avg_amount,
        sum(amount) AS total_amount
    FROM df
    GROUP BY product
    HAVING sum(amount) > 20
""").to_df()
#print(result)


customers = pd.DataFrame({
    'customer_id': [1, 2, 3],
    'name': ['John', 'Alice', 'Bob']
})

orders = pd.DataFrame({
    'order_id': [101, 102, 103, 104],
    'customer_id': [1, 1, 2, 4],
    'amount': [50, 75, 100, 200]
})
result = duckdb.query("""
    SELECT 
        c.customer_id,
        c.name,
        o.order_id,
        o.amount
    FROM customers c
    LEFT JOIN orders o
        ON c.customer_id = o.customer_id
""").to_df()
print(result)