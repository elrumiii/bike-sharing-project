import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import os

sns.set(style='whitegrid')

@st.cache_data
def load_data():
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "main_data(1).csv")
    
    df = pd.read_csv(file_path)
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
    st.write(""" Hasil analisis menunjukkan adanya perbedaan pola konsumsi yang kontras antara hari kerja dan hari libur, di mana hari kerja didominasi oleh pola komuter dengan dua puncak utama (rush hour) pada pukul 08:00 dan 17:00, sementara hari libur mencerminkan pola rekreasi dengan lonjakan permintaan yang stabil di tengah hari antara pukul 12:00 hingga 15:00. Temuan ini memberikan implikasi strategis bagi perusahaan untuk melakukan optimalisasi stok melalui distribusi unit maksimal di area residensial pada pagi hari kerja serta area perkantoran pada sore hari guna menangkap peluang permintaan tertinggi. Selain itu, perusahaan dapat meningkatkan efisiensi operasional dengan menjadwalkan perawatan sepeda (maintenance) pada jendela waktu rendah permintaan, yaitu pukul 10:00–14:00 di hari kerja dan sebelum pukul 10:00 di hari libur, guna memastikan ketersediaan unit tetap prima saat memasuki jam-jam sibuk..""")

st.subheader("Pengaruh Kecepatan Angin terhadap Jumlah Penyewaan")

with st.container():
    fig, ax = plt.subplots(figsize=(10, 6))
    category_order = ['Rendah', 'Sedang', 'Tinggi', 'Ekstrem']
    sns.barplot(
    data=day_df, 
    x='windspeed_category', 
    y='cnt', 
    order=category_order, 
    hue='windspeed_category', 
    palette='Reds_r',
    legend=False,            
    errorbar=None,
    ax=ax # Penting: masukkan ke axis yang sudah dibuat
    )

    ax.set_title('Pengaruh Kategori Kecepatan Angin terhadap Jumlah Penyewaan', fontsize=14)
    ax.set_xlabel('Kategori Kecepatan Angin', fontsize=12)
    ax.set_ylabel('Rata-rata Jumlah Penyewaan', fontsize=12)

# Menampilkan di Streamlit
    st.pyplot(fig)

with st.expander("insight"):
    st.write("""
    Berdasarkan hasil analisis, ditemukan bahwa kecepatan angin memiliki korelasi negatif yang nyata terhadap minat pengguna, di mana terjadi penurunan drastis jumlah penyewaan saat kondisi berpindah dari kategori 'Sedang' ke 'Tinggi' dan 'Ekstrem'. Hal ini menunjukkan bahwa faktor keamanan serta kenyamanan menjadi prioritas utama bagi pengguna dalam memutuskan untuk bersepeda. Sebagai langkah strategis, perusahaan dapat menerapkan kebijakan dynamic pricing berupa pemberian promo atau diskon otomatis saat sensor cuaca mendeteksi angin kategori 'Sedang' hingga 'Tinggi' guna menstimulasi permintaan yang cenderung menurun. Selain itu, integrasi sistem peringatan dini (safety alert) pada aplikasi untuk memberikan notifikasi keamanan saat angin kencang dapat meningkatkan kepercayaan dan loyalitas pelanggan. Terakhir, dari sisi efisiensi biaya, perusahaan dapat mengoptimalkan pengeluaran dengan mengurangi jumlah staf lapangan atau operasional truk penyeimbang (rebalancing truck) pada hari-hari dengan prakiraan angin 'Ekstrem', mengingat volume transaksi dipastikan rendah pada kondisi tersebut.""")

st.subheader("Komposisi Pengguna")
user_counts = [filtered_df.casual.sum(), filtered_df.registered.sum()]
user_labels = ['Casual', 'Registered']

fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
ax_pie.pie(user_counts, labels=user_labels, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=140)
ax_pie.axis('equal')  # Agar bentuknya lingkaran sempurna
st.pyplot(fig_pie)





