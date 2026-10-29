# FillMyDish
PBP E 12

### Latar Belakang
Mahasiswa yang memiliki bahan makanan sisa di kos ingin mengolahnya agar tidak terbuang dan lebih hemat serta sehat.

### Solusi
Platform yang memberikan rekomendasi resep berdasarkan bahan makanan dan alat masak yang diinput pengguna serta menyertakan informasi gizinya.

### Fitur Utama
- Profile: Pengguna dapat melihat profil, mengubah informasi akun dan bio, mengunggah foto profil, serta menambahkan tautan media sosial melalui fitur Connection
- Input System: form input untuk bahan makanan dan checkbox untuk alat masak yang tersedia
- Matchmaking & Output: muncul icon/gambar makanan dan deskripsi pendek -> icon diklik akan berganti halaman menampilkan resep dan bisa dislide untuk menampilkan informasi gizinya
- Simpan Resep: Kalau menemukan resep yang disuka ada pilihan untuk menyimpannya dan bisa lihat semua resep yang disimpan
- Meal Plan: Bisa membuat rencana makan menggunakan resep yang sudah disimpan atau mencari resep baru
- Feedback/Review Form: User Feedback kepada website kami
 
### API: https://spoonacular.com/food-api/docs

### Modul: 
1. Profile: Nadhif
2. Input bahan: Ridho
3. Simpan resep: Naira
4. Meal plan : Rona
5. Review/Feedback terkait website kita: Parsya

#### Penjelasan Modul Profile Page
- Pengguna dapat melihat halaman profil setelah masuk ke akun. Halaman ini menampilkan foto profil (atau inisial nama jika foto belum tersedia), username, nama lengkap, bio, dan tautan koneksi sosial.
- Tombol **Edit** ditampilkan pada profil milik pengguna yang sedang masuk. Pengguna dapat memperbarui foto profil, username, nama lengkap, email, tanggal lahir, bio, serta menambah, mengubah, atau menghapus koneksi sosial.
- Perubahan profil disimpan ke akun pengguna. Username dan email pada profil juga disinkronkan dengan akun login.
- Profil pengguna lain dapat dibuka melalui halaman profil berdasarkan username, tetapi hanya pemilik profil yang dapat mengeditnya. Halaman profil pribadi memerlukan login.
- Jika informasi tertentu belum diisi, halaman menggunakan nilai akun yang tersedia sebagai pengganti nama/username, menampilkan inisial sebagai avatar, atau memberi keterangan bahwa bio/koneksi belum tersedia.
   
### AI Disclosure Untuk Profile Page
Saya menggunakan ChatGPT sebagai bantuan dalam mengembangkan halaman profil pada website FillMyDish. AI membantu memberikan saran mengenai struktur HTML, styling CSS, responsive layout, serta implementasi fitur profil seperti pengeditan informasi pengguna dan penambahan tautan koneksi sosial. AI juga membantu menjelaskan beberapa konsep Django dan kode yang digunakan pada halaman profil. Selain itu, ChatGPT membantu menjelaskan konteks pendukung proyek, seperti proses Google Login, pembuatan dan pengambilan kredensial OAuth di Google Cloud, serta pengaturan GitHub Organization. Fokus pengerjaan saya tetap pada halaman profil; hal-hal pendukung tersebut dibahas untuk membantu memahami integrasi dan alur kerja proyek. Saya menyesuaikan struktur, tampilan, dan implementasinya secara manual agar sesuai dengan kebutuhan proyek. Saya juga memeriksa dan mengubah kode yang dihasilkan agar dapat berjalan sesuai kebutuhan halaman profil.
[Percakapan Bagian Profile Page](https://chatgpt.com/share/6ae30389-dc10-83ec-9ded-2c0aa0ac0cbd)

### User Roles:
1. User 
2. Admin (Filter/Ban)

### Figma:
https://www.figma.com/files/team/1569679838448420365/folder/655611366?fuid=1687367044933420310

### PWS:
https://pws.cs.ui.ac.id/musthofa.ridho/fillmydish
