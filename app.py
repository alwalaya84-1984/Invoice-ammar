import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import pytesseract
from PIL import Image
import re

st.set_page_config(page_title="Invoice Generator", page_icon="🧾")

st.title("🧾 Invoice Generator")
st.caption("Prepared by: Ammar | Contact: +973 38488644")

uploaded_file = st.file_uploader("📸 ارفع صورة الفاتورة للقراءة التلقائية", type=["png", "jpg", "jpeg"])

def extract_from_image(image):
    text = pytesseract.image_to_string(image)
    date_match = re.search(r'(\d{2,4}[/-]\d{1,2}[/-]\d{1,2,4})', text)
    invoice_match = re.search(r'(Invoice|INV)[\s#:]*([A-Z0-9/-]+)', text, re.I)
    return {
        'date': date_match.group(1) if date_match else datetime.now().strftime("%Y/%m/%d"),
        'invoice': invoice_match.group(2) if invoice_match else "",
        'raw_text': text
    }

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="الصورة المرفوعة", width=300)
    extracted = extract_from_image(img)
    default_date = extracted['date']
    default_invoice = extracted['invoice']
    st.success("تم قراءة البيانات من الصورة. راجعها وعدل لو فيها خطأ")
    with st.expander("النص المستخرج من الصورة"):
        st.text(extracted['raw_text'])
else:
    default_date = datetime.now().strftime("%Y/%m/%d")
    default_invoice = "BC/01/05-2026"

date = st.text_input("Date", value=default_date)
invoice_no = st.text_input("Invoice No.", value=default_invoice)
consignee = st.text_area("Consignee", value="M/S BLOOM SECURE CO. WLL\nMANAMA, BAHRAIN")

st.subheader("Items")
default_data = pd.DataFrame([
    {"Item": "Alarm Control Panel", "QTY": 1, "UNIT PRICE USD": 750},
])
edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True)

if st.button("Generate Excel", type="primary"):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        header_df = pd.DataFrame([
            ["Prepared by: Ammar | Contact: +973 38488644"],
            ["Date:", date],
            ["Invoice No.:", invoice_no],
            ["Consignee:", consignee],
            []
        ])
        header_df.to_excel(writer, index=False, header=False, startrow=0)
        edited_df.to_excel(writer, index=False, startrow=6)
    
    st.download_button(
        label="📥 Download Excel",
        data=output.getvalue(),
        file_name=f"{invoice_no}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
