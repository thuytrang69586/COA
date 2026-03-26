import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import datetime

# Cấu hình trang web
st.set_page_config(page_title="Quản lý Data_Web", layout="wide")
st.title("📊 Hệ thống Nhập liệu & Phân tích Dữ liệu")

# 1. KẾT NỐI GOOGLE SHEETS
# (Bạn cần cấu hình secrets trong Streamlit Cloud để kết nối với file 'Data_Web')
conn = st.connection("gsheets", type=GSheetsConnection)

# Đọc dữ liệu hiện tại
df = conn.read()

# 2. FORM NHẬP LIỆU HÀNG NGÀY
with st.sidebar:
    st.header("📥 Nhập dữ liệu mới")
    with st.form("input_form"):
        ngay = st.date_input("Ngày", datetime.now())
        san_pham = st.text_input("Tên sản phẩm")
        gia_nhap = st.number_input("Giá nhập", min_value=0, step=1000)
        gia_ban = st.number_input("Giá bán", min_value=0, step=1000)
        submit = st.form_submit_button("Lưu vào hệ thống")

        if submit:
            if san_pham:
                # Tạo dòng dữ liệu mới
                new_data = pd.DataFrame([{"Ngay": ngay.strftime('%Y-%m-%d'), 
                                          "San_Pham": san_pham, 
                                          "Gia_Nhap": gia_nhap, 
                                          "Gia_Ban": gia_ban}])
                # Cập nhật vào Google Sheets
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Đã lưu dữ liệu thành công!")
                st.rerun()
            else:
                st.error("Vui lòng nhập tên sản phẩm")

# 3. TRÍCH XUẤT & TÍNH TOÁN
if not df.empty:
    # Chuyển đổi kiểu dữ liệu số
    df['Gia_Nhap'] = pd.to_numeric(df['Gia_Nhap'])
    df['Gia_Ban'] = pd.to_numeric(df['Gia_Ban'])
    # Tự động tính Lợi nhuận
    df['Loi_Nhuan'] = df['Gia_Ban'] - df['Gia_Nhap']

    # 4. BỘ LỌC TRUY XUẤT
    st.header("🔍 Truy xuất & So sánh")
    col1, col2 = st.columns(2)
    with col1:
        filter_sp = st.multiselect("Chọn sản phẩm:", options=df["San_Pham"].unique(), default=df["San_Pham"].unique())
    
    # Lọc dữ liệu theo lựa chọn
    mask = df["San_Pham"].isin(filter_sp)
    filtered_df = df[mask]

    # Hiển thị bảng dữ liệu đã tính toán
    st.dataframe(filtered_df, use_container_width=True)

    # 5. BIỂU ĐỒ SO SÁNH HIỆU SUẤT
    st.header("📈 Biểu đồ so sánh Lợi nhuận")
    tab1, tab2 = st.tabs(["Theo Sản phẩm", "Theo Ngày"])
    
    with tab1:
        fig_sp = px.bar(filtered_df, x="San_Pham", y="Loi_Nhuan", color="San_Pham", title="Lợi nhuận theo từng mặt hàng")
        st.plotly_chart(fig_sp, use_container_width=True)
    
    with tab2:
        fig_date = px.line(filtered_df, x="Ngay", y="Loi_Nhuan", markers=True, title="Biến động lợi nhuận theo thời gian")
        st.plotly_chart(fig_date, use_container_width=True)
else:
    st.info("Chưa có dữ liệu. Vui lòng nhập dữ liệu ở thanh bên trái.")
