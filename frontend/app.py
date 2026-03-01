# app.py

import streamlit as st

# Setup Konfigurasi Halaman (Harus selalu menjadi perintah pertama)
st.set_page_config(
    page_title="Awardee Lifecycle Super App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. Injeksi Custom CSS bawaan untuk styling tambahan
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("assets/style.css")

# 2. Inisiasi Session State (Menyimpan Status User Terautentikasi)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "tipe_user" not in st.session_state:
    st.session_state.tipe_user = None

# Sidebar Branding
with st.sidebar:
    st.markdown("### 🎓 Awardee Super App")
    st.caption("v1.0.0 MVP Version")
    
    if st.session_state.logged_in and st.session_state.tipe_user != "admin":
        st.divider()
        st.info("💡 \"Pendidikan adalah senjata paling mematikan di dunia, karena dengan pendidikan Anda dapat mengubah dunia.\" \n\nSemangat menjalani studi!")

# 3. Deklarasi Halaman (Menggunakan fitur native st.navigation)
# -- Halaman Publik/Auth --
login_page = st.Page("pages/login.py", title="Log In", icon="🔑", default=True)

# -- Halaman Terproteksi --
dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True)
kuesioner_page = st.Page("pages/kuesioner.py", title="Daftar Kuesioner", icon="📝")

# 4. Logika Dynamic Routing
if not st.session_state.logged_in:
    # Jika user belum login, tampilkan grup navigasi "Akun" saja
    pg = st.navigation({
        "Akun": [login_page]
    })
else:
    # Jika user sudah login, tampilkan grup "Menu Utama"
    pg = st.navigation({
        "Menu Utama": [dashboard_page, kuesioner_page]
    })

# Jalankan halaman yang dipilih oleh sistem navigasi
pg.run()
