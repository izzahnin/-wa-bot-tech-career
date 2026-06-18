from handlers.sender import kirim_gambar_tombol, kirim_teks
from config.content import ROADMAP_PATHS

ROADMAP_IMAGES = {
    "path_backend_golang":  "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=800&q=80",
    "path_frontend_react":  "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&q=80",
    "path_cloud_engineer":  "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
    "path_fullstack":       "https://images.unsplash.com/photo-1555066931-4365d14431b9?w=800&q=80",
    "path_devops":          "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
    "path_mobile_flutter":  "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&q=80",
}



def kirim_detail_path(nomor: str, path_id: str):
    path = ROADMAP_PATHS.get(path_id)
    if not path:
        kirim_teks(nomor, "❌ Path tidak ditemukan. Silakan pilih ulang dari menu roadmap.")
        return

    stack_lines = "\n".join(f"• {s}" for s in path["stack"])
    salary_lines = "\n".join(f"• {s}" for s in path["salary"])

    body = (
        f"*{path['emoji']} {path['title']}*\n\n"
        f"_Dari nol sampai siap kerja di industri._\n\n"
        f"*Tech Stack yang akan kamu kuasai:*\n{stack_lines}\n\n"
        f"*📈 Ekspektasi Karir & Gaji (2026):*\n{salary_lines}\n\n"
        f"*⏱️ Durasi Roadmap:* {path['duration']}\n"
        f"*📦 Total Modul:* {path['total_modules']} modul + {path['total_challenges']} tantangan koding"
    )
    footer = "_Data gaji berdasarkan survei industri 2026_"
    buttons = [
        {"type": "reply", "reply": {"id": f"enroll_{path_id}", "title": "✅ Ikuti Path Ini"}},
        {"type": "reply", "reply": {"id": "btn_roadmap",       "title": "↩️ Ganti Path"}},
        {"type": "reply", "reply": {"id": "btn_main_menu",     "title": "🏠 Menu Utama"}},
    ]
    kirim_gambar_tombol(nomor, ROADMAP_IMAGES[path_id], body, footer, buttons)


def kirim_konfirmasi_enroll(nomor: str, nama: str, path_id: str):
    path = ROADMAP_PATHS.get(path_id)
    if not path:
        return

    kirim_teks(
        nomor,
        f"*🎉 Selamat, {nama}!*\n\n"
        f"Kamu resmi terdaftar di path *{path['emoji']} {path['title']}*.\n\n"
        f"*Apa yang akan terjadi selanjutnya:*\n"
        f"• Modul pertama sudah di-unlock ✅\n"
        f"• Tantangan harian pertama dikirim besok pagi jam 07.00 WIB ⚡\n"
        f"• Kamu bisa cek progres kapan saja lewat menu 📊\n\n"
        f"_Konsisten itu kunci. Sampai jumpa di sesi pertama!_ 💪"
    )
