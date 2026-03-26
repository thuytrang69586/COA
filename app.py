import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Thay link SheetDB của bạn vào đây
API_URL = "DÁN_LINK_SHEETDB_CỦA_BẠN_VÀO_ĐÂY"

st.title("📊 Quản lý Dữ liệu Nhóm (SheetDB)")

# 1. FORM NHẬP LIỆU
with st.sidebar:
    st.header("📥 Nhập dữ liệu mới")
    with st.form("input_form"):
        ngay = st.date_input("Ngày", datetime.now())
        san_pham = st.text_input("Tên sản phẩm")
        gia_nhap = st.number_input("Giá nhập", min_value=0)
        gia_ban = st.number_input("Giá bán", min_value=0)
        submit = st.form_submit_button("Lưu dữ liệu")

        if submit:
            data = {"Ngay": str(ngay), "San_Pham": san_pham, "Gia_Nhap": gia_nhap, "Gia_Ban": gia_ban}
            response = requests.post(API_URL, json={"data": [data]})
            if response.status_code == 201:
                st.success("Đã lưu thành công!")
                st.rerun()

# 2. HIỂN THỊ & TÍNH TOÁN
response = requests.get(API_URL)
if response.status_code == 200:
    df = pd.DataFrame(response.json())
    if not df.empty:
        df['Gia_Nhap'] = pd.to_numeric(df['Gia_Nhap'])
        df['Gia_Ban'] = pd.to_numeric(df['Gia_Ban'])
        df['Loi_Nhuan'] = df['Gia_Ban'] - df['Gia_Nhap']
        
        st.dataframe(df, use_container_width=True)
        
        # Biểu đồ
        fig = px.bar(df, x="San_Pham", y="Loi_Nhuan", title="Lợi nhuận theo sản phẩm")
        st.plotly_chart(fig)
