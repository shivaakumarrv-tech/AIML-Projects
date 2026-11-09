
# ============================================================
# CUSTOMER CHURN ANALYSIS
# Dataset: customers.csv, orders.csv, products.csv,
#          tickets.csv, policy_eval.csv
# The requied files are to be copied in the folder clean_data.
# ============================================================

# If necessary, install the required libraries:
# pip install pandas numpy matplotlib seaborn scikit-learn

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------

DATA_DIR = "./data/clean"  # Change this if your CSV files are elsewhere

customers = pd.read_csv(
    os.path.join(DATA_DIR, "customers.csv")
)

orders = pd.read_csv(
    os.path.join(DATA_DIR, "orders.csv")
)

products = pd.read_csv(
    os.path.join(DATA_DIR, "products.csv")
)

tickets = pd.read_csv(
    os.path.join(DATA_DIR, "tickets.csv")
)

policy_eval = pd.read_csv(
    os.path.join(DATA_DIR, "policy_eval.csv")
)

print("=" * 60)
print("DATASET OVERVIEW")
print("=" * 60)

for name, df in {
    "Customers": customers,
    "Orders": orders,
    "Products": products,
    "Tickets": tickets,
    "Policy Evaluation": policy_eval
}.items():
    print(f"\n{name}: {df.shape}")
    print(df.head(3))


# ------------------------------------------------------------
# 2. DATA CLEANING
# ------------------------------------------------------------

# Convert date columns
customers["signup_date"] = pd.to_datetime(
    customers["signup_date"], errors="coerce"
)

orders["order_ts"] = pd.to_datetime(
    orders["order_ts"], errors="coerce"
)

# Normalize text columns
for col in ["city", "gender"]:
    customers[col] = customers[col].astype("string").str.strip().str.title()

orders["status"] = (
    orders["status"].astype("string").str.strip().str.lower()
)

