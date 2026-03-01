-- 1. Buat Tabel Surveys
CREATE TABLE public.surveys (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Buat Tabel Questions
CREATE TABLE public.questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_id UUID REFERENCES public.surveys(id) ON DELETE CASCADE NOT NULL,
    text TEXT NOT NULL,
    qtype TEXT NOT NULL,
    options JSONB,
    logic_tree JSONB,
    order_index INTEGER NOT NULL DEFAULT 0,
    is_mandatory BOOLEAN DEFAULT false
);

-- 3. Aktifkan Row-Level Security (RLS)
ALTER TABLE public.surveys ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;

-- 4. Kebijakan (Policies) untuk Surveys

-- Awardee / Publik dapat melakukan SELECT (melihat) jika survey sedang aktif
CREATE POLICY "Publik dapat melihat survey aktif" 
ON public.surveys 
FOR SELECT 
USING (is_active = true);

-- Admin dapat melakukan semua operasi (INSERT, UPDATE, DELETE, SELECT) pada tabel surveys
CREATE POLICY "Admin memiliki akses penuh ke surveys" 
ON public.surveys 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);

-- 5. Kebijakan (Policies) untuk Questions

-- Awardee / Publik dapat melihat pertanyaan (SELECT) jika survey induknya sedang aktif
CREATE POLICY "Publik dapat melihat pertanyaan pada survey aktif" 
ON public.questions 
FOR SELECT 
USING (
    survey_id IN (SELECT id FROM public.surveys WHERE is_active = true)
);

-- Admin dapat melakukan semua operasi pada tabel questions
CREATE POLICY "Admin memiliki akses penuh ke questions" 
ON public.questions 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);
