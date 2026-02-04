import streamlit as st
import pandas as pd
from app import _load_data, create_invoice, mark_invoice_as_paid, delete_invoice, record_partial_payment

# Page configuration for a professional look
st.set_page_config(page_title="Freelance Finance Hub", layout="wide")
df = pd.DataFrame()
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
# Added 'History' tab here
tab1, tab2, tab3 = st.tabs(["📊 Overview", "⚙️ Management", "📜 History"])

data = _load_data()
invoices = data.get('invoices', [])

# TAB 1: Visuals (Ensure df is always defined to fix your error)
with tab1:
    df = pd.DataFrame(invoices) # Define df immediately
    
    if df.empty:
        st.info("No data available yet. Create your first invoice!")
    else:
        total_paid = df[df['status'] == 'Paid']['amount'].sum()
        total_pending = df[df['status'] == 'Pending']['amount'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Total Paid", f"${total_paid:,.2f}")
        c2.metric("Total Pending", f"${total_pending:,.2f}")
        st.bar_chart(df.groupby('status')['amount'].sum())
    
    st.divider()
    st.subheader("📥 Export Financial Data")
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Invoices as CSV", data=csv, file_name='finance_report.csv', mime='text/csv')
    else:
        st.write("No data available to export yet.")

# TAB 2: Management (Now with Partial Payment and Delete)
with tab2:
    pending_invoices = [i for i in invoices if i['status'] == 'Pending']
    if not pending_invoices:
        st.write("No pending invoices to manage.")
    else:
        # Header for the table
        h1, h2, h3, h4 = st.columns([2, 1, 1, 1])
        h1.write("**Client (Owed)**")
        h2.write("**Pay Amount**")
        h3.write("**Record**")
        h4.write("**Remove**")
        st.divider()

        for idx, inv in enumerate(pending_invoices):
            # Calculate what's still due
            balance = inv['amount'] - inv.get('paid_amount', 0.0)
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(f"**{inv['client']}**")
            col1.caption(f"Due: ${balance:,.2f} / Total: ${inv['amount']:,.2f}")
            
            # Partial payment input
            pay_amt = col2.number_input("Amt", min_value=0.0, max_value=balance, key=f"pay_{inv['id']}")
            
            if col3.button("Apply", key=f"btn_{inv['id']}"):
                if pay_amt > 0:
                    record_partial_payment(inv['id'], pay_amt)
                    st.rerun()

            # Direct delete for mistakes
            if col4.button("🗑️", key=f"del_{inv['id']}"):
                delete_invoice(inv['id'])
                st.rerun()
# TAB 3: History (The new tab you requested)
with tab3:
    st.subheader("Invoice History")
    if not invoices:
        st.write("Your history is empty.")
    else:
        # Show all invoices, including Paid ones
        for inv in invoices:
            h_col1, h_col2, h_col3 = st.columns([2, 1, 1])
            status_color = "🟢" if inv['status'] == "Paid" else "🟡"
            h_col1.write(f"{status_color} {inv['client']} - {inv['date']}")
            h_col2.write(f"${inv['amount']:,.2f}")
            
            # Allow deletion of Paid/Incorrect invoices here too
            if h_col3.button("Remove Record", key=f"hist_del_{inv['id']}"):
                delete_invoice(inv['id'])
                st.rerun()