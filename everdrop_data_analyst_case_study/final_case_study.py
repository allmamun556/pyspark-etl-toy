# %%
# ============================================================
# TASK 1 — STATISTICS
# ============================================================

# Given values from the task description:
P_cancel = 0.24                 # Base cancellation rate
FPR = 0.04                      # False positive rate
FNR = 0.00                      # False negative rate
loss_per_cancel = 10.0          # €10 loss per cancellation
insurance_cost = 8.5            # €8.5 insurance per customer

# True Positive Rate (sensitivity)
TPR = 1 - FNR   # = 1 because FNR = 0


# ============================================================
# 1(a) — Probability customer cancels GIVEN model predicts cancellation
# ============================================================

# Bayes numerator:
numerator = TPR * P_cancel

# Probability the model predicts cancellation at all:
P_model_cancel = TPR * P_cancel + FPR * (1 - P_cancel)

P_cancel_given_model = numerator / P_model_cancel

print("1(a) Probability customer cancels given model predicts cancel:")
print(f"P(cancel | model says cancel) = {P_cancel_given_model:.4f}  ({P_cancel_given_model*100:.2f}%)")
print()

# ============================================================
# 1(b) — Should we take the insurance? Compare two strategies:
#   Strategy 1: Insure EVERY customer
#   Strategy 2: Insure ONLY customers predicted to cancel
# ============================================================

# ---- Strategy 1: Insure everyone ----
expected_loss_without_insurance = P_cancel * loss_per_cancel
expected_cost_with_insurance = insurance_cost

print("1(b) Strategy 1: Insure every customer")
print(f"Expected loss without insurance = {expected_loss_without_insurance:.2f} €")
print(f"Insurance cost per customer =     {expected_cost_with_insurance:.2f} €")

if expected_cost_with_insurance < expected_loss_without_insurance:
    print("→ Decision: INSURE everyone\n")
else:
    print("→ Decision: DO NOT insure everyone\n")


# ---- Strategy 2: Insure only model-flagged customers ----
# For customers where model predicts 'cancel':
expected_loss_flagged = P_cancel_given_model * loss_per_cancel
insurance_flagged = insurance_cost

print("1(b) Strategy 2: Insure ONLY customers flagged by the model")
print(f"Expected loss for a flagged customer = {expected_loss_flagged:.3f} €")
print(f"Insurance cost for flagged customer   = {insurance_flagged:.3f} €")

if insurance_flagged < expected_loss_flagged:
    print(f"→ Decision: INSURE flagged customers (save: {expected_loss_flagged - insurance_flagged:.3f} €)")
else:
    print("→ Decision: DO NOT insure flagged customers")


# %% [markdown]
# Using the overall cancellation probability (24%), the expected loss per customer is 2.40€, which is far below the 8.50€ insurance premium, so we should not buy universal insurance.
# 
# If, hypothetically, we were allowed to insure only customers predicted to cancel by our model, then for those customers the expected loss is about 8.88€, slightly above the 8.50€ premium, so it would be profitable to insure that high-risk segment.

# %%
# ==========================================================
# TASK 2
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from itertools import combinations
from pandas.plotting import parallel_coordinates

plt.style.use("ggplot")

# %%
# ============================================================
# 1. Load data
# ============================================================
orders = pd.read_parquet("orders_data.parquet")
products = pd.read_parquet("products_data.parquet")

# %%
# ============================================================
# 2. Basic EDA + cleaning
# ============================================================
print("=== ORDERS HEAD ===")
print(orders.head())
print("\n=== PRODUCTS HEAD ===")
print(products.head())

print("\n=== ORDERS INFO ===")
print(orders.info())
print("\n=== PRODUCTS INFO ===")
print(products.info())

print("\n=== ORDERS NULLS ===")
print(orders.isna().sum())
print("\n=== PRODUCTS NULLS ===")
print(products.isna().sum())

# Deduplicate products by title (some titles appear multiple times)
products_unique = products.drop_duplicates(subset=["product_title"]).copy()

