import logging
from DATA import TELEGRAM_API, BASE_URL, lost_tag, API_TOKEN
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import requests
import asyncio
from functools import wraps
from login import login, login_required
from monitor import ClanWarMonitor

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

notifications_enabled = False

def get_clan_info(tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f'{BASE_URL}/clans/%23{tag}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Errore: {response.status_code}')
        return None

def get_war_log(tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f'{BASE_URL}/clans/%23{tag}/warlog'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Errore: {response.status_code}')
        return None

def get_current_war_info(lost_tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f"{BASE_URL}/clans/%23{lost_tag}/currentwar"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f'Errore: {response.status_code}')
        return None


async def notifications_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global notifications_enabled

    query = update.callback_query
    if query.data == 'notifications_on':
        notifications_enabled = True
        await query.answer("Notifiche abilitate.")
    elif query.data == 'notifications_off':
        notifications_enabled = False
        await query.answer("Notifiche disabilitate.")
    
    status = "attivate" if notifications_enabled else "disattivate"
    message = f"Le notifiche sono attualmente {status}."
    await query.edit_message_text(message)
    

@login_required
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Chat ID: {chat_id}")
    
async def war_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    war_info = get_current_war_info(lost_tag)

    if war_info and 'state' in war_info:
        if war_info['state'] == 'notInWar':
            await update.message.reply_text("🔍 Il clan non è attualmente in guerra.")
        else:
            message = (
                f"War contro: *{war_info['opponent']['name']}*\n"
                f"Giocatori: *{len(war_info['clan']['members'])}* vs *{len(war_info['opponent']['members'])}*\n\n"
                f"Punteggio attuale: *{war_info['clan']['stars']}* vs *{war_info['opponent']['stars']}*"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("*❌ Errore nel recupero delle informazioni, controllo errori API: 403*❌", parse_mode='Markdown')

@login_required
async def lostinfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    lost_info = get_clan_info(lost_tag)

    if lost_info:
        message = (
            f'🔰 *{lost_info["name"]}* 🔰\n'
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
                f'🟢 Guerre vinte: *{wins}*\n'
                f'🔴 Guerre perse: *{losses}*\n'
            )
            await query.message.reply_text(message, parse_mode='Markdown')
        else:
            await query.message.reply_text("Il registro delle guerre non è disponibile o si è verificato un errore.")


@login_required
async def notifiche(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global notifications_enabled

    status = "attivate" if notifications_enabled else "disattivate"
    message = f"Le notifiche sono attualmente {status}."

    keyboard = [
        [InlineKeyboardButton("ON", callback_data='notifications_on')],
        [InlineKeyboardButton("OFF", callback_data='notifications_off')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup)


def main() -> None:
    application = Application.builder().token(TELEGRAM_API).build()
    
    bot = Bot(token=TELEGRAM_API)
    chat_id = "-1002247603335"  # Sostituisci con l'ID della chat appropriata
    monitor = ClanWarMonitor(bot, chat_id, lost_tag, notifications_enabled)
    asyncio.ensure_future(monitor.start_monitoring())
    asyncio.ensure_future(monitor.send_reminder())
    application.add_handler(CommandHandler("lost", lostinfo))
    application.add_handler(CommandHandler("notifiche", notifiche))
    application.add_handler(CommandHandler("infowar", war_info_command))
    application.add_handler(CommandHandler("id", get_chat_id))
    application.add_handler(CallbackQueryHandler(notifications_callback, pattern='notifications_.*'))
    application.add_handler(CallbackQueryHandler(button_callback))  # Posizioniamo questo gestore per ultimo

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
