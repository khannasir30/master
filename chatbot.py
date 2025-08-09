import pandas as pd
import streamlit as st
from datetime import datetime

# ===== Load and Process Data =====
@st.cache_data
def load_data():
    file_path = r"C:\Users\Nasar_khan\Downloads\OPS MIS_BRD 3_V1.1 (1).xlsx"
    df = pd.read_excel(file_path, sheet_name="P&L")

    # Clean data
    df['Group1'] = df['Group1'].str.upper()
    df['FinalCustomerName'] = df['FinalCustomerName'].str.strip()

    # Revenue calculation
    revenue_groups = ["ONSITE", "OFFSHORE", "INDIRECT REVENUE"]
    df['Revenue'] = df.apply(lambda x: x['Amount in USD'] if x['Group1'] in revenue_groups else 0, axis=1)

    # Cost calculation
    cost_groups = [
        "DIRECT EXPENSE", "OWN OVERHEADS", "INDIRECT EXPENSE", "PROJECT LEVEL DEPRECIATION",
        "DIRECT EXPENSE - DU BLOCK SEATS ALLOCATION", "DIRECT EXPENSE - DU POOL ALLOCATION",
        "ESTABLISHMENT EXPENSES"
    ]
    df['Cost'] = df.apply(lambda x: x['Amount in USD'] if x['Group1'] in cost_groups else 0, axis=1)

    # Group by Client & Quarter
    df_grouped = df.groupby(['FinalCustomerName', 'Quarter']).agg(
        Revenue=('Revenue', 'sum'),
        Cost=('Cost', 'sum')
    ).reset_index()

    df_grouped['Margin %'] = ((df_grouped['Revenue'] - df_grouped['Cost']) / df_grouped['Revenue']) * 100
    return df_grouped

df = load_data()

# ===== Streamlit Chatbot =====
st.set_page_config(page_title="CM% Filter Chatbot", layout="centered")
st.title("📊 CM% Filter Chatbot (Live Data)")

user_query = st.chat_input("Ask: e.g., Show accounts with CM% < 30 in 2024-Q4")

if user_query:
    st.chat_message("user").write(user_query)

    # Defaults
    cm_threshold = 30
    quarter_filter = None

    # Detect CM% threshold from query
    if "<" in user_query:
        try:
            cm_threshold = int(user_query.split("<")[1].split()[0])
        except:
            pass

    # Detect quarter from query
    for q in df["Quarter"].unique():
        if str(q) in user_query:
            quarter_filter = str(q)

    # If no quarter provided, get last quarter automatically
    if not quarter_filter:
        current_quarter = (datetime.now().month - 1) // 3 + 1
        last_quarter = current_quarter - 1 if current_quarter > 1 else 4
        year = datetime.now().year if last_quarter > 0 else datetime.now().year - 1
        quarter_filter = f"{year}-Q{last_quarter if last_quarter > 0 else 4}"

    # Filter based on conditions
    filtered_df = df[(df["Margin %"] < cm_threshold) & (df["Quarter"] == quarter_filter)]
    negative_df = df[(df["Margin %"] < 0) & (df["Quarter"] == quarter_filter)]

    # Output
    st.chat_message("assistant").write(f"**Accounts with CM% < {cm_threshold} in {quarter_filter}**")
    st.chat_message("assistant").dataframe(filtered_df)

    st.chat_message("assistant").write(f"**Accounts with CM% < 0 in {quarter_filter}**")
    st.chat_message("assistant").dataframe(negative_df)