# Parse date columns in orders (strip ' UTC' and convert to datetime)
date_cols = ["processed_at", "created_at", "cancelled_at", "first_date_order"]
for col in date_cols:
    if col in orders.columns:
        orders[col] = pd.to_datetime(
            orders[col].str.replace(" UTC", "", regex=False),
            errors="coerce"
        )

# Create order_date and order_month (normalized to first day of month)
orders["order_date"] = pd.to_datetime(orders["processed_at"].dt.date)
orders["order_month"] = orders["order_date"].values.astype("datetime64[M]")

# Basic date sanity checks
print("\nOrder date range:", orders["order_date"].min(), "->", orders["order_date"].max())
print("Order month range:", orders["order_month"].min(), "->", orders["order_month"].max())


# %%
# ============================================================
# 3. Feature engineering: order-lines + revenue
# ============================================================
# Lookup table for product info
product_lookup = (
    products_unique
    .set_index("product_title")[["product_price", "product_category", "product_type"]]
)

def explode_order_products(df_orders: pd.DataFrame,
                           lookup: pd.DataFrame) -> pd.DataFrame:
    """
    Expand orders into one row per product line item.
    product_items is a comma-separated list of product_title.
    """
    records = []
    for _, row in df_orders.iterrows():
        items = [s.strip() for s in str(row["product_items"]).split(",")]
        for title in items:
            if title in lookup.index:
                rec = lookup.loc[title]
                price = rec["product_price"]
                category = rec["product_category"]
                ptype = rec["product_type"]
            else:
                # In case a title is missing in products table
                price = np.nan
                category = None
                ptype = None

            records.append(
                {
                    "order_number": row["order_number"],
                    "customer_id": row["customer_id"],
                    "order_date": row["order_date"],
                    "order_month": row["order_month"],
                    "product_title": title,
                    "product_price": price,
                    "product_category": category,
                    "product_type": ptype,
                }
            )
    return pd.DataFrame(records)

order_lines = explode_order_products(orders, product_lookup)

print("\n=== ORDER LINES HEAD ===")
print(order_lines.head())
print("\n=== ORDER LINES NULLS ===")
print(order_lines.isna().sum())

# Order-level revenue
order_revenue = (
    order_lines
    .groupby("order_number")["product_price"]
    .sum()
    .rename("order_revenue")
)

orders = orders.merge(order_revenue, on="order_number", how="left")

print("\nOrder revenue summary:")
print(orders["order_revenue"].describe())


# %% [markdown]
# 
# # ============================================================
# # TASK 2a — Customer Cohort Analysis
# # ============================================================

# %%
# ============================================================
# 4. Cohort setup (Customer Retention Cohort Analysis)
# ============================================================
# Cohort = first order month per customer
orders["cohort_month"] = (
    orders.groupby("customer_id")["order_month"]
    .transform("min")
)

def get_month_diff(d1: pd.Series, d2: pd.Series) -> pd.Series:
    """Difference in months between two Timestamps (d1 - d2)."""
    return (d1.dt.year - d2.dt.year) * 12 + (d1.dt.month - d2.dt.month)

# Cohort index (0,1,2,... months since first order)
orders["cohort_index"] = get_month_diff(orders["order_month"], orders["cohort_month"])

# One row per customer + month for cohort calculations
cohort_data = (
    orders[["customer_id", "cohort_month", "order_month", "cohort_index"]]
    .drop_duplicates()
)

# Cohort sizes (customers in period 0)
cohort_sizes = (
    cohort_data[cohort_data["cohort_index"] == 0]
    .groupby("cohort_month")["customer_id"]
    .nunique()
    .rename("cohort_size")
)

# Retention counts by cohort & period
retention_counts = (
    cohort_data
    .groupby(["cohort_month", "cohort_index"])["customer_id"]
    .nunique()
    .rename("n_customers")
    .reset_index()
)

