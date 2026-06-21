from datetime import datetime, date, timedelta

from handlers.sender import kirim_teks, kirim_tombol, kirim_list
from config.content import SERVICES, TIME_SLOTS, STATUS_LABEL
from db.supabase_client import (
    get_state, set_state,
    save_booking, get_bookings, update_booking_status, is_slot_available,
)


def _format_rupiah(harga: int) -> str:
    return f"Rp {harga:,}".replace(",", ".")


def mulai_booking(nomor: str, service_id: str):
    """Dipanggil setelah user klik 'Booking Sekarang' dari detail layanan."""
    svc = SERVICES.get(service_id)
    if not svc:
        kirim_teks(nomor, "Maaf, layanan tidak ditemukan.")
        return

    set_state(nomor, "PILIH_PAKET", {"service_id": service_id})

    rows = []
    for paket_id, paket in svc["paket"].items():
        rows.append({
            "id": f"paket_{service_id}_{paket_id}",
            "title": f"{paket['nama']} — {_format_rupiah(paket['harga'])}",
            "description": ", ".join(paket["include"][:2]) + "...",
        })

    kirim_list(
        nomor=nomor,
        header=f"Pilih Paket — {svc['nama']}",
        body="Pilih paket yang sesuai dengan kebutuhan Anda:",
        footer="_Harga sudah termasuk editing foto_",
        button_label="Pilih Paket",
        sections=[{"title": "Pilihan Paket", "rows": rows}],
    )


def proses_paket(nomor: str, service_id: str, paket_id: str):
    """Dipanggil setelah user memilih paket dari list."""
    svc = SERVICES.get(service_id)
    if not svc:
        kirim_teks(nomor, "Maaf, layanan tidak ditemukan.")
        return

    paket = svc["paket"].get(paket_id)
    if not paket:
        kirim_teks(nomor, "Maaf, paket tidak ditemukan.")
        return

    set_state(nomor, "TUNGGU_TANGGAL", {"service_id": service_id, "paket_id": paket_id})

    besok = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
    maks = (date.today() + timedelta(days=30)).strftime("%d/%m/%Y")

    kirim_teks(
        nomor,
        f"Oke! Anda memilih *{svc['nama']}* paket *{paket['nama']}* "
        f"({_format_rupiah(paket['harga'])}).\n\n"
        f"📅 *Silakan ketik tanggal sesi Anda:*\n"
        f"Format: DD/MM/YYYY\n\n"
        f"Contoh: {besok}\n"
        f"_(Tersedia: {besok} s/d {maks})_"
    )


def proses_tanggal(nomor: str, teks: str, nama: str):
    """Dipanggil saat state = TUNGGU_TANGGAL dan user mengirim teks."""
    state = get_state(nomor)
    ctx = state.get("context_data", {})

    try:
        tgl = datetime.strptime(teks.strip(), "%d/%m/%Y").date()
    except ValueError:
        kirim_teks(
            nomor,
            "Format tanggal tidak valid. Gunakan format *DD/MM/YYYY*.\nContoh: 25/07/2025"
        )
        return

    hari_ini = date.today()
    if tgl <= hari_ini:
        kirim_teks(nomor, "Tanggal harus minimal *besok*. Silakan pilih tanggal lain.")
        return

    if tgl > hari_ini + timedelta(days=30):
        kirim_teks(nomor, "Booking hanya tersedia *maksimal 30 hari* ke depan.")
        return

    tgl_str = tgl.strftime("%Y-%m-%d")
    tgl_label = tgl.strftime("%d %B %Y")

    # Cek ketersediaan setiap slot
    rows = []
    for jam in TIME_SLOTS:
        tersedia = is_slot_available(tgl_str, jam)
        if tersedia:
            rows.append({
                "id": f"jam_{jam.replace('.', '_')}",
                "title": f"🕐 {jam} WIB",
                "description": "Tersedia",
            })

    if not rows:
        kirim_teks(
            nomor,
            f"Maaf, tidak ada slot tersedia pada *{tgl_label}*.\nSilakan ketik tanggal lain."
        )
        return

    ctx["tanggal"] = tgl_str
    ctx["tanggal_label"] = tgl_label
    set_state(nomor, "PILIH_JAM", ctx)

    kirim_list(
        nomor=nomor,
        header=f"Pilih Jam — {tgl_label}",
        body="Pilih jam sesi yang tersedia:",
        footer="_Sesi berdurasi sesuai paket yang dipilih_",
        button_label="Pilih Jam",
        sections=[{"title": "Jam Tersedia", "rows": rows}],
    )


