# Multi-Agent Crypto Signal Manager

Sistem multi-agent untuk melakukan riset pasar cryptocurrency dan mengirimkan **signal** ke Telegram. Sistem ini dirancang sebagai alat bantu analisis bergaya fund manager: setiap agent memiliki peran berbeda, saling memberikan penilaian, dan dievaluasi berdasarkan hasil signal sebelumnya.

> **Peringatan penting:** proyek ini hanya menghasilkan signal dan tidak mengeksekusi transaksi. Signal bukan nasihat keuangan. Trading crypto, terutama leverage, memiliki risiko kehilangan modal yang tinggi.

## Tujuan

- Mencari dan menyaring kandidat aset sebelum dianalisis lebih lanjut.
- Membagi analisis ke dua tim: **Spot** dan **Leverage Long/Short**.
- Menggunakan beberapa agent dengan keahlian yang berbeda, bukan satu pendapat tunggal.
- Menghasilkan pesan Telegram yang singkat, jelas, dan mudah dipahami.
- Mencatat performa signal untuk memberikan reward atau penalti secara objektif.
- Meningkatkan kualitas bobot dan kolaborasi agent dari data evaluasi historis, tanpa mengubah aturan secara berisiko secara otomatis.

## Tim dan batasan analisis

### Tim Spot

Fokus pada peluang pembelian aset secara spot, dengan analisis multi-timeframe dan tanpa eksekusi order.

### Tim Leverage Long/Short

Fokus pada peluang long dan short. Tim ini harus menerapkan pemeriksaan risiko yang lebih ketat karena leverage dapat memperbesar keuntungan maupun kerugian.

### Aturan timeframe

Kedua tim **tidak melakukan scalping**. Timeframe terkecil yang dapat digunakan adalah **M5**, lalu dikonfirmasi dengan timeframe yang lebih besar seperti M15, H1, H4, dan D1 sesuai kebutuhan. Signal tidak boleh hanya bergantung pada satu candle atau satu indikator.

## Peran agent

Implementasi akan dimulai dari nol dan sekurang-kurangnya mencakup peran berikut:

1. **Candidate Screener** — menyaring aset berdasarkan likuiditas, volume, volatilitas, spread, dan kelayakan data.
2. **Market Regime Analyst** — menentukan kondisi bullish, bearish, sideways, atau berisiko.
3. **Technical Analyst** — menganalisis struktur harga, tren, momentum, support/resistance, dan multi-timeframe.
4. **Market Data Researcher** — mengumpulkan data exchange, on-chain, berita, sentimen, dan sumber publik lain.
5. **Risk Manager** — menghitung invalidation, stop loss, target, risk/reward, dan ukuran risiko teoretis.
6. **Signal Validator** — memeriksa konsistensi, kualitas data, konflik antar-agent, dan kondisi sebelum signal diterbitkan.
7. **Fund Manager / Orchestrator** — menggabungkan hasil agent, menentukan tingkat keyakinan, dan memilih apakah signal layak dikirim.

Setiap tim memiliki minimal lima agent aktif. Agent yang sama boleh digunakan pada kedua tim, tetapi konfigurasi, fokus, bobot, dan kriteria evaluasinya harus berbeda.

## Data dan rate limit

Prioritas proyek adalah menggunakan sumber data gratis atau endpoint publik, misalnya data publik exchange, sumber berita, data on-chain, GitHub, dan sumber web yang memiliki izin penggunaan.

Sistem akan memiliki:

- cache dan penyimpanan data historis untuk mengurangi permintaan berulang;
- pemantauan rate limit dan kuota setiap sumber;
- rotasi/fallback ke sumber alternatif sebelum sumber utama habis kuota;
- retry dengan exponential backoff dan circuit breaker;
- health check agar sumber yang gagal tidak membuat seluruh sistem mati;
- logging sumber, waktu pengambilan, kualitas, dan umur data.

