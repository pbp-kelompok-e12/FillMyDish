
# FillMyDish

PBP E 12

## Gambaran Umum

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

## Informasi Proyek

### API

https://spoonacular.com/food-api/docs

### Modul

1. Profile: Nadhif
2. Input bahan: Ridho
3. Simpan resep: Naira
4. Meal plan : Rona
5. Review/Feedback terkait website kita: Parsya

### User Roles

1. User
2. Admin (Filter/Ban)

### Figma

https://www.figma.com/files/team/1569679838448420365/folder/655611366?fuid=1687367044933420310

### PWS:
https://musthofa-ridho-fillmydish.pws.cs.ui.ac.id


## Panduan Fitur dan Alur Penggunaan

Bagian ini menjelaskan fitur, alur penggunaan, dan file utama dari setiap modul aplikasi FillMyDish.


### Profile Page

Modul Profile Page memungkinkan pengguna melihat dan mengelola informasi profil pribadi setelah login.

#### Fitur

- Menampilkan foto profil, username, nama lengkap, bio, dan koneksi sosial.
- Mengedit username, nama lengkap, email, tanggal lahir, bio, dan foto profil.
- Menampilkan preview foto sebelum disimpan.
- Menambah, mengubah, dan menghapus koneksi sosial.
- Menyinkronkan username dan email dengan akun login.
- Menampilkan pesan validasi dan konfirmasi perubahan.
- Membatasi akses pengeditan hanya untuk pemilik akun.

#### Alur melihat profil

1. Login dan buka menu Profile melalui navbar.
2. Sistem menampilkan informasi profil pengguna.
3. Tekan Edit untuk memperbarui informasi.

#### Alur mengedit profil

1. Buka Profile dan pilih Edit.
2. Ubah informasi profil atau foto sesuai kebutuhan.
3. Tambahkan, ubah, atau hapus koneksi sosial.
4. Tekan Update Profile untuk menyimpan perubahan.
5. Pilih Cancel untuk membatalkan perubahan.

#### File utama

- `FillMyDish/models.py` — model Profile dan Connection.
- `FillMyDish/forms.py` — form dan validasi profil.
- `FillMyDish/views.py` — logika menampilkan dan memperbarui profil.
- `FillMyDish/urls.py` — URL halaman Profile.
- `templates/profile.html` — tampilan profil pengguna.
- `templates/edit_profile.html` — form pengeditan profil.
- `static/css/style.css` — styling halaman Profile.


### Recipe Finder

Modul recipe finder (input bahan) menangani request yang dikirim pengguna dengan API.

#### Fitur

- Page utama (tidak perlu login) yang berisi hanya tombol untuk masuk menu input bahan
- Menu input bahan (perlu login) dimana pengguna bisa mengisi bahan untuk dipakai, bahan untuk dihindari, dan alat yang tersedia
- Popup konfirmasi terkait input yang ingin dikirim
- Rate limit & filter
- Halaman yang menampilkan preview hasil resep dari API
- Informasi lanjut tentang resep-resep

#### Alur pencarian resep

Dari page utama pengguna bisa pencet tombol “find” yang bakal redirect ke halaman input bahan atau login kalau belum login

Pengguna bisa mengisi menu input bahan. Baris akan ditambahkan dengan JS jika pengguna pencet enter pada baris terbawah

Saat pengguna memencet tombol submit, JS akan memunculkan popup konfirmasi

Argument pengguna dikirim sebagai query pada get request ke halaman resep

Argument terkait alat karena dari API-nya terbatas yang valid akan di filter menggunakan wordlist dari API, jika alat tidak ada pada list, muncul error untuk mencoba lagi

Argument bahan pengguna akan melewati filter sederhana untuk mendeteksi request mencurigakan, jika termasuk, akan dibikin log untuk direview moderator dan requestnya tidak diproses sehingga kelihatannya seperti tidak ada resep yang muncul

Jika pengguna mengirim >5 request dalam 1 menit akan kena rate limit yang memunculkan pesan error untuk mencoba lagi nanti

Jika request pengguna aman, argument requestnya disimpan di dalam RecipeCache dan dikirim ke API, request pertama setiap hari akan reset RecipeCache

Hasil dari API dinormalisasi untuk bisa ditampilkan dalam halaman resep dan disimpan sebagai object Recipe dalam DB

Dalam halaman resep pengguna bisa pencet resepnya untuk melihat informasi lebih lanjut, informasi tersebut merupakan nutrisi, instruksi, dan source resep

#### File utama

- 'recipefinder/models.py' : model untuk menyimpan resep dan cache
- ’recipefinder/views.py' : mengatur operasi CRUD (soft-delete saat reset cache) dan menampilkan template HTML yang sesuai.
- 'recipefinder/tests.py' : unit test untuk model recipefinder
- 'recipefinder/wordlist.py' : menangani wordlist untuk alat
- 'templates/find.html' : halaman tombol
- 'templates/input.html' : halaman untuk input bahan
- 'templates/results.html' : halaman untuk hasil resep dari API
- 'templates/details.html' : halaman untuk informasi lanjut tentang resep
- 'static/find.css' : styling
- 'static/input.css' : styling
- 'static/results.css' : styling
- 'static/details.css' : styling


