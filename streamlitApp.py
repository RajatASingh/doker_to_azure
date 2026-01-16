import io
from datetime import timedelta
import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="RFM Analyzer", layout="wide")
st.title("RFM Analyzer")

selected = option_menu(
    None,
    ["RFM Analyzer", "About"],
    icons=["database-down", "info-circle"],
    orientation="horizontal"
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel or CSV file",
    type=["xlsx", "xls", "csv"]
)

# ---------------- RFM FUNCTIONS ----------------
def compute_rfm(df, date_col, customer_col, amount_col):
    df = df[[date_col, customer_col, amount_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
    df.dropna(subset=[date_col, customer_col], inplace=True)

    ref_date = df[date_col].max() + timedelta(days=1)

    rfm = df.groupby(customer_col).agg({
        date_col: lambda x: (ref_date - x.max()).days,
        customer_col: "count",
        amount_col: "sum"
    }).rename(columns={ customer_col: 'Frequency' }).reset_index()


    rfm.columns = ["Customer", "Recency", "Frequency", "Monetary"]

    rfm["R"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)

    rfm["RFM_Score"] = rfm["R"] + rfm["F"] + rfm["M"]

    return rfm, df

def rfm_segment(row):
    if row["RFM_Score"] >= 13:
        return "Champions"
    elif row["RFM_Score"] >= 11:
        return "Loyal Customers"
    elif row["RFM_Score"] >= 9:
        return "Potential Loyalists"
    elif row["RFM_Score"] >= 8:
        return "Recent Customers"
    elif row["RFM_Score"] >= 7:
        return "Promising"
    elif row["RFM_Score"] >= 6:
        return "Customers Needing Attention"
    elif row["RFM_Score"] == 5:
        return "About To Sleep"
    elif row["RFM_Score"] == 4:
        return "At Risk"
    elif row["RFM_Score"] == 3:
        return "Can't Lose Them"
    elif row["RFM_Score"] == 2:
        return "Hibernating"
    else:
        return "Lost"

# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    if uploaded_file.name.endswith(("xls", "xlsx")):
        raw = pd.read_excel(uploaded_file)
    else:
        raw = pd.read_csv(uploaded_file)

    # st.subheader("Preview of Uploaded Data")
    # st.dataframe(raw.head())

    cols = raw.columns.tolist()
    date_col = st.sidebar.selectbox("Order Date Column", cols)
    customer_col = st.sidebar.selectbox("Customer Column", cols)
    amount_col = st.sidebar.selectbox("Amount Column", cols)

    if st.sidebar.button("Run RFM Analysis"):
        rfm, base_df = compute_rfm(raw, date_col, customer_col, amount_col)
        rfm["Segment"] = rfm.apply(rfm_segment, axis=1)

        # ---------------- TABS ----------------
        tab1, tab2 = st.tabs(["📋 RFM Table", "📊 RFM Visuals"])

        # -------- TAB 1 : TABLE --------
        with tab2:
            st.subheader("Customer RFM Segmentation")
            st.dataframe(
                rfm.sort_values("RFM_Score", ascending=False),
                use_container_width=True
            )

            st.download_button(
                "Download RFM Table",
                rfm.to_csv(index=False),
                "rfm_results.csv",
                "text/csv"
            )

        # -------- TAB 2 : VISUALS --------
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Customers", rfm.shape[0])
        col2.metric("Total Sales", f"{rfm['Monetary'].sum():,.2f}")
        col3.metric("Avg RFM Score", f"{rfm['RFM_Score'].mean():.2f}")

        st.subheader("RFM Insights")

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(
                rfm["Segment"].value_counts().reset_index(name="count"),
                x="Segment",
                y="count",
                labels={"count": "Customers"}
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.pie(
                rfm,
                values="Monetary",
                names="Segment",
                hole=0.4
            )
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("Top 10 Customers by Sales")

        #top_cust = rfm.sort_values("Monetary", ascending=False).head(10)

        fig3 = px.line(
            rfm,
            x=date_col,
            y= amount_col,
            #ext_auto=True
        )

        st.plotly_chart(fig3, use_container_width=True)




else:
    st.info("Upload a CSV or Excel file to begin.")

if selected == "About":
    

    st.markdown("""
    ### What is RFM?
    RFM stands for **Recency, Frequency, and Monetary value**.  
    It is a proven customer segmentation technique used to identify **high-value customers**, **at-risk customers**, and **growth opportunities** based on purchase behavior.

    - **Recency** – How recently a customer purchased  
    - **Frequency** – How often they purchase  
    - **Monetary** – How much money they spend  

    Customers are grouped into **11 meaningful segments**, each requiring a different business strategy.
    """)

    st.markdown("---")
    st.subheader("RFM Customer Segments & Recommended Actions")

    rfm_actions = {
        "Champions": (
            "Best customers – recent, frequent, and high spenders.",
            "Reward loyalty, offer exclusive deals, early product access, referral programs."
        ),
        "Loyal Customers": (
            "Consistent buyers who trust your brand.",
            "Upsell premium products, cross-sell, personalized recommendations."
        ),
        "Potential Loyalists": (
            "Recent customers with growing engagement.",
            "Nurture with targeted offers, loyalty programs, product education."
        ),
        "New Customers": (
            "Recently acquired customers.",
            "Strong onboarding, welcome discounts, brand storytelling."
        ),
        "Promising": (
            "Recent buyers but low frequency.",
            "Engagement campaigns, reminders, limited-time offers."
        ),
        "Need Attention": (
            "Above average customers losing momentum.",
            "Re-engagement emails, personalized offers, feedback surveys."
        ),
        "About to Sleep": (
            "Customers showing signs of inactivity.",
            "Urgent incentives, flash sales, reminder notifications."
        ),
        "At Risk": (
            "High spenders who haven’t purchased recently.",
            "Win-back campaigns, personalized communication, exclusive discounts."
        ),
        "Cannot Lose Them": (
            "Previously loyal customers now inactive.",
            "One-to-one outreach, special loyalty offers, relationship rebuilding."
        ),
        "Hibernating": (
            "Inactive, low-spending customers.",
            "Low-cost marketing, awareness campaigns, seasonal promotions."
        ),
        "Lost": (
            "Churned customers with no recent activity.",
            "Minimal spend on reactivation, analyze churn reasons instead."
        ),
    }

    for segment, (meaning, action) in rfm_actions.items():
        st.markdown(f"""
    **🔹 {segment}**  
    **Meaning:** {meaning}  
    **Action:** {action}  
    """)

