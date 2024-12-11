import streamlit as st
import folium  # type: ignore
import networkx as nx  # type: ignore
import requests
import matplotlib.pyplot as plt
import random
from streamlit_folium import st_folium  # type: ignore

# Fungsi untuk mengambil data JSON dari GitHub atau URL lain
def load_data_from_github(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from GitHub: {e}")
        return {}

# Fungsi untuk memuat data kota dan koordinatnya
def load_city_coordinates():
    # Koordinat untuk kota-kota di berbagai provinsi
    return {
        "Banten": {
            "Serang": {"lat": -6.1169309, "lon": 106.1538494},
            "Tangerang": {"lat": -6.176654, "lon": 106.633728},
            "Tangerang Selatan": {"lat": -6.342414, "lon": 106.738881},
            "Cilegon": {"lat": -6.0186834, "lon": 106.0558263},
            "Pandeglang": {"lat": -6.308830, "lon": 106.106520},
            "Serpong": {"lat": -6.300641, "lon": 106.652548}
        },
        "Jawa Barat": {
            "Bandung": {"lat": -6.917464, "lon": 107.619123},
            "Bekasi": {"lat": -6.238270, "lon": 106.975573},
            "Bogor": {"lat": -6.597147, "lon": 106.806039},
            "Depok": {"lat": -6.402484, "lon": 106.794241},
            "Sukabumi": {"lat": -6.919917, "lon": 106.927229},
            "Cirebon": {"lat": -6.706275, "lon": 108.557016},
            "Garut": {"lat": -7.210933, "lon": 107.906349},
            "Tasikmalaya": {"lat": -7.327406, "lon": 108.220985},
            "Karawang": {"lat": -6.323015, "lon": 107.337579},
            "Purwakarta": {"lat": -6.556962, "lon": 107.432252}
        }
    }

# Fungsi untuk membuat peta
def create_map(city_connections, city_coordinates, selected_cities):
    map_center = [-6.1754, 106.6321]
    m = folium.Map(location=map_center, zoom_start=8)

    for city, coords in city_coordinates.items():
        if city in selected_cities:
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                popup=city,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

    G = nx.Graph()
    for city in city_connections:
        G.add_node(city)
    for city, connections in city_connections.items():
        for connected_city in connections:
            if connected_city in city_connections:
                G.add_edge(city, connected_city)

    for edge in G.edges():
        if edge[0] in city_coordinates and edge[1] in city_coordinates:
            if edge[0] in selected_cities and edge[1] in selected_cities:
                city1_coords = city_coordinates[edge[0]]
                city2_coords = city_coordinates[edge[1]]
                folium.PolyLine(
                    locations=[[city1_coords["lat"], city1_coords["lon"]], [city2_coords["lat"], city2_coords["lon"]]],
                    color="red", weight=2.5, opacity=1
                ).add_to(m)

    return m

# Fungsi untuk membuat dan memvisualisasikan graf
def create_graph_and_visualize(num_nodes, num_edges):
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))

    added_edges = 0
    while added_edges < num_edges:
        node1, node2 = random.sample(range(num_nodes), 2)
        if not G.has_edge(node1, node2):
            G.add_edge(node1, node2)
            added_edges += 1

    fig, ax = plt.subplots()
    nx.draw(G, with_labels=True, node_color='skyblue', node_size=500, font_size=10, font_weight='bold', ax=ax)
    ax.set_title(f"Graph with {num_nodes} Nodes and {num_edges} Edges")
    st.pyplot(fig)

# Menu utama
def main():
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Pilih Menu", ["Profil", "Graph", "Peta Koneksi Kota"])

    if menu == "Profil":
        st.title("Profil Tim")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.image("https://github.com/Achphasesyafiq/Discrete-2/blob/main/021202400001__ACHMAD_PHASE_SYAFIQ.jpg?raw=true")
            st.write("Nama: Achmad Phase Syafiq")
            st.write("Prodi: Actuarial Science")

        with col2:
            st.image("https://github.com/Achphasesyafiq/Discrete-2/blob/main/WhatsApp%20Image%202024-12-11%20at%2016.18.48_551fd3ff.jpg?raw=true")
            st.write("Nama: Richela Machalaren Yasper")
            st.write("Prodi: Actuarial Science")

        with col3:
            st.image("https://github.com/Achphasesyafiq/Discrete-2/blob/main/WhatsApp%20Image%202024-12-11%20at%2016.18.47_142de48d.jpg?raw=true")
            st.write("Nama: Rahel Jennia Sembiring")
            st.write("Prodi: Actuarial Science")

    elif menu == "Graph":
        st.title("Graph Visualization")
        num_nodes = st.number_input("Enter the number of nodes:", min_value=2, value=5, step=1)
        num_edges = st.number_input("Enter the number of edges:", min_value=1, value=4, step=1)

        if st.button("Generate Graph"):
            create_graph_and_visualize(num_nodes, num_edges)

    elif menu == "Peta Koneksi Kota":
        st.title("Visualisasi Jaringan Kota")
        url = "https://raw.githubusercontent.com/Achphasesyafiq/Discrete-2/refs/heads/main/koneksi%201.json"
        city_connections = load_data_from_github(url)

        if not city_connections:
            st.error("Gagal memuat data atau URL tidak valid.")
            return

        provinces = list(city_connections.keys())
        selected_province = st.selectbox("Pilih Provinsi", provinces)
        city_coordinates = load_city_coordinates().get(selected_province, {})
        province_connections = city_connections.get(selected_province, {})

        st.write("Pilih Kota yang Akan Ditampilkan:")
        selected_cities = []
        for city in city_coordinates.keys():
            if st.checkbox(city, value=True):
                selected_cities.append(city)

        if not selected_cities:
            st.warning("Silakan pilih setidaknya satu kota untuk ditampilkan.")
            return

        if province_connections:
            st.write(f"Menampilkan koneksi kota untuk Provinsi {selected_province}...")
            m = create_map(province_connections, city_coordinates, selected_cities)
            st_folium(m)
        else:
            st.error("Data koneksi untuk provinsi ini tidak ditemukan.")

if __name__ == "__main__":
    main()
