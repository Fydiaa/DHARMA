import asyncio
import logging

import coc
# Funzione per controllare lo stato dei server
async def check_server_status(coc_client):
    try:
        maintenance_info = await coc_client.get_maintenance()
        if maintenance_info:
            return "I server sono attualmente in manutenzione."
        else:
            return "I server sono attivi."
    except coc.Maintenance as error:
        return f"Errore nel controllo dello stato dei server: {error}"

# Comando /stato
async def stato_command():
    status = await check_server_status(coc_client)
    print(status)
    
    
# Evento di ingresso di un nuovo membro nel clan
@coc.ClanEvents.member_join()
async def on_member_join(player, clan):
    print(f"{player.name} ({player.tag}) è appena entrato nel clan {clan.name} ({clan.tag})")

# Evento di uscita di un membro dal clan
@coc.ClanEvents.member_leave()
async def on_member_leave(player, clan):
    print(f"{player.name} ({player.tag}) ha appena lasciato il clan {clan.name} ({clan.tag})")



# Evento di inizio degli assalti del weekend
@coc.ClientEvents.raid_weekend_start()
async def on_raid_weekend_start(clan):
    print(f"L'assalto del weekend è iniziato per il clan {clan.name} ({clan.tag}).")

# Evento di fine degli assalti del weekend
@coc.ClientEvents.raid_weekend_end()
async def on_raid_weekend_end(clan):
    print(f"L'assalto del weekend è terminato per il clan {clan.name} ({clan.tag}).")


'''
async def test_events(coc_client):
    # Simula ingresso di un membro
    await on_member_join(coc.Player(data={"tag": "#PLAYER1", "name": "Player1"}), coc.Clan(data={"tag": "#CLAN1", "name": "Clan1"}))
    # Simula uscita di un membro
    await on_member_leave(coc.Player(data={"tag": "#PLAYER2", "name": "Player2"}), coc.Clan(data={"tag": "#CLAN2", "name": "Clan2"}))
    # Simula inizio assalti del weekend
    await on_raid_weekend_start(coc.Clan(data={"tag": "#CLAN1", "name": "Clan1"}))
    # Simula fine assalti del weekend
    await on_raid_weekend_end(coc.Clan(data={"tag": "#CLAN2", "name": "Clan2"}))
    # Simula inizio war
    await on_war_start(coc.Clan(data={"tag": "#CLAN1", "name": "Clan1"}))
    # Simula notifica di fine battaglia
    await on_war_end_soon(coc.Clan(data={"tag": "#CLAN1", "name": "Clan1"}))
'''
# Aggiungi la chiamata alla funzione di test nel main
async def main():
    coc_client = coc.EventsClient()
    try:
        await coc_client.login("fedestefanini@gmail.com", ".pamyMZ#u5ivP3@")
    except coc.InvalidCredentials as error:
        exit(error)

    # Registra tutti i clan che vuoi monitorare
    list_of_clan_tags = ["#2Q9992ULV"]
    coc_client.add_clan_updates(*list_of_clan_tags)

    # Registra i callback per ciascuno degli eventi che stai monitorando
    coc_client.add_events(
        on_member_join,
        on_member_leave,
        on_raid_weekend_start,
        on_raid_weekend_end,
    )

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
