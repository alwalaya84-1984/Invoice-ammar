import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Invoice - Ammar", page_icon="🧾", layout="wide")

SHIPPER_NAME = "Ammar"
SHIPPER_CONTACT = "38488644"

st.title("🧾 Invoice Generator")
st.caption(f"Prepared by: {SHIPPER_NAME} | Contact: +973 {SHIPPER_CONTACT}")

col1, col2 = st.columns(2)
with col1:
    inv_date = st.date_input("Date", value=date(2026, 2, 26))
    inv_no = st.text_input("Invoice No.", "BC/22/02-2026")
with col2:
    consignee = st.text_area("Consignee", "M/S BLOOM SECURE CO. WLL\nMANAMA, BAHRAIN")

df = pd.DataFrame({
    'ITEMS DESCRIPTION': ['Intelligent 4 Loop Fire Alarm Control Panel','Addressable Photo Electric Smoke Detector'],
    'QTY': [1,225], 'UNIT PRICE USD': [750,14]
})
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
edited_df['TOTAL USD'] = edited_df['QTY'] * edited_df['UNIT PRICE USD']
total = edited_df['TOTAL USD'].sum()
st.metric("TOTAL C & F USD", f"${total:,.2f}")

if st.button("📥 Download Excel"):
    with pd.ExcelWriter('Invoice.xlsx', engine='openpyxl') as writer:
        edited_df.to_excel(writer, sheet_name='Items', index=False)
    with open('Invoice.xlsx', 'rb') as f:
        st.download_button('⬇️ تحميل الفاتورة', f, file_name=f'Invoice_{inv_no}.xlsx')

st.caption(f"© 2026 {SHIPPER_NAME} | +973 {SHIPPER_CONTACT}")
