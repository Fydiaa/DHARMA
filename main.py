import logging
import platform 
import os
from DATA import TELEGRAM_API, BASE_URL, lost_tag, API_TOKEN
import coc
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import requests
from datetime import datetime, timedelta
from admin import admin_required
import asyncio
from functools import wraps
from login import login, login_required

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


#/lost and /claninfo
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

#button war /claninfo
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

#/playerinfo
def get_player_info(player_tag):
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }
    url = f"{BASE_URL}/players/%23{player_tag}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Errore: {response.status_code}')
        return None
        
        
#/infowar
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


#/start and /login module
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Benvenuto nel bot ufficiale di LOST! Per favore, effettua il login utilizzando /login <password> per qualsiasi problema contatta @fedends")



#Handler welcome message
async def welcome(update: Update, context: CallbackContext) -> None:
    for member in update.message.new_chat_members:
        username = member.username
        if username:
            welcome_message = (
                f"Benvenuto *{username}* nel gruppo ufficiale di LOST! Sono il bot del gruppo🤖.\n"
                "Digita /help per la lista comandi!\n\n"
                "❗️*Comunica alla chat il tuo nome su Clash*❗️\n\n"
                "Per utilizzarmi in chat privata dovrai loggarti con una password e con il seguente comando:\n"
                "*'/login ||desmondcaposupremo||'*"
            )
        else:
            welcome_message = (
                f"Benvenuto nel gruppo ufficiale di LOST! Sono il bot del gruppo🤖.\n"
                "Digita /help per la lista comandi!\n\n"
                "❗️*Comunica alla chat il tuo nome su Clash*❗️\n\n"
                "Per utilizzarmi in chat privata dovrai loggarti con una password e con il seguente comando:\n"
                "*'/login ||desmondcaposupremo||'*"
            )

        with open("benvenuto.png", "rb") as photo:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo,
                caption=welcome_message,
                parse_mode='Markdown'
            )

####
####
#Commands
####
####


#/help
@login_required
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    first_name = user.first_name
    message = (
        f"📟Ciao *{first_name}*, questi sono i comandi del bot:\n\n\n"
        "⚔️ Comandi specifici Clash of Clans: ⚔️\n\n"
        "'/lost'  *visualizza le statistiche generali del nostro clan.*\n\n"
        "'/playerinfo <tag>'  *visualizza le info generali di un giocatore.*\n\n"
        "'/claninfo <tag>'  *visualizza le info del clan richiesto.*\n\n"
        "'/infowar'  *visualizza l'andamento della nostra war corrente.*\n\n"
        "'/utils'  *link e app utili per Clash of Clans.*\n\n\n"
        "⚙ ***Comandi specifici bot:*** ⚙\n\n"
        "📢 '/notifiche'  *comando riservato agli amministratori dei gruppi per abilitare le notifiche globali riguardo leghe, war, giochi del clan e assalti della capitale.*\n\n"
        "🆔 '/id'  *utilizzando il comando in privato riceverai il tuo chat id, per abilitare le notifiche relative alle war, se richiesto.*\n\n"
        "🔒 '/login <psw>'  *utilizzabile in privato per poter usare il bot.*\n\n"
        "⚠️ '/info' *visualizza le info del bot.*"
    )    
    
    await update.message.reply_text(message, parse_mode="Markdown")
    
#/info
@login_required
async def infobot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
    "⚡*Info generali bot*⚡\n\n"
    "*Stato memoria*: ✅\n"
    "*Stato connessione API*: ✅\n"
    "*Stato server Clash Of Clans*: ✅\n"
    "*Stato richiesta base_url*: ✅\n"
    "*RoyaleAPI Proxy*: ✅\n"
    "*Python version*: `3.12.1`\n"
    "*Level logging*: `INFO(), WARNING`\n\n\n"
    "📄 [Cliccami](https://github.com/Fydiaa/DHARMA) *per aprire il repository del bot sul mio profilo GitHub e visualizzare il codice.*"
    )
    await update.message.reply_text(message, parse_mode="Markdown")
    
#/id
@login_required
async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await update.message.reply_text(f"Chat ID, clicca per copiare: `{chat_id}`", parse_mode='Markdown')
    
