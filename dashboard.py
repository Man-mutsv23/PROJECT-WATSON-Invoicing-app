import streamlit as st
import pandas as pd
from app import _load_data, create_invoice, mark_invoice_as_paid, delete_invoice

# Page configuration for a professional look
st.set_page_config(page_title="Freelance Finance Hub", layout="wide")

# --- SIDEBAR: Input Form ---
st.sidebar.header("➕ New Invoice")
with st.sidebar.form("invoice_form", clear_on_submit=True):
    client = st.text_input("Client Name")
    amount = st.number_input("Amount ($)", min_value=0.0, step=50.0)
    desc = st.text_area("Description")
    
    if st.form_submit_button("Create Invoice"):
        if client and amount > 0:
            msg = create_invoice(client, amount, desc)
            st.sidebar.success(msg)
            st.rerun()
        else:
            st.sidebar.error("Please enter a client and amount.")

# --- MAIN UI: Tabs ---
st.title("💼 Freelance Finance Hub")
tab1, tab2 = st.tabs(["📊 Overview", "⚙️ Management"])

data = _load_data()
invoices = data.get('invoices', [])

# TAB 1: Visuals
with tab1:
    if not invoices:
        st.info("No data available yet. Create your first invoice!")
    else:
        # Calculate totals from your existing logic
        total_paid = sum(i['amount'] for i in invoices if i.get('status') == 'Paid')
        total_pending = sum(i['amount'] for i in invoices if i.get('status') == 'Pending')
        
        c1, c2 = st.columns(2)
        c1.metric("Total Paid", f"${total_paid:,.2f}")
        c2.metric("Total Pending", f"${total_pending:,.2f}")
        
        # Simple Bar Chart
        df = pd.DataFrame(invoices)
        st.bar_chart(df.groupby('status')['amount'].sum())

# TAB 2: Action Center
with tab2:
    if not invoices:
        st.write("No invoices to manage.")
    else:
        # Table Header
        h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
        h1.write("**Client**")
        h2.write("**Amount**")
        h3.write("**Status**")
        h4.write("**Action**")
        st.divider()
        
        for idx, inv in enumerate(invoices):
            r1, r2, r3, r4 = st.columns([2, 1, 1, 1])
            r1.write(inv['client'])
            r2.write(f"${inv['amount']:,.2f}")
            r3.write(f"**{inv['status']}**")
            
            # Using idx in the key ensures no 'StreamlitDuplicateElementKey' error
            if inv['status'] == "Pending":
                if r4.button("Confirm Paid", key=f"pay_{inv['id']}_{idx}"):
                    mark_invoice_as_paid(inv['id'])
                    st.rerun()
            else:
                if r4.button("Delete", key=f"del_{inv['id']}_{idx}"):
                    delete_invoice(inv['id'])
                    st.rerun()