# Add cohort sizes and compute retention rate
retention = retention_counts.merge(cohort_sizes, on="cohort_month", how="left")
retention["retention_rate"] = retention["n_customers"] / retention["cohort_size"]

# Retention matrix for heatmap: cohorts x months since first order
retention_pivot = retention.pivot_table(
    index="cohort_month",
    columns="cohort_index",
    values="retention_rate"
)

print("\n=== Cohort Retention Matrix (head) ===")
print(retention_pivot.head())

# ----------------   Customer Cohort Purchase Count   ----------------
orders_per_customer = (
    orders
    .groupby(["customer_id", "cohort_month", "cohort_index"])["order_number"]
    .nunique()
    .reset_index(name="n_orders")
)

cohort_purchase = (
    orders_per_customer
    .groupby(["cohort_month", "cohort_index"])["n_orders"]
    .mean()
    .rename("avg_orders_per_customer")
    .unstack("cohort_index")
)

print("\n=== Cohort Purchase Count (avg orders per customer) ===")
print(cohort_purchase.head())

# ----------------   Average Retention Curve Across Cohorts   ----------------
avg_retention_curve = (
    retention
    .groupby("cohort_index")["retention_rate"]
    .mean()
)

print("\n=== Average Retention Curve (head) ===")
print(avg_retention_curve.head())

# ----------------   PLOTS: Cohort heatmap + avg retention curve   ----------------
plt.figure(figsize=(12, 6))
sns.heatmap(
    retention_pivot,
    annot=False,
    fmt=".0%",
    cmap="Blues"
)
plt.title("Customer Retention Cohort Analysis")
plt.ylabel("Cohort (first order month)")
plt.xlabel("Months since first order")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 4))
avg_retention_curve.plot(marker="o")
plt.title("Average Retention Curve Across Cohorts")
plt.xlabel("Months since first order")
plt.ylabel("Retention rate")
plt.tight_layout()
plt.show()


# %% [markdown]
# * Most customers do not return after their first month.
# - After month 1, retention drops to 3–5%
# - By month 3–6, retention is around 2–3%
# 
# * This line graph averages retention rates across all cohorts, showing a typical customer lifecycle.
# - Month 0 → 100% (everyone buys)
# - Month 1 → massive drop to ~4%
# - Months 2+ → stabilizes around 2–3%
# 
# Most customers behave like one-time purchasers. Very small percentage form a loyal customer base.

# %% [markdown]
# 
# # ============================================================
# # TASK 2b — High-Level Business Development
# # ============================================================

# %%
# ============================================================
# 5. Monthly Revenue & Average Order Value per Month
# ============================================================
monthly = (
    orders
    .groupby("order_month")
    .agg(
        monthly_revenue=("order_revenue", "sum"),
        n_orders=("order_number", "nunique"),
        n_customers=("customer_id", "nunique")
    )
)

monthly["avg_order_value"] = monthly["monthly_revenue"] / monthly["n_orders"]

print("\n=== Monthly summary ===")
print(monthly.head())

# Monthly revenue
plt.figure(figsize=(10, 4))
monthly["monthly_revenue"].plot(marker="o")
plt.title("Monthly Revenue")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# Average order value per month
plt.figure(figsize=(10, 4))
monthly["avg_order_value"].plot(marker="o")
plt.title("Average Order Value per Month")
plt.xlabel("Month")
plt.ylabel("AOV")
plt.tight_layout()
plt.show()

# ============================================================
# 6. Revenue by Product Category (over time & total)
# ============================================================
rev_cat_month = (
    order_lines
    .groupby(["order_month", "product_category"])["product_price"]
    .sum()
    .rename("revenue")
    .reset_index()
)

# Revenue by product category over time (lines)
plt.figure(figsize=(12, 6))
for cat, sub in rev_cat_month.groupby("product_category"):
    sub_sorted = sub.sort_values("order_month")
    plt.plot(sub_sorted["order_month"], sub_sorted["revenue"], label=cat)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.title("Revenue by Product Category Over Time")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# Total revenue by product category (bar)
