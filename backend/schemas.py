from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any

class UserSignup(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: str
    password: str
    nama_lengkap: str

class UserLogin(BaseModel):
    model_config = ConfigDict(extra='forbid')
    email: str
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    email: str
    nama_lengkap: str
    tipe_user: str


class QuestionnaireCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: str
    description: Optional[str] = None
    is_active: bool = False

class QuestionCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    questionnaire_id: str
    text: str
    type: str # 'teks' atau 'pilihan'
    options: Optional[Dict[str, Any]] = None
    order_index: int = Field(default=0, ge=0) # Memastikan urutan selalu integer positif (0 ke atas)
    logic_jump: Optional[Dict[str, Any]] = None

class ResponseCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    questionnaire_id: str
    answers: Dict[str, Any]
