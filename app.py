import streamlit as st
import pytesseract
from PIL import Image
import re
from fpdf import FPDF
import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Invoice Generator", layout="wide")
st.title("📄 Invoice Generator - Ammar")

# تهيئة الـ session state
if 'invoice_no' not in st.session_state:
    st.session_state.invoice_no = ""
if 'date' not in st.session_state:
    st.session_state.date = datetime.date.today().strftime("%d/%m/%Y")
if 'consignee' not in st.session_state:
    st.session_state.consignee = ""
if 'description' not in st.session_state:
    st.session_state.description = ""
if 'qty' not in st.session_state:
    st.session_state.qty = 1
if 'unit_price' not in st.session_state:
    st.session_state.unit_price = 0.0
if 'total_amount' not in st.session_state:
    st.session_state.total_amount = 0.0

# --- قسم قراءة الفاتورة من الصورة ---
st.subheader("📸 ارفع صورة الفاتورة للقراءة التلقائية")
uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

if uploaded_file is not None:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption="الفاتورة المرفوعة", use_column_width=True)
        
        with st.spinner('جاري قراءة الفاتورة...'):
            # قراءة بدقة عالية للجداول
            text = pytesseract.image_to_string(img, config='--psm 6')
            
            # 1. رقم الفاتورة
            inv_no = re.search(r'Invoice No\s+([A-Z0-9-]+)', text, re.IGNORECASE)
            if inv_no: 
                st.session_state.invoice_no = inv_no.group(1)
            
            # 2. التاريخ
            date = re.search(r'Date\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text, re.IGNORECASE)
            if date: 
                st.session_state.date = date.group(1)
            
            # 3. اسم الزبون - يوقف عند Flag أو Building
            consignee = re.search(r'Consignee\s*\n(.*?)(?:\nFlag:|\nBuilding:)', text, re.DOTALL | re.IGNORECASE)
            if consignee: 
                st.session_state.consignee = consignee.group(1).strip().replace('\n', ' ')
            
            # 4. الإجمالي
            total = re.search(r'Total Price\s+\$?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
            if total: 
                st.session_state.total_amount = float(total.group(1).replace(',', ''))
            
            # 5. أول بند من الجدول للوصف والسعر
            first_item = re.search(r'1\s+([A-Z0-9-]+\s+[A-Z\s]+.*?)\s+Ea\s+1\s+[\d.]+\s+([\d,]+\.?\d*)', text)
            if first_item:
                st.session_state.description = first_item.group(1).strip()
                st.session_state.unit_price = float(first_item.group(2).replace(',', ''))
                st.session_state.qty = 1
                
        st.success("✅ تمت القراءة! راجع البيانات تحت وعدل إذا احتجت")
        
    except Exception as e:
        st.error(f"خطأ في القراءة: {e}")

st.divider()

# --- قسم إدخال البيانات ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Invoice Details")
    st.session_state.invoice_no = st.text_input("Invoice No.", value=st.session_state.invoice_no)
    st.session_state.date = st.text_input("Date", value=st.session_state.date)
    st.session_state.consignee = st.text_area("Consignee", value=st.session_state.consignee, height=100)

with col2:
    st.subheader("Item Details")
    st.session_state.description = st.text_input("Description", value=st.session_state.description)
    st.session_state.qty = st.number_input("Quantity", value=int(st.session_state.qty), min_value=1)
    st.session_state.unit_price = st.number_input("Unit Price USD", value=float(st.session_state.unit_price), format="%.2f")
    st.session_state.total_amount = st.session_state.qty * st.session_state.unit_price
    st.metric("Total Amount USD", f"{st.session_state.total_amount:,.2f}")

# --- توليد PDF ---
st.divider()
if st.button("Generate Invoice PDF", type="primary"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "COMMERCIAL INVOICE", 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Invoice No: {st.session_state.invoice_no}", 0, 1)
    pdf.cell(0, 8, f"Date: {st.session_state.date}", 0, 1)
    pdf.multi_cell(0, 8, f"Consignee: {st.session_state.consignee}")
    pdf.ln(5)
    
    # جدول البنود
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 8, "Description", 1)
    pdf.cell(20, 8, "Qty", 1)
    pdf.cell(35, 8, "Unit Price", 1)
    pdf.cell(35, 8, "Total", 1, 1)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(100, 8, st.session_state.description[:50], 1)
    pdf.cell(20, 8, str(st.session_state.qty), 1)
    pdf.cell(35, 8, f"{st.session_state.unit_price:,.2f}", 1)
    pdf.cell(35, 8, f"{st.session_state.total_amount:,.2f}", 1, 1)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(155, 8, "Total Amount USD:", 0, 0, 'R')
    pdf.cell(35, 8, f"{st.session_state.total_amount:,.2f}", 1, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, "Prepared by: Ammar", 0, 1)
    
    # السطر المصحح حق fpdf2
    pdf_output = bytes(pdf.output())
    
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_output,
        file_name=f"Invoice_{st.session_state.invoice_no}.pdf",
        mime="application/pdf"
    )