# Convert monetary values to numeric
orders["order_amount"] = pd.to_numeric(
    orders["order_amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip(),
    errors="coerce"
)

orders["quantity"] = pd.to_numeric(
    orders["quantity"], errors="coerce"
)

orders["discount_pct"] = pd.to_numeric(
    orders["discount_pct"], errors="coerce"
)

orders["delivery_minutes"] = pd.to_numeric(
    orders["delivery_minutes"], errors="coerce"
)

# Remove duplicate records
customers = customers.drop_duplicates(
    subset=["customer_id"]
)

orders = orders.drop_duplicates(
    subset=["order_id"]
)

products = products.drop_duplicates(
    subset=["product_id"]
)

tickets = tickets.drop_duplicates(
    subset=["ticket_id"]
)

# Keep orders that can be assigned to a customer and a date
orders = orders.dropna(
    subset=["customer_id", "order_ts"]
)

# Analysis cutoff is the final date in the dataset
AS_OF_DATE = orders["order_ts"].max().normalize()

# Define a 90-day inactivity threshold
CHURN_DAYS = 90

print("\nAnalysis cutoff:", AS_OF_DATE.date())
print("Churn inactivity threshold:", CHURN_DAYS, "days")

print("\nOrder status distribution:")
print(orders["status"].value_counts(dropna=False))


# ------------------------------------------------------------
# 3. DESCRIPTIVE CHURN ANALYSIS
# ------------------------------------------------------------

# Use completed orders to measure purchasing behavior
completed_orders = orders[
    orders["status"] == "completed"
].copy()

# Calculate order-level metrics for each customer
order_features = completed_orders.groupby(
    "customer_id"
).agg(
    total_completed_orders=("order_id", "nunique"),
    total_spend=("order_amount", lambda x: x.sum(min_count=1)),
    average_order_value=("order_amount", "mean"),
    total_quantity=("quantity", "sum"),
    average_discount=("discount_pct", "mean"),
    average_delivery_minutes=("delivery_minutes", "mean"),
    first_order_date=("order_ts", "min"),
    last_order_date=("order_ts", "max")
).reset_index()

# Count all orders by status
status_counts = orders.pivot_table(
    index="customer_id",
    columns="status",
    values="order_id",
    aggfunc="nunique",
    fill_value=0
)

status_counts.columns = [
    f"{str(col)}_orders" for col in status_counts.columns
]

status_counts = status_counts.reset_index()

# Combine customer information and order metrics
customer_analysis = customers.merge(
    order_features,
    on="customer_id",
    how="left"
)

customer_analysis = customer_analysis.merge(
    status_counts,
    on="customer_id",
    how="left"
)

# Fill missing order counts with zero
count_columns = [
    col for col in customer_analysis.columns
    if col.endswith("_orders") or col == "total_quantity"
]

customer_analysis[count_columns] = (
    customer_analysis[count_columns].fillna(0)
)

# Calculate days since the last completed purchase
customer_analysis["days_since_last_order"] = (
    AS_OF_DATE - customer_analysis["last_order_date"]
).dt.days

# Customers without completed purchases are treated as inactive
customer_analysis["days_since_last_order"] = (
    customer_analysis["days_since_last_order"].fillna(
        (AS_OF_DATE - customer_analysis["signup_date"]).dt.days
    )
)

# Calculate customer tenure
customer_analysis["customer_tenure_days"] = (
    AS_OF_DATE - customer_analysis["signup_date"]
).dt.days

# Avoid classifying customers who have not yet reached
# the inactivity threshold as churned.
customer_analysis["churn"] = (
    customer_analysis["days_since_last_order"] >= CHURN_DAYS
).astype(int)

customer_analysis["churn_status"] = (
    customer_analysis["churn"]
    .map({1: "Churned", 0: "Active"})
)

# ------------------------------------------------------------
# 4. OVERALL CHURN METRICS
# ------------------------------------------------------------

total_customers = len(customer_analysis)

churned_customers = int(
    customer_analysis["churn"].sum()
)

active_customers = total_customers - churned_customers

churn_rate = (
    churned_customers / total_customers * 100
    if total_customers > 0 else 0
)

print("\n" + "=" * 60)
print("OVERALL CHURN SUMMARY")
print("=" * 60)

print("Total customers:", total_customers)
print("Churned customers:", churned_customers)
print("Active customers:", active_customers)
print(f"Churn rate: {churn_rate:.2f}%")
print(f"Retention rate: {100 - churn_rate:.2f}%")

print("\nChurn status distribution:")
print(customer_analysis["churn_status"].value_counts())


# ------------------------------------------------------------
# 5. CHURN BY CITY
# ------------------------------------------------------------

city_churn = customer_analysis.groupby(
    "city", dropna=False
).agg(
    total_customers=("customer_id", "nunique"),
    churned_customers=("churn", "sum"),
    average_spend=("total_spend", "mean")
).reset_index()

city_churn["churn_rate_pct"] = (
    city_churn["churned_customers"]
    / city_churn["total_customers"].replace(0, np.nan)
    * 100
)

city_churn = city_churn.sort_values(
    "churn_rate_pct", ascending=False
)

print("\n" + "=" * 60)
print("CHURN BY CITY")
print("=" * 60)
print(city_churn.to_string(index=False))


# ------------------------------------------------------------
# 6. CHURN BY GENDER
# ------------------------------------------------------------

gender_churn = customer_analysis.groupby(
    "gender", dropna=False
).agg(
    total_customers=("customer_id", "nunique"),
    churned_customers=("churn", "sum")
).reset_index()

gender_churn["churn_rate_pct"] = (
    gender_churn["churned_customers"]
    / gender_churn["total_customers"].replace(0, np.nan)
    * 100
)

print("\n" + "=" * 60)
print("CHURN BY GENDER")
print("=" * 60)
print(gender_churn.to_string(index=False))


# ------------------------------------------------------------
# 7. CHURN BY AGE GROUP
# ------------------------------------------------------------

customer_analysis["age_group"] = pd.cut(
    customer_analysis["age"],
    bins=[0, 24, 34, 44, 54, 120],
    labels=[
        "18-24", "25-34", "35-44", "45-54", "55+"
    ],
    include_lowest=True
)

age_churn = customer_analysis.groupby(
    "age_group", observed=False, dropna=False
).agg(
    total_customers=("customer_id", "nunique"),
    churned_customers=("churn", "sum")
).reset_index()

age_churn["churn_rate_pct"] = (
    age_churn["churned_customers"]
    / age_churn["total_customers"].replace(0, np.nan)
    * 100
)

print("\n" + "=" * 60)
print("CHURN BY AGE GROUP")
print("=" * 60)
print(age_churn.to_string(index=False))


# ------------------------------------------------------------
# 8. SUPPORT TICKET ANALYSIS
# ------------------------------------------------------------

# Count tickets by customer
ticket_features = tickets.groupby(
    "customer_id"
).agg(
    total_tickets=("ticket_id", "nunique"),
    ticket_categories=("true_category", "nunique")
).reset_index()

customer_analysis = customer_analysis.merge(
    ticket_features,
    on="customer_id",
    how="left"
)

customer_analysis["total_tickets"] = (
    customer_analysis["total_tickets"].fillna(0)
)

customer_analysis["ticket_categories"] = (
    customer_analysis["ticket_categories"].fillna(0)
)

# Note: this is a descriptive association.
# Tickets may have been created after a customer's inactivity
# started, so ticket counts are not used in the predictive model.

ticket_churn = customer_analysis.groupby(
    customer_analysis["total_tickets"] > 0
).agg(
    total_customers=("customer_id", "nunique"),
    churned_customers=("churn", "sum"),
    average_spend=("total_spend", "mean")
).reset_index()

ticket_churn["ticket_group"] = ticket_churn[
    "total_tickets"
].map({
    True: "Has support tickets",
    False: "No support tickets"
})

ticket_churn["churn_rate_pct"] = (
    ticket_churn["churned_customers"]
    / ticket_churn["total_customers"].replace(0, np.nan)
    * 100
)

print("\n" + "=" * 60)
print("CHURN AND SUPPORT TICKETS")
print("=" * 60)
print(ticket_churn.to_string(index=False))


# ------------------------------------------------------------
# 9. PRODUCT CATEGORY ANALYSIS
# ------------------------------------------------------------

product_orders = completed_orders.merge(
    products[["product_id", "product_name", "category"]],
    on="product_id",
    how="left"
)

category_analysis = product_orders.groupby(
    "category", dropna=False
).agg(
    total_orders=("order_id", "nunique"),
    total_quantity=("quantity", "sum"),
    total_revenue=("order_amount", "sum")
).reset_index()

category_analysis = category_analysis.sort_values(
    "total_revenue", ascending=False
)

print("\n" + "=" * 60)
print("PRODUCT CATEGORY PERFORMANCE")
print("=" * 60)
print(category_analysis.to_string(index=False))


# ------------------------------------------------------------
# 10. VISUALIZE CHURN
# ------------------------------------------------------------

# Chart 1: Churn distribution
plt.figure(figsize=(7, 5))

sns.countplot(
    data=customer_analysis,
    x="churn_status"
)

plt.title("Customer Churn Distribution")
plt.xlabel("Customer Status")
plt.ylabel("Number of Customers")
plt.tight_layout()
plt.show()


# Chart 2: Churn by city
plot_city = city_churn.dropna(
    subset=["city", "churn_rate_pct"]
)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=plot_city,
    x="city",
    y="churn_rate_pct"
)

