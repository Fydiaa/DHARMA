import asyncio
import requests
from telegram import Bot
from DATA import BASE_URL, lost_tag, API_TOKEN

class ClanWarMonitor:
    def __init__(self, bot: Bot, chat_id: str, lost_tag: str, notifications_enabled: bool):
        self.bot = bot
        self.chat_id = chat_id
        self.lost_tag = lost_tag
        self.notifications_enabled = notifications_enabled
        self.last_state = None
        self.war_end_time = None

    def get_current_war_info(self):
        headers = {
            'Authorization': f'Bearer {API_TOKEN}'
        }
        url = f"{BASE_URL}/clans/%23{self.lost_tag}/currentwar"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f'Errore: {response.status_code}')
            return None

    async def check_war_state(self):
        war_info = self.get_current_war_info()
        if war_info and 'state' in war_info:
            current_state = war_info['state']
            opponent_name = war_info['opponent']['name']
            if current_state != self.last_state:
                self.last_state = current_state
                message = ""
                if current_state == 'preparation':
                    message = f"🚨 Il clan è entrato in preparazione per una nuova guerra contro {opponent_name}!"
                elif current_state == 'inWar':
                    message = f"⚔️ La guerra contro {opponent_name} è iniziata! Buona fortuna!"
                    # Calcola l'ora di fine guerra
                    self.war_end_time = asyncio.get_event_loop().time() + 22 * 3600
                elif current_state == 'warEnded':
                    result = "Risultato della guerra:\n"
                    result += f"⭐️ Stelle del clan: {war_info['clan']['stars']}\n"
                    result += f"⭐️ Stelle dell'avversario ({opponent_name}): {war_info['opponent']['stars']}\n"
                    message = f"🏁 La guerra contro {opponent_name} è terminata!\n{result}"

                if self.notifications_enabled:
                    await self.bot.send_message(chat_id=self.chat_id, text=message)
            else:
                print("Lo stato della guerra non è cambiato.")
        else:
            print("Non è stato possibile recuperare le informazioni sulla guerra.")

    async def send_reminder(self):
        while True:
            if self.war_end_time and asyncio.get_event_loop().time() >= self.war_end_time:
                war_info = self.get_current_war_info()
                if war_info and war_info['state'] == 'inWar':
                    attacks_left = sum(member['attacks'] for member in war_info['clan']['members'])
                    message = (
                        f"⌛️ 2 ore alla fine della guerra! Rimangono {attacks_left} attacchi. "
                        "Ricordate di attaccare!"
                    )
                    if self.notifications_enabled:
                        await self.bot.send_message(chat_id=self.chat_id, text=message)
                self.war_end_time = None  # Resetta il timer dopo l'invio del promemoria
            await asyncio.sleep(60)  # Controlla ogni minuto

    async def start_monitoring(self):
        while True:
            await self.check_war_state()
            await asyncio.sleep(180)
        asyncio.ensure_future(self.send_reminder())
