import json
import logging
import requests
import DATA
from DATA import BROADCAST_ID, TELEGRAM_API, API_TOKEN, BASE_URL
from telegram import Bot
import asyncio

CLAN_TAG = '#2Q9992ULV'
API_URL = f'{BASE_URL}/clans/{CLAN_TAG.replace("#", "%23")}/currentwar'
CLAN_LINK_BASE = 'https://link.clashofclans.com/it?action=OpenClanProfile&tag='

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
    'Authorization': f'Bearer {API_TOKEN}'
}

def get_war_state():
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        war_data = response.json()
        return war_data.get('state'), war_data
    else:
        logger.error(f'Errore nella richiesta: {response.status_code}')
        return None, None
        

def generate_opponent_clan_link(opponent_tag):
    return f"{CLAN_LINK_BASE}{opponent_tag.strip('#')}"

async def handle_war_state_change(new_state, war_data, bot):
    if DATA.NOTIFICHE_ATTIVE:  
        opponent_name = war_data['opponent']['name']
        opponent_tag = war_data['opponent']['tag']
        opponent_clan_link = generate_opponent_clan_link(opponent_tag)
        
        if new_state == 'preparation':
            message = (
                f"⌛Giorno dei preparativi contro [{opponent_name}]({opponent_clan_link}) iniziato!\n\n"
                f"👥Giocatori: *{len(war_data['clan']['members'])}* vs *{len(war_data['opponent']['members'])}*"
            )
            await broadcast_message(message, bot)
            
        elif new_state == 'inWar':
            message = (
                f"⚔️Giorno della war contro [{opponent_name}]({opponent_clan_link}) iniziato!\n\n"
                f"👥Giocatori: *{len(war_data['clan']['members'])}* vs *{len(war_data['opponent']['members'])}*"
            )
            await broadcast_message(message, bot)
            
            await asyncio.sleep(54000)
            current_state, war_data = get_war_state()
            if current_state == 'inWar' and DATA.NOTIFICHE_ATTIVE:
                message = (
                    f"⚠️La war contro [{opponent_name}]({opponent_clan_link}) terminerà tra circa 9 ore, ricordatevi di attaccare!\n\n"
                    f"📈Stato attuale:\n"
                    f"✨*{war_data['clan']['stars']} - {war_data['opponent']['stars']}*✨"
                )
                await broadcast_message(message, bot)
                
            await asyncio.sleep(82800)
            current_state, war_data = get_war_state()
            if current_state == 'inWar' and DATA.NOTIFICHE_ATTIVE:
                message = (
                    f"⚠️⚠️La war contro [{opponent_name}]({opponent_clan_link}) terminerà tra circa 1 ora, chi non ha attaccato lo faccia adesso!⚠️⚠️\n\n"
                    f"📈Stato attuale:\n"
                    f"✨*{war_data['clan']['stars']} - {war_data['opponent']['stars']}*✨"
                )
                await broadcast_message(message, bot)
                
        elif new_state == 'warEnded':
            message = (
                f"🏆War contro [{opponent_name}]({opponent_clan_link}) terminata!\n\n"
                f"📈Risultati:\n"
                f"*✨{war_data['clan']['stars']} - {war_data['opponent']['stars']}✨*"
            )
            await broadcast_message(message, bot)

async def broadcast_message(message, bot):
    if DATA.NOTIFICHE_ATTIVE:  
        for chat_id in BROADCAST_ID:
            try:
                await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown', disable_web_page_preview=True)
            except Exception as e:
                logger.error(f"Errore nell'invio del messaggio a {chat_id}: {e}")

async def check_war_state():
    bot = Bot(token=TELEGRAM_API)
    last_state = None

    while True:
        current_state, war_data = get_war_state()

        if current_state:
            if current_state != last_state:
                await handle_war_state_change(current_state, war_data, bot)
                last_state = current_state
            #else:
                #logger.info(f"Check avvenuto, stato attuale: {current_state}")

        await asyncio.sleep(180)