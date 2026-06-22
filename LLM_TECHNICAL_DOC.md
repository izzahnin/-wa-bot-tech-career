# Dokumentasi Teknis: Cara Kerja LLM di Bot Ini

## Apa Itu LLM?

**LLM (Large Language Model)** adalah model AI yang dilatih pada miliaran teks sehingga bisa memahami dan menghasilkan bahasa manusia. Contoh: Gemini (Google), GPT-4 (OpenAI), Claude (Anthropic).

Bot ini menggunakan **Google Gemini 2.0 Flash** — model yang cepat dan gratis hingga 1500 request/hari.

---

## Arsitektur: Bagaimana Pesan Mengalir ke LLM

```
[User kirim pesan WhatsApp]
          │
          ▼
    app.py — terima_pesan()
          │
          ├─ tipe: "interactive" (klik tombol)
          │         └─ _handle_interactive() ──→ handler sesuai pilihan
          │
          └─ tipe: "text" (ketik bebas)
                    └─ _handle_text()
                              │
                              ▼
                    ai_router.route_message()
                              │
                    ┌─────────┴──────────────┐
                    │                        │
               State = IDLE            State = FREE_TEXT
               teks = "tanya ai"       (sudah di mode AI)
                    │                        │
                    ▼                        ▼
             ENTER_AI_MODE              AI_LLM
                    │                        │
              set_state                      │
             "FREE_TEXT"                     │
                    │                        │
                    └─────────┬──────────────┘
                              ▼
                   llm_client.tanya_llm()
                              │
                    ┌─────────▼──────────┐
                    │  build_system_     │
                    │  prompt(nama)      │  ← Konteks siapa bot ini
                    │  + pesan_user      │  ← Apa yang ditulis user
                    └─────────┬──────────┘
                              │
                              ▼
                  Google Gemini API (internet)
                              │
                              ▼
                    response.text (jawaban AI)
                              │
                              ▼
                   kirim_teks(nomor, jawaban)
                              │
                              ▼
                  [User terima jawaban di WhatsApp]
```

---

## Komponen Kunci

### 1. State Machine (Mesin State)

Bot menggunakan **state** untuk tahu sedang di tahap mana percakapan user.

| State | Artinya | Pesan teks diarahkan ke |
|-------|---------|------------------------|
| `IDLE` | Idle / menu utama | Menu utama |
| `TUNGGU_TANGGAL` | Menunggu input tanggal booking | Handler booking |
| `PILIH_PAKET` | Sedang pilih paket | (via tombol interaktif) |
| `PILIH_JAM` | Sedang pilih jam | (via tombol interaktif) |
| `KONFIRMASI` | Konfirmasi booking | (via tombol interaktif) |
| `FREE_TEXT` | **Mode AI aktif** | **LLM (Gemini)** |

State disimpan di **Supabase** tabel `conversation_state`, bukan di memori server.
Ini penting agar state tidak hilang kalau server restart.

---

### 2. System Prompt

**System prompt** adalah instruksi rahasia yang dikirim ke LLM di setiap request — user tidak melihatnya. Ini yang membentuk "kepribadian" dan batasan bot.

```
System Prompt                     Pesan User
─────────────                     ──────────
"Kamu adalah asisten    +         "Berapa harga foto wisuda?"
studio foto, jawab                
dalam bahasa Indonesia,
jangan bahas topik lain..."
         │                               │
         └─────────────┬─────────────────┘
                       ▼
              [Gemini memproses]
                       ▼
              "Untuk foto wisuda, kami
               punya 3 paket mulai dari
               Rp 175.000..."
```

File: `handlers/ai_router.py` → fungsi `build_system_prompt(nama)`

---

### 3. Token & Batas Panjang

LLM mengukur teks dalam satuan **token** (±1 token = ¾ kata bahasa Indonesia).

| Bagian | Estimasi Token |
|--------|---------------|
| System prompt | ~200 token |
| Pesan user | ~50–100 token |
| Jawaban bot | maks 500 token (dibatasi di kode) |
| **Total per request** | **~750–800 token** |

Pengaturan di `llm_client.py`:
```python
generation_config={"max_output_tokens": 500, "temperature": 0.7}
```

- **`max_output_tokens: 500`** — batas panjang jawaban (~375 kata). Cukup untuk 3 paragraf WhatsApp.
- **`temperature: 0.7`** — tingkat "kreativitas" (0 = kaku/konsisten, 1 = kreatif/random). 0.7 = balance.

---

### 4. Alur Data Lengkap (dengan kode)

```
User ketik "tanya ai"
    ↓
app.py: _handle_text(nomor="628xx", nama="Budi", teks="tanya ai")
    ↓
state = get_state("628xx") → {"current_state": "IDLE"}
    ↓
ai_router.route_message({"type":"text","text":{"body":"tanya ai"}}, "IDLE")
    → return "ENTER_AI_MODE"
    ↓
set_state("628xx", "FREE_TEXT", {})   ← simpan ke Supabase
    ↓
kirim_teks("628xx", "Halo Budi! Tanyakan apapun...")


User ketik "berapa harga photobooth?"
    ↓
app.py: _handle_text(nomor="628xx", nama="Budi", teks="berapa harga photobooth?")
    ↓
state = get_state("628xx") → {"current_state": "FREE_TEXT"}
    ↓
ai_router.route_message(..., "FREE_TEXT") → return "AI_LLM"
    ↓
system = build_system_prompt("Budi")
    → "Kamu adalah asisten studio foto... Pelanggan: Budi..."
    ↓
llm_client.tanya_llm(system, "berapa harga photobooth?")
    ↓
  [HTTP POST ke api.gemini.google.com]
  payload: {
    model: "gemini-2.0-flash",
    contents: "<system_prompt>\n\nPelanggan: berapa harga photobooth?"
  }
    ↓
  response.text = "Photobooth tersedia dengan 3 paket:
                   Basic Rp 100.000 (30 menit)..."
    ↓
kirim_teks("628xx", "Photobooth tersedia dengan 3 paket...")
```

---

## Keterbatasan Saat Ini

| Keterbatasan | Penjelasan | Solusi ke Depan |
|--------------|-----------|----------------|
| **Tanpa memori** | Setiap pesan ke LLM tidak tahu isi percakapan sebelumnya | Simpan riwayat chat di Supabase, kirim sebagai konteks |
| **Tidak tahu data realtime** | LLM tidak tahu slot booking yang tersedia | Inject data dari DB ke system prompt |
| **Konteks hanya dari system prompt** | LLM tidak tahu harga pasti kecuali ada di prompt | Masukkan `SERVICES` dari `config/content.py` ke prompt |

---

## Cara Mendapatkan API Key Gemini (Gratis)

1. Buka **`aistudio.google.com`**
2. Login dengan akun Google
3. Klik **"Get API key"** → **"Create API key"**
4. Key yang valid diawali **`AIza...`** (panjang ~39 karakter)
5. Salin ke `.env`:
   ```
   GEMINI_API_KEY=AIzaSy...
   ```

> ⚠️ Key yang diawali `AQ.` adalah OAuth token, **bukan** API key — tidak akan berfungsi.

---

## Free Tier Gemini 2.0 Flash

| Limit | Nilai |
|-------|-------|
| Request per menit | 15 RPM |
| Request per hari | 1.500 RPD |
| Token per menit | 1.000.000 TPM |
| Biaya | **Gratis** |

Untuk skala kecil-menengah (< 500 pesan AI/hari), free tier sudah lebih dari cukup.
