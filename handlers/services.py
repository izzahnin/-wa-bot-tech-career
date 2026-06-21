from handlers.sender import kirim_list, kirim_teks, kirim_tombol
from config.content import SERVICES


def kirim_list_layanan(nomor: str):
    rows = []
    for service_id, svc in SERVICES.items():
        rows.append({
            "id": f"svc_{service_id}",
            "title": f"{svc['emoji']} {svc['nama']}",
            "description": f"Mulai Rp {svc['harga_mulai']:,} • {svc['durasi']}".replace(",", "."),
        })

    sections = [{"title": "Pilih Layanan", "rows": rows}]
    kirim_list(
        nomor=nomor,
        header="📸 Layanan Studio Foto",
        body="Kami menyediakan berbagai layanan foto profesional. Pilih layanan yang Anda butuhkan:",
        footer="_Harga dapat berubah sewaktu-waktu_",
        button_label="Lihat Layanan",
        sections=sections,
    )


def kirim_detail_layanan(nomor: str, service_id: str):
    svc = SERVICES.get(service_id)
    if not svc:
        kirim_teks(nomor, "Maaf, layanan tidak ditemukan.")
        return

    paket_lines = []
    for paket_id, paket in svc["paket"].items():
        include_str = ", ".join(paket["include"])
        paket_lines.append(
            f"*{paket['nama']}* — Rp {paket['harga']:,}\n_{include_str}_".replace(",", ".")
        )
    paket_text = "\n\n".join(paket_lines)

    body = (
        f"{svc['emoji']} *{svc['nama']}*\n\n"
        f"{svc['deskripsi']}\n\n"
        f"⏱ Durasi: {svc['durasi']}\n\n"
        f"— *Pilihan Paket* —\n\n"
        f"{paket_text}"
    )
    footer = "_Pilih paket lalu klik Booking_"
    buttons = [
        {"type": "reply", "reply": {"id": f"booking_{service_id}", "title": "📅 Booking Sekarang"}},
        {"type": "reply", "reply": {"id": "btn_layanan",           "title": "🔙 Kembali"}},
    ]
    kirim_tombol(nomor, body, footer, buttons)


def kirim_pilih_paket(nomor: str, service_id: str):
    svc = SERVICES.get(service_id)
    if not svc:
        kirim_teks(nomor, "Maaf, layanan tidak ditemukan.")
        return

    rows = []
    for paket_id, paket in svc["paket"].items():
        rows.append({
            "id": f"paket_{service_id}_{paket_id}",
            "title": f"{paket['nama']} — Rp {paket['harga']:,}".replace(",", "."),
            "description": ", ".join(paket["include"][:2]) + "...",
        })

    sections = [{"title": "Pilih Paket", "rows": rows}]
    kirim_list(
        nomor=nomor,
        header=f"Pilih Paket — {svc['nama']}",
        body="Pilih paket yang sesuai dengan kebutuhan Anda:",
        footer="_Harga sudah termasuk editing foto_",
        button_label="Pilih Paket",
        sections=sections,
    )