Tidak ada jaminan bahwa semua sumber eksternal selalu gratis, stabil, atau tanpa batas. Sistem harus mematuhi terms of service, robots policy, rate limit, dan lisensi setiap sumber. Jika seluruh sumber valid tidak tersedia, agent wajib menandai data sebagai tidak cukup dan tidak mengarang data.

## Reward dan penalti agent

Setiap agent akan memiliki skor performa berdasarkan signal yang dapat dievaluasi:

- **Reward** diberikan jika target profit tercapai sesuai aturan evaluasi.
- **Penalti** diberikan jika stop loss atau invalidation tersentuh.
- Signal yang belum selesai tidak dihitung sebagai menang atau kalah.
- Hasil dievaluasi setelah biaya, slippage teoretis, dan konteks leverage diperhitungkan.
- Skor tidak boleh digunakan untuk menjamin profit; skor hanya membantu pengaturan bobot dan audit kualitas agent.
- Performa akan dipisahkan berdasarkan tim, aset, kondisi pasar, dan timeframe agar agent tidak mendapat skor menyesatkan.

Sistem tidak boleh memperketat filter secara berlebihan sampai hampir tidak pernah menghasilkan signal. Frekuensi signal akan dikontrol dengan ambang kualitas minimum, cooldown, deduplikasi, dan batas risiko—bukan dengan menghilangkan semua kandidat.

## Format pesan Telegram

Pesan harus ringkas dan mudah dibaca, sekurang-kurangnya memuat:

- aset dan tim;
- arah: spot, long, atau short;
- timeframe analisis;
- area entry atau kondisi pemicu;
- stop loss/invalidation;
- target bertahap;
- risk/reward teoretis;
- tingkat keyakinan dan alasan utama;
- waktu signal, umur data, dan status bahwa ini **bukan eksekusi otomatis**.

Token bot Telegram wajib disimpan melalui environment variable atau secret manager, bukan di repository.

## Prinsip keselamatan

- Tidak ada private key atau fungsi submit order pada sistem signal.
- Tidak ada eksekusi transaksi otomatis.
- Tidak mengklaim akurasi 100 persen.
- Signal dengan data basi, konflik besar, likuiditas rendah, atau risiko tidak terukur harus ditahan.
- Semua keputusan agent harus dapat ditelusuri melalui log dan alasan yang jelas.
- Backtesting dan paper trading dilakukan sebelum penggunaan nyata.

## Rencana tahap pengembangan

1. Menetapkan struktur proyek, konfigurasi, skema signal, dan logging.
2. Membuat data adapter, cache, fallback, dan health monitoring.
3. Membuat candidate screener dan dua pipeline tim.
4. Membuat agent analisis, risk manager, validator, dan orchestrator.
5. Membuat evaluator reward/penalti dan dashboard metrik.
6. Menambahkan formatter serta pengiriman Telegram yang aman.
7. Menjalankan unit test, backtest, paper trading, dan simulasi kegagalan sumber data.
8. Menyempurnakan bobot agent berdasarkan hasil evaluasi yang dapat diaudit.

## Cara menjalankan

Persyaratan: **Python 3.11 atau lebih baru**.

```bash
# 1. Buat dan aktifkan virtual environment
python3 -m venv .venv
source .venv/bin/activate       # Linux/macOS
# Windows PowerShell: .venv\\Scripts\\Activate.ps1

# 2. Instal project dalam mode editable
python -m pip install --upgrade pip
python -m pip install -e .

# 3. Jalankan demo signal (belum mengambil data internet)
crypto-signals
```

Alternatif tanpa instalasi editable:

```bash
PYTHONPATH=src python -m crypto_signals.cli
```

Untuk satu siklus data publik live dari exchange:

```bash
crypto-signals-live
# atau tanpa instalasi:
PYTHONPATH=src python -m crypto_signals.run_live
```

