from handlers.sender import kirim_gambar_tombol, kirim_list

BANNER_URL = "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&q=80"

def kirim_menu_utama(nomor: str, nama: str):
    body = (
        f"*Halo, {nama}! Selamat datang di Tech-Career Mentor! 🚀*\n\n"
        "_Platform belajar untuk developer pemula yang ingin naik level._\n\n"
        "Pilih jalur karir kamu, ikuti roadmap terstruktur, dan selesaikan "
        "tantangan koding harian — semua lewat WhatsApp.\n\n"
        "Mau mulai dari mana?"
    )
    footer = "_Gratis untuk 30 hari pertama ✨_"
    buttons = [
        {"type": "reply", "reply": {"id": "btn_roadmap",   "title": "🗺️ Pilih Roadmap"}},
        {"type": "reply", "reply": {"id": "btn_progress",  "title": "📊 Progres Saya"}},
        {"type": "reply", "reply": {"id": "btn_challenge", "title": "⚡ Tantangan Hari Ini"}},
    ]
    kirim_gambar_tombol(nomor, BANNER_URL, body, footer, buttons)


def kirim_menu_roadmap(nomor: str):
    sections = [{
        "title": "Pilih Disiplin Ilmu",
        "rows": [
            {"id": "path_backend_golang",  "title": "🐹 Backend — Golang",      "description": "REST API, gRPC, PostgreSQL, Docker"},
            {"id": "path_frontend_react",  "title": "⚛️ Frontend — React",       "description": "React 19, TypeScript, Next.js, Tailwind"},
            {"id": "path_cloud_engineer",  "title": "☁️ Cloud Engineer",         "description": "AWS/GCP, Terraform, CI/CD, Kubernetes"},
            {"id": "path_fullstack",       "title": "🔥 Fullstack (Go + React)", "description": "Combo Backend + Frontend production-ready"},
            {"id": "path_devops",          "title": "🛠️ DevOps Engineer",        "description": "Linux, Docker, GitHub Actions, Monitoring"},
            {"id": "path_mobile_flutter",  "title": "📱 Mobile — Flutter",       "description": "Dart, Flutter, Firebase, App Store deploy"},
        ],
    }]
    kirim_list(
        nomor=nomor,
        header="Pilih Jalur Karir Kamu 🎯",
        body=(
            "Setiap path dirancang dari *nol sampai siap kerja*.\n"
            "Pilih disiplin yang paling sesuai dengan tujuan karir kamu:"
        ),
        footer="_Bisa ganti path kapan saja_",
        button_label="Lihat Semua Path",
        sections=sections,
    )
