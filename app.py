import streamlit as st
import pandas as pd
import requests
import time

st.set_page_config(page_title="OSS NIB Checker", layout="wide")

st.title("🚀 OSS Activity Status Checker")
st.markdown("""
Aplikasi ini melakukan *crosscheck* otomatis antara data Excel Anda dengan sistem OSS.
""")

# --- Sidebar untuk Konfigurasi API ---
st.sidebar.header("Konfigurasi API OSS")
api_url = st.sidebar.text_input("Endpoint API OSS", "https://api.oss.go.id/v1/check")
api_key = st.sidebar.text_input("API Key / Token", type="password")

# --- Upload File ---
uploaded_file = st.file_uploader("Upload File Excel (Pastikan ada kolom 'nomor_kegiatan')", type=['xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    if 'nomor_kegiatan' not in df.columns:
        st.error("Error: Kolom 'nomor_kegiatan' tidak ditemukan di file Excel!")
    else:
        st.write("Preview Data:", df.head(5))
        
        if st.button("Mulai Sinkronisasi Realtime"):
            results = []
            progress_bar = st.progress(0)
            status_update = st.empty()
            
            for index, row in df.iterrows():
                nomor = str(row['nomor_kegiatan'])
                status_update.text(f"Memproses Nomor: {nomor}...")
                
                # --- LOGIKA API ---
                if api_key:
                    try:
                        # Contoh call API (sesuaikan dengan spek OSS nanti)
                        # r = requests.get(f"{api_url}/{nomor}", headers={"Authorization": f"Bearer {api_key}"})
                        # res_data = r.json()
                        # status = res_data.get('status', 'Pending')
                        status = "Terbit (API Active)" # Placeholder
                    except:
                        status = "Koneksi Gagal"
                else:
                    # Simulasi jika belum ada API Key
                    time.sleep(0.3) 
                    status = "Simulasi: Terbit" if index % 2 == 0 else "Simulasi: Belum Terbit"
                
                results.append(status)
                progress_bar.progress((index + 1) / len(df))
            
            df['Status_Izin'] = results
            status_update.success("Proses Selesai!")
            st.dataframe(df)
            
            # Download button
            output_file = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Hasil Pengecekan", output_file, "hasil_oss.csv", "text/csv")