### Saved Recipe

Modul Saved Recipe memungkinkan pengguna menyimpan dan mengelola resep favorit dari halaman Recipe Details.

#### Fitur

- Menampilkan daftar resep milik pengguna.
- Menyimpan resep dari Recipe Details dan mencegah duplikasi.
- Mencari resep berdasarkan nama dan memfilter kategori makanan.
- Melihat detail resep dengan mengklik card.
- Mengedit kategori dan status Favorite melalui popup.
- Menghapus resep melalui popup konfirmasi.
- Menggunakan AJAX untuk proses Edit dan Delete.
- Mengintegrasikan resep tersimpan dengan Meal Plan.
- Membatasi akses agar pengguna hanya mengelola resep miliknya.

#### Alur menyimpan resep

1. Buka Find Recipe dan pilih resep yang diinginkan.
2. Pada Recipe Details, tekan Save Recipe.
3. Resep disimpan dan pengguna diarahkan ke Saved Recipe.
4. Jika sudah tersimpan, tombol berubah menjadi View Saved Recipes.

#### Alur mengelola resep

1. Buka Saved Recipe melalui navbar.
2. Gunakan search bar atau filter kategori untuk mencari resep.
3. Klik card untuk melihat informasi lengkap resep.
4. Tekan Edit untuk mengubah kategori atau status Favorite.
5. Tekan Save Changes untuk menyimpan atau Cancel untuk membatalkan.
6. Tekan Delete dan konfirmasi untuk menghapus resep.

#### File utama

- `saved_recipe/models.py` — model resep tersimpan dan relasi pengguna.
- `saved_recipe/views.py` — CRUD, pencarian, filter, dan validasi akses.
- `saved_recipe/forms.py` — form pengelolaan resep.
- `saved_recipe/urls.py` — URL modul Saved Recipe.
- `saved_recipe/tests.py` — pengujian fitur dan integrasi.
- `templates/saved_recipe/saved_recipe.html` — tampilan Saved Recipe dan popup.
- `static/css/saved_recipe.css` — styling halaman.
- `static/js/saved_recipe.js` — interaksi popup dan AJAX.
- `templates/details.html` — integrasi tombol Save Recipe.


### Meal Plan

Modul Meal Plan memungkinkan pengguna yang sudah login membuat dan mengelola kumpulan resep.

#### Fitur

- Menampilkan daftar meal plan milik pengguna.
- Membuat plan dengan judul wajib, deskripsi opsional, dan minimal satu resep.
- Memilih resep dari Saved Recipe saat membuat atau mengedit plan.
- Melihat detail plan dan resep-resep di dalamnya.
- Mengedit judul, deskripsi, serta pilihan resep. Perubahan diterapkan saat pengguna menekan **Save Changes**.
- Membatalkan proses pembuatan atau perubahan yang belum disimpan.
- Menghapus plan melalui konfirmasi tanpa membuka halaman baru.
- Membatasi akses agar pengguna hanya bisa melihat dan mengelola plan miliknya.

#### Alur membuat plan

1. Buka halaman **Meal Plan**, lalu pilih **Make a New One**.
2. Isi judul plan. Deskripsi boleh dikosongkan.
3. Pilih **Add from Saved Recipe** untuk membuka Saved Recipe dalam mode pemilihan.
4. Tekan **Add to Plan** pada resep yang ingin dimasukkan.
5. Kembali ke Meal Plan, lalu pilih **Save This Plan**.
6. Plan disimpan setelah memenuhi aturan validasi, termasuk memiliki minimal satu resep.

#### Alur mengedit plan

1. Buka salah satu plan, lalu pilih **Edit Your Plan**.
2. Ubah judul atau deskripsi jika diperlukan.
3. Pilih **Manage Recipes** untuk menambah atau mengeluarkan resep melalui tombol **Add to Plan**.
4. Kembali ke halaman edit dan pilih **Save Changes** untuk menerapkan semua perubahan.
5. Pilih **Cancel** untuk membuang perubahan yang belum disimpan.

#### File utama

- `mealplan/models.py` — model plan dan hubungan plan dengan resep.
- `mealplan/views.py` — alur membuat, melihat, mengedit, membatalkan, dan menghapus plan.
- `mealplan/urls.py` — URL untuk halaman Meal Plan.
- `mealplan/tests.py` — pengujian alur dan aturan akses Meal Plan.
- `templates/mealplan*.html` — template halaman Meal Plan.
- `static/css/mealplan.css` — styling halaman Meal Plan.


### Review

Modul Review menangani ulasan dari pengguna terhadap website FillMyDish speerti menampilkan, mengedit, dan menghapus ulasan dari pengguna. Daftar review dimuat lewat AJAX, sedangkan pembuatan review bisa lewat AJAX maupun form biasa.

#### Fitur