Adapter live mencoba Binance, lalu Kraken, lalu Coinbase. Data disimpan sementara di `data/runtime/cache/` agar request berulang memakai cache dan tidak membebani sumber. Tidak diperlukan API key. Untuk menganalisis banyak aset yang lolos filter universe publik:

```bash
crypto-signals-scheduler --all-public --max-symbols 100 --timeframe H1 --once
```

Atau tentukan daftar sendiri:

```bash
crypto-signals-scheduler --symbols BTC/USDT,ETH/USDT,SOL/USDT --timeframe H1 --once
```

`--all-public` menggabungkan daftar pair aktif dari registry provider publik, memberi prioritas pada volume 24 jam Binance, dan meneruskannya satu per satu ke filter kandidat. Universe di-refresh pada setiap cycle sehingga perubahan kandidat dapat terdeteksi. Angka `--max-symbols` adalah pengaman agar rate limit tidak dihabiskan dalam satu cycle. Registry ini extensible; “semua internet” tidak bisa dijamin karena tidak ada API universal dan setiap sumber memiliki lisensi, format, dan rate limit berbeda.

Perintah ini hanya mengambil candle publik, membuat signal, lalu mencetak pesan; belum mengirim Telegram dan tidak memiliki fungsi order. Jika jaringan atau semua sumber sedang tidak tersedia, program berhenti dengan aman tanpa membuat signal.

Perintah demo menggunakan snapshot BTCUSDT tiruan untuk membuktikan pipeline Spot dan Leverage berjalan. Ini **bukan data market live** dan bukan signal trading nyata. Saat ini belum ada konektor exchange atau pengiriman Telegram live.

Untuk menjalankan test setelah dependency tersedia:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Panduan pemula: mengirim signal ke Telegram

### 1. Siapkan komputer/server

Gunakan Linux VPS atau komputer yang dapat menyala terus. Python yang dibutuhkan adalah versi 3.11 atau lebih baru.

Periksa versi Python:

```bash
python3 --version
```

Clone repository dan masuk ke foldernya:

```bash
git clone https://github.com/ari2407/geni.v1.git
cd geni.v1
```

Jika Anda memakai branch pengembangan saat ini:

```bash
git checkout arena/01a05138-geni-v1
```

### 2. Buat virtual environment

Untuk cara paling ringan, project juga menyediakan launcher tanpa instalasi package:

```bash
python3 run_scheduler.py --help
```

Launcher ini hanya memakai standard library dan folder `src`. Instalasi editable di bawah tetap disarankan untuk mendapatkan perintah `crypto-signals-scheduler`.

Virtual environment memisahkan dependency project dari Python sistem:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

### 3. Buat bot Telegram

1. Buka Telegram dan cari akun **@BotFather**.
2. Kirim `/newbot`.
3. Ikuti instruksi dan simpan token bot secara rahasia.
4. Kirim pesan apa pun ke bot yang baru dibuat.
5. Untuk memperoleh chat ID, buka:
   `https://api.telegram.org/botTOKEN_ANDA/getUpdates`
6. Cari nilai `message.chat.id` pada respons JSON.
7. Untuk grup, tambahkan bot ke grup dan kirim pesan di grup tersebut terlebih dahulu.
8. Untuk channel, tambahkan bot sebagai administrator dengan izin yang diperlukan.

Jangan memasukkan token ke source code, README, commit, atau chat publik.

### 4. Isi environment variable

Salin contoh konfigurasi:

```bash
cp .env.example .env
```

Edit `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=123456789:token_dari_botfather
TELEGRAM_CHAT_ID=123456789
```

Muat variable ke terminal Linux:

```bash
set -a
source .env
set +a
```

File `.env` sudah masuk `.gitignore` dan tidak boleh di-commit.

### 5. Tes tanpa Telegram terlebih dahulu

Jalankan satu cycle dan hanya cetak output ke terminal:

```bash
crypto-signals-scheduler --once
```

