# External candidate catalog

Repository ini tidak dapat secara aman “memanggil semua AI agent di internet”. Internet tidak menyediakan daftar agent universal, banyak repository dapat berubah, dan menjalankan kode remote secara otomatis dapat memasukkan malware, lisensi yang tidak sesuai, atau fungsi eksekusi order.

Karena itu, tahap pertama menggunakan katalog metadata yang dapat diaudit. Kandidat dikelompokkan berdasarkan fungsi, bukan langsung dipercaya sebagai agent produksi:

| Kelompok | Kandidat awal | Keputusan |
|---|---|---|
| Data exchange | CCXT | Kandidat utama untuk adapter data publik; API key privat tidak diperlukan untuk data publik. |
| Backtest/evaluasi | Freqtrade | Hanya permukaan backtest, dry-run, dan evaluasi; execution adapter dilarang. |
| Technical | CryptoSignal | Referensi teknikal, tetapi perlu audit karena proyek terlihat lebih lama. |
| Sentiment | Cryptocurrency-Sentiment-Bot | Referensi saja sampai lisensi, sumber, dan pemeliharaan diverifikasi. |
| Orchestration | LangGraph, CrewAI | Kandidat infrastruktur workflow; bukan sumber signal atau bukti profit. |

## Proses pemilihan

1. Ambil metadata repository dan dokumentasi resmi.
2. Verifikasi lisensi, aktivitas, dependensi, izin penggunaan data, dan fungsi eksekusi.
3. Jalankan dependency/license/security scan.
4. Tempatkan setiap kandidat ke adapter terisolasi.
5. Beri skor berdasarkan kecocokan signal-only, risiko pemeliharaan, dan keragaman peran.
6. Uji pada data historis dan paper trading sebelum agent diberi bobot.
7. Evaluasi ulang berkala; tidak ada self-modification atau eksekusi remote tanpa review.

Sumber awal: [CCXT](https://github.com/ccxt/ccxt), [Freqtrade](https://github.com/freqtrade/freqtrade), [CryptoSignal](https://github.com/CryptoSignal/Crypto-Signal), [Cryptocurrency-Sentiment-Bot](https://github.com/CyberPunkMetalHead/Cryptocurrency-Sentiment-Bot), [LangGraph](https://github.com/langchain-ai/langgraph), dan [CrewAI](https://github.com/crewAIInc/crewAI).
