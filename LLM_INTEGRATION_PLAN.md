# Blueprint: Integrasi LLM ke Bot WhatsApp Studio Foto

> Blueprint ini bisa dibaca dan dipersiapkan **tanpa membeli API terlebih dahulu**.
> Semua kode sudah ditulis dan siap dijalankan — tinggal isi API key saat sudah siap.

---

## Gambaran Arsitektur

### Alur Pesan Sekarang (Rule-Based)
```
User kirim pesan
      ↓
  app.py (terima_pesan)
      ↓
  Tipe pesan?
  ├── interactive → _handle_interactive() → handler sesuai pilihan
  └── text        → _handle_text()        → tampilkan menu utama
```

### Alur Pesan Setelah Integrasi LLM
```
User kirim pesan
      ↓
  app.py (terima_pesan)
      ↓
  Tipe pesan?
  ├── interactive → _handle_interactive() → handler sesuai pilihan
  └── text        → _handle_text()
                        ↓
                    ai_router.route_message()
                        ↓
              ┌─────────┴──────────┐
         RULE_BASED           AI_LLM
              ↓                    ↓
         kirim_menu_utama()   llm_client.tanya_llm()
                                   ↓
                              kirim_teks(jawaban)
```

### Komponen yang Terlibat

| Komponen | Status | Aksi |
|----------|--------|------|
| `app.py` | Sudah ada | **Modifikasi** `_handle_text()` |
| `handlers/ai_router.py` | Draft (belum aktif) | **Aktifkan & sesuaikan** |
| `handlers/llm_client.py` | Belum ada | **Buat baru** |
| `handlers/menu.py` | Sudah ada | **Modifikasi** (tambah tombol AI) |
| `.env` | Sudah ada | **Tambah** key LLM |
| `requirements.txt` | Sudah ada | **Tambah** `openai` |

---

## Pilihan Provider LLM

| Provider | Model | Free Tier | Harga Per Pesan* | Kecepatan | Rekomendasi |
|----------|-------|-----------|-----------------|-----------|-------------|
| **Groq** | llama-3.1-8b | ✅ Gratis (30 req/menit) | $0 | ⚡ Sangat cepat | **Testing gratis** |
| **OpenAI** | gpt-4o-mini | ❌ Pay-as-you-go | ~Rp 2–5/pesan | Cepat | **Produksi** |
| **Google Gemini** | gemini-1.5-flash | ✅ 1500 req/hari | $0 s/d limit | Cepat | Alternatif gratis |
| Ollama (lokal) | llama3.2 | ✅ Gratis | $0 | Lambat | Dev lokal saja |

*\*Estimasi untuk pesan ~200 token*

> **Rekomendasi strategi:**
> 1. Mulai dengan **Groq** (gratis, daftar di `console.groq.com`) untuk testing
> 2. Pindah ke **OpenAI gpt-4o-mini** saat siap produksi (sangat murah)
> 3. Kodenya **tidak perlu diubah** — cukup ganti env var `LLM_PROVIDER`

---

## Step-by-Step Implementasi

### Step 0 — Daftar API Key (Pilih Satu)

**Opsi A: Groq (Gratis)**
1. Buka `console.groq.com`
2. Daftar / Login dengan akun Google
3. Klik **API Keys** → **Create API Key**
4. Salin key → simpan ke `.env` sebagai `GROQ_API_KEY=gsk_...`

**Opsi B: OpenAI (Berbayar, ~$5 untuk mulai)**
1. Buka `platform.openai.com`
2. Daftar akun → **Settings** → **Billing** → isi minimal $5
3. **API Keys** → **Create new secret key**
4. Salin key → simpan ke `.env` sebagai `OPENAI_API_KEY=sk-...`

---

### Step 1 — Install Dependensi

```bash
pip install openai
```

Tambahkan ke `requirements.txt`:
```
openai>=1.0.0
```

> Groq menggunakan SDK yang sama dengan OpenAI (`openai` package) — tidak perlu install tambahan.

---

### Step 2 — Update `.env`