Jika semua endpoint exchange tidak dapat diakses, program akan berhenti aman tanpa mengarang signal.

### 6. Tes kirim Telegram satu kali

Setelah environment variable benar:

```bash
crypto-signals-scheduler --telegram --once
```

Jika berhasil, pesan signal akan muncul di chat Telegram. Program hanya mengirim teks signal; tidak ada API key trading, private key, atau endpoint order.

### 7. Jalankan 24/7

```bash
crypto-signals-scheduler \\
  --telegram \\
  --symbol BTC/USDT \\
  --timeframe H1 \\
  --interval 300 \\
  --cooldown 1800 \\
  --retries 3
```

Arti parameter:

- `--telegram`: aktifkan pengiriman Telegram. Tanpa flag ini output hanya ke terminal.
- `--symbol`: pair yang dianalisis, contoh `BTC/USDT`.
- `--timeframe`: pilih `M5`, `M15`, `H1`, `H4`, atau `D1`.
- `--interval 300`: jalankan cycle setiap 5 menit.
- `--cooldown 1800`: cegah signal identik selama 30 menit.
- `--retries 3`: ulangi pengambilan data jika terjadi error.

Untuk menghentikan dengan aman tekan `Ctrl+C`. Di server, kirim `SIGTERM`; scheduler akan menyelesaikan handler shutdown dan berhenti tanpa menjalankan order.

### 8. Menjalankan sebagai service Linux

Buat file `/etc/systemd/system/crypto-signals.service`:

```ini
[Unit]
Description=Crypto Signal Telegram Scheduler
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=USER_LINUX_ANDA
WorkingDirectory=/path/ke/geni.v1
EnvironmentFile=/path/ke/geni.v1/.env
ExecStart=/path/ke/geni.v1/.venv/bin/crypto-signals-scheduler --telegram --symbol BTC/USDT --timeframe H1 --interval 300 --cooldown 1800 --retries 3
Restart=on-failure
RestartSec=30
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Ganti `USER_LINUX_ANDA` dan path project, lalu:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now crypto-signals
sudo systemctl status crypto-signals
journalctl -u crypto-signals -f
```

Untuk menghentikan:

```bash
sudo systemctl stop crypto-signals
```

### 9. Troubleshooting umum

- **`TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required`**: `.env` belum dimuat atau nama variable salah.
- **Telegram tidak menerima pesan**: pastikan sudah mengirim pesan ke bot, chat ID benar, dan bot sudah menjadi anggota grup/channel.
- **`all public market-data sources failed`**: server tidak bisa mengakses endpoint publik, DNS bermasalah, exchange sedang membatasi request, atau pair tidak tersedia. Tidak ada signal yang dibuat dalam kondisi ini.
- **Tidak ada signal**: ini dapat terjadi karena filter validasi, confidence, liquidity, volatility, atau cooldown. Tidak berarti program mati.
- **Signal berulang**: periksa apakah pair, timeframe, arah, dan nilai `--cooldown` sesuai. Deduplikasi hanya berlaku selama proses berjalan; state cooldown belum persisten setelah restart.

### 10. Pengujian developer

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Discovery kandidat eksternal

Sistem tidak menjalankan kode dari seluruh internet secara otomatis. Kandidat eksternal dicatat dalam katalog metadata, dikelompokkan berdasarkan fungsi, lalu dipilih melalui audit lisensi, keamanan, pemeliharaan, dan kecocokan signal-only. Katalog awal dan keputusan seleksi tersedia di [`docs/agent-catalog.md`](docs/agent-catalog.md). Modul `discovery.py` menyediakan grouping dan ranking kandidat, sedangkan `agent_groups.py` memisahkan mandat Spot dan Leverage.

## Scheduler 24/7

Scheduler signal-only tersedia melalui:

```bash
crypto-signals-scheduler
```

Konfigurasi contoh:

