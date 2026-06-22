# Struktur Folder Proyek

```
bot-testing/
├── app.py                    # Entry point utama — Flask webhook & routing pesan masuk
├── requirements.txt          # Daftar dependensi Python
├── Procfile                  # Konfigurasi proses untuk deploy (Render/Heroku)
├── Procfile.txt
├── .env                      # Environment variables (tidak di-commit ke git)
├── .gitignore
├── ngrok.exe                 # Tool tunnel lokal untuk testing webhook
│
├── PROJECT_STRUCTURE.md      # Dokumentasi struktur folder & fungsi tiap file (file ini)
├── LLM_INTEGRATION_PLAN.md   # Blueprint & tutorial step-by-step integrasi LLM
├── LLM_TECHNICAL_DOC.md      # Dokumentasi teknis cara kerja LLM & arsitektur AI
│
├── config/
│   ├── __init__.py
│   └── content.py            # Data master layanan, slot waktu, dan label status booking
│
├── db/
│   ├── __init__.py
│   ├── supabase_client.py    # Koneksi & semua query ke Supabase
│   └── schema.sql            # Definisi skema tabel database
│
├── handlers/
│   ├── __init__.py
│   ├── admin.py              # Notifikasi booking baru ke admin
│   ├── ai_router.py          # Routing pesan ke LLM — aktif sejak integrasi Gemini
│   ├── llm_client.py         # Wrapper Google Gemini API — fungsi tanya_llm()
│   ├── booking.py            # Alur booking lengkap (pilih paket → tanggal → jam → konfirmasi)
│   ├── challenge.py          # Fitur challenge/tantangan harian
│   ├── menu.py               # Kirim menu utama WhatsApp
│   ├── roadmap.py            # Fitur learning path & enrollment
│   ├── sender.py             # Utilitas kirim pesan & media ke WhatsApp Cloud API
│   └── services.py           # Tampilkan daftar & detail layanan foto studio
│
└── venv/                     # Virtual environment Python (tidak di-commit ke git)
```

---

## Detail File & Fungsi

### `app.py`
Entry point Flask. Menerima semua webhook dari Meta, lalu mendispatch ke handler yang sesuai.

| Fungsi | Keterangan |
|--------|-----------|
| `_verifikasi_response(req)` | Validasi token webhook dari Meta (handshake awal) |
| `verifikasi()` | Endpoint GET `/webhook` — verifikasi webhook |
| `verifikasi_hub()` | Endpoint GET `/hub` — alternatif verifikasi webhook |
| `terima_pesan()` | Endpoint POST `/webhook` — entry point semua pesan masuk WhatsApp |
| `_handle_text(nomor, nama, teks)` | Routing pesan teks berdasarkan state percakapan user |
| `_handle_interactive(nomor, nama, pilihan)` | Routing klik tombol/list ke fungsi yang sesuai |
| `test_send()` | Endpoint debug: kirim pesan test ke admin langsung dari server |
| `debug_token()` | Endpoint debug: cek status token & Phone ID ke Meta API |

---

### `config/content.py`
File konfigurasi statis. Tidak ada fungsi — hanya berisi konstanta data.

| Konstanta | Keterangan |
|-----------|-----------|
| `SERVICES` | Data master 5 layanan foto (Studio Indoor, Photobooth, Foto Produk, Foto Wisuda, Pre-Wedding); tiap layanan punya 3 tier paket (Basic/Standard/Premium) |
| `TIME_SLOTS` | Slot jam tersedia: `09.00`, `11.00`, `13.00`, `15.00`, `17.00` |
| `STATUS_LABEL` | Mapping status booking ke teks label + emoji |

---

### `db/supabase_client.py`
Lapisan database. Semua query ke Supabase ada di sini.

| Fungsi | Keterangan |
|--------|-----------|
| `get_client()` | Singleton Supabase client (lazy-load dari env var) |
| `upsert_user(wa_number, name)` | Simpan/update data user, update `last_seen_at` |
| `get_user(wa_number)` | Ambil profil user dari tabel `users` |
| `save_enrollment(user_id, path_id)` | Daftarkan user ke learning path baru, nonaktifkan path lama |
| `get_state(wa_number)` | Baca state percakapan user saat ini |
| `set_state(wa_number, state, context_data)` | Simpan/update state percakapan + data konteks |
| `save_challenge_response(user_id, path_id, day, status)` | Simpan atau update jawaban challenge harian |
| `get_streak(user_id)` | Hitung streak hari berturut-turut challenge selesai |
| `get_challenge_day(user_id, path_id)` | Ambil nomor hari challenge berikutnya |
| `save_booking(wa_number, nama, layanan, paket, tanggal, jam)` | Buat booking baru, status awal `menunggu_konfirmasi` |
| `get_bookings(wa_number)` | Ambil semua booking aktif (non-dibatalkan) milik user |
| `update_booking_status(booking_id, status)` | Update status booking (dikonfirmasi/selesai/dibatalkan) |
| `is_slot_available(tanggal, jam)` | Cek ketersediaan slot — maks 2 booking per slot waktu |

---

### `handlers/sender.py`
Abstraksi pengiriman pesan ke WhatsApp Cloud API (Meta Graph API v18.0).

