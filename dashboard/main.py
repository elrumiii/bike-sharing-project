import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='whitegrid')

@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df

main_df = load_data()

def kategori_jam(hour):
    if 5 <= hour <= 9: return 'Pagi (Berangkat)'
    elif 10 <= hour <= 15: return 'Siang (Rekreasi)'
    elif 16 <= hour <= 19: return 'Sore (Pulang)'
    else: return 'Malam/Dini Hari'

main_df['waktu_hari'] = main_df['hr'].apply(kategori_jam)

# SIDEBAR 
with st.sidebar:
    st.header("Bike Sharing")
    min_date = main_df["dteday"].min()
    max_date = main_df["dteday"].max()
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_df = main_df[(main_df["dteday"] >= pd.to_datetime(start_date)) & 
                      (main_df["dteday"] <= pd.to_datetime(end_date))]

# DASHBOARD DISPLAY
st.title('Bike Sharing Analytics Dashboard:sparkles:')

# --- METRIC SECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    total_rentals = filtered_df.cnt.sum()
    st.metric("Total Penyewaan", value=f"{total_rentals:,}")

with col2:
    # Menghitung persentase pengguna registered
    total_reg = filtered_df.registered.sum()
    reg_ratio = (total_reg / total_rentals) * 100 if total_rentals > 0 else 0
    st.metric("Pengguna Berlangganan (Reg)", value=f"{total_reg:,}", delta=f"{reg_ratio:.1f}%")

with col3:
    # Menampilkan rata-rata suhu (pastikan dikalikan 41 jika datanya masih ternormalisasi)
    # Jika data Anda sudah bersih dan dalam Celcius, langsung gunakan .mean()
    avg_temp = filtered_df.temp.mean() * 41 
    st.metric("Rata-rata Suhu", value=f"{avg_temp:.1f} °C")

# Pertanyaan 1: Blok Waktu
st.subheader('Penggunaan Sepeda Berdasarkan Blok Waktu')

# Membuat plot Matplotlib
with st.container():
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(
    data=filtered_df, 
    x='waktu_hari', 
    y='cnt', 
    hue='workingday', 
    estimator='mean',
    order=['Pagi (Berangkat)', 'Siang (Rekreasi)', 'Sore (Pulang)', 'Malam/Dini Hari'],
    palette='viridis',
    ax=ax
)
# Merapikan tampilan seperti kode Anda
    ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Blok Waktu', fontsize=14)
    ax.set_xlabel('Blok Waktu', fontsize=12)
    ax.set_ylabel('Rata-rata Jumlah Penyewa', fontsize=12)
    ax.legend(title='Hari', labels=['Libur (0)', 'Kerja (1)'])
    ax.grid(axis='y', linestyle='--', alpha=0.7)
# Menampilkan di Streamlit
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
    data=filtered_df, 
    x='hr', 
    y='cnt', 
    hue='workingday', 
    marker='o', 
    ax=ax
)
    ax.set_title("Pola Penggunaan Sepeda: Hari Kerja vs Hari Libur")
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Rata-rata Penyewaan")
    ax.legend(title="Tipe Hari", labels=["Hari Libur/Weekend", "Hari Kerja"])
    st.pyplot(fig)

with st.expander("Insight"):
    st.write(""" Berdasarkan kedua visualisasi tersebut, dapat disimpulkan bahwa penggunaan sepeda mencapai puncaknya pada jam berangkat (08:00) dan pulang kantor (17:00) di hari kerja, sedangkan pada hari libur penggunaan cenderung stabil dengan puncak tunggal di siang hari (12:00-15:00) untuk aktivitas rekreasi.""")

st.subheader("Apakah Kecepatan Angin Menurunkan Minat Sewa?")

with st.container():
    bins = [0, 0.1, 0.3, 0.5, 1.0]
    labels = ['Rendah', 'Sedang', 'Tinggi', 'Ekstrem']
    filtered_df['wind_category'] = pd.cut(filtered_df['windspeed'], bins=bins, labels=labels)

# 2. Membuat Visualisasi Bar Chart
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
    data=filtered_df, 
    x='wind_category', 
    y='cnt', 
    palette='Blues_d', 
    estimator='mean',
    capsize=.1,
    ax=ax
)

# 3. Merapikan Tampilan
    ax.set_title('Rata-rata Penyewaan Sepeda Berdasarkan Kategori Kecepatan Angin', fontsize=14)
    ax.set_xlabel('Kategori Kecepatan Angin', fontsize=12)
    ax.set_ylabel('Rata-rata Jumlah Penyewa', fontsize=12)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

# 4. Tampilkan di Streamlit
    st.pyplot(fig)


with st.expander("insight"):
    st.write("""
    Berdasarkan bar chart tersebut, terlihat bahwa minat penyewaan sepeda tetap tinggi dan stabil pada kategori kecepatan angin Rendah hingga Sedang, bahkan seringkali mencapai puncaknya pada kondisi angin sedang karena biasanya dibarengi dengan suhu udara yang sejuk. Namun, terjadi penurunan jumlah penyewaan yang cukup terlihat saat angin memasuki kategori Tinggi, dan menurun sangat signifikan pada kategori Ekstrem. Hal ini membuktikan bahwa kecepatan angin memang menurunkan minat penyewa, tetapi efeknya baru terasa sangat drastis ketika angin sudah mencapai level yang mengganggu kenyamanan berkendara atau stabilitas sepeda di jalan.""")

st.subheader("Komposisi Pengguna")
user_counts = [filtered_df.casual.sum(), filtered_df.registered.sum()]
user_labels = ['Casual', 'Registered']

fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
ax_pie.pie(user_counts, labels=user_labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=140)
ax_pie.axis('equal')  # Agar bentuknya lingkaran sempurna
st.pyplot(fig_pie)



