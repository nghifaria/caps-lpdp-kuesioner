from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from database import supabase
import schemas

# Memuat environment variables
load_dotenv()

# Inisialisasi aplikasi FastAPI
app = FastAPI(
    title="Awardee Lifecycle Super App API",
    description="Backend API for LPDP Awardee Lifecycle Tracking",
    version="1.0.0"
)

# Dependency Security untuk mengambil Bearer token dari Header
security = HTTPBearer()

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency untuk mengecek apakah user adalah admin.
    Mengembalikan user_id jika sukses.
    """
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Token tidak valid atau telah kedaluwarsa.")
            
        user_id = user_response.user.id
        # Mengecek secara database apakah user ini punya profil dengan otoritas admin
        profile_response = supabase.table("profiles").select("tipe_user").eq("id", user_id).single().execute()
        
        if not profile_response.data or profile_response.data.get("tipe_user") != 'admin':
            raise HTTPException(status_code=403, detail="Akses ditolak: Hanya Admin yang dapat melakukan aksi ini.")
            
        return user_id
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Otorisasi gagal. Pastikan info login benar. Error detail: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "Awardee Lifecycle API is running"}

@app.get("/test-db")
def test_db_connection():
    try:
        response = supabase.table("universities").select("*").execute()
        return {
            "status": "success", 
            "message": "Koneksi ke Supabase berhasil!",
            "data": response.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal terhubung ke database atau mengambil data universitas: {str(e)}")

@app.post("/auth/signup")
def signup(user: schemas.UserSignup):
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "full_name": user.nama_lengkap
                }
            }
        })
        return {
            "status": "success",
            "message": "Akun berhasil dibuat. Silakan periksa email Anda (jika konfirmasi email aktif di Supabase).",
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Gagal mendaftar: Pastikan format email benar dan belum digunakan.")

@app.post("/auth/login")
def login(user: schemas.UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        return {
            "status": "success",
            "message": "Login berhasil.",
            "access_token": response.session.access_token,
            "user": response.user
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Email atau password salah. Pastikan kredensial benar.")

@app.get("/auth/me")
def get_me(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Token tidak valid atau telah kedaluwarsa.")
            
        user_id = user_response.user.id
        profile_response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        
        return {
            "status": "success",
            "data": {
                "auth": user_response.user,
                "profile": profile_response.data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Gagal mengambil profil. Otorisasi mungkin telah berakhir.")

@app.post("/admin/questionnaires", tags=["Admin"])
def create_questionnaire(questionnaire: schemas.QuestionnaireCreate, admin_id: str = Depends(require_admin)):
    try:
        data_to_insert = {
            "title": questionnaire.title,
            "description": questionnaire.description,
            "is_active": questionnaire.is_active,
            "created_by": admin_id
        }
        response = supabase.table("questionnaires").insert(data_to_insert).execute()
        return {"status": "success", "message": "Kuesioner berhasil dibuat", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal membuat kuesioner ke database: {str(e)}")

@app.get("/questionnaires/{id}")
def get_questionnaire(id: str):
    try:
        # maybe_single() lebih aman dari single() bila item tak ada (karena tidak me-raise error di level SDK)
        q_response = supabase.table("questionnaires").select("*").eq("id", id).maybe_single().execute()
        if not q_response.data:
            raise HTTPException(status_code=404, detail="Kuesioner tidak ditemukan. Pastikan ID kuesioner valid.")
            
        questions_resp = supabase.table("questions").select("*").eq("questionnaire_id", id).order("order_index").execute()
        
        return {
            "status": "success",
            "data": {
                "questionnaire": q_response.data,
                "questions": questions_resp.data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat mengambil kuesioner: Cek format UUID id.")

@app.post("/admin/questions", tags=["Admin"])
async def create_question(question: schemas.QuestionCreate, user_id: str = Depends(require_admin)):
    try:
        data = supabase.table("questions").insert({
            "questionnaire_id": str(question.questionnaire_id),
            "text": question.text,
            "type": question.type,
            "options": question.options,
            "order_index": question.order_index,
            "logic_jump": question.logic_jump
        }).execute()
        
        return {"status": "success", "message": "Pertanyaan berhasil ditambahkan", "data": data.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menambah pertanyaan. Pastikan Format Questionnaire_ID Valid.")

@app.post("/responses")
def submit_response(response_data: schemas.ResponseCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(status_code=401, detail="Token tidak valid atau telah kedaluwarsa.")
            
        user_id = user_response.user.id
        
        data_to_insert = {
            "questionnaire_id": response_data.questionnaire_id,
            "user_id": user_id,
            "answers": response_data.answers
        }
        result = supabase.table("responses").insert(data_to_insert).execute()
        return {"status": "success", "message": "Jawaban berhasil direkam", "data": result.data}
        
    except Exception as e:
        err_str = str(e).lower()
        if "duplicate key value" in err_str or "unique_user_questionnaire" in err_str:
             raise HTTPException(status_code=400, detail="Anda sudah pernah mengisi kuesioner ini sebelumnya.")
        if "foreign key constraint" in err_str or "invalid input syntax for type uuid" in err_str:
             raise HTTPException(status_code=404, detail="Kuesioner yang Anda coba isi tidak valid atau tidak ditemukan.")
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan jawaban. Mohon coba lagi nanti.")

@app.get("/admin/questionnaires/{id}/responses", tags=["Admin"])
def get_questionnaire_responses(id: str, admin_id: str = Depends(require_admin)):
    try:
        questions_resp = supabase.table("questions").select("id, text").eq("questionnaire_id", id).execute()
        question_map = {q["id"]: q["text"] for q in questions_resp.data}

        responses_resp = supabase.table("responses").select("id, created_at, answers, profiles(nama_lengkap, nik)").eq("questionnaire_id", id).execute()
        
        mapped_responses = []
        for row in responses_resp.data:
            mapped_answers = {}
            for q_id, q_ans in row["answers"].items():
                q_text = question_map.get(q_id, f"Pertanyaan Dihapus ({q_id})")
                mapped_answers[q_text] = q_ans

            mapped_responses.append({
                "response_id": row["id"],
                "tanggal_isi": row["created_at"],
                "awardee": row["profiles"],
                "jawaban": mapped_answers
            })

        return {
            "status": "success", 
            "total_responden": len(mapped_responses),
            "data": mapped_responses
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat agregasi jawaban. Cek kebenaran ID kuesioner.")

@app.get("/admin/questionnaires/{id}/export", tags=["Admin"])
def export_questionnaire_responses(id: str, admin_id: str = Depends(require_admin)):
    try:
        questions_resp = supabase.table("questions").select("id, text, order_index").eq("questionnaire_id", id).order("order_index").execute()
        responses_resp = supabase.table("responses").select("created_at, answers, profiles(nama_lengkap, nik)").eq("questionnaire_id", id).execute()
        
        flattened_data = []
        for row in responses_resp.data:
            flat_row = {
                "Waktu Submit": row["created_at"],
                "Nama Lengkap": row["profiles"].get("nama_lengkap", "N/A") if row["profiles"] else "N/A",
                "NIK": row["profiles"].get("nik", "N/A") if row["profiles"] else "N/A",
            }
            
            for q in questions_resp.data:
                jawaban = row["answers"].get(q["id"], "")
                flat_row[q["text"]] = jawaban
                
            flattened_data.append(flat_row)

        return {
            "status": "success",
            "message": "Data siap disalin (copy-paste) ke Excel",
            "total_baris": len(flattened_data),
            "data": flattened_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan ekspor jawaban: Cek Format UUID.")