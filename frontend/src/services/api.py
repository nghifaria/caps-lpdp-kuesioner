# api.py

import requests

# Base URL backend FastAPI Anda
BASE_URL = "http://127.0.0.1:8000"

def login_user(email: str, password: str):
    """
    Mengirim request POST ke endpoint /auth/login.
    Mengembalikan data session jika sukses.
    Melempar string error jika gagal.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10 # Beri batas waktu 10 detik agar aplikasi tidak hang
        )
        data = response.json()
        
        # Jika HTTP status 200 OK
        if response.status_code == 200:
            return data
        else:
            # Mengambil detail pesan error dari FastAPI (biasanya di key 'detail')
            error_msg = data.get("detail", "Login gagal. Silakan coba lagi.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server. Pastikan backend (FastAPI) sedang berjalan.")
    except Exception as e:
        raise e

def register_user(email: str, password: str, full_name: str):
    """
    Mengirim request POST ke endpoint /auth/signup.
    """
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email, 
                "password": password, 
                "nama_lengkap": full_name
            },
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200:
            return data
        else:
            error_msg = data.get("detail", "Registrasi gagal. Silakan coba lagi.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server. Pastikan backend (FastAPI) sedang berjalan.")
    except Exception as e:
        raise e

def get_questionnaire(questionnaire_id: str, token: str):
    """
    Mengambil data kuesioner dan daftar pertanyaannya berdasaarkan ID.
    Perlu access_token di Header (Bearer).
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/questionnaires/{questionnaire_id}",
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200:
            return data["data"]
        else:
            error_msg = data.get("detail", "Gagal mengambil data kuesioner.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server Backend.")
    except Exception as e:
        raise e

def submit_response(payload: dict, token: str):
    """
    Mengirim jawaban (submisi) kuesioner ke server.
    Memerlukan format dict/JSON sesuai ResponseCreate di backend.
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/responses",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200:
            return data
        else:
            error_msg = data.get("detail", "Gagal mengirim jawaban.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server Backend.")
    except Exception as e:
        raise e

def get_export_data(questionnaire_id: str, token: str):
    """
    Mengambil data export (flattened) dari kuesioner berdasarkan ID.
    Hanya dapat diakses oleh Admin. Perlu access_token di Header (Bearer).
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/admin/questionnaires/{questionnaire_id}/export",
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200:
            return data["data"]
        else:
            error_msg = data.get("detail", "Gagal mengambil data ekspor kuesioner.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server Backend.")
    except Exception as e:
        raise e

def create_question(payload: dict, token: str):
    """
    Mengirim request POST ke endpoint /admin/questions untuk membuat pertanyaan baru.
    Perlu access_token Admin di Header (Bearer).
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/admin/questions",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code in [200, 201]:
            return data
        else:
            error_msg = data.get("detail", "Gagal menambah pertanyaan.")
            raise Exception(error_msg)
            
    except requests.exceptions.ConnectionError:
        raise Exception("Tidak dapat terhubung ke server Backend.")
    except Exception as e:
        raise e