import os
import requests
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    MessageHandler, filters, ContextTypes
)
from datetime import datetime

LIGAS = {
    "eurocopa": {"id": "4588", "nombre": "UEFA Eurocopa"},
    "euro": {"id": "4588", "nombre": "UEFA Eurocopa"},
    "champions": {"id": "4480", "nombre": "UEFA Champions League"},
    "champions league": {"id": "4480", "nombre": "Champions League"},
    "ucl": {"id": "4480", "nombre": "Champions League"},
    "premier": {"id": "4328", "nombre": "Premier League"},
    "premier league": {"id": "4328", "nombre": "Premier League"},
    "la liga": {"id": "4335", "nombre": "La Liga"},
    "laliga": {"id": "4335", "nombre": "La Liga"},
    "bundesliga": {"id": "4331", "nombre": "Bundesliga"},
    "serie a": {"id": "4332", "nombre": "Serie A"},
    "ligue 1": {"id": "4334", "nombre": "Ligue 1"},
    "libertadores": {"id": "4484", "nombre": "Copa Libertadores"},
    "copa america": {"id": "4689", "nombre": "Copa América"},
    "copa américa": {"id": "4689", "nombre": "Copa América"},
    "mundial": {"id": "4429", "nombre": "FIFA World Cup"},
    "world cup": {"id": "4429", "nombre": "FIFA World Cup"},
    "mls": {"id": "4346", "nombre": "MLS"},
}

def obtener_partidos(liga_id, liga_nombre):
    url = (
        "https://www.thesportsdb.com/api/v1/json/3"
        f"/eventsnextleague.php?id={liga_id}"
    )
    try:
        r = requests.get(url, timeout=10)
        eventos = r.json().get("events") or []
        if not eventos:
            return None
        partidos = []
        for e in eventos[:5]:
            local = e.get("strHomeTeam", "?")
            visita = e.get("strAwayTeam", "?")
            fecha = e.get("dateEvent", "")
            hora = e.get("strTime", "")
            estadio = e.get("strVenue", "")
            try:
                d = datetime.strptime(fecha, "%Y-%m-%d")
                fecha = d.strftime("%d/%m/%Y")
            except Exception:
                pass
            linea = f"⚽ {local} vs {visita}\n📅 {fecha}"
            if hora:
                linea += f"  🕐 {hora[:5]} UTC"
            if estadio:
                linea += f"\n🏟  {estadio}"
            partidos.append(linea)
        return partidos
    except Exception:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu bot de fútbol ⚽\n\n"
        "Pregúntame por los próximos partidos de cualquier liga.\n\n"
        "Ejemplo: ¿Cuáles son los partidos de la Champions?\n\n"
        "Ligas disponibles:\n"
        "🏆 Champions League\n"
        "🇪🇺 Eurocopa\n"
        "🏴 Premier League\n"
        "🇪🇸 La Liga\n"
        "🇩🇪 Bundesliga\n"
        "🇮🇹 Serie A\n"
        "🇫🇷 Ligue 1\n"
        "🌎 Copa Libertadores\n"
        "🌍 Copa América\n"
        "🌐 Mundial / World Cup\n"
        "🇺🇸 MLS"
    )

async def mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower()
    liga = None
    for clave, datos in LIGAS.items():
        if clave in texto:
            liga = datos
            break
    if not liga:
        await update.message.reply_text(
            "No reconocí la liga. Intenta con:\n"
            "Champions, Premier, La Liga, Bundesliga,\n"
            "Serie A, Ligue 1, Eurocopa, Libertadores,\n"
            "Copa América, Mundial, MLS"
        )
        return
    await update.message.reply_text(
        f"Buscando partidos de {liga['nombre']}..."
    )
    partidos = obtener_partidos(liga["id"], liga["nombre"])
    if not partidos:
        await update.message.reply_text(
            f"No encontré partidos próximos de {liga['nombre']}."
        )
        return
    respuesta = (
        f"📋 Próximos partidos — {liga['nombre']}:\n\n"
        + "\n\n".join(partidos)
    )
    await update.message.reply_text(respuesta)

def main():
    token = os.environ["TELEGRAM_TOKEN"]
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje)
    )
    print("Bot corriendo...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