total_rev_cat = (
    rev_cat_month
    .groupby("product_category")["revenue"]
    .sum()
    .sort_values(ascending=False)
)

plt.figure(figsize=(10, 5))
total_rev_cat.plot(kind="bar")
plt.title("Total Revenue by Product Category")
plt.xlabel("Product Category")
plt.ylabel("Total Revenue")
plt.tight_layout()
plt.show()


# %% [markdown]
# ## Revenue by month across the full dataset.
# 
# we can see:
# 
# * Strong growth throughout 2020
# 
# * Seasonality patterns (peaks in late year: November, December, January)
# 
# * A noticeable spike around holiday season
# 
# * Dip in early 2021
# 
#  Seems this is typical for sports / retail:
# 
# * Q4 peak (holiday sales)
# 
# * January spike (new-year fitness goals)
# 
# * Summer slowdown
# 
# ## Average Order Value (AOV)
# What the graph shows:
# 
# * AOV fluctuates slightly but generally:
# 
# * Stays within €260–€305
# 
# * Peaks around Oct–Nov (higher priced bundles)
# 
# * Lower in earlier months
# 
# Seems customers are consistently spending around the same amount. Peaks during holiday season can signal:
# 
# * High-priced gift purchases
# 
# * More bundles sold
# 
# * Higher-margin product demand
# 
# ## Revenue by Product Category (Trend)
# 
# * Each product category’s monthly revenue trend:
# * golf dominates revenue by far
# * Multi-sport bundles are second
# * Tennis is also strong
# * Football & swimming grow later in the dataset
# * Accessories contribute small but steady amounts
# 
# Here seems the business is very dependent on: Golf (primary revenue driver), Multi-sport bundles and Tennis.
# 
# ## Total Revenue by Product Category (Bar Chart)
# 
# This is the overall revenue contribution:
# * Golf is by far your biggest category
# * Multi-sport bundles are second
# * Tennis comes third
# * Accessories, football, swimming are small contributors
# 
# This is a classic Pareto distribution (80/20 rule): A few categories generate most of your revenue. The rest are niche
# 
# 
# ## Main Findings
# * Customer retention is very low → most customers buy once
# * No cohort is performing significantly better → churn is structural
# * Revenue is growing but seasonal
# * Golf is the core of the business
# * Tennis and bundles are strong secondary categories
# * Smaller categories could be optimized or rethought

# %% [markdown]
# # ============================================================
# # EXTRA ANALYSIS SECTION
# # ============================================================
# # Revenue heatmaps
# # Product category correlation
# # Parallel coordinates customer profiles
# # Stacked area revenue
# # Product affinity network
# # Survival curve

# %%
# ============================================================
# 7. Revenue & Order Count Heatmaps by Month and Product Category
# ============================================================
rev_heatmap = rev_cat_month.pivot_table(
    index="product_category",
    columns="order_month",
    values="revenue",
    fill_value=0
)

plt.figure(figsize=(12, 6))
sns.heatmap(rev_heatmap, cmap="BuGn")
plt.title("Revenue Heatmap by Month and Product Category")
plt.xlabel("Month")
plt.ylabel("Product Category")
plt.tight_layout()
plt.show()

# Order count heatmap
order_counts_cat_month = (
    order_lines
    .groupby(["order_month", "product_category"])["order_number"]
    .nunique()
    .rename("n_orders")
    .reset_index()
)

order_count_heatmap = order_counts_cat_month.pivot_table(
    index="product_category",
    columns="order_month",
    values="n_orders",
    fill_value=0
)

plt.figure(figsize=(12, 6))
sns.heatmap(order_count_heatmap, cmap="PuBu")
plt.title("Order Count Heatmap by Month and Product Category")
plt.xlabel("Month")
plt.ylabel("Product Category")
plt.tight_layout()
plt.show()

# ============================================================
# 8. Correlation of Product Categories (monthly revenue)
# ============================================================
cat_month_matrix = rev_cat_month.pivot_table(
    index="order_month",
    columns="product_category",
    values="revenue",
    fill_value=0
)

