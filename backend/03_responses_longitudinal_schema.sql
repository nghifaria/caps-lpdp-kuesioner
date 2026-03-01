-- 1. Buat Tabel Responses (Jawaban)
CREATE TABLE public.responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    survey_id UUID REFERENCES public.surveys(id) ON DELETE CASCADE NOT NULL,
    question_id UUID REFERENCES public.questions(id) ON DELETE CASCADE NOT NULL,
    answer JSONB NOT NULL,
    period TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Buat Index untuk pencarian cepat
-- Mempercepat pencarian data berdasarkan responden (profile_id)
CREATE INDEX idx_responses_profile_id ON public.responses(profile_id);

-- Mempercepat pencarian data analitik berdasarkan survey (survey_id)
CREATE INDEX idx_responses_survey_id ON public.responses(survey_id);

-- 3. Aktifkan Row-Level Security (RLS) pada tabel responses
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;

-- 4. Kebijakan (Policies) RLS untuk tabel responses

-- Kebijakan 1: Awardee (Pengguna) dapat melihat jawabannya sendiri
CREATE POLICY "Pengguna dapat melihat jawaban sendiri" 
ON public.responses 
FOR SELECT 
USING (auth.uid() = profile_id);

-- Kebijakan 2: Awardee (Pengguna) dapat memasukkan jawabannya sendiri
-- Catatan: WITH CHECK memastikan data baru yang dimasukkan (profile_id) sesuai dengan auth.uid()
CREATE POLICY "Pengguna dapat menyimpan jawabannya sendiri" 
ON public.responses 
FOR INSERT 
WITH CHECK (auth.uid() = profile_id);

-- Kebijakan 3: Admin dapat melihat semua jawaban (Read-Only for Admin)
-- Admin diberikan akses SELECT agar bisa melihat semua data untuk Dashboard IPA
CREATE POLICY "Admin dapat melihat semua jawaban (Read-Only)" 
ON public.responses 
FOR SELECT 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);
