import streamlit as st
import folium # type: ignore
import networkx as nx # type: ignore
import requests
from folium import plugins # type: ignore
from streamlit_folium import st_folium # type: ignore

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

# Fungsi untuk membuat peta dan menambahkan marker
def create_map(city_connections, city_coordinates, selected_cities):
    # Memulai peta di posisi tengah Indonesia
    map_center = [-6.1754, 106.6321]  # Lokasi Tangerang sebagai pusat default
    m = folium.Map(location=map_center, zoom_start=8)

    # Menambahkan marker untuk kota yang dipilih
    for city, coords in city_coordinates.items():
        if city in selected_cities:
            folium.Marker(
                location=[coords["lat"], coords["lon"]],
                popup=city,
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)

    # Membuat grafik jaringan untuk visualisasi hubungan antar kota
    G = nx.Graph()

    # Menambahkan simpul (nodes)
    for city in city_connections:
        G.add_node(city)

    # Menambahkan hubungan (edges)
    for city, connections in city_connections.items():
        for connected_city in connections:
            if connected_city in city_connections:  # Pastikan kota tujuan ada
                G.add_edge(city, connected_city)

    # Menambahkan edge ke peta sebagai garis
    for edge in G.edges():
        if edge[0] in city_coordinates and edge[1] in city_coordinates:
            if edge[0] in selected_cities and edge[1] in selected_cities:  # Tampilkan hanya jika kedua kota dipilih
                city1_coords = city_coordinates[edge[0]]
                city2_coords = city_coordinates[edge[1]]
                folium.PolyLine(
                    locations=[[city1_coords["lat"], city1_coords["lon"]], [city2_coords["lat"], city2_coords["lon"]]],
                    color="red", weight=2.5, opacity=1
                ).add_to(m)
        else:
            st.warning(f"City {edge[0]} or {edge[1]} not found in coordinates.")

    return m

# UI untuk aplikasi Streamlit
def app():
    st.title("Visualisasi Jaringan Kota")

    # URL file JSON yang berisi koneksi antar kota
    url = "https://raw.githubusercontent.com/Achphasesyafiq/Discrete-2/refs/heads/main/koneksi%201.json"

    # Memuat data dari GitHub
    city_connections = load_data_from_github(url)

    if not city_connections:
        st.error("Gagal memuat data atau URL tidak valid.")
        return

    # Memilih provinsi
    provinces = list(city_connections.keys())
    selected_province = st.selectbox("Pilih Provinsi", provinces)

    # Memuat koordinat kota untuk provinsi yang dipilih
    city_coordinates = load_city_coordinates().get(selected_province, {})

    # Mendapatkan koneksi kota dari provinsi yang dipilih
    province_connections = city_connections.get(selected_province, {})

    # Menambahkan checkbox untuk memilih kota yang akan ditampilkan
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

        # Membuat peta interaktif
        m = create_map(province_connections, city_coordinates, selected_cities)

        # Menampilkan peta dengan Streamlit
        st_folium(m)
    else:
        st.error("Data koneksi untuk provinsi ini tidak ditemukan.")

# Fungsi untuk menampilkan peta di Streamlit
if __name__ == "__main__":
    app()