cat_corr = cat_month_matrix.corr()

plt.figure(figsize=(10, 8))
sns.heatmap(cat_corr, cmap="coolwarm", center=0)
plt.title("Correlation of Product Categories (Monthly Revenue)")
plt.tight_layout()
plt.show()

# ============================================================
# 9. Parallel Coordinates: Sampled Customer Profiles
# ============================================================
cust_orders = (
    orders
    .groupby("customer_id")
    .agg(
        first_order=("order_month", "min"),
        last_order=("order_month", "max"),
        n_orders=("order_number", "nunique"),
        total_revenue=("order_revenue", "sum")
    )
)

cust_cats = (
    order_lines
    .groupby("customer_id")["product_category"]
    .nunique()
    .rename("n_categories")
)

cust_features = cust_orders.join(cust_cats, how="left")
cust_features["lifetime_months"] = get_month_diff(
    cust_features["last_order"], cust_features["first_order"]
) + 1

cust_features_num = cust_features[["n_orders", "total_revenue", "n_categories", "lifetime_months"]].copy()

# Segment customers by total revenue (low / mid / high)
cust_features_num["segment"] = pd.qcut(
    cust_features_num["total_revenue"],
    q=3,
    labels=["low", "mid", "high"]
)

# Sample customers for plotting
sampled = cust_features_num.sample(
    n=min(500, len(cust_features_num)),
    random_state=42
)

plt.figure(figsize=(10, 6))
parallel_coordinates(
    sampled.reset_index(),
    class_column="segment",
    cols=["n_orders", "total_revenue", "n_categories", "lifetime_months"],
    alpha=0.3
)
plt.title("Parallel Coordinates Plot of Sampled Customer Profiles")
plt.tight_layout()
plt.show()

# ============================================================
# 10. Revenue Composition Over Time (Stacked Area)
# ============================================================
rev_comp = rev_cat_month.pivot_table(
    index="order_month",
    columns="product_category",
    values="revenue",
    fill_value=0
).sort_index()

plt.figure(figsize=(12, 6))
plt.stackplot(
    rev_comp.index,
    rev_comp.values.T,
    labels=rev_comp.columns
)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.title("Revenue Composition Over Time (Stacked Area)")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# ============================================================
# 11. Product Category Affinity Network (strongest co-occurrence)
# ============================================================
order_cat_sets = (
    order_lines
    .dropna(subset=["product_category"])
    .groupby("order_number")["product_category"]
    .apply(lambda x: sorted(set(x)))
)

edge_weights = {}
for cats in order_cat_sets:
    if len(cats) < 2:
        continue
    for c1, c2 in combinations(cats, 2):
        edge = tuple(sorted((c1, c2)))
        edge_weights[edge] = edge_weights.get(edge, 0) + 1

edges_df = (
    pd.DataFrame(
        [
            {"source": e[0], "target": e[1], "weight": w}
            for e, w in edge_weights.items()
        ]
    )
    .sort_values("weight", ascending=False)
)

print("\n=== Top 20 category co-occurrences ===")
print(edges_df.head(20))

# Build network on strongest edges (top 30)
top_edges = edges_df.head(30)

G = nx.Graph()
for _, row in top_edges.iterrows():
    G.add_edge(row["source"], row["target"], weight=row["weight"])

plt.figure(figsize=(8, 8))
pos = nx.spring_layout(G, k=0.5, seed=42)
weights = [d["weight"] for (_, _, d) in G.edges(data=True)]
nx.draw_networkx_nodes(G, pos, node_size=800)
nx.draw_networkx_edges(
    G,
    pos,
    width=[w / max(weights) * 5 for w in weights],
    alpha=0.7
)
nx.draw_networkx_labels(G, pos, font_size=9)
plt.title("Product Category Affinity Network (Top Co-occurrences)")
plt.axis("off")
plt.tight_layout()
plt.show()

