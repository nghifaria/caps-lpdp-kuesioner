# login.py
import streamlit as st
import sys
import os

# Menambahkan direktori root (di atas pages/) ke path agar import src.services berjalan
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.api import login_user, register_user

st.title("Masuk ke Sistem")
st.write("Silakan login atau daftar menggunakan akun Awardee Anda.")

# Membuat 2 Tab
tab_login, tab_register = st.tabs(["💳 Masuk", "📝 Daftar Baru"])

# --- TAB MASUK ---
with tab_login:
    st.subheader("Login Akun")
    with st.form("form_login"):
        login_email = st.text_input("Email", placeholder="contoh@domain.com")
        login_password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Masuk", type="primary")
        
        if submit_login:
            if not login_email or not login_password:
                st.error("Email dan Password tidak boleh kosong!")
            else:
                with st.spinner("Mohon tunggu, sedang memverifikasi..."):
                    try:
                        # Memanggil Service API Login
                        res = login_user(login_email, login_password)
                        
                        # Jika sukses, update Session State Global
                        st.session_state.logged_in = True
                        st.session_state.access_token = res["access_token"]
                        st.session_state.user_data = res["user"]
                        
                        # Set default tipe_user (Nantinya idealnya kita ambil dari /auth/me)
                        st.session_state.tipe_user = "awardee" # Asumsi default, bisa di-update nanti
                        
                        st.success("Login berhasil! Mengalihkan ke Dashboard...")
                        
                        # Rerun aplikasi untuk berpindah rute (redirect)
                        st.rerun()
                        
                    except Exception as e:
                        # Jika error (salah password atau server mati), tampilkan notasi merah di halaman
                        st.error(str(e))

# --- TAB DAFTAR BARU ---
with tab_register:
    st.subheader("Buat Akun Baru")
    with st.form("form_register"):
        reg_fullname = st.text_input("Nama Lengkap Sesuai KTP")
        reg_email = st.text_input("Email Valid")
        reg_password = st.text_input("Password (Min 6 Karakter)", type="password")
        submit_register = st.form_submit_button("Daftar Akun")
        
        if submit_register:
            if not reg_fullname or not reg_email or not reg_password:
                st.error("Semua kolom harus diisi!")
            elif len(reg_password) < 6:
                st.error("Password minimal 6 karakter!")
            else:
                with st.spinner("Membuat akun Anda..."):
                    try:
                        res = register_user(reg_email, reg_password, reg_fullname)
                        st.success("✅ Akun berhasil dibuat! Silakan pindah ke Tab Masuk untuk Login.")
                    except Exception as e:
                        st.error(str(e))
