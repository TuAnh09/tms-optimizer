import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# Tiêu đề trang
st.set_page_config(page_title="TMS - Tối ưu hóa tuyến đường", layout="wide")
st.title("🚚 Ứng dụng Tối ưu hoá Tuyến đường Vận tải (TMS)")

st.write("""
Ứng dụng mô phỏng hệ thống **Transportation Management System (TMS)** — giúp nhập dữ liệu tuyến đường, 
tính toán chi phí vận chuyển và hiển thị bản đồ tuyến.
""")

# Nhập dữ liệu
st.sidebar.header("📦 Nhập dữ liệu")
uploaded_file = st.sidebar.file_uploader("Tải file CSV (chứa Tên điểm, Vĩ độ, Kinh độ, Quãng đường_km)", type="csv")

# Nếu không có file, cho phép nhập thủ công
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.sidebar.write("Hoặc nhập dữ liệu mẫu:")
    data = {
        "Tên điểm": ["Kho", "Cửa hàng A", "Cửa hàng B"],
        "Vĩ độ": [10.762622, 10.776889, 10.780100],
        "Kinh độ": [106.660172, 106.695200, 106.640000],
        "Quãng đường_km": [0, 5.2, 3.8]
    }
    df = pd.DataFrame(data)

st.subheader("📋 Dữ liệu tuyến đường")
st.dataframe(df)

# Tính toán chi phí vận tải
fuel_cost = st.sidebar.number_input("Chi phí nhiên liệu (VND/km):", value=15000)
driver_cost = st.sidebar.number_input("Chi phí tài xế (VND/giờ):", value=80000)
avg_speed = st.sidebar.number_input("Tốc độ trung bình (km/h):", value=40)

df["Thời gian (giờ)"] = df["Quãng đường_km"] / avg_speed
df["Chi phí vận chuyển (VND)"] = df["Quãng đường_km"] * fuel_cost + df["Thời gian (giờ)"] * driver_cost

st.subheader("💰 Kết quả tính toán")
st.dataframe(df)

# Tổng chi phí
total_cost = df["Chi phí vận chuyển (VND)"].sum()
st.success(f"**Tổng chi phí dự kiến:** {total_cost:,.0f} VND")

# Hiển thị bản đồ
st.subheader("🗺️ Bản đồ tuyến đường")
m = folium.Map(location=[df["Vĩ độ"].mean(), df["Kinh độ"].mean()], zoom_start=13)

for i, row in df.iterrows():
    folium.Marker(
        location=[row["Vĩ độ"], row["Kinh độ"]],
        popup=f"{row['Tên điểm']}: {row['Quãng đường_km']} km",
        icon=folium.Icon(color="blue" if i == 0 else "green")
    ).add_to(m)

st_folium(m, width=700, height=500)
