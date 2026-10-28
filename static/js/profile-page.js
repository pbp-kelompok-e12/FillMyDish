// Jalankan pengaturan avatar setelah dokumen selesai dimuat.
document.addEventListener("DOMContentLoaded", function () { // Menunggu markup profil siap digunakan.
  const avatar = document.querySelector(".profile-avatar"); // Mencari wadah foto profil.
  if (!avatar) return; // Berhenti jika halaman tidak memiliki wadah avatar.
  const image = avatar.querySelector("img.avatar-circle"); // Mencari foto profil jika tersedia.
  const placeholder = avatar.querySelector(".avatar-fallback"); // Mencari placeholder jika foto memang tidak ada.
  const fullName = document.querySelector(".profile-fullname")?.textContent.trim(); // Mengambil nama lengkap profil.
  const getInitials = function (name) { // Membuat maksimal dua inisial dari nama.
    const words = name.trim().split(/\s+/).filter(Boolean); // Memisahkan nama menjadi kata-kata.
    if (words.length > 1) return (words[0][0] + words[1][0]).toUpperCase(); // Mengambil huruf awal dua kata pertama.
    return words[0]?.slice(0, 2).toUpperCase() || "?"; // Mengambil dua huruf nama tunggal atau tanda tanya.
  }; // Mengakhiri fungsi pembentuk inisial.
  if (placeholder) { // Menangani profil yang tidak memiliki foto.
    placeholder.textContent = getInitials(placeholder.dataset.profileName || fullName || ""); // Menampilkan inisial nama profil.
    return; // Mengakhiri proses karena placeholder sudah tersedia.
  } // Mengakhiri penanganan profil tanpa foto.
  if (!image) return; // Berhenti jika gambar dan placeholder tidak tersedia.
  image.addEventListener("error", function () { // Menangani URL foto yang gagal dimuat.
    const label = image.alt.replace(/\s+profile picture$/i, "").trim(); // Mengambil nama dari teks alternatif.
    const fallback = document.createElement("span"); // Membuat elemen pengganti foto.
    fallback.className = "avatar-circle avatar-fallback"; // Memakai bentuk lingkaran avatar.
    fallback.textContent = getInitials(fullName || label); // Menampilkan inisial nama lengkap atau teks alternatif.
    fallback.setAttribute("aria-label", "Profile picture unavailable"); // Memberi keterangan aksesibilitas.
    image.replaceWith(fallback); // Mengganti foto rusak dengan placeholder.
  }, { once: true }); // Memastikan penggantian hanya dilakukan satu kali.
}); // Mengakhiri pengaturan avatar profil.
