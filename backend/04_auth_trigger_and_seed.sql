-- 1. Fungsi penanganan user baru (Trigger Function)
-- Fungsi ini akan dijalankan secara otomatis setiap ada user baru di tabel auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  -- Menyisipkan data ke public.profiles
  -- id dari auth.users akan dipakai sebagai id profil
  -- nama_lengkap akan diambil dari metadata, jika kosong akan diisi dengan bagian depan email, atau default 'User Baru'
  INSERT INTO public.profiles (id, nama_lengkap)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', split_part(NEW.email, '@', 1), 'User Baru')
  )
  -- Jika ternyata id sudah ada, jangan lakukan apa-apa (hindari error)
  ON CONFLICT (id) DO NOTHING;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Trigger untuk mengeksekusi fungsi di atas
-- Pastikan menghapus trigger yang lama jika sudah ada agar bisa dijalankan ulang dengan aman
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Buat trigger baru pada tabel auth.users Supabase
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();


-- 3. Seed Data (Data Contoh) untuk tabel universities
-- Kita menggunakan pengecekan agar tidak terjadi duplikasi saat skrip dijalankan ulang
INSERT INTO public.universities (nama, negara)
SELECT * FROM (VALUES 
    ('Institut Teknologi Bandung (ITB)', 'Indonesia'),
    ('Universitas Indonesia (UI)', 'Indonesia'),
    ('Universitas Gadjah Mada (UGM)', 'Indonesia'),
    ('University of Oxford', 'Inggris (UK)'),
    ('Harvard University', 'Amerika Serikat (USA)')
) AS t(nama, negara)
WHERE NOT EXISTS (
    SELECT 1 FROM public.universities WHERE public.universities.nama = t.nama
);