Tambahkan baris berikut ke file `.env`:

```env
# LLM Integration
LLM_PROVIDER=groq              # Ganti ke "openai" saat siap produksi

GROQ_API_KEY=gsk_xxxxxxxx      # Isi jika pakai Groq
# OPENAI_API_KEY=sk-xxxxxxxx   # Isi jika pakai OpenAI
```

---

### Step 3 — Buat `handlers/llm_client.py`

Buat file baru ini. Desainnya **provider-agnostic** — ganti provider hanya dengan env var.

```python
import os
from openai import OpenAI


def _get_client() -> OpenAI:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "groq":
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1",
        )
    else:  # openai
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _get_model() -> str:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    return "llama-3.1-8b-instant" if provider == "groq" else "gpt-4o-mini"


def tanya_llm(system_prompt: str, pesan_user: str) -> str:
    """
    Kirim pesan ke LLM dan return jawaban sebagai string.
    Provider dikontrol via env var LLM_PROVIDER (groq | openai).
    """
    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": pesan_user},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[LLM_ERROR] {e}")
        return "Maaf, asisten AI sedang tidak tersedia. Silakan coba lagi nanti."
```

---

### Step 4 — Update `handlers/ai_router.py`

File ini sudah ada sebagai blueprint. Sesuaikan `build_system_prompt()` untuk konteks studio foto:

```python
FREE_TEXT_STATES = {"FREE_TEXT"}


def route_message(pesan: dict, user_state: str) -> str:
    tipe = pesan.get("type")
    if tipe == "interactive":
        return "RULE_BASED"
    if tipe == "text":
        if user_state in FREE_TEXT_STATES:
            return "AI_LLM"
        teks = pesan.get("text", {}).get("body", "").lower().strip()
        if teks in ("tanya ai", "chat", "tanya"):
            return "ENTER_AI_MODE"
        return "REDIRECT_TO_MENU"
    return "IGNORE"


def build_system_prompt(nama: str) -> str:
    return f"""
Kamu adalah asisten virtual Studio Foto profesional yang melayani pelanggan via WhatsApp.

## Identitas
- Nama: Asisten Studio Foto
- Tone: Ramah, sopan, helpful — seperti staf CS yang berpengalaman
- Bahasa: Indonesia, santai tapi profesional

## Pelanggan Saat Ini
- Nama: {nama}

## Tugas Utama
- Jawab pertanyaan seputar layanan foto studio (indoor, photobooth, produk, wisuda, prewedding)
- Bantu pelanggan memilih paket yang sesuai kebutuhan & budget
- Jelaskan proses booking, persiapan sesi foto, tips foto, dll
- Jika ditanya harga atau ingin booking → arahkan untuk ketik "menu" agar kembali ke menu utama

## Batasan
- JANGAN bahas topik di luar fotografi dan layanan studio
- JANGAN buat janji spesifik di luar yang ada di sistem (harga, tanggal, slot)
- Jika tidak tahu jawaban pasti → sarankan hubungi CS langsung
- Respons maksimal 3 paragraf pendek agar nyaman dibaca di WhatsApp

Untuk kembali ke menu utama, pelanggan bisa ketik: *menu*
""".strip()
```

---

### Step 5 — Modifikasi `app.py`

Update fungsi `_handle_text()` untuk mendeteksi dan menangani mode AI:

```python
# Tambah import di atas
from handlers.ai_router import route_message, build_system_prompt
from handlers.llm_client import tanya_llm

def _handle_text(nomor: str, nama: str, teks: str):
    state = get_state(nomor)
    current = state.get("current_state", "IDLE")

    # Flow booking yang sudah ada
    if current == "TUNGGU_TANGGAL":
        proses_tanggal(nomor, teks, nama)
        return

    # Keluar dari mode AI
    if current == "FREE_TEXT" and teks.lower().strip() in ("menu", "selesai", "keluar"):
        set_state(nomor, "IDLE", {})
        kirim_menu_utama(nomor, nama)
        return

    # Routing ke AI atau menu
    aksi = route_message({"type": "text", "text": {"body": teks}}, current)

    if aksi == "AI_LLM":
        system = build_system_prompt(nama)
        jawaban = tanya_llm(system, teks)
        kirim_teks(nomor, jawaban)

    elif aksi == "ENTER_AI_MODE":
        set_state(nomor, "FREE_TEXT", {})
        kirim_teks(
            nomor,
            f"Halo {nama}! Saya siap menjawab pertanyaan seputar fotografi dan layanan studio kami. 📸\n\n"
            "_Ketik *menu* kapan saja untuk kembali ke menu utama._"
        )

    else:
        kirim_menu_utama(nomor, nama)
```