plt.title("Customer Churn Rate by City")
plt.xlabel("City")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Chart 3: Churn by age group
plot_age = age_churn.dropna(
    subset=["age_group", "churn_rate_pct"]
)

plt.figure(figsize=(8, 5))

sns.barplot(
    data=plot_age,
    x="age_group",
    y="churn_rate_pct"
)

plt.title("Customer Churn Rate by Age Group")
plt.xlabel("Age Group")
plt.ylabel("Churn Rate (%)")
plt.tight_layout()
plt.show()


# Chart 4: Revenue by product category
plt.figure(figsize=(10, 6))

sns.barplot(
    data=category_analysis,
    x="category",
    y="total_revenue"
)

plt.title("Revenue by Product Category")
plt.xlabel("Product Category")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 11. PREDICTIVE CHURN MODEL
# ------------------------------------------------------------
# A more defensible setup:
#
# Observation window: all activity up to a snapshot date.
# Prediction window: the following 90 days.
#
# Label = 1 if a customer makes no completed purchase
# during the following 90 days.
#
# Only customers registered on or before the snapshot date
# are included. All model features use information available
# on or before that date.

PREDICTION_DAYS = 90

SNAPSHOT_DATE = (
    AS_OF_DATE - pd.Timedelta(days=PREDICTION_DAYS)
)

PREDICTION_END = SNAPSHOT_DATE + pd.Timedelta(
    days=PREDICTION_DAYS
)

print("\n" + "=" * 60)
print("PREDICTIVE MODEL SETUP")
print("=" * 60)

print("Observation cutoff:", SNAPSHOT_DATE.date())
print("Prediction window ends:", PREDICTION_END.date())

# Eligible customers must have registered by the snapshot date
eligible_customers = customers[
    customers["signup_date"].notna()
    & (customers["signup_date"] <= SNAPSHOT_DATE)
].copy()

