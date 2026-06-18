from flask import Flask, request, jsonify, Response
import os
from dotenv import load_dotenv

from handlers.sender import kirim_teks
from handlers.menu import kirim_menu_utama, kirim_menu_roadmap
from handlers.roadmap import kirim_detail_path, kirim_konfirmasi_enroll
from handlers.challenge import kirim_tantangan_harian, kirim_respons_challenge, kirim_placeholder_progress
from db.supabase_client import (
    upsert_user, get_user, save_enrollment,
    save_challenge_response, get_streak, get_challenge_day, get_done_this_week,
)

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ADMIN_NUMBER = os.getenv("ADMIN_NUMBER")

ROADMAP_PATH_IDS = {
    "path_backend_golang",
    "path_frontend_react",
    "path_cloud_engineer",
    "path_fullstack",
    "path_devops",
    "path_mobile_flutter",
}


def _verifikasi_response(req):
    incoming_token = req.args.get("hub.verify_token")
    print(f"[VERIFY] incoming={repr(incoming_token)} expected={repr(VERIFY_TOKEN)}")
    if incoming_token == VERIFY_TOKEN:
        resp = Response(req.args.get("hub.challenge", ""))
        resp.headers["ngrok-skip-browser-warning"] = "true"
        return resp
    return "Token salah", 403

@app.route("/webhook", methods=["GET"])
def verifikasi():
    return _verifikasi_response(request)


@app.route("/hub", methods=["GET"])
def verifikasi_hub():
    return _verifikasi_response(request)


@app.route("/webhook", methods=["POST"])
def terima_pesan():
    data = request.json
    print("[WEBHOOK]", data)
    try:
        entry = data["entry"][0]["changes"][0]["value"]
        if "messages" not in entry:
            return jsonify({"status": "ok"})

        pesan = entry["messages"][0]
        nomor = pesan["from"]
        nama = entry["contacts"][0]["profile"]["name"]
        tipe = pesan["type"]

        print(f"[MSG] dari={nomor} nama={nama} tipe={tipe}")

        upsert_user(nomor, nama)

        if tipe == "text":
            kirim_menu_utama(nomor, nama)

        elif tipe == "interactive":
            pilihan = (
                pesan["interactive"].get("button_reply", {}).get("id")
                or pesan["interactive"].get("list_reply", {}).get("id")
            )
            _handle_interactive(nomor, nama, pilihan)

    except Exception as e:
        print(f"[ERROR] {e}")

    return jsonify({"status": "ok"})


def _handle_interactive(nomor: str, nama: str, pilihan: str):
    if pilihan is None:
        kirim_teks(nomor, "Maaf, terjadi kesalahan. Coba lagi ya!")
        return

    # ── Navigasi utama ──────────────────────────────────────────────────────
    if pilihan == "btn_roadmap" or pilihan == "btn_main_menu_roadmap":
        kirim_menu_roadmap(nomor)
        return

    if pilihan == "btn_main_menu":
        kirim_menu_utama(nomor, nama)
        return

    if pilihan == "btn_progress":
        kirim_placeholder_progress(nomor, nama)
        return

    if pilihan == "btn_challenge":
        user = get_user(nomor)
        path_id = user.get("active_path") or "path_backend_golang"
        day = get_challenge_day(user["id"], path_id) if user.get("id") else 1
        kirim_tantangan_harian(nomor, path_id=path_id, day=day)
        return

    # ── Pilih roadmap (dari list message) ──────────────────────────────────
    if pilihan in ROADMAP_PATH_IDS:
        kirim_detail_path(nomor, pilihan)
        return

    # ── Enroll ke path ──────────────────────────────────────────────────────
    if pilihan.startswith("enroll_"):
        path_id = pilihan.replace("enroll_", "", 1)
        user = upsert_user(nomor, nama)
        if user.get("id"):
            save_enrollment(user["id"], path_id)
        kirim_konfirmasi_enroll(nomor, nama, path_id)
        # Notifikasi ke admin
        if ADMIN_NUMBER:
            kirim_teks(
                ADMIN_NUMBER,
                f"🔔 *Enrollment Baru!*\n\n"
                f"👤 Nama: {nama}\n"
                f"📱 Nomor: +{nomor}\n"
                f"🗺️ Path: {path_id}\n"
                f"🔗 wa.me/{nomor}"
            )
        return

    # ── Respons tantangan harian ────────────────────────────────────────────
    if pilihan.startswith("challenge_"):
        parts = pilihan.split("_")
        action = parts[1]
        day = int(parts[2].replace("day", "")) if len(parts) > 2 else 1
        user = get_user(nomor)
        if user.get("id") and action in ("done", "skip"):
            path_id = user.get("active_path") or "path_backend_golang"
            status = "done" if action == "done" else "skipped"
            save_challenge_response(user["id"], path_id, day, status)
            streak = get_streak(user["id"])
            done_week = get_done_this_week(user["id"])
        else:
            streak, done_week = 0, 0
        kirim_respons_challenge(nomor, nama, day, action, streak=streak, done_this_week=done_week)
        return

    # ── Tanya CS ─────────────────────────────────────────────────────────────
    if pilihan == "cs":
        if ADMIN_NUMBER:
            kirim_teks(
                ADMIN_NUMBER,
                f"🔔 *Ada pengguna butuh bantuan!*\n\n"
                f"👤 Nama: {nama}\n📱 Nomor: +{nomor}\n🔗 wa.me/{nomor}"
            )
        kirim_teks(
            nomor,
            "✅ *Pesanmu sudah diterima!*\n\n"
            "Tim kami akan segera menghubungimu.\n"
            "_Jam layanan: Senin–Jumat 09.00–17.00 WIB_ 😊"
        )
        return

    kirim_teks(nomor, "Maaf, opsi tidak dikenali. Ketik sembarang untuk kembali ke menu utama.")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
