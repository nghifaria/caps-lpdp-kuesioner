-- Siklus 3, Repetisi 1: Questionnaire Engine Migration
-- Jika sebelumnya ada tabel questions/surveys dengan nama yang mirip, Anda opsional bisa drop di sini jika itu hanya skema lama.

-- 1. Buat Tabel questionnaires
CREATE TABLE public.questionnaires (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    created_by UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Buat Tabel questions
CREATE TABLE public.questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    questionnaire_id UUID REFERENCES public.questionnaires(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    type TEXT NOT NULL,
    options JSONB,
    order_index INTEGER DEFAULT 0,
    logic_jump JSONB
);

-- 3. Aktifkan Row-Level Security
ALTER TABLE public.questionnaires ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;

-- 4. Policies untuk questionnaires

-- Publik (Awardee) bisa melihat kuesioner jika is_active
CREATE POLICY "Publik dapat melihat kuesioner aktif" 
ON public.questionnaires FOR SELECT 
USING (is_active = true);

-- Admin bisa Insert, Select, Update, Delete
CREATE POLICY "Admin dapat mengelola kuesioner" 
ON public.questionnaires 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);

-- 5. Policies untuk questions

-- Publik (Awardee) bisa melihat pertanyaan jika kuesionernya is_active
CREATE POLICY "Publik dapat melihat pertanyaan" 
ON public.questions FOR SELECT 
USING (
    questionnaire_id IN (SELECT id FROM public.questionnaires WHERE is_active = true)
);

-- Admin bisa mengelola pertanyaan
CREATE POLICY "Admin dapat mengelola pertanyaan" 
ON public.questions 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);
