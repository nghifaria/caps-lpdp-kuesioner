-- Siklus 4, Repetisi 1: Response System Migration

-- 1. Buat Tabel responses
-- Kita menggunakan JSONB untuk jawaban agar bisa menampung struktur { "id_pertanyaan_1": "jawaban", "id_pertanyaan_2": ["A", "B"] } dsb.
CREATE TABLE public.responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    questionnaire_id UUID REFERENCES public.questionnaires(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    answers JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    -- UNIQUE CONSTRAINT: Satu user hanya bisa mengisi satu kuesioner satu kali.
    -- Mencegah duplicate entry untuk kombinasi questionnaire_id dan user_id.
    CONSTRAINT unique_user_questionnaire UNIQUE (questionnaire_id, user_id)
);

-- 2. Aktifkan Row-Level Security
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- 3. Policies untuk responses

-- Kebijakan 1: Awardee (Pengguna) dapat melihat jawabannya sendiri
CREATE POLICY "Pengguna dapat melihat responnya sendiri" 
ON public.responses FOR SELECT 
USING (auth.uid() = user_id);

-- Kebijakan 2: Awardee (Pengguna) dapat memasukkan jawabannya sendiri
CREATE POLICY "Pengguna dapat submit responnya sendiri" 
ON public.responses FOR INSERT 
WITH CHECK (auth.uid() = user_id);

-- Kebijakan 3: Admin dapat melihat semua jawaban (Read-Only)
CREATE POLICY "Admin dapat melihat semua respon" 
ON public.responses FOR SELECT 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);
