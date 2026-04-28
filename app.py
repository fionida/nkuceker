import streamlit as st
import pandas as pd
import requests
import time

# Konfigurasi Halaman
st.set_page_config(page_title="OSS Status Checker", page_icon="🔍", layout="wide")

# Styling Header
st.title("🔍 OSS NIB & Kegiatan Usaha Checker")
st.markdown("---")

# --- SIDEBAR: KONFIGURASI API ---
st.sidebar.header("⚙️ Konfigurasi API")
st.sidebar.info("Gunakan data dari Tab Network (Inspect Element) untuk mengisi bagian ini.")

# Input untuk Token (Bearer)
api_token = st.sidebar.text_area("Masukkan Authorization Token (Bearer)", help="Tempel token panjang yang Anda temukan di tab Network.")

# Input untuk Endpoint
api_url = st.sidebar.text_input("Endpoint URL", value="https://api-prd.oss.go.id/v1/consumer-notif/v1/notification/get-status")

# --- MAIN INTERFACE: UPLOAD FILE ---
uploaded_file = st.file_uploader("Unggah File Excel Daftar Kegiatan Usaha", type=['xlsx', 'xls'])

if uploaded_file:
    # Membaca data excel
    df = pd.read_excel(uploaded_file)
    
    st.subheader("Preview Data Excel")
    st.dataframe(df.head(10)) # Tampilkan 10 baris pertama

    # Pilih kolom yang berisi ID atau Nomor Kegiatan
    kolom_id = st.selectbox("Pilih Kolom ID/Nomor Kegiatan Usaha:", df.columns)

    if st.button("🚀 Mulai Pengecekan Realtime"):
        if not api_token:
            st.error("Silakan masukkan Token Authorization di sidebar terlebih dahulu!")
        else:
            # Tempat penampung hasil
            status_list = []
            
            # Progress Bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            table_placeholder = st.empty() # Untuk update tabel secara realtime

            # Iterasi setiap baris di Excel
            for index, row in df.iterrows():
                id_target = str(row[kolom_id])
                status_text.text(f"Sedang mengecek nomor: {id_target} ({index+1}/{len(df)})")
                
                # --- LOGIKA REQUEST KE API OSS ---
                headers = {
                    "Authorization": f"Bearer {api_token.strip()}",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                # Menyiapkan parameter (Sesuaikan dengan tab Payload di Network)
                # Jika API meminta nomor_kegiatan di URL, ubah bagian ini
                params = {"id": id_target} 

                try:
                    response = requests.get(api_url, headers=headers, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data_api = response.json()
                        # --- KOREKSI PARSING DISINI ---
                        # Sesuaikan 'status' dengan field asli di JSON Response OSS
                        hasil_status = data_api.get('status', 'Data Ditemukan') 
                    elif response.status_code == 401:
                        hasil_status = "Token Expired"
                    else:
                        hasil_status = f"HTTP Error {response.status_code}"
                except Exception as e:
                    hasil_status = f"Error Koneksi: {str(e)}"

                # Masukkan ke list
                status_list.append(hasil_status)
                
                # Update Progress
                progress_bar.progress((index + 1) / len(df))
                
                # Menampilkan hasil sementara di layar (Realtime)
                # Kita buat DataFrame bayangan untuk update visual
                df_temp = df.head(index + 1).copy()
                df_temp['Status_Terbit'] = status_list
                table_placeholder.dataframe(df_temp.tail(10)) # Tampilkan 10 data terakhir yang diproses
                
                # Jeda sedikit agar tidak membebani server/kena blokir
                time.sleep(0.5)

            # Selesai Proses
            df['Status_Terbit'] = status_list
            status_text.success("✅ Pengecekan Selesai!")
            st.subheader("Hasil Akhir Keseluruhan")
            st.dataframe(df)

            # Tombol Download Hasil
            output_csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Hasil Pengecekan (.csv)",
                data=output_csv,
                file_name="hasil_cek_oss.csv",
                mime="text/csv",
            )

st.markdown("---")
st.caption("Aplikasi ini dibuat untuk kebutuhan internal. Pastikan Anda memiliki hak akses API yang sah.")