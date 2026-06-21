import os
from handlers.sender import kirim_teks


def kirim_notif_admin(booking: dict):
    admin_number = os.getenv("ADMIN_NUMBER")
    if not admin_number:
        return

    pesan = (
        f"🔔 *Booking Baru!*\n\n"
        f"👤 Nama: {booking.get('nama', '-')}\n"
        f"📱 No WA: wa.me/{booking.get('wa_number', '-')}\n"
        f"📸 Layanan: {booking.get('layanan', '-')}\n"
        f"📦 Paket: {booking.get('paket', '-')}\n"
        f"📅 Tanggal: {booking.get('tanggal', '-')}\n"
        f"🕐 Jam: {booking.get('jam', '-')} WIB\n\n"
        f"Status: ⏳ Menunggu Konfirmasi"
    )
    kirim_teks(admin_number, pesan)