def proses_jam(nomor: str, jam_id: str, nama: str):
    """Dipanggil setelah user memilih jam dari list."""
    # jam_id format: jam_09_00
    jam = jam_id.replace("jam_", "").replace("_", ".")

    state = get_state(nomor)
    ctx = state.get("context_data", {})

    service_id = ctx.get("service_id")
    paket_id = ctx.get("paket_id")
    tanggal = ctx.get("tanggal")
    tanggal_label = ctx.get("tanggal_label")

    svc = SERVICES.get(service_id, {})
    paket = svc.get("paket", {}).get(paket_id, {})

    ctx["jam"] = jam
    set_state(nomor, "KONFIRMASI", ctx)

    include_str = "\n".join([f"  ✓ {item}" for item in paket.get("include", [])])
    body = (
        f"📋 *Ringkasan Booking Anda:*\n\n"
        f"📸 Layanan: {svc.get('nama', '-')}\n"
        f"📦 Paket: {paket.get('nama', '-')} — {_format_rupiah(paket.get('harga', 0))}\n"
        f"📅 Tanggal: {tanggal_label}\n"
        f"🕐 Jam: {jam} WIB\n\n"
        f"*Yang termasuk:*\n{include_str}\n\n"
        f"Konfirmasi booking ini?"
    )
    buttons = [
        {"type": "reply", "reply": {"id": "btn_konfirmasi", "title": "✅ Konfirmasi"}},
        {"type": "reply", "reply": {"id": "btn_batal_booking", "title": "❌ Batalkan"}},
    ]
    kirim_tombol(nomor, body, "_Booking akan dikonfirmasi oleh tim kami_", buttons)


def konfirmasi_booking(nomor: str, nama: str):
    """Dipanggil setelah user klik Konfirmasi."""
    from handlers.admin import kirim_notif_admin

    state = get_state(nomor)
    ctx = state.get("context_data", {})

    service_id = ctx.get("service_id")
    paket_id = ctx.get("paket_id")
    tanggal = ctx.get("tanggal")
    jam = ctx.get("jam")

    svc = SERVICES.get(service_id, {})
    paket = svc.get("paket", {}).get(paket_id, {})

    booking = save_booking(
        wa_number=nomor,
        nama=nama,
        layanan=svc.get("nama", service_id),
        paket=paket.get("nama", paket_id),
        tanggal=tanggal,
        jam=jam,
    )

    set_state(nomor, "IDLE", {})

    tgl_label = ctx.get("tanggal_label", tanggal)
    kirim_teks(
        nomor,
        f"✅ *Booking Berhasil!*\n\n"
        f"Terima kasih, *{nama}*!\n"
        f"Booking Anda telah kami terima.\n\n"
        f"📸 {svc.get('nama', '-')} — Paket {paket.get('nama', '-')}\n"
        f"📅 {tgl_label}, pukul {jam} WIB\n\n"
        f"Tim kami akan segera menghubungi Anda untuk konfirmasi.\n"
        f"_Jam layanan: Senin–Sabtu 09.00–18.00 WIB_"
    )

    kirim_notif_admin({
        "nama": nama,
        "wa_number": nomor,
        "layanan": svc.get("nama", service_id),
        "paket": paket.get("nama", paket_id),
        "tanggal": tgl_label,
        "jam": jam,
    })


def kirim_daftar_booking(nomor: str):
    """Tampilkan booking aktif milik pelanggan."""
    bookings = get_bookings(nomor)

    if not bookings:
        kirim_teks(
            nomor,
            "📅 Anda belum memiliki booking aktif.\n\n"
            "Ketuk *Lihat Layanan* untuk mulai booking."
        )
        return

    lines = ["📅 *Booking Anda:*\n"]
    for i, b in enumerate(bookings, start=1):
        status_label = STATUS_LABEL.get(b["status"], b["status"])
        try:
            tgl = datetime.strptime(b["tanggal"], "%Y-%m-%d").strftime("%d %b %Y")
        except Exception:
            tgl = b["tanggal"]
        lines.append(
            f"*{i}. {b['layanan']}*\n"
            f"   Paket: {b['paket']}\n"
            f"   Tanggal: {tgl}, {b['jam']} WIB\n"
            f"   Status: {status_label}\n"
            f"   ID: `{b['id'][:8]}...`"
        )

    pesan = "\n\n".join(lines)
    buttons = [
        {"type": "reply", "reply": {"id": "btn_layanan",      "title": "📸 Booking Lagi"}},
        {"type": "reply", "reply": {"id": "btn_kembali_menu", "title": "🔙 Menu Utama"}},
    ]
    kirim_tombol(nomor, pesan, "_Hubungi CS untuk membatalkan booking_", buttons)
