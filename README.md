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

## Status

Repository ini sengaja dimulai ulang dari nol. Implementasi akan ditambahkan bertahap setelah fondasi arsitektur dan aturan evaluasi disepakati.
