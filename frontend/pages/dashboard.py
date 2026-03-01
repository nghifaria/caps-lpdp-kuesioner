# dashboard.py

import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.services.api import get_export_data

# 1. Proteksi Halaman (Wajib Login)
if not st.session_state.get("logged_in"):
    st.warning("Harap login terlebih dahulu untuk mengakses halaman ini!")
    st.stop()

# Konstanta ID Kuesioner (Sementara)
QUESTIONNAIRE_ID = "c0a5df77-07a4-4f13-a543-bb58fe7cacd3"
token = st.session_state.get("access_token")

# 2. Logika Tampilan Berbasis Akses (Smart View)
try:
    with st.spinner("Memuat data analitik..."):
        data = get_export_data(QUESTIONNAIRE_ID, token)
        
    # --- JIKA SUKSES (Admin View) ---
    st.subheader("Dashboard Command Center")
    
    if data:
        df = pd.DataFrame(data)
        
        # Pisahkan menjadi dua tab
        tab_analitik, tab_kelola = st.tabs(["📊 Analitik Data", "⚙️ Kelola Pertanyaan"])
        
        with tab_analitik:
            # 1. Row Metrik Atas
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Responden", len(df))
            with col_m2:
                # Mengonversi waktu ISO 8601 string ke datetime untuk visualisasi terakhir diisi
                df['Waktu Submit'] = pd.to_datetime(df['Waktu Submit'])
                last_submit = df['Waktu Submit'].max().strftime('%d %b %Y, %H:%M')
                st.metric("Pembaruan Terakhir", last_submit)
            
            st.divider()
            
            # 2. Two-Column Layout (Data Vis + Raw Data)
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### Distribusi Jawaban Mayoritas")
                # Hitung distribusi jawaban kolom status pekerjaan 
                target_col = None
                for col in df.columns:
                    if 'pekerjaan' in col.lower() or 'bekerja' in col.lower() or 'status' in col.lower():
                        target_col = col
                        break
                
                # Jika kolom tidak ketemu, gunakan kolom pilihan pertama yang tersedia
                if not target_col and len(df.columns) > 3:
                     target_col = df.columns[3]
                     
                if target_col:
                    distribusi = df[target_col].value_counts()
                    st.bar_chart(distribusi)
                    st.caption(f"Distribusi untuk pertanyaan: *{target_col}*")
                else:
                     st.info("Visualisasi data spesifik belum tersedia untuk struktur form ini.")
                     
            with col2:
                st.markdown("#### Tabel Raw Data")
                # Tampilkan tabel data secara rapi
                st.dataframe(df, use_container_width=True)
                
                # Sediakan tombol unduh CSV untuk memudahkan copy-paste ke Excel
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Data (CSV)",
                    data=csv,
                    file_name="hasil_kuesioner.csv",
                    mime="text/csv"
                )

        with tab_kelola:
            st.markdown("#### Tambah Pertanyaan Baru ke Kuesioner")
            with st.form("form_tambah_pertanyaan"):
                q_text = st.text_input("Teks Pertanyaan Baru")
                # Backend schema: type ("text" atau "multiple_choice", di frontend pakai "teks", "pilihan", atau sesuai enum backend)
                q_type = st.selectbox("Tipe Pertanyaan", ["teks", "pilihan"])
                q_options = st.text_input("Pilihan Jawaban (Khusus tipe Pilihan. Pisahkan dengan koma. Misal: Setuju, Ragu, Tidak)")
                submit_btn = st.form_submit_button("Tambah Pertanyaan", type="primary")

                if submit_btn:
                    if not q_text:
                        st.error("Teks pertanyaan tidak boleh kosong!")
                    else:
                        payload = {
                            "questionnaire_id": QUESTIONNAIRE_ID,
                            "text": q_text,
                            "type": q_type,
                            "order_index": 0 # Default order
                        }
                        
                        if q_type == "pilihan" and q_options:
                            choices_list = [opt.strip() for opt in q_options.split(",")]
                            payload["options"] = {"choices": choices_list}
                        
                        with st.spinner("Menyimpan pertanyaan..."):
                            try:
                                # Import function (Assumes import at top of file, we will fix imports shortly)
                                from src.services.api import create_question
                                res = create_question(payload, token)
                                st.success("✅ Pertanyaan berhasil ditambahkan ke Kuesioner!")
                            except Exception as e:
                                st.error(str(e))
    else:
        st.info("Belum ada responden yang mengisi kuesioner ini.")

except Exception as e:
    err_msg = str(e)
    # --- JIKA ERROR / BUKAN ADMIN (Awardee View) ---
    if "Akses ditolak" in err_msg or "Hanya Admin" in err_msg or "403" in err_msg:
        st.title("Awardee Dashboard")
        st.info("Selamat datang di Awardee Lifecycle Super App! Silakan buka menu Daftar Kuesioner di samping untuk mulai mengisi survei longitudinal Anda.")
    else:
        # Penanganan error lainnya (Misalnya server down atau ID salah)
        st.error(f"Terjadi kesalahan saat memuat data: {err_msg}")

st.divider()

# Pilihan Logout yang dapat diakses semua pengguna      
if st.button("Keluar (Logout)", type="secondary"):
    st.session_state.logged_in = False
    st.session_state.tipe_user = None
    st.session_state.access_token = None
    st.session_state.user_data = None
    st.rerun() # Refresh untuk memicu re-routing st.navigation kembali ke halaman Login
