import asyncio
import logging

import coc

# Funzione per gestire l'evento di nuovo messaggio nella chat del clan
@coc.ClanEvents.chat()
async def on_new_chat_message(clan, message):
    print(f"Nuovo messaggio nel clan {clan.name}: {message.sender.name}: {message.content}")

# Funzione per gestire l'evento di ingresso di un nuovo membro nel clan
@coc.ClanEvents.member_join()
async def foo(player, clan):
    print(f"{player.name} ({player.tag}) è appena entrato nel clan {clan.name} ({clan.tag})")

# Funzione per gestire l'evento di donazioni di un membro
@coc.ClanEvents.member_donations()
async def bar(old_member, member):
    troops_donated = member.donations - old_member.donations
    print(f"{member.name} ha appena donato {troops_donated} truppe!")

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
        foo,
        bar,
        on_new_chat_message  # Aggiungi la funzione di monitoraggio della chat
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