# Orders available at prediction time
past_orders = orders[
    (orders["order_ts"] <= SNAPSHOT_DATE)
].copy()

# Completed orders used to build historical purchase features
past_completed = past_orders[
    past_orders["status"] == "completed"
].copy()

# Build features from historical completed orders
past_features = past_completed.groupby(
    "customer_id"
).agg(
    historical_completed_orders=("order_id", "nunique"),
    historical_spend=("order_amount", lambda x: x.sum(min_count=1)),
    historical_avg_order_value=("order_amount", "mean"),
    historical_avg_discount=("discount_pct", "mean"),
    historical_avg_delivery=("delivery_minutes", "mean"),
    historical_last_order=("order_ts", "max")
).reset_index()

# Count historical order statuses
past_status_counts = past_orders.pivot_table(
    index="customer_id",
    columns="status",
    values="order_id",
    aggfunc="nunique",
    fill_value=0
)

past_status_counts.columns = [
    f"past_{col}_orders" for col in past_status_counts.columns
]

past_status_counts = past_status_counts.reset_index()

# Only use tickets created on or before the snapshot.
# The dataset has no ticket creation timestamp, so we cannot
# safely include ticket information in the prediction model.

model_data = eligible_customers.merge(
    past_features,
    on="customer_id",
    how="left"
)

model_data = model_data.merge(
    past_status_counts,
    on="customer_id",
    how="left"
)

# Historical ticket data is intentionally excluded from
# the model because ticket timestamps are not available.

# Calculate recency at the snapshot date
model_data["historical_recency_days"] = (
    SNAPSHOT_DATE - model_data["historical_last_order"]
).dt.days

model_data["historical_recency_days"] = (
    model_data["historical_recency_days"].fillna(
        (SNAPSHOT_DATE - model_data["signup_date"]).dt.days
    )
)

model_data["tenure_days"] = (
    SNAPSHOT_DATE - model_data["signup_date"]
).dt.days

# Replace missing historical order counts with zero
model_count_cols = [
    col for col in model_data.columns
    if col.startswith("past_")
    and col.endswith("_orders")
]

model_data[model_count_cols] = (
    model_data[model_count_cols].fillna(0)
)

model_data["historical_completed_orders"] = (
    model_data["historical_completed_orders"].fillna(0)
)

# Create labels using the next 90 days
future_orders = orders[
    (orders["order_ts"] > SNAPSHOT_DATE)
    & (orders["order_ts"] <= PREDICTION_END)
    & (orders["status"] == "completed")
]

future_purchase_counts = future_orders.groupby(
    "customer_id"
)["order_id"].nunique()

model_data["future_completed_orders"] = (
    model_data["customer_id"]
    .map(future_purchase_counts)
    .fillna(0)
)

model_data["churn_target"] = (
    model_data["future_completed_orders"] == 0
).astype(int)

print("Eligible customers:", len(model_data))
print(
    "Future-window churn rate:",
    f"{model_data['churn_target'].mean() * 100:.2f}%"
    if len(model_data) else "Not available"
)

# Exclude identifiers, dates, and future information.
# Recency is included because it is known at the snapshot.
# It does not directly define the future target.
#
# Historical purchase features are available before prediction.
# No future order counts are used as model predictors.

categorical_features = [
    "city",
    "gender"
]

numeric_features = [
    "age",
    "tenure_days",
    "historical_recency_days",
    "historical_completed_orders",
    "historical_spend",
    "historical_avg_order_value",
    "historical_avg_discount",
    "historical_avg_delivery"
] + model_count_cols

feature_columns = categorical_features + numeric_features

# Ensure columns exist
for col in feature_columns:
    if col not in model_data.columns:
        model_data[col] = np.nan

X = model_data[feature_columns].copy()
y = model_data["churn_target"].copy()

# Check that enough data and both target classes exist
if (
    len(model_data) < 30
    or y.nunique() < 2
    or y.value_counts().min() < 2
):
    print(
        "\nNot enough examples from both classes to train "
        "a reliable churn model. Use the descriptive analysis "
        "above, or collect more historical data."
    )

