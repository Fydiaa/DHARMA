# admin.py

# Lista degli amministratori
ADMIN_LIST = [129971898]  # Esempio di ID di amministratori

# Decoratore per controllare se l'utente è un amministratore
def admin_required(func):
    async def wrapper(update, context):
        user_id = update.message.from_user.id
        
        if user_id in ADMIN_LIST:
            return await func(update, context)
        else:
            await update.message.reply_text("Per utilizzare questo comando devi essere un amministratore!")
    return wrapper
