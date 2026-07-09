import { Telegraf } from 'telegraf'
import 'dotenv/config'
import fetch from 'node-fetch'
import fs from 'fs'

const bot = new Telegraf(process.env.BOT_TOKEN!)

// ====== CONFIG YANG HARUS LO ISI ======
const ADMIN_IDS = (process.env.ADMIN_IDS || '').split(',').map(Number).filter(Boolean)
// contoh: ADMIN_IDS=12345678,87654321 di .env

// ====== LOAD CONFIG DARI FILE ======
let config:any = {
  mode: process.env.MODE || 'demo',
  buy: Number(process.env.BUY_AMOUNT) || 0.2,
  tp: Number(process.env.TP_PERCENT) || 100,
  sl: Number(process.env.SL_PERCENT) || 35,
  score: 85,
  trades: 0,
  win: 0,
  pnlSol: 0
}
try {
  const saved = JSON.parse(fs.readFileSync('config.json','utf8'))
  config = {...config, ...saved}
} catch {}

// ====== SECURITY: HANYA ADMIN ======
bot.use((ctx, next) => {
  if (!ctx.from || !ADMIN_IDS.includes(ctx.from.id)) {
    return ctx.reply('❌ Akses ditolak. Hanya admin.')
  }
  return next()
})

function saveConfig(){ fs.writeFile('config.json', JSON.stringify(config), ()=>{}) }

// ====== CACHE HARGA IDR (biar gak kena limit CoinGecko) ======
let idrCache = { price: 24000000, ts: 0 } // default 24jt
async function solToIdr(sol:number){
  try{
    if(Date.now() - idrCache.ts > 60000){ // update 1 menit sekali
      const r = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=idr')
      const j:any = await r.json()
      idrCache = { price: j.solana.idr, ts: Date.now() }
    }
    return Math.round(sol * idrCache.price)
  }catch{
    return Math.round(sol * idrCache.price)
  }
}

// ====== PNL DUMMY (ganti dengan DB asli nanti) ======
async function getPNL(){
  return {
    sol: config.pnlSol,
    pct: config.trades ? ((config.pnlSol / (config.buy||0.2)) * 100).toFixed(1) : '0',
    trades: config.trades,
    win: config.win
  }
}

// ====== COMMANDS ======
bot.start(ctx => ctx.reply(
`🚀 GENI V1 AKTIF
Mode: ${config.mode.toUpperCase()}

Perintah:
/set buy 0.2
/set tp 100
/set sl 35
/set score 85
/pnl
/stop
/sharepnl`
, {parse_mode:'Markdown'}))

bot.command('set', ctx => {
  const parts = ctx.message.text.split(' ').filter(Boolean)
  const key = parts[1]?.toLowerCase()
  const val = parts[2]
  
  const allowed = ['buy','tp','sl','score','mode']
  if(!key || !val || !allowed.includes(key)){
    return ctx.reply('Format: /set buy 0.2  |  /set tp 100  |  /set mode demo')
  }
  
  if(key === 'mode' && !['demo','real'].includes(val)){
    return ctx.reply('Mode hanya demo atau real')
  }
  
  const numVal = Number(val)
  config[key] = isNaN(numVal) ? val : numVal
  saveConfig()
  ctx.reply(`✅ ${key} = ${val}`)
})

bot.command('pnl', async ctx => {
  try{
    const pnl = await getPNL()
    const idr = await solToIdr(pnl.sol)
    const idrStr = idr.toLocaleString('id-ID').replace(/\./g,',')
    ctx.reply(`PNL Sekarang:
${pnl.sol} SOL (${pnl.pct}%)
≈ Rp ${idrStr}
Trades: ${pnl.trades} | Win: ${pnl.win}`)
  }catch(e){ ctx.reply('Error ambil PNL') }
})

bot.command('stop', async ctx => {
  try{
    const pnl = await getPNL()
    const idr = await solToIdr(pnl.sol)
    const idrStr = idr.toLocaleString('id-ID').replace(/\./g,',')
    // pakai Markdown biasa (bukan V2) biar aman
    const msg = `*GENI V1 STOPPED*
Mode: ${config.mode}
Config: Buy ${config.buy} | TP ${config.tp}% | SL ${config.sl}%
Trades: ${pnl.trades} | Win: ${pnl.win}
*PNL: ${pnl.sol} SOL (${pnl.pct}%) ≈ Rp ${idrStr}*`
    ctx.reply(msg, {parse_mode:'Markdown'})
  }catch(e){ ctx.reply('Error stop') }
})

bot.command('sharepnl', async ctx => {
  // untuk demo, kirim text dulu. Nanti bisa generate PNG
  const pnl = await getPNL()
  ctx.reply(`📊 Share PNL GENI V1
${pnl.sol} SOL (${pnl.pct}%)`)
})

// ====== CONTOH PANGGIL API GRATIS (dengan fallback) ======
async function getTokenPrice(mint:string){
  try{
    // 1. Dexscreener dulu
    const ds = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${mint}`)
    const dsj:any = await ds.json()
    const solPair = dsj.pairs?.find((p:any)=>p.chainId==='solana')
    if(solPair) return solPair.priceUsd
    
    // 2. Fallback Birdeye (butuh API KEY)
    if(process.env.BIRDEYE_API_KEY){
      const by = await fetch(`https://public-api.birdeye.so/defi/price?address=${mint}`, {
        headers: {'X-API-KEY': process.env.BIRDEYE_API_KEY}
      })
      const byj:any = await by.json()
      return byj.data?.value
    }
  }catch{}
  return null
}

// simulasi trade biar PNL jalan (hapus kalau sudah connect real bot)
setInterval(()=>{ config.trades++; config.pnlSol += 0.01; if(Math.random()>0.5) config.win++; saveConfig() }, 60000)

bot.launch().then(()=>console.log('Bot jalan...')).catch(console.error)
process.once('SIGINT', () => bot.stop('SIGINT'))