# ============================================================
# 12. Customer Lifetime Survival Curve (Discrete)
# ============================================================
lifetimes = cust_features["lifetime_months"].astype(int)

max_life = lifetimes.max()
survival = []
for t in range(0, max_life + 1):
    surv = (lifetimes > t).mean()
    survival.append({"month": t, "survival": surv})

survival_df = pd.DataFrame(survival)

plt.figure(figsize=(8, 4))
plt.step(survival_df["month"], survival_df["survival"], where="post")
plt.title("Customer Lifetime Survival Curve (Discrete, months since first order)")
plt.xlabel("Months since first order")
plt.ylabel("Survival probability")
plt.tight_layout()
plt.show()


# %% [markdown]
# ## Revenue Heatmap
# 
# From this visualization, it is clear that the golf category consistently generates the highest revenue, as shown by its darker shading throughout the timeline. Multi-sport bundles also contribute significantly; however, their revenue is more seasonal, with noticeable peaks during the fourth quarter. Tennis shows steady but moderate revenue, while categories such as accessories, football, and swimming generate comparatively little revenue, reflected by their lighter shading.
# 
# ## Order Count Heatmap
# The data reveals that golf has both a high order count and high revenue, indicating strong customer demand. Multi-sport bundles receive fewer orders but still produce substantial revenue, suggesting that they are higher-priced items. Accessories, on the other hand, are ordered fairly often but contribute less to revenue due to their lower price point. Together, these insights show that bundles generate large revenue per order, while accessories rely more on volume but remain low-revenue items overall.
# 
# ## Category Correlation Heatmap 
# This analysis reveals that golf and multi-sport bundles have a moderate positive correlation, suggesting that customers may browse or purchase these categories during similar seasonal periods. Tennis shows some correlation with football and swimming, potentially reflecting shared seasonal interest in outdoor or summer sports. Accessories display weak correlations with other categories, meaning they behave independently of seasonal trends. This insight helps identify which categories share demand patterns and may benefit from combined marketing strategies.
# 
# ## Parallel Coordinates Plot 
# The visualization makes clear distinctions between segments: high spenders tend to make more orders, remain active for longer periods, and purchase from multiple categories, showing broad engagement with the product range. In contrast, low spenders typically make only one purchase, have short lifetimes, and generally buy from just one category. This highlights the behavioral differences between valuable repeat customers and one-time buyers, providing guidance for targeted retention strategies.
# 
# ## Stacked Area Chart 
# The chart demonstrates that golf consistently represents the largest portion of total revenue, confirming its position as the primary revenue driver. Multi-sport bundles play a major role during the fourth quarter, showing strong seasonality, while tennis contributes moderately with some seasonal variation. Smaller categories, such as accessories, football, and swimming, consistently make up only a small part of total revenue.
# 
# ## Product Category Affinity Network
# The product category affinity network visualizes how frequently product categories are purchased together within the same order. Nodes represent categories, while edges show co-occurrence strength—thicker edges indicate stronger relationships. The network reveals strong affinities between golf and accessories, as well as between bundles and nearly all major categories, indicating that these products are often purchased together. Tennis also shows meaningful connections to accessories and golf, suggesting shared customer interest. In contrast, football and swimming categories have weak links, indicating they are typically purchased alone.
# 
# ## Customer Lifetime Survival Curve
# At month zero, all customers are active by definition, but the curve drops sharply after the first month, showing that many customers do not return to make a second purchase. After six months, only a very small proportion of customers remain active, and by twelve months, the survival probability approaches zero. This pattern highlights a significant retention issue: most customers are one-time buyers and do not engage in long-term purchasing behavior.

# %% [markdown]
# ## References & Acknowledgments
# 
# I took help from these resources.
# * OpenAI ChatGPT for brainstorming and methodological clarification.
# * Stack Overflow – for troubleshooting and examples of Python/pandas usage.
# * NetworkX documentation: https://networkx.org/documentation/stable/
# 
# 

# %% [markdown]
# 


