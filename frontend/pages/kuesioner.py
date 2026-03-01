# kuesioner.py

import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.services.api import get_questionnaire, submit_response

# 1. Proteksi Halaman (Wajib Login)
if not st.session_state.get("logged_in"):
    st.warning("Harap login terlebih dahulu untuk mengakses halaman ini!")
    st.stop() # Menghentikan eksekusi script di bawahnya

st.title("Kuesioner Saya")

# Konstanta ID Kuesioner (Siklus 7: Hardcoded sementara untuk percobaan)
# Sesuaikan dengan UUID kuesioner yang Anda miliki di database
QUESTIONNAIRE_ID = "c0a5df77-07a4-4f13-a543-bb58fe7cacd3" 
token = st.session_state.get("access_token")

# 2. Fetch Data Kuesioner dari Backend
with st.spinner("Memuat Kuesioner..."):
    try:
        q_data = get_questionnaire(QUESTIONNAIRE_ID, token)
        meta = q_data["questionnaire"]
        questions = q_data["questions"]
    except Exception as e:
        st.error(str(e))
        st.stop()

# Menampilkan Header Kuesioner
st.subheader(meta["title"])
if meta.get("description"):
    st.write(meta["description"])

st.divider()

# 3. Dynamic Form Generator
with st.form("form_kuesioner"):
    # Dictionary sementara untuk menyimpan jawaban responden
    jawaban_sementara = {}
    
    # Looping semua pertanyaan
    for q in questions:
        q_id = q["id"]
        q_text = q["text"]
        q_type = q["type"]
        
        # Render berdasarkan tipe pertanyaan
        # Update logika ini di kuesioner.py agar sinkron dengan database
        if q_type in ["pilihan", "multiple_choice"]:
            choices = []
            if isinstance(q.get('options'), dict):
                choices = q['options'].get('choices', [])
            
            jawaban_sementara[q_id] = st.radio(
                label=q_text,
                options=choices,
                index=None if not choices else 0 
            )
            
        elif q_type in ["teks", "text"]:
            jawaban_sementara[q_id] = st.text_input(label=q_text)
            
        else:
            # Fallback jika tipe benar-benar tidak dikenali
            st.error(f"Tipe data '{q_type}' tidak dikenali oleh sistem.")
            jawaban_sementara[q_id] = None
    # Area Submit Button
    st.write("") # Spacing 
    submitted = st.form_submit_button("Kirim Jawaban", type="primary")
    
    # 4. Aksi Submit ke Backend
    if submitted:
        # Validasi Pre-Submit: Cek Wajib Isi & Format NIK
        for q in questions:
            q_id = q["id"]
            q_text = q["text"]
            jawaban = jawaban_sementara.get(q_id)
            
            # 1. Validasi Wajib Isi (Tidak boleh kosong atau None)
            if jawaban is None or str(jawaban).strip() == "":
                st.error("Semua pertanyaan wajib diisi!")
                st.stop()
                
            # 2. Validasi Spesifik NIK (Jika ada pertanyaan NIK)
            if "nik" in q_text.lower():
                jawaban_str = str(jawaban).strip()
                if len(jawaban_str) != 16 or not jawaban_str.isdigit():
                    st.error("NIK harus terdiri dari tepat 16 digit angka!")
                    st.stop()

        # Susun Payload JSON sesuai ekspektasi Pydantic Schema di FastAPI
        payload = {
            "questionnaire_id": QUESTIONNAIRE_ID,
            "answers": jawaban_sementara
        }
        
        with st.spinner("Mengirim jawaban Anda..."):
            try:
                res = submit_response(payload, token)
                st.success("✅ " + res["message"])
                st.balloons() # Efek animasi balon jika sukses!
            except Exception as e:
                # Menampilkan pesan error dari backend (termasuk deteksi duplikat pengisian)
                st.error(str(e))
