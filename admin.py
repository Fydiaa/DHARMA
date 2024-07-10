# admin.py

# Lista degli amministratori
ADMIN_LIST = []  # Esempio di ID di amministratori

# Decoratore per controllare se l'utente è un amministratore
def admin_required(func):
    async def wrapper(update, context):
        user_id = update.message.from_user.id
        
        if user_id in ADMIN_LIST:
            return await func(update, context)
        else:
            await update.message.reply_text("*⛔Non hai i permessi sufficienti per eseguire il comando.*", parse_mode='Markdown')
    return wrapper
