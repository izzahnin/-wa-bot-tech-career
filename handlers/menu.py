from handlers.sender import kirim_tombol


def kirim_menu_utama(nomor: str, nama: str):
    body = (
        f"*Halo, {nama}! Selamat datang di Studio Foto Kami 📸*\n\n"
        "Kami siap membantu mengabadikan momen berharga Anda dengan hasil foto profesional.\n\n"
        "Ada yang bisa kami bantu?"
    )
    footer = "_Senin–Sabtu, 09.00–18.00 WIB_"
    buttons = [
        {"type": "reply", "reply": {"id": "btn_layanan",  "title": "📸 Lihat Layanan"}},
        {"type": "reply", "reply": {"id": "btn_cek_booking", "title": "📅 Cek Booking Saya"}},
        {"type": "reply", "reply": {"id": "btn_cs",       "title": "💬 Tanya CS"}},
    ]
    kirim_tombol(nomor, body, footer, buttons)
