from flask import Flask, request, jsonify, Response
import os
import threading
from dotenv import load_dotenv

from handlers.sender import kirim_teks
from handlers.menu import kirim_menu_utama
from handlers.services import kirim_list_layanan, kirim_detail_layanan
from handlers.booking import (
    mulai_booking, proses_paket, proses_tanggal,
    proses_jam, konfirmasi_booking, kirim_daftar_booking,
)
from handlers.ai_router import route_message, build_system_prompt
from handlers.llm_client import tanya_llm
from db.supabase_client import upsert_user, get_state, set_state

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER")


def _verifikasi_response(req):
    incoming_token = req.args.get("hub.verify_token")
    if incoming_token == VERIFY_TOKEN:
        resp = Response(req.args.get("hub.challenge", ""))
        resp.headers["ngrok-skip-browser-warning"] = "true"
        return resp
    return "Token salah", 403


@app.route("/test-send")
def test_send():
    secret = request.args.get("secret")
    if not secret or secret != os.getenv("RENDER_SECRET", ""):
        return "Forbidden", 403
    import requests as req
    token = os.getenv("TOKEN", "")
    phone_id = os.getenv("PHONE_ID", "")
    payload = {
        "messaging_product": "whatsapp",
        "to": ADMIN_NUMBER or "",
        "type": "text",
        "text": {"body": "test dari render — Studio Foto Bot"},
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = req.post(f"https://graph.facebook.com/v18.0/{phone_id}/messages",
                 headers=headers, json=payload)
    return jsonify({"status": r.status_code, "response": r.json()})


@app.route("/debug-token")
def debug_token():
    import requests as req
    token = os.getenv("TOKEN", "")
    phone_id = os.getenv("PHONE_ID", "")
    r = req.get(f"https://graph.facebook.com/v18.0/{phone_id}",
                params={"access_token": token})
    return jsonify({
        "token_length": len(token),
        "token_prefix": token[:20] if token else "EMPTY",
        "phone_id": phone_id,
        "meta_api_status": r.status_code,
        "meta_api_response": r.json(),
    })


@app.route("/webhook", methods=["GET"])
def verifikasi():
    return _verifikasi_response(request)


@app.route("/hub", methods=["GET"])
def verifikasi_hub():
    return _verifikasi_response(request)


@app.route("/webhook", methods=["POST"])
def terima_pesan():
    data = request.json
    threading.Thread(target=_proses_webhook, args=(data,), daemon=True).start()
    return jsonify({"status": "ok"})


def _proses_webhook(data):
    print("[WEBHOOK]", data)
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" not in entry:
            return

        pesan = entry["messages"][0]
        nomor = pesan["from"]
        nama = entry["contacts"][0]["profile"]["name"]
        tipe = pesan["type"]

        print(f"[MSG] dari={nomor} nama={nama} tipe={tipe}")

        upsert_user(nomor, nama)

        if tipe == "text":
            _handle_text(nomor, nama, pesan["text"]["body"])

        elif tipe == "interactive":
            pilihan = (
                pesan["interactive"].get("button_reply", {}).get("id")
                or pesan["interactive"].get("list_reply", {}).get("id")
            )
            _handle_interactive(nomor, nama, pilihan)

    except Exception as e:
        print(f"[ERROR] {e}")


def _handle_text(nomor: str, nama: str, teks: str):
    state = get_state(nomor)
    current = state.get("current_state", "IDLE")

    if current == "TUNGGU_TANGGAL":
        proses_tanggal(nomor, teks, nama)
        return

    # Keluar dari mode AI
    if current == "FREE_TEXT" and teks.lower().strip() in ("menu", "selesai", "keluar"):
        set_state(nomor, "IDLE", {})
        kirim_menu_utama(nomor, nama)
        return

    aksi = route_message({"type": "text", "text": {"body": teks}}, current)

    if aksi == "AI_LLM":
        system = build_system_prompt(nama)
        jawaban = tanya_llm(system, teks)
        kirim_teks(nomor, jawaban)

    elif aksi == "ENTER_AI_MODE":
        set_state(nomor, "FREE_TEXT", {})
        kirim_teks(
            nomor,
            f"Halo {nama}! Saya siap menjawab pertanyaan seputar fotografi dan layanan studio kami 📸\n\n"
            "_Ketik *menu* kapan saja untuk kembali ke menu utama._",
        )

    else:
        kirim_menu_utama(nomor, nama)


def _handle_interactive(nomor: str, nama: str, pilihan: str):
    if pilihan is None:
        kirim_teks(nomor, "Maaf, terjadi kesalahan. Silakan coba lagi.")
        return

    # ── Menu utama ────────────────────────────────────────────────────────────
    if pilihan == "btn_layanan":
        kirim_list_layanan(nomor)
        return

    if pilihan == "btn_cek_booking":
        kirim_daftar_booking(nomor)
        return

    if pilihan in ("btn_kembali_menu", "btn_main_menu"):
        kirim_menu_utama(nomor, nama)
        return

    if pilihan == "btn_ai":
        set_state(nomor, "FREE_TEXT", {})
        kirim_teks(
            nomor,
            f"Halo {nama}! Tanyakan apapun seputar fotografi dan layanan studio kami 📸\n\n"
            "_Ketik *menu* kapan saja untuk kembali ke menu utama._",
        )
        return

    if pilihan == "btn_cs":
        if ADMIN_NUMBER:
            kirim_teks(
                ADMIN_NUMBER,
                f"🔔 *Pelanggan butuh bantuan CS!*\n\n"
                f"👤 Nama: {nama}\n"
                f"📱 No WA: wa.me/{nomor}"
            )
        kirim_teks(
            nomor,
            "✅ *Pesanmu sudah kami terima!*\n\n"
            "Tim CS kami akan segera menghubungi Anda.\n"
            "_Jam layanan: Senin–Sabtu 09.00–18.00 WIB_ 😊"
        )
        return

    # ── Pilih layanan dari list ───────────────────────────────────────────────
    if pilihan.startswith("svc_"):
        service_id = pilihan[4:]
        kirim_detail_layanan(nomor, service_id)
        return

    # ── Mulai booking (dari detail layanan) ──────────────────────────────────
    if pilihan.startswith("booking_"):
        service_id = pilihan[8:]
        mulai_booking(nomor, service_id)
        return

    # ── Pilih paket dari list ─────────────────────────────────────────────────
    # format: paket_{service_id}_{paket_id}
    if pilihan.startswith("paket_"):
        parts = pilihan[6:].rsplit("_", 1)
        if len(parts) == 2:
            service_id, paket_id = parts
            proses_paket(nomor, service_id, paket_id)
        return

    # ── Pilih jam dari list ───────────────────────────────────────────────────
    if pilihan.startswith("jam_"):
        proses_jam(nomor, pilihan, nama)
        return

    # ── Konfirmasi atau batal booking ─────────────────────────────────────────
    if pilihan == "btn_konfirmasi":
        konfirmasi_booking(nomor, nama)
        return

    if pilihan == "btn_batal_booking":
        set_state(nomor, "IDLE", {})
        kirim_teks(nomor, "Booking dibatalkan. Ketuk menu di bawah untuk mulai lagi.")
        kirim_menu_utama(nomor, nama)
        return

    kirim_teks(nomor, "Maaf, opsi tidak dikenali. Ketuk sembarang untuk kembali ke menu.")


if __name__ == "__main__":
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    port = int(os.getenv("PORT", 5000))
    print(f"Server berjalan di http://0.0.0.0:{port}")
    from waitress import serve
    serve(app, host="0.0.0.0", port=port)
