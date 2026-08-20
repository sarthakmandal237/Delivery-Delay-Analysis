"""
Delivery Delay Analysis - EDA + Prediction Model
(Updated version - fixes applied based on review feedback)

Fixes applied:
1. Time-based train/test split (not random) - train on older orders, test on newer
2. Full evaluation: precision, recall, F1, ROC-AUC, confusion matrix (not just accuracy)
3. Explicit missing value handling
4. StandardScaler + LogisticRegression inside a proper sklearn Pipeline
5. Wording changed from "causes" to "associated with" (correlation, not causation)
6. Model evaluated on test data FIRST, then final model retrained on full data for risk scores
7. Business metric added: "if we check the top 10% riskiest orders, how many late orders do we catch?"
8. Still a simple Logistic Regression - no unnecessary complexity
"""

import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------
# STEP 1: Load the data
# -------------------------------------------------
df = pd.read_csv('C:/Users/USER/Documents/Data Analyst/delivery-delay-analysis/data/raw_orders_dataset.csv')
df['order_date'] = pd.to_datetime(df['order_date'])  # needed for time-based split later

print("Shape of data:", df.shape)
print(df.head())


# -------------------------------------------------
# STEP 2: Check and handle missing values
# -------------------------------------------------
print("\nMissing values before handling:\n", df.isnull().sum())

# Decision: for this dataset, if any row is missing hub, courier, or distance,
# we drop it - these are core fields we can't reasonably guess.
# (If it was something like a missing 'notes' field, we could fill with 'Unknown' instead.)
required_cols = ['hub', 'courier_partner', 'distance_km', 'is_late']
before_rows = len(df)
df = df.dropna(subset=required_cols)
after_rows = len(df)
print(f"\nRows dropped due to missing critical fields: {before_rows - after_rows}")


# -------------------------------------------------
# STEP 3: EDA CHART 1 - Late % by Hub
# -------------------------------------------------
late_by_hub = df.groupby('hub')['is_late'].mean().sort_values(ascending=False) * 100

plt.figure(figsize=(8,5))
late_by_hub.plot(kind='bar', color='indianred')
plt.title('Late Delivery % by Hub')
plt.ylabel('Late %')
plt.xlabel('Hub')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('chart1_late_by_hub.png')
plt.close()
print("\nChart 1 saved - Late % by Hub")
print(late_by_hub)


# -------------------------------------------------
# STEP 4: EDA CHART 2 - Late % by Courier
# -------------------------------------------------
late_by_courier = df.groupby('courier_partner')['is_late'].mean().sort_values(ascending=False) * 100

plt.figure(figsize=(8,5))
late_by_courier.plot(kind='bar', color='steelblue')
plt.title('Late Delivery % by Courier Partner')
plt.ylabel('Late %')
plt.xlabel('Courier')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('chart2_late_by_courier.png')
plt.close()
print("\nChart 2 saved - Late % by Courier")
print(late_by_courier)


# -------------------------------------------------
# STEP 5: EDA CHART 3 - Late % by Distance Band
# -------------------------------------------------
def distance_band(km):
    if km < 100:
        return '1. Under 100km'
    elif km < 250:
        return '2. 100-250km'
    elif km < 400:
        return '3. 250-400km'
    else:
        return '4. Over 400km'

df['distance_band'] = df['distance_km'].apply(distance_band)
late_by_distance = df.groupby('distance_band')['is_late'].mean().sort_index() * 100

plt.figure(figsize=(8,5))
late_by_distance.plot(kind='bar', color='seagreen')
plt.title('Late Delivery % by Distance Band')
plt.ylabel('Late %')
plt.xlabel('Distance Band')
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig('chart3_late_by_distance.png')
plt.close()
print("\nChart 3 saved - Late % by Distance Band")
print(late_by_distance)


# -------------------------------------------------
# STEP 6: EDA CHART 4 - Late % by Month (trend over year)
# -------------------------------------------------
month_order = ['January','February','March','April','May','June',
                'July','August','September','October','November','December']
late_by_month = df.groupby('order_month')['is_late'].mean().reindex(month_order) * 100

plt.figure(figsize=(10,5))
late_by_month.plot(kind='line', marker='o', color='darkorange')
plt.title('Late Delivery % Trend Across Months')
plt.ylabel('Late %')
plt.xlabel('Month')
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig('chart4_late_by_month.png')
plt.close()
print("\nChart 4 saved - Late % Trend by Month")

print("\n--- EDA DONE ---")
print("""
NOTE ON WORDING: The charts above show which hubs/couriers/distances are
ASSOCIATED WITH higher late-delivery rates. This is correlation, not proof
of causation - there could be other factors involved. We treat these as
strong signals worth investigating operationally, not as proven root causes.
""")


# -------------------------------------------------
# STEP 7: Prepare features for modeling
# -------------------------------------------------
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, roc_auc_score, confusion_matrix, classification_report)

# Sort by date - required for a proper time-based split
df = df.sort_values('order_date').reset_index(drop=True)

