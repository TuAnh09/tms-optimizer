import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

st.set_page_config(page_title="TMS - Tối ưu tuyến đường", layout="wide")
st.title("🚚 Ứng dụng TMS tối ưu hóa tuyến đường")

# Nhập dữ liệu đơn hàng
st.sidebar.header("📦 Nhập đơn hàng")
address = st.sidebar.text_input("Địa chỉ (mô tả)")
lat = st.sidebar.number_input("Latitude", format="%.6f")
lng = st.sidebar.number_input("Longitude", format="%.6f")
weight = st.sidebar.number_input("Trọng lượng", min_value=0.0)

if "orders" not in st.session_state:
    st.session_state.orders = []

if st.sidebar.button("Thêm đơn hàng"):
    st.session_state.orders.append({
        "address": address,
        "lat": lat,
        "lng": lng,
        "weight": weight
    })

df = pd.DataFrame(st.session_state.orders)
st.subheader("📋 Danh sách đơn hàng")
st.dataframe(df)

# Tối ưu tuyến đường
if st.button("🚀 Tối ưu tuyến đường"):
    if len(df) < 2:
        st.warning("Cần ít nhất 2 đơn hàng để tối ưu.")
    else:
        locations = list(zip(df['lat'], df['lng']))
        distance_matrix = [
            [int(geodesic(a, b).km) for b in locations]
            for a in locations
        ]

        manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
        routing = pywrapcp.RoutingModel(manager)

        def distance_callback(i, j):
            return distance_matrix[manager.IndexToNode(i)][manager.IndexToNode(j)]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.time_limit.seconds = 10
        solution = routing.SolveWithParameters(search_parameters)

        route = []
        index = routing.Start(0)
        while not routing.IsEnd(index):
            route.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        route.append(manager.IndexToNode(index))

        # Hiển thị bản đồ
        st.subheader("🗺️ Bản đồ tuyến đường tối ưu")
        m = folium.Map(location=locations[0], zoom_start=13)
        for i in route:
            folium.Marker(locations[i], tooltip=f"Order {i}: {df.iloc[i]['address']}").add_to(m)
        folium.PolyLine([locations[i] for i in route], color="blue").add_to(m)
        st_folium(m, width=800, height=500)

        # Báo cáo
        total_distance = sum(
            geodesic(locations[route[i]], locations[route[i+1]]).km
            for i in range(len(route)-1)
        )
        st.subheader("📊 Báo cáo kết quả")
        st.metric("Tổng quãng đường", f"{total_distance:.2f} km")
        st.metric("Số đơn hàng", len(df))
        st.metric("Thứ tự giao hàng", " → ".join([str(i) for i in route]))
