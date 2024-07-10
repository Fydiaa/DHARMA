import coc
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from DATA import lost_tag

# Funzione per ottenere le informazioni della lega
async def get_league_info():
    coc_client = coc.Client()
    try:
        await coc_client.login(email="", password="")
        
        # Recupera il gruppo della lega del clan
        league_group = await coc_client.get_league_group(lost_tag)
        
        if league_group.state == "notInWar":
            return "La lega della stagione è terminata.", [], []
        elif league_group.state not in ["preparation", "inWar", "warEnded"]:
            return "Stato della lega non riconosciuto. Controllare console per errori!"

        league_state = "In corso" if league_group.state == "inWar" else "Preparazione" if league_group.state == "preparation" else "Terminata"
        season = league_group.season

        clans = [clan.name for clan in league_group.clans]

        # Recupera i dettagli delle guerre del clan specificato
        war_details = []
        for round_index, round in enumerate(league_group.rounds, start=1):
            for war_tag in round:
                war = await coc_client.get_league_war(war_tag)
                if war.clan.name == "Lost" or war.opponent.name == "Lost":
                    opponent = war.opponent.name if war.clan.name == "Lost" else war.clan.name
                    own_stars = war.clan.stars if war.clan.name == "Lost" else war.opponent.stars
                    opponent_stars = war.opponent.stars if war.clan.name == "Lost" else war.clan.stars
                    state = war.state
                    team_size = war.team_size
                    war_details.append({
                        'round': round_index,
                        'opponent': opponent,
                        'own_stars': own_stars,
                        'opponent_stars': opponent_stars,
                        'state': state,
                        'team_size': team_size
                    })

        return f"*🏆Stato della lega*: {league_state}\n*📅Stagione*: {season}", clans, war_details

    except coc.InvalidCredentials as error:
        return f"*Credenziali non valide*: {error}", [], []
    except coc.errors.NotFound:
        return f"*⚠️La lega di questa stagione è terminata. Aspetta il primo giorno del prossimo mese!*", [], []
    except coc.errors.Forbidden:
        return "*Accesso negato. Assicurati che il tuo token API sia corretto.*", [], []
    finally:
        await coc_client.close()

# Comando del bot per /lega
async def lega(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Invia un messaggio di attesa
    waiting_message = await update.message.reply_text("*🚀Richiesta API in corso, attendere...*", parse_mode='Markdown')

    # Esegui la richiesta API
    message, clans, war_details = await get_league_info()

    if not clans:
        await waiting_message.edit_text(message, parse_mode='Markdown')
        return

    # Costruzione del messaggio iniziale
    response_message = f"{message}\n\n*📋Clan partecipanti*:\n\n" + "\n".join([f"*🔰Clan*: {clan}" for clan in clans]) + "\n\n\n*ℹ️Visualizza i dettagli dei gironi sotto:*"

    # Creazione dei pulsanti per ogni round
    keyboard = [
        [InlineKeyboardButton(f"▪ Giorno {detail['round']} ▪", callback_data=f"round_{detail['round']}")]
        for detail in war_details
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await waiting_message.edit_text(response_message, reply_markup=reply_markup, parse_mode='Markdown')

async def button_league_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    callback_data = query.data

    # Controlla se il callback è per il menu della lega
    if callback_data.startswith('round_') or callback_data == 'back_to_menu':
        # Modifica il messaggio esistente con il messaggio di attesa
        await query.edit_message_text("*🚀Richiesta API in corso, attendere...*", parse_mode='Markdown')

        if callback_data.startswith('round_'):
            try:
                round_number = int(callback_data.split('_')[1])
            except ValueError:
                await query.answer("Errore nella selezione del round.")
                return

            message, clans, war_details = await get_league_info()

            round_details = [detail for detail in war_details if detail['round'] == round_number]
            if round_details:
                detail = round_details[0]

                # Controllo dello stato della guerra
                if detail['state'] == "preparation":
                    war_state_message = f"*⌛Giorno dei preparativi contro*: {detail['opponent']}"
                elif detail['state'] == "inWar":
                    war_state_message = f"*⚔️Giorno della battaglia contro*: {detail['opponent']}"
                elif detail['state'] == "warEnded":
                    war_state_message = f"*⚰️Guerra terminata contro*: {detail['opponent']}"
                else:
                    war_state_message = f"*Stato sconosciuto contro*: {detail['opponent']}"

                round_message = (
                    f"*Round* {round_number}:\n"
                    f"{war_state_message}\n"
                    f"*Giocatori*: {detail['team_size']}\n"
                    f"*Lost*: {detail['own_stars']} - {detail['opponent']}: {detail['opponent_stars']}"
                )
                # Aggiungi il pulsante "Indietro"
                keyboard = [[InlineKeyboardButton("🔙", callback_data="back_to_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(round_message, reply_markup=reply_markup, parse_mode='Markdown')

        elif callback_data == 'back_to_menu':
            # Ricostruisci il messaggio iniziale con i pulsanti dei round
            message, clans, war_details = await get_league_info()
            response_message = response_message = f"{message}\n\n*Clan partecipanti*:\n" + "\n".join([f"*🔰Clan*: {clan}" for clan in clans]) + "\n\n*ℹ️Visualizza i dettagli dei gironi sotto:*"

            keyboard = [
                [InlineKeyboardButton(f"▪ Giorno {detail['round']} ▪", callback_data=f"round_{detail['round']}")]
                for detail in war_details
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(response_message, reply_markup=reply_markup, parse_mode='Markdown')
