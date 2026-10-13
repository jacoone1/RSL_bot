import os
import pandas as pd
import yfinance as yf
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Inserisci il token fornito da BotFather
TOKEN = "8874950291:AAE4tZzIFElTJlKvzBbACPJCb7aqwnDTl8Y"

# Lista di esempio di azioni S&P 500 (puoi estenderla)
TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "LLY", "V"]

def calculate_rsl():
    """Calcola l'RSL (Prezzo attuale / Media Mobile 26 settimane)"""
    results = []
    # Scarica i dati storici settimanali per i ticker
    data = yf.download(TICKERS, period="1y", interval="1wk", progress=False)
    
    for ticker in TICKERS:
        try:
            # Estrae la serie dei prezzi di chiusura
            closes = data['Close'][ticker].dropna()
            if len(closes) >= 26:
                current_price = closes.iloc[-1]
                ma26 = closes.tail(26).mean()
                rsl = current_price / ma26
                results.append({"Ticker": ticker, "Price": current_price, "RSL": rsl})
        except Exception as e:
            continue
            
    df = pd.DataFrame(results)
    if not df.empty:
        # Ordina in base al valore RSL decrescente
        df = df.sort_values(by="RSL", ascending=False).reset_index(drop=True)
    return df

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Benvenuto nel Bot RSL Scanner!\n"
        "Invia il comando /scan per analizzare la forza relativa delle azioni."
    )

async def scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Scansione RSL in corso... Attendi qualche secondo.")
    df = calculate_rsl()
    
    if df.empty:
        await update.message.reply_text("❌ Errore durante il recupero dei dati.")
        return
        
    msg = "📊 **CLASSIFICA FORZA RELATIVA (RSL)** 📊\n\n"
    for idx, row in df.iterrows():
        emoji = "🟢" if idx < 3 else "⚪"
        msg += f"{emoji} **#{idx+1} {row['Ticker']}** | RSL: `{row['RSL']:.3f}` | Prezzo: `${row['Price']:.2f}`\n"
        
    await update.message.reply_text(msg, parse_mode="Markdown")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("scan", scan))
    
    print("Bot in ascolto...")
    app.run_polling()
