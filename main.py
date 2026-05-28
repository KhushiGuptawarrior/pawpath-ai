import re
import math
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score

# ── Global state ──────────────────────────────────────────────────────────────
state = {}

def build_pipeline():
    # 1. Load data
    data = pd.read_csv('Smart_Customer_Analytics_Dataset.csv')
    df = pd.DataFrame(data)

    # Keep original for customer-facing responses
    original_df = df.copy()

    # 2. Ordinal encoding — exact order matters
    education_order  = ['High School', 'Graduate', 'Post-Graduate', 'Doctorate']
    discount_order   = ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
    membership_order = ['Bronze', 'Silver', 'Gold', 'Platinum']
    df['Education']       = pd.Categorical(df['Education'],       categories=education_order,  ordered=True)
    df['Discount_Usage']  = pd.Categorical(df['Discount_Usage'],  categories=discount_order,   ordered=True)
    df['Membership_Tier'] = pd.Categorical(df['Membership_Tier'], categories=membership_order, ordered=True)

    # 3. One-hot encode all remaining object columns except Customer_ID
    nominal_cols = df.select_dtypes(include='object').columns.drop('Customer_ID', errors='ignore')
    df = pd.get_dummies(df, columns=nominal_cols, drop_first=True)

    # 4. Convert booleans to int
    bool_cols = df.select_dtypes(include='bool').columns
    df[bool_cols] = df[bool_cols].astype(int)

    # 5. Ordinal to integer codes
    df['Membership_Tier'] = pd.Categorical(df['Membership_Tier'], categories=membership_order, ordered=True).codes
    df['Education']       = pd.Categorical(df['Education'],       categories=education_order,  ordered=True).codes

    # 6. Feature columns — exact list and order
    feature_cols = [
        'Days_Since_Last_Purchase','Num_Purchases','Total_Spend',
        'Loyalty_Points','Membership_Tier','Visits_Per_Month',
        'Cart_Abandonment_Rate','Num_Returns','Return_Rate',
        'Age','Annual_Income','Satisfaction_Score','Support_Tickets',
        'Months_Active','Gender_Male','Gender_Other','Education',
        'Email_Open_Rate','Wishlist_Items','Referrals_Made','Reviews_Given'
    ]
    occupation_cols = [c for c in df.columns if c.startswith('Occupation_')]
    city_cols       = [c for c in df.columns if c.startswith('City_')]
    feature_cols.extend(occupation_cols)
    feature_cols.extend(city_cols)

    X = df[feature_cols]
    y = df['Will_Purchase_Next_Month']

    # 7. Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 8. Scale
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(scaler.fit_transform(X_train), columns=X_train.columns, index=X_train.index)
    X_test_scaled  = pd.DataFrame(scaler.transform(X_test),      columns=X_test.columns,  index=X_test.index)

    # 9. SMOTE
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

    # 10. Train — DO NOT CHANGE THIS MODEL
    rf_model = RandomForestClassifier(random_state=42)
    rf_model.fit(X_train_resampled, y_train_resampled)

    # 11. K-Means clustering with K=4 — DO NOT CHANGE
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X_train_scaled)

    # Accuracy
    y_pred = rf_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)

    # Assign clusters to ALL original rows
    X_all_scaled = pd.DataFrame(scaler.transform(X), columns=X.columns, index=X.index)
    all_clusters = kmeans.predict(X_all_scaled)
    original_df['cluster'] = all_clusters

    # Predict probabilities for all customers
    proba_all = rf_model.predict_proba(X_all_scaled)[:, 1]
    original_df['purchase_probability'] = proba_all

    return {
        'rf_model': rf_model,
        'kmeans': kmeans,
        'scaler': scaler,
        'feature_cols': feature_cols,
        'original_df': original_df,
        'encoded_df': df,
        'X': X,
        'X_test_scaled': X_test_scaled,
        'y_test': y_test,
        'accuracy': accuracy,
        'occupation_cols': occupation_cols,
        'city_cols': city_cols,
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Training ML pipeline...")
    state.update(build_pipeline())
    print(f"Pipeline ready. Accuracy: {state['accuracy']:.4f}")
    yield

app = FastAPI(title="Smart Customer Analytics API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper: encode one customer row ──────────────────────────────────────────
def encode_customer(cid: str):
    original_df = state['original_df']
    row = original_df[original_df['Customer_ID'] == cid]
    if row.empty:
        return None, None
    idx = row.index[0]
    X = state['X']
    if idx not in X.index:
        return None, None
    X_row = pd.DataFrame(state['scaler'].transform(X.loc[[idx]]), columns=X.columns)
    return row.iloc[0], X_row


# ── POST /api/query ───────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str

@app.post("/api/query")
def query(req: QueryRequest):
    q = req.question.strip()
    ql = q.lower()
    original_df = state['original_df']
    rf_model    = state['rf_model']
    feature_cols = state['feature_cols']

    # Extract customer ID if present
    cid_match = re.search(r'cust\d+', ql)
    cid = cid_match.group(0).upper() if cid_match else None

    # ── Will CUSTXXXX purchase next month?
    if cid and ('will' in ql or 'purchase' in ql or 'buy' in ql) and ('next month' in ql or 'predict' in ql):
        row, X_row = encode_customer(cid)
        if row is None:
            return {"answer": f"Customer {cid} not found in the dataset.", "chart_type": "none", "chart_data": {}, "highlight": ""}
        pred = rf_model.predict(X_row)[0]
        prob = rf_model.predict_proba(X_row)[0][1]
        verdict = "YES — likely to purchase" if pred == 1 else "NO — unlikely to purchase"
        return {
            "answer": f"{cid} ({row['Occupation']}, {row['City']}): Prediction = {verdict}. Purchase probability: {prob:.1%}. Segment: {row['Customer_Segment']}.",
            "chart_type": "none", "chart_data": {}, "highlight": f"{prob:.1%}"
        }

    # ── Purchase probability for CUSTXXXX
    if cid and 'probabilit' in ql:
        row, X_row = encode_customer(cid)
        if row is None:
            return {"answer": f"Customer {cid} not found.", "chart_type": "none", "chart_data": {}, "highlight": ""}
        prob = rf_model.predict_proba(X_row)[0][1]
        return {
            "answer": f"Purchase probability for {cid}: {prob:.1%}. Segment: {row['Customer_Segment']}. Membership: {row['Membership_Tier']}.",
            "chart_type": "none", "chart_data": {}, "highlight": f"{prob:.1%}"
        }

    # ── Tell me about CUSTXXXX
    if cid and ('tell' in ql or 'about' in ql or 'profile' in ql or 'info' in ql):
        row, _ = encode_customer(cid)
        if row is None:
            return {"answer": f"Customer {cid} not found.", "chart_type": "none", "chart_data": {}, "highlight": ""}
        prob = row['purchase_probability']
        ans = (f"{cid} is a {int(row['Age'])}-year-old {row['Gender']} {row['Occupation']} from {row['City']}. "
               f"Education: {row['Education']}. Annual Income: ₹{int(row['Annual_Income']):,}. "
               f"Membership: {row['Membership_Tier']} (Loyalty Points: {int(row['Loyalty_Points'])}). "
               f"Segment: {row['Customer_Segment']}. Cluster: {int(row['cluster'])}. "
               f"Total Spend: ₹{int(row['Total_Spend']):,}. Satisfaction: {row['Satisfaction_Score']}/5. "
               f"Purchase probability next month: {prob:.1%}.")
        return {"answer": ans, "chart_type": "none", "chart_data": {}, "highlight": f"{prob:.1%}"}

    # ── What segment is CUSTXXXX in?
    if cid and 'segment' in ql:
        row = original_df[original_df['Customer_ID'] == cid]
        if row.empty:
            return {"answer": f"Customer {cid} not found.", "chart_type": "none", "chart_data": {}, "highlight": ""}
        seg = row.iloc[0]['Customer_Segment']
        return {"answer": f"{cid} is in the '{seg}' segment.", "chart_type": "none", "chart_data": {}, "highlight": seg}

    # ── Which cluster does CUSTXXXX belong to?
    if cid and 'cluster' in ql:
        row = original_df[original_df['Customer_ID'] == cid]
        if row.empty:
            return {"answer": f"Customer {cid} not found.", "chart_type": "none", "chart_data": {}, "highlight": ""}
        cl = int(row.iloc[0]['cluster'])
        return {"answer": f"{cid} belongs to Cluster {cl}.", "chart_type": "none", "chart_data": {}, "highlight": f"Cluster {cl}"}

    # ── Which customers will buy next month?
    if ('which customers' in ql or 'who will' in ql) and ('buy' in ql or 'purchase' in ql):
        buyers = original_df[original_df.apply(
            lambda r: r['purchase_probability'], axis=1
        ) > 0.5].sort_values('purchase_probability', ascending=False).head(20)
        labels = buyers['Customer_ID'].tolist()
        values = [round(p * 100, 1) for p in buyers['purchase_probability'].tolist()]
        return {
            "answer": f"Top {len(buyers)} customers likely to purchase next month (probability > 50%).",
            "chart_type": "bar",
            "chart_data": {"labels": labels, "values": values, "xlabel": "Customer", "ylabel": "Purchase Probability (%)"},
            "highlight": f"{len(buyers)} customers"
        }

    # ── At risk / churn
    if 'churn' in ql or 'at risk' in ql or 'risk' in ql:
        at_risk = original_df[original_df['purchase_probability'] < 0.3].sort_values('Days_Since_Last_Purchase', ascending=False).head(20)
        labels = at_risk['Customer_ID'].tolist()
        values = at_risk['Days_Since_Last_Purchase'].tolist()
        return {
            "answer": f"{len(at_risk)} customers are at risk of churning (low purchase probability + high days since last purchase). Top shown.",
            "chart_type": "bar",
            "chart_data": {"labels": labels, "values": values, "xlabel": "Customer", "ylabel": "Days Since Last Purchase"},
            "highlight": f"{len(at_risk)} at risk"
        }

    # ── Top spenders
    if 'top' in ql and 'spend' in ql:
        top = original_df.sort_values('Total_Spend', ascending=False).head(10)
        return {
            "answer": f"Top 10 customers by total spend. Highest: {top.iloc[0]['Customer_ID']} at ₹{int(top.iloc[0]['Total_Spend']):,}.",
            "chart_type": "bar",
            "chart_data": {"labels": top['Customer_ID'].tolist(), "values": top['Total_Spend'].tolist(), "xlabel": "Customer", "ylabel": "Total Spend (₹)"},
            "highlight": f"₹{int(top.iloc[0]['Total_Spend']):,}"
        }

    # ── Feature importance
    if 'drive' in ql or 'feature' in ql or 'import' in ql or 'influ' in ql:
        importances = rf_model.feature_importances_
        feat_imp = pd.Series(importances, index=feature_cols).sort_values(ascending=False).head(10)
        return {
            "answer": f"Top 10 features driving purchase predictions. Most important: '{feat_imp.index[0]}' with importance {feat_imp.iloc[0]:.4f}.",
            "chart_type": "bar",
            "chart_data": {"labels": feat_imp.index.tolist(), "values": [round(v, 4) for v in feat_imp.values.tolist()], "xlabel": "Feature", "ylabel": "Importance"},
            "highlight": feat_imp.index[0]
        }

    # ── Customers in cluster N
    cl_match = re.search(r'cluster\s*([0-3])', ql)
    if cl_match:
        cl_num = int(cl_match.group(1))
        cluster_cust = original_df[original_df['cluster'] == cl_num]
        segs = cluster_cust['Customer_Segment'].value_counts()
        return {
            "answer": f"Cluster {cl_num} has {len(cluster_cust)} customers. Top segments: {', '.join([f'{s} ({c})' for s,c in segs.head(3).items()])}.",
            "chart_type": "pie",
            "chart_data": {"labels": segs.index.tolist(), "values": segs.values.tolist()},
            "highlight": f"{len(cluster_cust)} customers"
        }

    # ── How many [Membership_Tier]?
    for tier in ['Bronze', 'Silver', 'Gold', 'Platinum']:
        if tier.lower() in ql:
            count = len(original_df[original_df['Membership_Tier'] == tier])
            all_tiers = original_df['Membership_Tier'].value_counts()
            return {
                "answer": f"There are {count} {tier} members out of {len(original_df)} total customers ({count/len(original_df):.1%}).",
                "chart_type": "pie",
                "chart_data": {"labels": all_tiers.index.tolist(), "values": all_tiers.values.tolist()},
                "highlight": f"{count} {tier}"
            }

    # ── Membership tier distribution general
    if 'membership' in ql and ('count' in ql or 'many' in ql or 'distribut' in ql):
        vc = original_df['Membership_Tier'].value_counts()
        return {
            "answer": f"Membership tier distribution: {', '.join([f'{t}: {c}' for t,c in vc.items()])}.",
            "chart_type": "pie",
            "chart_data": {"labels": vc.index.tolist(), "values": vc.values.tolist()},
            "highlight": f"{vc.index[0]}: {vc.iloc[0]}"
        }

    # ── Most popular category / channel / city
    if 'popular' in ql or 'most' in ql:
        if 'categor' in ql:
            vc = original_df['Preferred_Category'].value_counts()
            return {
                "answer": f"Most popular product category: '{vc.index[0]}' with {vc.iloc[0]} customers ({vc.iloc[0]/len(original_df):.1%}).",
                "chart_type": "bar",
                "chart_data": {"labels": vc.index.tolist(), "values": vc.values.tolist(), "xlabel": "Category", "ylabel": "Count"},
                "highlight": vc.index[0]
            }
        if 'channel' in ql:
            vc = original_df['Preferred_Channel'].value_counts()
            return {
                "answer": f"Most popular channel: '{vc.index[0]}' with {vc.iloc[0]} customers.",
                "chart_type": "pie",
                "chart_data": {"labels": vc.index.tolist(), "values": vc.values.tolist()},
                "highlight": vc.index[0]
            }
        if 'city' in ql or 'cities' in ql:
            vc = original_df['City'].value_counts()
            return {
                "answer": f"City with most customers: '{vc.index[0]}' with {vc.iloc[0]} customers.",
                "chart_type": "bar",
                "chart_data": {"labels": vc.index[:10].tolist(), "values": vc.values[:10].tolist(), "xlabel": "City", "ylabel": "Customers"},
                "highlight": vc.index[0]
            }

    # ── Average [column]
    avg_match = re.search(r'average|mean|avg', ql)
    if avg_match:
        numeric_cols = original_df.select_dtypes(include='number').columns.tolist()
        for col in numeric_cols:
            if col.lower().replace('_', ' ') in ql or col.lower() in ql:
                val = original_df[col].mean()
                return {
                    "answer": f"Average {col}: {val:.2f}.",
                    "chart_type": "none", "chart_data": {},
                    "highlight": f"{val:.2f}"
                }
        # Generic average satisfaction
        if 'satisfaction' in ql:
            val = original_df['Satisfaction_Score'].mean()
            return {"answer": f"Average satisfaction score: {val:.2f}/5.", "chart_type": "none", "chart_data": {}, "highlight": f"{val:.2f}"}
        if 'income' in ql:
            val = original_df['Annual_Income'].mean()
            return {"answer": f"Average annual income: ₹{val:,.0f}.", "chart_type": "none", "chart_data": {}, "highlight": f"₹{val:,.0f}"}
        if 'spend' in ql:
            val = original_df['Total_Spend'].mean()
            return {"answer": f"Average total spend: ₹{val:,.0f}.", "chart_type": "none", "chart_data": {}, "highlight": f"₹{val:,.0f}"}
        if 'age' in ql:
            val = original_df['Age'].mean()
            return {"answer": f"Average customer age: {val:.1f} years.", "chart_type": "none", "chart_data": {}, "highlight": f"{val:.1f} years"}

    # ── Customers in city / segment / occupation
    for city in original_df['City'].unique():
        if city.lower() in ql:
            subset = original_df[original_df['City'] == city]
            return {
                "answer": f"There are {len(subset)} customers in {city}. Average spend: ₹{subset['Total_Spend'].mean():,.0f}. Average satisfaction: {subset['Satisfaction_Score'].mean():.2f}.",
                "chart_type": "none", "chart_data": {},
                "highlight": f"{len(subset)} customers"
            }

    for seg in original_df['Customer_Segment'].unique():
        if seg.lower() in ql:
            subset = original_df[original_df['Customer_Segment'] == seg]
            return {
                "answer": f"'{seg}' segment has {len(subset)} customers. Average spend: ₹{subset['Total_Spend'].mean():,.0f}. Avg purchase probability: {subset['purchase_probability'].mean():.1%}.",
                "chart_type": "none", "chart_data": {},
                "highlight": f"{len(subset)} customers"
            }

    for occ in original_df['Occupation'].unique():
        if occ.lower() in ql:
            subset = original_df[original_df['Occupation'] == occ]
            return {
                "answer": f"There are {len(subset)} {occ} customers. Average income: ₹{subset['Annual_Income'].mean():,.0f}. Avg satisfaction: {subset['Satisfaction_Score'].mean():.2f}.",
                "chart_type": "none", "chart_data": {},
                "highlight": f"{len(subset)} customers"
            }

    # ── Segment distribution
    if 'segment' in ql and ('distribut' in ql or 'all' in ql or 'breakdown' in ql):
        vc = original_df['Customer_Segment'].value_counts()
        return {
            "answer": f"Customer segment distribution: {', '.join([f'{s}: {c}' for s,c in vc.items()])}.",
            "chart_type": "pie",
            "chart_data": {"labels": vc.index.tolist(), "values": vc.values.tolist()},
            "highlight": f"{vc.index[0]}: {vc.iloc[0]}"
        }

    # ── City distribution
    if 'city' in ql or 'cities' in ql:
        vc = original_df['City'].value_counts()
        return {
            "answer": f"Top cities: {', '.join([f'{c} ({n})' for c,n in vc.head(5).items()])}. Total cities covered: {len(vc)}.",
            "chart_type": "bar",
            "chart_data": {"labels": vc.index[:10].tolist(), "values": vc.values[:10].tolist(), "xlabel": "City", "ylabel": "Customers"},
            "highlight": f"{len(vc)} cities"
        }

    # ── Fallback: keyword match on column names
    for col in original_df.select_dtypes(include='number').columns:
        if col.lower().replace('_', ' ') in ql or col.lower() in ql:
            val = original_df[col].mean()
            return {
                "answer": f"Average {col} across all {len(original_df)} customers: {val:.2f}.",
                "chart_type": "none", "chart_data": {},
                "highlight": f"{val:.2f}"
            }

    # Ultimate fallback
    total = len(original_df)
    avg_prob = original_df['purchase_probability'].mean()
    return {
        "answer": f"I couldn't parse a specific operation from your question, but here's a quick snapshot: {total} customers analysed. Average purchase probability: {avg_prob:.1%}. Top segment: '{original_df['Customer_Segment'].value_counts().index[0]}'. Try asking about a specific customer ID, metric, or segment.",
        "chart_type": "none", "chart_data": {},
        "highlight": f"{avg_prob:.1%} avg prob"
    }


# ── GET /api/stats ─────────────────────────────────────────────────────────────
@app.get("/api/stats")
def get_stats():
    original_df = state['original_df']
    vc_clusters  = original_df['cluster'].value_counts().sort_index()
    vc_segments  = original_df['Customer_Segment'].value_counts()
    return {
        "total_customers": len(original_df),
        "model_accuracy": round(state['accuracy'] * 100, 2),
        "cluster_distribution": {str(k): int(v) for k, v in vc_clusters.items()},
        "segment_distribution": {k: int(v) for k, v in vc_segments.items()},
        "avg_satisfaction": round(float(original_df['Satisfaction_Score'].mean()), 2),
        "top_city": original_df['City'].value_counts().index[0],
        "top_category": original_df['Preferred_Category'].value_counts().index[0],
        "num_segments": int(original_df['Customer_Segment'].nunique()),
        "num_cities": int(original_df['City'].nunique()),
    }


# ── GET /api/customers ─────────────────────────────────────────────────────────
@app.get("/api/customers")
def get_customers(page: int = 1, per_page: int = 20):
    original_df = state['original_df']
    total = len(original_df)
    start = (page - 1) * per_page
    end   = start + per_page
    subset = original_df.iloc[start:end]
    customers = []
    for _, row in subset.iterrows():
        customers.append({
            "customer_id": row['Customer_ID'],
            "age": int(row['Age']),
            "gender": row['Gender'],
            "city": row['City'],
            "membership_tier": row['Membership_Tier'],
            "segment": row['Customer_Segment'],
            "purchase_probability": round(float(row['purchase_probability']), 4),
            "cluster": int(row['cluster']),
            "occupation": row['Occupation'],
            "annual_income": int(row['Annual_Income']),
            "total_spend": int(row['Total_Spend']),
            "satisfaction_score": float(row['Satisfaction_Score']),
        })
    return {
        "customers": customers,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": math.ceil(total / per_page),
    }


# ── GET /api/customer/{customer_id} ───────────────────────────────────────────
@app.get("/api/customer/{customer_id}")
def get_customer(customer_id: str):
    original_df = state['original_df']
    row_df = original_df[original_df['Customer_ID'] == customer_id.upper()]
    if row_df.empty:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found.")
    row = row_df.iloc[0]
    return {k: (int(v) if isinstance(v, (np.integer,)) else float(v) if isinstance(v, (np.floating,)) else v)
            for k, v in row.items()}
