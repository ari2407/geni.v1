YANG HARUS LO ISI MANUAL (tanpa coding):

1. BOT_TOKEN
   - Buka Telegram -> @BotFather -> /newbot -> copy token
   - Tempel di .env

2. ADMIN_IDS
   - Buka Telegram -> @userinfobot -> copy "Id"
   - Tempel di .env (kalau mau 2 orang: 123,456)

3. HELIUS_API_KEY
   - Kamu sudah punya, tempel

4. BIRDEYE_API_KEY (GRATIS, penting)
   - Buka birdeye.so -> Sign up -> Dashboard -> copy API Key
   - Tanpa ini harga kadang kosong

5. WALLET_PRIVATE_KEY (KOSONGKAN DULU)
   - Hanya isi kalau mau tes REAL
   - Ambil dari Phantom -> Export Private Key (base58)
   - JANGAN share ke siapapun

6. MODE
   - isi 'demo' untuk presentasi
   - ganti ke 'real' hanya saat dosen minta live

SETELAH ISI, upload ke Railway.app -> Deploy -> Bot langsung hidup 24 jam