feature_cols = ['hub', 'courier_partner', 'distance_km', 'order_weekday']
categorical_cols = ['hub', 'courier_partner', 'order_weekday']
numeric_cols = ['distance_km']

X = df[feature_cols]
y = df['is_late']


# -------------------------------------------------
# STEP 8: TIME-BASED train/test split
# (train on the FIRST 80% of dates, test on the LAST 20% - simulates predicting the future)
# -------------------------------------------------
split_index = int(len(df) * 0.8)

X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

print(f"\nTrain period: {df['order_date'].iloc[0].date()} to {df['order_date'].iloc[split_index-1].date()}")
print(f"Test period:  {df['order_date'].iloc[split_index].date()} to {df['order_date'].iloc[-1].date()}")
print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}")


# -------------------------------------------------
# STEP 9: Build a Pipeline (scaling + one-hot encoding + model together)
# This keeps preprocessing consistent between train and test, and avoids leakage.
# -------------------------------------------------
from sklearn.preprocessing import OneHotEncoder

preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), numeric_cols),                      # scale distance_km
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)  # encode text columns
])

model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Train ONLY on training data (older orders)
model_pipeline.fit(X_train, y_train)


# -------------------------------------------------
# STEP 10: Evaluate on TEST data (newer, unseen orders) - full metrics, not just accuracy
# -------------------------------------------------
y_pred = model_pipeline.predict(X_test)
y_proba = model_pipeline.predict_proba(X_test)[:, 1]  # probability of being late

print("\n--- MODEL EVALUATION (on held-out future/test data) ---")
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.1%}")
print(f"Precision: {precision_score(y_test, y_pred):.1%}  (of orders we flagged as late, how many really were late)")
print(f"Recall:    {recall_score(y_test, y_pred):.1%}  (of all actual late orders, how many did we catch)")
print(f"F1-score:  {f1_score(y_test, y_pred):.1%}")
print(f"ROC-AUC:   {roc_auc_score(y_test, y_proba):.3f}  (1.0 = perfect, 0.5 = random guessing)")

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(pd.DataFrame(cm,
                    index=['Actual: On-time', 'Actual: Late'],
                    columns=['Predicted: On-time', 'Predicted: Late']))

print("\nFull classification report:")
print(classification_report(y_test, y_pred))


# -------------------------------------------------
# STEP 11: BUSINESS METRIC - "Top 10% riskiest orders" catch rate
# This is more useful to ops than accuracy: if they only have time to check
# the top 10% highest-risk orders, how many actual late orders would they catch?
# -------------------------------------------------
results = X_test.copy()
results['actual_late'] = y_test.values
results['risk_score'] = y_proba

top_10pct_cutoff = results['risk_score'].quantile(0.90)
top_10pct_orders = results[results['risk_score'] >= top_10pct_cutoff]

total_late_in_test = results['actual_late'].sum()
late_caught_in_top10pct = top_10pct_orders['actual_late'].sum()
catch_rate = late_caught_in_top10pct / total_late_in_test

print("\n--- BUSINESS METRIC: Top 10% Highest-Risk Orders ---")
print(f"Total orders in test set: {len(results)}")
print(f"Total actual late orders in test set: {total_late_in_test}")
print(f"Orders flagged in top 10% risk: {len(top_10pct_orders)}")
print(f"Actual late orders caught in that top 10%: {late_caught_in_top10pct}")
print(f"==> By checking just the top 10% riskiest orders, ops would catch {catch_rate:.1%} of all late orders")


# -------------------------------------------------
# STEP 12: Which factors are ASSOCIATED WITH late risk (not "cause" - just correlation)
# -------------------------------------------------
feature_names = model_pipeline.named_steps['preprocessor'].get_feature_names_out()
coefficients = model_pipeline.named_steps['classifier'].coef_[0]
importance = pd.Series(coefficients, index=feature_names).sort_values(ascending=False)

print("\nTop factors ASSOCIATED WITH higher late risk (correlation, not proven cause):")
print(importance.head(5))
print("\nTop factors ASSOCIATED WITH lower late risk:")
print(importance.tail(5))


# -------------------------------------------------
# STEP 13: Retrain FINAL model on ALL historical data
# (Now that we've honestly validated performance on unseen/future data above,
#  we retrain on the full dataset to get the best possible model for actually
#  scoring current/upcoming orders for the ops team.)
# -------------------------------------------------
final_model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000))
])
final_model.fit(X, y)  # trained on 100% of historical data

df['late_risk_score'] = final_model.predict_proba(X)[:, 1]
df.to_csv('orders_with_risk_score.csv', index=False)

print("\n--- FINAL MODEL ---")
print("Trained on full historical dataset (after validation above).")
print("Saved: orders_with_risk_score.csv - includes late_risk_score column for each order")
print("\nNOTE: The evaluation metrics reported above (accuracy, precision, recall, etc.)")
print("come from the TEST set using the earlier model - not this final model - to give")
print("an honest, unbiased view of real-world performance.")