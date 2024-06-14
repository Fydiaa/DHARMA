import logging
from API_TOKEN import API_TOKEN
import coc
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import requests
from datetime import datetime, timedelta
import asyncio
from functools import wraps
from login import login, login_required

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

TELEGRAM_API = '7162988957:AAGqUiYf2T4bsxb7qYY8OMU86yMW5sg_zFg'

BASE_URL = 'https://cocproxy.royaleapi.dev/v1'

monitoring_enabled = False

lost_tag = '2Q9992ULV'

@coc.ClanEvents.member_join()
async def on_member_join():
    if monitoring_enabled:
        message = f"{player.name} ({player.tag}) just joined {clan.name} ({clan.tag})"
        print(message)  # Stampa per debugging
        await bot.send_message(chat_id=CHAT_ID, text=message)  # Invio del messaggio su Telegram
# Evento di uscita di un membro dal clan
@coc.ClanEvents.member_leave()
async def on_member_leave(player, clan):
    if monitoring_enabled:
        message = f"{player.name} ({player.tag}) è uscito {clan.name} ({clan.tag})"
        print(message)  # Stampa per debugging
        await bot.send_message(chat_id=CHAT_ID, text=message)  # Invio del messaggio su Telegram


async def coc_event_listener():
    coc_client = coc.EventsClient()
    try:
        await coc_client.login("fedestefanini@gmail.com", ".pamyMZ#u5ivP3@")
    except coc.InvalidCredentials as error:
        exit(error)

    # Registra tutti i clan che vuoi monitorare
    list_of_clan_tags = ["#2Q9992ULV"]
    coc_client.add_clan_updates(*list_of_clan_tags)
    
    coc_client.add_events(
        on_member_join,
        on_member_leave,
    )
'''/lost'''
def get_clan_info(tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f'{BASE_URL}/clans/%23{tag}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Errore: {response.status_code}')
        return None

'''button war /claninfo'''
def get_war_log(tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f'{BASE_URL}/clans/%23{tag}/warlog'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Errore: {response.status_code}')
        return None

'''/infowar'''
def get_current_war_info(lost_tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f"{BASE_URL}/clans/%23{lost_tag}/currentwar"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Errore: {response.status_code}')
        return None

@login_required
async def war_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get information about the current war."""
    war_info = get_current_war_info(lost_tag)

    if war_info and 'state' in war_info:
        if war_info['state'] == 'notInWar':
            await update.message.reply_text("🔍Il clan non è attualmente in guerra.")
        else:
            message = (
                f"War contro: *{war_info['opponent']['name']}*\n"
                f"Giocatori: *{len(war_info['clan']['members'])}* vs *{len(war_info['opponent']['members'])}*\n\n"
                f"Punteggio attuale: *{war_info['clan']['stars']}* vs *{war_info['opponent']['stars']}*"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("*❌Errore nel recupero delle informazioni, controllo errori API: 403*❌", parse_mode='Markdown')

@login_required
async def lostinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get clan information."""
    lost_info = get_clan_info(lost_tag)

    if lost_info:
        message = (
            f'🔰*{lost_info["name"]}*🔰\n'
            f'Tag: *{lost_info["tag"]}*\n'
            f'Livello: *{lost_info["clanLevel"]}*\n'
            f'Membri: *{lost_info["members"]}*\n'
            f'Punti totali: *{lost_info["clanPoints"]}*\n'
            f'Trofei richiesti: *{lost_info["requiredTrophies"]}*\n'
            f'Descrizione: \n{lost_info["description"]}\n'
        )
        
        keyboard = [
            [InlineKeyboardButton("Membri", callback_data=f'members_{lost_tag}')],
            [InlineKeyboardButton("Registro guerre", callback_data=f'warlog_{lost_tag}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text("*Si è verificato un errore nel recupero delle informazioni sul clan.*", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    data = query.data.split('_')
    action = data[0]
    tag = data[1]

    if action == 'members':
        clan_info = get_clan_info(tag)
        if clan_info and 'memberList' in clan_info:
            members = clan_info['memberList']
            member_names = [member['name'] for member in members]
            message = f'Membri del clan ({len(members)}):\n\n'
            message += '\n'.join(member_names)
            await query.message.reply_text(message)
        else:
            await query.message.reply_text("Si è verificato un errore nel recupero della lista dei membri del clan.")
    elif action == 'warlog':
        war_log = get_war_log(tag)
        if war_log:
            wins = sum(1 for entry in war_log['items'] if entry.get('result') == 'win')
            losses = sum(1 for entry in war_log['items'] if entry.get('result') == 'lose')
            message = (
                f'🟢Guerre vinte: *{wins}*\n'
                f'🔴Guerre perse: *{losses}*\n'
            )
            await query.message.reply_text(message, parse_mode='Markdown')
        else:
            await query.message.reply_text("Il registro delle guerre non è disponibile o si è verificato un errore.")

@login_required
async def start_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global monitoring_enabled
    monitoring_enabled = True
    await update.message.reply_text("✅ Monitoraggio del clan attivato.")

@login_required
async def stop_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global monitoring_enabled
    monitoring_enabled = False
    await update.message.reply_text("🛑 Monitoraggio del clan disattivato.")

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_API).build()
    application.add_handler(CommandHandler("lost", lostinfo))
    application.add_handler(CommandHandler("infowar", war_info_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("startmonitoring", start_monitoring))
    application.add_handler(CommandHandler("stopmonitoring", stop_monitoring))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger()

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
