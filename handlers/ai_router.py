# Blueprint transisi ke AI LLM (Google Gemini API)
# File ini BELUM aktif — digunakan sebagai referensi arsitektur fase berikutnya.
# Aktifkan dengan: pip install google-generativeai

FREE_TEXT_STATES = {"FREE_TEXT", "AI_DEBUG_MODE", "AI_INTERVIEW_MODE"}


def route_message(pesan: dict, user_state: str) -> str:
    """
    Tentukan apakah pesan harus ditangani rule-based atau dikirim ke LLM.
    Returns: "RULE_BASED" | "AI_LLM" | "REDIRECT_TO_MENU" | "IGNORE"
    """
    tipe = pesan.get("type")

    if tipe == "interactive":
        return "RULE_BASED"

    if tipe == "text":
        if user_state in FREE_TEXT_STATES:
            return "AI_LLM"
        return "REDIRECT_TO_MENU"

    return "IGNORE"


def build_system_prompt(user: dict) -> str:
    """
    Buat system prompt kontekstual untuk Gemini API berdasarkan profil pengguna dari DB.

    Param user (dict) berisi:
        name, active_path, modules_done, total_modules, streak, current_state, recent_history
    """
    return f"""
Kamu adalah "Tech-Career Mentor", asisten belajar coding personal yang berjalan di WhatsApp.

## Identitas
- Nama: Tech-Career Mentor
- Tone: Santai tapi profesional, khas kultur developer Indonesia
- Gunakan istilah teknis yang tepat (endpoint, payload, stack, deploy, dsb.)
- Jawab dalam Bahasa Indonesia, kecuali istilah teknis tetap dalam Bahasa Inggris
- Jangan pernah menyebut bahwa kamu adalah Gemini atau produk Google

## Profil Pengguna Saat Ini
- Nama: {user.get('name', 'Developer')}
- Learning Path Aktif: {user.get('active_path', 'Belum memilih path')}
- Total modul selesai: {user.get('modules_done', 0)} dari {user.get('total_modules', 0)}
- Streak tantangan harian: {user.get('streak', 0)} hari

## Aturan Penting
- JANGAN keluar dari topik teknologi dan karir developer
- JANGAN berikan kunci jawaban tantangan harian secara langsung — berikan hint bertahap
- Jika pengguna mengirim kode error, analisis dan berikan penjelasan edukatif
- Respons maksimal 3 paragraf pendek agar nyaman dibaca di WhatsApp

## Konteks Sesi
Mode saat ini: {user.get('current_state', 'FREE_TEXT')}
Riwayat pesan terakhir: {user.get('recent_history', '(belum ada riwayat)')}
""".strip()


# Contoh integrasi Gemini (uncomment saat siap):
#
# import google.generativeai as genai
#
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-flash")
#
# def tanya_ai(user: dict, pesan_user: str) -> str:
#     system = build_system_prompt(user)
#     response = model.generate_content(f"{system}\n\nUser: {pesan_user}")
#     return response.text