#/playerinfo    
@login_required
async def player_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("Per favore, fornisci il tag del giocatore, lo puoi trovare aprendo il tuo profilo su Clash of Clans, sotto il tuo nome. Esempio: /playerinfo #1234ABCD")
        return

    player_tag = context.args[0].strip('#')
    player_info = get_player_info(player_tag)

    if player_info:
        message = (
            f"*🛡Informazioni generali:*\n"
            f"Nome: *{player_info['name']}*\n"
            f"Livello: *{player_info['expLevel']}*\n"
            f"Livello Municipio: *{player_info['townHallLevel']}*\n\n"
            f"📅*Informazioni sulla stagione attuale:*\n"
            
        )

        if 'league' in player_info:
            message += (
                f"Lega: *{player_info['league']['name']}*\n"
                f"Trofei: *{player_info['trophies']}*\n"
                f"Record Trofei: *{player_info['bestTrophies']}*\n"
            )

        message += (
            f"Attacchi vinti: *{player_info['attackWins']}*\n"
            f"Difese vinte: *{player_info['defenseWins']}*\n\n"
        )

        if 'clan' in player_info:
            message += (
                f"📉*Statistiche relative al clan:*\n"
                f"Clan: *{player_info['clan']['name']}*\n"
                f"Stelle Guerra: *{player_info['warStars']}*\n"
                f"Donazioni: *{player_info['donations']}*\n"
                f"Donazioni Ricevute: *{player_info['donationsReceived']}*\n"
                f"Contributi Capitale del Clan: *{player_info['clanCapitalContributions']}*\n"
            )

        if 'legendStatistics' in player_info:
            legend_stats = player_info['legendStatistics']
            message += (
                f"\n*📈Statistiche Lega Leggende:*\n"
                f"Trofei Leggenda: *{legend_stats['legendTrophies']}*\n"
                f"Miglior Stagione: *{legend_stats['bestSeason']['id']}* con *{legend_stats['bestSeason']['trophies']}* trofei\n"
            )

        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("Errore nel recupero delle informazioni, digita /playerinfo per le informazioni riguardo al comando.")
        
 #/infowar       
@login_required
async def war_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    war_info = get_current_war_info(lost_tag)

    if war_info and 'state' in war_info:
        if war_info['state'] == 'notInWar':
            await update.message.reply_text("🔍Il clan non è attualmente in guerra.")
        elif war_info['state'] == 'preparation':
            message = (
                f"⌛Giorno dei preparativi contro: *{war_info['opponent']['name']}*\n\n"
                f"👥Giocatori: *{len(war_info['clan']['members'])}* vs *{len(war_info['opponent']['members'])}*\n\n"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            message = (
                f"🗡️War contro: *{war_info['opponent']['name']}*\n"
                f"👥Giocatori: *{len(war_info['clan']['members'])}* vs *{len(war_info['opponent']['members'])}*\n\n"
                f"📈Punteggio attuale: *{war_info['clan']['stars']}* vs *{war_info['opponent']['stars']}*"
            )
            await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("*❌Errore nel recupero delle informazioni, controllo errori API: 403*❌", parse_mode='Markdown')
      
#/claninfo
@login_required
async def claninfo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get clan information."""
    if len(context.args) != 1:
        await update.message.reply_text("Per favore fornisci un tag valido del clan. Esempio: /claninfo <tagclan>")
        return
    
    tag = context.args[0].strip('#')
    clan_info = get_clan_info(tag)

    if clan_info:
        message = (
            f'🔰*{clan_info["name"]}*🔰\n'
            f'Tag: *{clan_info["tag"]}*\n'
            f'Livello: *{clan_info["clanLevel"]}*\n'
            f'Membri: *{clan_info["members"]}*\n'
            f'Punti totali: *{clan_info["clanPoints"]}*\n'
            f'Trofei richiesti: *{clan_info["requiredTrophies"]}*\n'
            f'Descrizione: {clan_info["description"]}\n\n'
        )
        
        keyboard = [
            [InlineKeyboardButton("Membri", callback_data=f'members_{tag}')],
            [InlineKeyboardButton("Registro guerre", callback_data=f'warlog_{tag}')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text("*Si è verificato un errore nel recupero delle informazioni sul clan.*", parse_mode='Markdown')

#/losinfo
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

#Button callback for /claninfo and /lostinfo
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
                f'🟢Guerre vinte: *{wins}*\n'
                f'🔴Guerre perse: *{losses}*\n'
            )
            await query.message.reply_text(message, parse_mode='Markdown')
        else:
            await query.message.reply_text("Il registro delle guerre non è disponibile o si è verificato un errore.")


def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_API).build()

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", infobot))   
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("login", login))
    application.add_handler(CommandHandler("lost", lostinfo))
    application.add_handler(CommandHandler("playerinfo", player_info_command))
    application.add_handler(CommandHandler("claninfo", claninfo))
    application.add_handler(CommandHandler("id", get_chat_id))
    application.add_handler(CommandHandler("infowar", war_info_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