- Daftar review (login tidak diperlukan) yang ditampilkan berdasarkan urutan ditambahkan.
- Tambah review (menerima field rating (skala 1 - 5) dan pesan review.
- Edit dan Review hanya dapat dilakukan oleh pemilik review.
- Django admin dapat menyembunyikan ulasan tertentu lewat field is_visible (untuk moderasi)
- Review menampilkan info profil pembuat review.

#### Alur membuat review

- Pastikan sudah melakukan login terlebih dahulu (atau register jika belum punya akun).
- Dari laman utama, pada navbar pilih menu review
- klik tombol "Add Yours" berwarna kuning (anda akan diarahkan ke laman login jika belum melakukan login).
- Form untuk membuat review akan tampil.
- Masukkan rating (bintang 1 - 5) dan juga pesan review anda.
- Klik tombol "Submit" untuk membuat review.

#### Alur edit review

- Dari laman utama, pada navbar pilih menu review
- Pada review anda yang ingin di edit klik tombol "Edit" pada bagian bawah card review milik anda.
- Form untuk mengedit akan tampil, silahkan masukkan Rating/Pesan baru.
- Klik submit untuk menerapkan perubahan pada review anda.

#### Alur menghapus review

- Dari laman utama, pada navbar pilih menu review.
- Pada review yang ingin anda hapus klik tombol "Delete" pada bagian bawah card review miliki anda.
- Pop-up untuk konfirmasi penghapusan akan muncul
- Klik tombol "Confirm Delete" untuk menghapus review anda atau cancel untuk batal menghapus.

#### Hak akses dan keamanan

- Edit dan Delete memakai get_object_or_404() sehingga jika user lain akan mendapat error 404.
- Delete hanya menerima POST.
- CSRF token
- Field 'user' dan 'is_visible' tidak bisa diisi dari POST.
- review_list.html aman dari XSS, Semua data dari user di render lewat DOM API, bukan innerHTML.

#### File utama

- 'review/models.py' : model untuk review yang berinteraksi dengan review yang disimpan di db.
- 'review/views.py' : mengatur operasi CRUD, AJAX dan menampilkan template HTML yang sesuai.
- 'review/tests.py' : unit test untuk modul review.
- 'templates/review_list.html' : tampilan html untuk menampilkan semua review.
- 'templates/review_form.html' : tampilan html untuk form pembuatan dan edit review.
- 'static/review.css' : styling untuk template html review.


### Moderator

Sub-modul yang menangani filter dan ban

#### Fitur

- Page untuk melihat semua log request mencurigakan
- Popup untuk review log

#### Alur menangani filter

User yang merupakan moderator bisa akses halaman log, yang bukan akan redirect ke main

Log terisi dengan request mencurigakan dari recipefinder

Moderator bisa review log, flag atau cleared

Flag akan ngeban user yang terkait

Cleared akan unban user yang terkait

#### File utama

- ’moderation/models.py' : model untuk menyimpan request mencurigakan
- ’moderation/views.py' : mengatur penampilan log dan review pada log
- 'moderation/tests.py' : unit test untuk model moderation menggunakan selenium agar htmx diload
- 'FillMyDish/models.py' : pembuatan model User baru yang memiliki atribut is_moderator dan is_banned
- ’FillMyDish/forms.py' : hidden input moderator_key saat mendaftar dan pengecekan ban saat login
- 'templates/logs.html' : halaman utama untuk log
- 'templates/logs/_logs.html' : kartu yang ditampilkan menggunakan htmx
- 'templates/logs/_review.html' : popup saat review log menggunakan htmx
- 'static/review.css' : styling dipinjam


## Penggunaan AI

### AI Disclosure Untuk Profile Page

Saya menggunakan ChatGPT sebagai bantuan dalam mengembangkan halaman profil pada website FillMyDish. AI membantu memberikan saran mengenai struktur HTML, styling CSS, responsive layout, serta implementasi fitur profil seperti pengeditan informasi pengguna dan penambahan tautan koneksi sosial. AI juga membantu menjelaskan beberapa konsep Django dan kode yang digunakan pada halaman profil. Selain itu, ChatGPT membantu menjelaskan konteks pendukung proyek, seperti proses Google Login, pembuatan dan pengambilan kredensial OAuth di Google Cloud, serta pengaturan GitHub Organization. Fokus pengerjaan saya tetap pada halaman profil; hal-hal pendukung tersebut dibahas untuk membantu memahami integrasi dan alur kerja proyek. Saya menyesuaikan struktur, tampilan, dan implementasinya secara manual agar sesuai dengan kebutuhan proyek. Saya juga memeriksa dan mengubah kode yang dihasilkan agar dapat berjalan sesuai kebutuhan halaman profil.

[Percakapan Bagian Profile Page](https://chatgpt.com/share/6ae2fec7-da90-83ec-bf8f-8d69c833db36)

[recipefinder/moderation](/recipefinder/docs/AI_DISCLOSURE.md)
[mealplan](/mealplan/AI_DISCLOSURE.md)
[review](/review/AI_DISCLOSURE.md)
[saved_recipe](/saved_recipe/README.md)