---

### Step 6 — (Opsional) Tambah Tombol "Tanya AI" di Menu

Update `handlers/menu.py` untuk menambah entry point ke mode AI.
Karena WhatsApp hanya support maks 3 tombol, ganti tombol "Tanya CS" jadi "Tanya AI"
atau buat flow baru:

```python
# Opsi: Ganti btn_cs jadi btn_ai
{"type": "reply", "reply": {"id": "btn_ai", "title": "🤖 Tanya AI"}},
```

Tambahkan handler di `_handle_interactive()` di `app.py`:
```python
if pilihan == "btn_ai":
    set_state(nomor, "FREE_TEXT", {})
    kirim_teks(
        nomor,
        f"Halo {nama}! Tanyakan apapun seputar layanan studio kami. 📸\n\n"
        "_Ketik *menu* untuk kembali ke menu utama._"
    )
    return
```

---

### Step 7 — Testing Lokal

```bash
# Terminal 1: jalankan server
python app.py

# Terminal 2: buka tunnel ngrok
./ngrok http 5000
```

1. Set webhook WhatsApp ke URL ngrok yang muncul
2. Kirim pesan "tanya ai" ke bot → harus masuk mode AI
3. Kirim pertanyaan → harus dapat jawaban dari LLM
4. Ketik "menu" → harus kembali ke menu utama

---

### Step 8 — Deploy ke Render

1. Buka **Render Dashboard** → pilih service bot
2. **Environment** → tambahkan:
   ```
   LLM_PROVIDER = groq
   GROQ_API_KEY = gsk_xxxxxxxx
   ```
3. Push ke GitHub → Render auto-deploy
4. Test via WhatsApp

---

## Estimasi Biaya

| Skenario | Provider | Biaya Bulanan |
|----------|----------|--------------|
| Testing (dev) | Groq | **Rp 0** |
| 100 pelanggan/hari, 5 pesan AI/orang | OpenAI gpt-4o-mini | ~**Rp 15.000–30.000/bulan** |
| 500 pelanggan/hari | OpenAI gpt-4o-mini | ~**Rp 75.000–150.000/bulan** |

> OpenAI gpt-4o-mini: $0.15 per 1 juta input token, $0.60 per 1 juta output token.
> Rata-rata 1 percakapan ~500 token = $0.0001 ≈ Rp 1.6

---

## Ringkasan Perubahan File

```
handlers/
├── llm_client.py      ← BUAT BARU (kode ada di Step 3)
├── ai_router.py       ← UPDATE (kode ada di Step 4)
├── menu.py            ← UPDATE opsional (Step 6)
└── ...

app.py                 ← UPDATE _handle_text() (Step 5)
.env                   ← TAMBAH key LLM (Step 2)
requirements.txt       ← TAMBAH openai (Step 1)
```

---

## Urutan Eksekusi yang Disarankan

```
[ ] Step 0: Daftar Groq (gratis, 5 menit)
[ ] Step 1: pip install openai + update requirements.txt
[ ] Step 2: Tambah env var ke .env
[ ] Step 3: Buat handlers/llm_client.py
[ ] Step 4: Update handlers/ai_router.py
[ ] Step 5: Update app.py
[ ] Step 6: (Opsional) Tambah tombol di menu.py
[ ] Step 7: Test lokal dengan ngrok
[ ] Step 8: Deploy ke Render
```
