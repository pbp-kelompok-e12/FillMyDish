// Jalankan pengaturan avatar setelah dokumen selesai dimuat.
document.addEventListener("DOMContentLoaded", function () { // Menunggu markup profil siap digunakan.
  const avatar = document.querySelector(".profile-avatar"); // Mencari wadah foto profil.
  const image = avatar?.querySelector("img.avatar-circle"); // Mencari foto jika tersedia.
  if (!avatar || !image) return; // Berhenti jika profil tidak memiliki foto.
  image.addEventListener("error", function () { // Menangani URL foto yang gagal dimuat.
    const label = image.alt.replace(/\s+profile picture$/i, "").trim(); // Mengambil nama dari teks alternatif.
    const initials = label.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase(); // Membentuk maksimal dua inisial.
    const fallback = document.createElement("span"); // Membuat elemen pengganti foto.
    fallback.className = "avatar-circle avatar-fallback"; // Memakai bentuk lingkaran avatar.
    fallback.textContent = initials || "?"; // Menampilkan inisial atau tanda tanya.
    fallback.setAttribute("aria-label", "Profile picture unavailable"); // Memberi keterangan aksesibilitas.
    image.replaceWith(fallback); // Mengganti foto rusak dengan placeholder.
  }, { once: true }); // Memastikan penggantian hanya dilakukan satu kali.
}); // Mengakhiri pengaturan avatar profil.