else:
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    # Numeric preprocessing
    numeric_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]
    )

    # Categorical preprocessing
    categorical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            )
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                numeric_transformer,
                numeric_features
            ),
            (
                "cat",
                categorical_transformer,
                categorical_features
            )
        ]
    )

    # Random Forest classifier
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    class_weight="balanced",
                    random_state=42,
                    min_samples_leaf=2
                )
            )
        ]
    )

    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)

    y_probability = model.predict_proba(X_test)[:, 1]

    print("\n" + "=" * 60)
    print("CHURN MODEL PERFORMANCE")
    print("=" * 60)

    print(
        "Accuracy:",
        round(accuracy_score(y_test, y_pred), 4)
    )

    print(
        "Precision:",
        round(
            precision_score(
                y_test, y_pred, zero_division=0
            ),
            4
        )
    )

    print(
        "Recall:",
        round(
            recall_score(
                y_test, y_pred, zero_division=0
            ),
            4
        )
    )

    print(
        "F1 Score:",
        round(
            f1_score(
                y_test, y_pred, zero_division=0
            ),
            4
        )
    )

    if y_test.nunique() == 2:
        print(
            "ROC-AUC:",
            round(
                roc_auc_score(y_test, y_probability),
                4
            )
        )

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=["Retained", "Churned"],
            zero_division=0
        )
    )

    # Confusion matrix
    cm = confusion_matrix(
        y_test,
        y_pred,
        labels=[0, 1]
    )

    plt.figure(figsize=(6, 5))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        xticklabels=["Retained", "Churned"],
        yticklabels=["Retained", "Churned"]
    )

    plt.title("Churn Model Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.tight_layout()
    plt.show()

    # Feature importance
    fitted_preprocessor = model.named_steps["preprocessor"]

    feature_names = fitted_preprocessor.get_feature_names_out()

    importances = (
        model.named_steps["classifier"].feature_importances_
    )

    feature_importance = pd.DataFrame({
        "feature": feature_names,
        "importance": importances
    }).sort_values(
        "importance", ascending=False
    )

    print("\nTop 15 Important Features:")
    print(feature_importance.head(15).to_string(index=False))

    plt.figure(figsize=(10, 7))

    sns.barplot(
        data=feature_importance.head(15),
        x="importance",
        y="feature"
    )

    plt.title("Top 15 Churn Predictors")
    plt.xlabel("Feature Importance")
    plt.ylabel("Feature")
    plt.tight_layout()
    plt.show()

    # Risk scores for all eligible customers
    model_data["predicted_churn_probability"] = (
        model.predict_proba(X)[:, 1]
    )

    model_data["risk_category"] = pd.cut(
        model_data["predicted_churn_probability"],
        bins=[-0.001, 0.30, 0.60, 1.001],
        labels=["Low", "Medium", "High"]
    )

    print("\nChurn Risk Distribution:")
    print(
        model_data["risk_category"]
        .value_counts()
        .sort_index()
    )

    # Export predictive model results
    model_data.to_csv(
        "churn_prediction_results.csv",
        index=False
    )

    feature_importance.to_csv(
        "churn_feature_importance.csv",
        index=False
    )

    print("\nSaved:")
    print("- churn_prediction_results.csv")
    print("- churn_feature_importance.csv")


# ------------------------------------------------------------
# 12. EXPORT DESCRIPTIVE ANALYSIS RESULTS
# ------------------------------------------------------------

customer_analysis.to_csv(
    "customer_churn_analysis.csv",
    index=False
)

city_churn.to_csv(
    "churn_by_city.csv",
    index=False
)

gender_churn.to_csv(
    "churn_by_gender.csv",
    index=False
)

age_churn.to_csv(
    "churn_by_age_group.csv",
    index=False
)

category_analysis.to_csv(
    "product_category_analysis.csv",
    index=False
)

ticket_churn.to_csv(
    "churn_by_support_tickets.csv",
    index=False
)

# Summary report
summary = pd.DataFrame({
    "metric": [
        "Analysis cutoff",
        "Churn threshold (days)",
        "Total customers",
        "Churned customers",
        "Active customers",
        "Churn rate (%)",
        "Retention rate (%)"
    ],
    "value": [
        str(AS_OF_DATE.date()),
        CHURN_DAYS,
        total_customers,
        churned_customers,
        active_customers,
        round(churn_rate, 2),
        round(100 - churn_rate, 2)
    ]
})

summary.to_csv(
    "churn_summary.csv",
    index=False
)

print("\n" + "=" * 60)
print("CHURN ANALYSIS COMPLETED")
print("=" * 60)

print("Exported descriptive analysis files:")
print("- customer_churn_analysis.csv")
print("- churn_by_city.csv")
print("- churn_by_gender.csv")
print("- churn_by_age_group.csv")
print("- product_category_analysis.csv")
print("- churn_by_support_tickets.csv")
print("- churn_summary.csv")