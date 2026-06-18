from handlers.sender import kirim_gambar_tombol, kirim_teks
from config.content import DAILY_CHALLENGES

CHALLENGE_CARD_URL = "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=800&q=80"


def kirim_tantangan_harian(nomor: str, path_id: str, day: int):
    challenges = DAILY_CHALLENGES.get(path_id, [])
    challenge = next((c for c in challenges if c["day"] == day), None)

    if not challenge:
        kirim_teks(
            nomor,
            f"*⚡ Tantangan Hari Ini — Day {day}*\n\n"
            f"_Tantangan untuk hari ini sedang disiapkan. Stay tuned!_ 🔧"
        )
        return

    body = (
        f"*⚡ Tantangan Hari Ini — Day {day}*\n"
        f"_Path: {path_id.replace('path_', '').replace('_', ' ').title()} · "
        f"Topik: {challenge['topic']}_\n\n"
        f"───────────────────\n\n"
        f"*📋 Studi Kasus:*\n{challenge['case']}\n\n"
        f"*⏰ Deadline submit:* Hari ini sebelum tengah malam"
    )
    buttons = [
        {"type": "reply", "reply": {"id": f"challenge_done_day{day}",  "title": "✅ Sudah Selesai!"}},
        {"type": "reply", "reply": {"id": f"challenge_hint_day{day}",  "title": "💡 Minta Hint"}},
        {"type": "reply", "reply": {"id": f"challenge_skip_day{day}",  "title": "⏭️ Skip Hari Ini"}},
    ]
    kirim_gambar_tombol(nomor, CHALLENGE_CARD_URL, body, "_Kerjakan dengan jujur ya!_", buttons)


def kirim_respons_challenge(nomor: str, nama: str, day: int, action: str, streak: int = 1, done_this_week: int = 1):
    if action == "done":
        kirim_teks(
            nomor,
            f"*🎉 Mantap, {nama}!*\n\n"
            f"Day {day} sudah kamu centang. _Keep the momentum!_\n\n"
            f"📊 *Progres minggu ini:* {done_this_week}/7 tantangan selesai\n"
            f"🔥 *Streak aktif:* {streak} hari berturut-turut\n\n"
            f"Tantangan berikutnya unlock besok pagi jam 07.00 WIB.\n"
            f"Sampai jumpa, _senior engineer_! 💪"
        )
    elif action == "hint":
        kirim_teks(
            nomor,
            f"*💡 Hint untuk Day {day}*\n\n"
            f"Coba pikirkan dari sisi *kompleksitas waktu* dulu:\n"
            f"• Apakah kamu bisa selesaikan dengan satu kali loop?\n"
            f"• Data structure apa yang bisa membantu menyimpan state sementara?\n\n"
            f"_Kalau masih mentok, ketik pertanyaanmu secara bebas — "
            f"AI Mentor kita akan segera hadir untuk bantu debug!_ 🤖"
        )
    elif action == "skip":
        kirim_teks(
            nomor,
            f"*⏭️ Okay, {nama}. Hari ini di-skip.*\n\n"
            f"Streak kamu akan reset ke 0, tapi tidak apa-apa!\n"
            f"Yang penting tetap konsisten besok. 💪\n\n"
            f"_Tantangan hari ini akan tetap tersimpan di riwayat kamu._"
        )


def kirim_placeholder_progress(nomor: str, nama: str):
    kirim_teks(
        nomor,
        f"*📊 Progres Belajar — {nama}*\n\n"
        f"_Fitur ini akan aktif setelah kamu memilih path belajar._\n\n"
        f"Yuk pilih roadmap dulu! Ketuk tombol di bawah untuk mulai 👇"
    )