| Fungsi | Keterangan |
|--------|-----------|
| `_headers()` | Buat header HTTP dengan Authorization Bearer token |
| `_post(payload)` | Kirim POST ke API, log status & response (internal) |
| `kirim_teks(nomor, pesan)` | Kirim pesan teks biasa |
| `kirim_tombol(nomor, body, footer, buttons, header_text)` | Kirim pesan interaktif dengan tombol (maks 3 tombol) |
| `kirim_gambar_tombol(nomor, image_url, body, footer, buttons)` | Kirim pesan interaktif dengan header gambar + tombol |
| `kirim_list(nomor, header, body, footer, button_label, sections)` | Kirim pesan list interaktif (pilihan bergulir/dropdown) |

---

### `handlers/menu.py`
Menampilkan menu utama saat user pertama kali berinteraksi atau kembali ke home.

| Fungsi | Keterangan |
|--------|-----------|
| `kirim_menu_utama(nomor, nama)` | Kirim sambutan + 3 tombol: Lihat Layanan, Cek Booking, Tanya CS |

---

### `handlers/services.py`
Menampilkan katalog layanan foto studio.

| Fungsi | Keterangan |
|--------|-----------|
| `kirim_list_layanan(nomor)` | Tampilkan semua layanan dalam format list interaktif (emoji, nama, harga mulai) |
| `kirim_detail_layanan(nomor, service_id)` | Tampilkan detail layanan + semua paket + tombol Booking & Kembali |
| `kirim_pilih_paket(nomor, service_id)` | Tampilkan pilihan paket layanan dalam format list |

---

### `handlers/booking.py`
Mengelola seluruh alur booking: pilih paket → isi tanggal → pilih jam → konfirmasi → simpan.

State machine: `IDLE → PILIH_PAKET → TUNGGU_TANGGAL → PILIH_JAM → KONFIRMASI → IDLE`

| Fungsi | Keterangan |
|--------|-----------|
| `_format_rupiah(harga)` | Format integer ke string `Rp X.XXX` |
| `mulai_booking(nomor, service_id)` | Inisiasi booking, tampilkan list paket, set state `PILIH_PAKET` |
| `proses_paket(nomor, service_id, paket_id)` | Proses pilihan paket, minta input tanggal (DD/MM/YYYY), set state `TUNGGU_TANGGAL` |
| `proses_tanggal(nomor, teks, nama)` | Validasi tanggal (format, min besok, maks 30 hari), tampilkan slot jam tersedia |
| `proses_jam(nomor, jam_id, nama)` | Proses pilihan jam, tampilkan ringkasan booking untuk konfirmasi |
| `konfirmasi_booking(nomor, nama)` | Simpan booking ke DB, kirim konfirmasi ke pelanggan & notif ke admin |
| `kirim_daftar_booking(nomor)` | Tampilkan semua booking aktif beserta status, tanggal, dan jam |

---

### `handlers/admin.py`
Handler khusus untuk notifikasi ke nomor admin.

| Fungsi | Keterangan |
|--------|-----------|
| `kirim_notif_admin(booking)` | Kirim pesan WhatsApp ke admin berisi detail booking baru yang masuk |

---

### `handlers/ai_router.py`
Router yang menentukan apakah pesan diteruskan ke LLM atau ditangani rule-based.

| Fungsi | Keterangan |
|--------|-----------|
| `route_message(pesan, user_state)` | Return `"RULE_BASED"` / `"AI_LLM"` / `"ENTER_AI_MODE"` / `"REDIRECT_TO_MENU"` / `"IGNORE"` berdasarkan tipe pesan & state user |
| `build_system_prompt(nama)` | Buat system prompt kontekstual untuk Gemini — mendefinisikan identitas, batasan, dan tugas bot |

---

### `handlers/llm_client.py`
Abstraksi komunikasi ke Google Gemini API.

| Fungsi | Keterangan |
|--------|-----------|
| `_get_client()` | Singleton `genai.Client` — lazy-init dari env var `GEMINI_API_KEY` |
| `tanya_llm(system_prompt, pesan_user)` | Kirim prompt ke Gemini 2.0 Flash, return jawaban sebagai string; handle error dengan pesan fallback |

---

### `handlers/challenge.py`
Fitur tantangan harian untuk user yang sedang mengikuti learning path.

| Fungsi | Keterangan |
|--------|-----------|
| `kirim_tantangan_harian(nomor, path_id, day)` | Kirim soal tantangan harian dengan tombol: Selesai, Hint, Lewati |
| `kirim_respons_challenge(nomor, nama, day, action, streak, done_this_week)` | Kirim balasan sesuai aksi user: apresiasi (done), petunjuk bertahap (hint), atau peringatan streak (skip) |
| `kirim_placeholder_progress(nomor, nama)` | Placeholder jika user belum memilih learning path |

---

### `handlers/roadmap.py`
Fitur pemilihan learning path dan enrollment.

| Fungsi | Keterangan |
|--------|-----------|
| `kirim_detail_path(nomor, path_id)` | Tampilkan detail learning path: tech stack, ekspektasi gaji, durasi, jumlah modul; tombol Enroll/Ganti/Menu |
| `kirim_konfirmasi_enroll(nomor, nama, path_id)` | Kirim konfirmasi setelah enrollment berhasil + info langkah selanjutnya |

---

### `db/schema.sql`
Definisi skema database Supabase.

| Tabel | Fungsi |
|-------|--------|
| `users` | Data pengguna: nomor WA, nama, last_seen_at, active_path |
| `conversation_state` | State mesin percakapan per user: current_state, context_data |
| `bookings` | Data booking: layanan, paket, tanggal, jam, status |
| `time_slots` | Override ketersediaan slot waktu oleh admin |
| `enrollments` | Riwayat enrollment learning path user |
| `daily_challenges` | Rekaman jawaban & progress challenge harian |