```bash
crypto-signals-scheduler --symbol BTC/USDT --timeframe H1 --interval 300 --cooldown 1800 --retries 3
```

Fitur scheduler:

- polling berkala dengan interval yang dapat diatur;
- retry data dengan exponential backoff;
- cooldown dan deduplikasi berdasarkan aset, tim, arah, dan timeframe;
- memory deduplikasi dibatasi agar tidak tumbuh tanpa batas;
- error satu cycle dicatat lalu scheduler tetap hidup;
- `SIGINT` dan `SIGTERM` menghentikan loop secara aman;
- `--once` menjalankan satu cycle untuk pengujian;
- tidak memiliki jalur order execution.

Untuk menghentikan proses foreground, tekan `Ctrl+C`. Pada server, gunakan service supervisor seperti systemd atau Docker dan kirim `SIGTERM` saat deployment agar shutdown berjalan bersih.

## Menjalankan dengan Docker

Docker Compose tersedia untuk deployment signal-only:

```bash
cp .env.example .env
# isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID
sudo docker compose up -d --build
sudo docker compose logs -f crypto-signals
```

State SQLite disimpan di volume Docker dan tetap ada ketika container dibuat ulang. Hentikan dengan `sudo docker compose down`.

## Model kuantitatif ringan: Kelly dan Monte Carlo

`quant_models.py` menyediakan Kelly Criterion dan simulasi Monte Carlo tanpa NumPy atau dependency berat. Keduanya adalah diagnostic bagi Critical Manager untuk membantu menilai payoff dan risiko hipotetis signal, bukan ukuran modal nyata, bukan jaminan profit, dan bukan eksekusi. Input invalid membuat signal ditolak secara fail-closed.

## Mode laptop kentang dan model internet-only

Default project memakai profile `lite`, tanpa model lokal besar, tanpa GPU, tanpa PyTorch, dan tanpa dependency ML berat. Profile ini cocok untuk laptop RAM kecil:

```bash
crypto-signals-scheduler --all-public --profile lite --max-symbols 20 --telegram
```

Profile `remote` dapat dipakai jika Anda memiliki endpoint LLM hosted yang kompatibel OpenAI:

```bash
crypto-signals-scheduler --all-public --profile remote --max-symbols 100 --telegram
```

Konfigurasi optional di `.env`:

```dotenv
LLM_BASE_URL=https://provider-anda.example/v1
LLM_MODEL=nama-model
LLM_API_KEY=token-jika-diperlukan
```

`remote_adviser.py` hanya mengirim bukti market yang terbatas untuk riset melalui HTTPS. Ia tidak mempunyai tools, wallet, exchange credential, Telegram credential, atau kemampuan eksekusi. Profile remote tidak wajib; profile lite tetap berjalan tanpa LLM.

Project memiliki registry model provider-agnostic di `src/crypto_signals/model_registry.py`. Tidak ada layanan yang dapat menjamin semua model LLM gratis dan tanpa limit; gunakan hanya provider yang memiliki izin dan ketentuan penggunaan yang sesuai. Baseline lokal selalu aktif, sementara model remote hanya penasihat dan tidak boleh melewati Critical Manager.

Tidak ada cara aman atau realistis untuk “mengambil semua LLM di internet”. Model remote dapat berubah, membutuhkan lisensi/credential, memiliki rate limit, atau tidak aman. Karena itu project tetap dapat berjalan tanpa LLM berbayar dan tidak mengunduh atau mengeksekusi model remote secara otomatis.

## Status

Project sudah memiliki engine signal-only, team branches, candidate discovery, source rotation, live public data adapter, universe refresh, scheduler 24/7, self-review terbatas, critical manager, persistent state, reward/penalty, Telegram delivery, daily recap, dan Docker deployment. Sebelum production eksternal, pengguna tetap harus mengisi credential Telegram, menjalankan paper signal, dan memverifikasi jaringan/provider dari server deployment.
