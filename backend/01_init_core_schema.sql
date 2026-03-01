-- 1. Buat Tabel Universities (Data Master)
CREATE TABLE public.universities (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nama TEXT NOT NULL,
    negara TEXT NOT NULL
);

-- 2. Buat Tabel Profiles
CREATE TABLE public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    nama_lengkap TEXT NOT NULL,
    nik TEXT UNIQUE,
    tipe_user TEXT NOT NULL CHECK (tipe_user IN ('admin', 'awardee')) DEFAULT 'awardee',
    university_id UUID REFERENCES public.universities(id) ON DELETE SET NULL
);

-- 3. Aktifkan Row-Level Security (RLS) pada tabel profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- 4. Kebijakan (Policy) RLS

-- Kebijakan 1: Pengguna (Awardee) hanya bisa melihat profil mereka sendiri
CREATE POLICY "Pengguna dapat melihat profilnya sendiri" 
ON public.profiles 
FOR SELECT 
USING (auth.uid() = id);

-- Kebijakan 2: Admin dapat melihat semua profil
-- Kita cek apakah user yang sedang login memiliki tipe_user = 'admin' di tabel profiles
CREATE POLICY "Admin dapat melihat semua profil" 
ON public.profiles 
FOR SELECT 
USING (
    (SELECT tipe_user FROM public.profiles WHERE id = auth.uid()) = 'admin'
);
