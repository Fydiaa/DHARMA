import os

PASSWORD = "desmondcaposupremo"
REGISTERED_USERS_FILE = "registered_users.txt"
EXEMPT_GROUP_IDS = [-1002247603335, -1002134951076]  # Sostituisci con gli ID dei tuoi gruppi

def is_user_registered(user_id):
    if not os.path.exists(REGISTERED_USERS_FILE):
        return False
    with open(REGISTERED_USERS_FILE, "r") as file:
        registered_users = file.read().splitlines()
        return str(user_id) in registered_users

def register_user(user_id):
    with open(REGISTERED_USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")

async def login(update, context):
    user_id = update.message.from_user.id

    if is_user_registered(user_id):
        await update.message.reply_text("⚠️Sei già registrato!")
        return True

    password = update.message.text.split()[1] if len(update.message.text.split()) > 1 else None
    if password == PASSWORD:
        register_user(user_id)
        await update.message.reply_text("✅Registrazione completata, digita /help per la lista comandi!")
        return True
    else:
        await update.message.reply_text("❌Password errata. Riprova.")
        return False

def login_required(func):
    async def wrapper(update, context):
        user_id = update.message.from_user.id
        chat_id = update.message.chat.id
        
        if chat_id in EXEMPT_GROUP_IDS or is_user_registered(user_id):
            return await func(update, context)
        else:
            await update.message.reply_text("⚠️Per favore, effettua il login utilizzando /login <password>")
    return wrapper
