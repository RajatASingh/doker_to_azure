import io
from datetime import timedelta

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="RFM Analyzer", layout="wide")

st.title("RFM Analyzer")
st.markdown("Upload an Excel file (or CSV) containing your order data, then pick the columns for order date, customer identifier, and amount.")

uploaded_file = st.file_uploader("Upload Excel or CSV file", type=["xlsx", "xls", "csv"])

def compute_rfm(df, date_col, customer_col, amount_col):
    df = df[[date_col, customer_col, amount_col]].copy()
    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df = df.dropna(subset=[date_col, customer_col])
    df[amount_col] = pd.to_numeric(df[amount_col], errors='coerce').fillna(0)

    # reference date = max(date) + 1 day
    max_date = df[date_col].max()
    ref_date = max_date + timedelta(days=1)

    agg = df.groupby(customer_col).agg({
        date_col: lambda x: (ref_date - x.max()).days,
        customer_col: 'count',
        amount_col: 'sum'
    }).rename(columns={
        date_col: 'Recency',
        customer_col: 'Frequency',
        amount_col: 'Monetary'
    }).reset_index()

    # RFM scoring (1-5)
    agg['R_Score'] = pd.qcut(agg['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
    agg['F_Score'] = pd.qcut(agg['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    agg['M_Score'] = pd.qcut(agg['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)

    agg['RFM_Score'] = agg['R_Score'].map(str) + agg['F_Score'].map(str) + agg['M_Score'].map(str)
    agg['RFM_Sum'] = agg['R_Score'] + agg['F_Score'] + agg['M_Score']

    return agg, ref_date, df[date_col].min(), max_date


if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(('xls', 'xlsx')):
            raw = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            raw = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Could not read uploaded file: {e}")
        st.stop()

    st.success(f"Loaded file: {uploaded_file.name}")
    st.write("Preview of uploaded data:")
    st.dataframe(raw.head())

    cols = raw.columns.tolist()
    st.markdown("### Select columns")
    date_col = st.selectbox("Order date column", options=cols)
    customer_col = st.selectbox("Customer id / name column", options=cols, index=0)
    amount_col = st.selectbox("Amount column", options=cols, index=0)

    if st.button("Run RFM Analysis"):
        with st.spinner("Computing RFM..."):
            rfm_table, ref_date, min_date, max_date = compute_rfm(raw, date_col, customer_col, amount_col)

        days_span = (max_date - min_date).days if pd.notnull(min_date) and pd.notnull(max_date) else None

        st.markdown("### Date range for analysis")
        st.write(f"Min date in data: {min_date}")
        st.write(f"Max date in data: {max_date}")
        if days_span is not None:
            st.write(f"Analysis covers {days_span} days (used reference date {ref_date.date()}).")

        st.markdown("### RFM Results")
        st.dataframe(rfm_table.sort_values('RFM_Sum', ascending=False).reset_index(drop=True))

        st.markdown("### Summary stats")
        col1, col2, col3 = st.columns(3)
        col1.metric("Customers", f"{rfm_table.shape[0]:,}")
        col2.metric("Avg Recency", f"{rfm_table['Recency'].mean():.1f} days")
        col3.metric("Avg Monetary", f"{rfm_table['Monetary'].mean():.2f}")

        st.markdown("### RFM score distribution")
        rfm_counts = rfm_table['RFM_Score'].value_counts().sort_index()
        st.bar_chart(rfm_counts)

        # Provide download
        csv = rfm_table.to_csv(index=False).encode('utf-8')
        st.download_button("Download RFM results (CSV)", data=csv, file_name='rfm_results.csv', mime='text/csv')

else:
    st.info("Upload an Excel or CSV file to get started.")
