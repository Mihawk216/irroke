import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, CallbackContext, filters
)

# Этапы диалога для начальной настройки
BIRTHDAY, INTERVAL = range(2)
# Этапы диалога для изменения настроек
CHANGE_CHOICE, CHANGE_BIRTHDAY, CHANGE_INTERVAL = range(3)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Привет! Давай настроим оповещения.\n"
        "Сначала укажи, когда твой день рождения.\n"
        "Введи дату в формате ДД.ММ.ГГГГ (например, 31.12.1990)."
    )
    return BIRTHDAY

def birthday(update: Update, context: CallbackContext) -> int:
    try:
        birthday_date = datetime.datetime.strptime(update.message.text, "%d.%m.%Y").date()
        context.user_data['birthday'] = birthday_date
        reply_keyboard = [['День', 'Неделя', 'Месяц']]
        update.message.reply_text(
            "Отлично! Теперь выбери интервал оповещений:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return INTERVAL
    except ValueError:
        update.message.reply_text("Неверный формат даты. Попробуй ещё раз, например: 31.12.1990")
        return BIRTHDAY

def interval(update: Update, context: CallbackContext) -> int:
    interval_choice = update.message.text.lower()
    if interval_choice not in ['день', 'неделя', 'месяц']:
        update.message.reply_text("Пожалуйста, выбери один из предложенных вариантов: День, Неделя, Месяц")
        return INTERVAL
    context.user_data['interval'] = interval_choice
    birthday_date = context.user_data['birthday']
    update.message.reply_text(
        f"Настройки сохранены!\n"
        f"День рождения: {birthday_date.strftime('%d.%m.%Y')}\n"
        f"Интервал оповещений: {interval_choice.capitalize()}",
        reply_markup=ReplyKeyboardRemove()
    )
    # Здесь можно запустить дополнительный функционал, например, планировщик оповещений.
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Настройка отменена.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# --- Обработка изменения настроек ---
def change_start(update: Update, context: CallbackContext) -> int:
    # Проверяем, существуют ли сохранённые настройки
    if 'birthday' not in context.user_data or 'interval' not in context.user_data:
        update.message.reply_text(
            "Пока настроек нет. Используй команду /start для их создания."
        )
        return ConversationHandler.END
    reply_keyboard = [['Дата рождения', 'Интервал оповещений', 'Оба']]
    update.message.reply_text(
        "Что ты хочешь изменить?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return CHANGE_CHOICE

def change_choice(update: Update, context: CallbackContext) -> int:
    choice = update.message.text.lower()
    if choice == 'дата рождения':
        update.message.reply_text(
            "Введи новую дату рождения в формате ДД.ММ.ГГГГ (например, 31.12.1990):",
            reply_markup=ReplyKeyboardRemove()
        )
        return CHANGE_BIRTHDAY
    elif choice == 'интервал оповещений':
        reply_keyboard = [['День', 'Неделя', 'Месяц']]
        update.message.reply_text(
            "Выбери новый интервал оповещений:",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        )
        return CHANGE_INTERVAL
    elif choice == 'оба':
        update.message.reply_text(
            "Введи новую дату рождения в формате ДД.ММ.ГГГГ (например, 31.12.1990):",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data['change_both'] = True  # Флаг, что нужно изменить оба параметра
        return CHANGE_BIRTHDAY
    else:
        update.message.reply_text("Пожалуйста, выбери один из вариантов: Дата рождения, Интервал оповещений, Оба")
        return CHANGE_CHOICE

def change_birthday(update: Update, context: CallbackContext) -> int:
    try:
        new_birthday = datetime.datetime.strptime(update.message.text, "%d.%m.%Y").date()
        context.user_data['birthday'] = new_birthday
        if context.user_data.get('change_both'):
            # Если требуется изменить оба параметра, переходим к изменению интервала
            reply_keyboard = [['День', 'Неделя', 'Месяц']]
            update.message.reply_text(
                "Теперь выбери новый интервал оповещений:",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
            )
            return CHANGE_INTERVAL
        else:
            # Изменение только даты
            interval_value = context.user_data['interval']
            update.message.reply_text(
                f"Новая дата рождения сохранена: {new_birthday.strftime('%d.%m.%Y')}\n"
                f"Интервал оповещений: {interval_value.capitalize()}",
                reply_markup=ReplyKeyboardRemove()
            )
            return ConversationHandler.END
    except ValueError:
        update.message.reply_text("Неверный формат даты. Попробуй ещё раз, например: 31.12.1990")
        return CHANGE_BIRTHDAY

def change_interval(update: Update, context: CallbackContext) -> int:
    new_interval = update.message.text.lower()
    if new_interval not in ['день', 'неделя', 'месяц']:
        update.message.reply_text("Пожалуйста, выбери один из вариантов: День, Неделя, Месяц")
        return CHANGE_INTERVAL
    context.user_data['interval'] = new_interval
    birthday_date = context.user_data['birthday']
    update.message.reply_text(
        f"Новые настройки сохранены!\n"
        f"День рождения: {birthday_date.strftime('%d.%m.%Y')}\n"
        f"Интервал оповещений: {new_interval.capitalize()}",
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.pop('change_both', None)
    return ConversationHandler.END

def main():
    # Замените токен на токен вашего бота
    application = ApplicationBuilder().token("7678998458:AAHihA8X6HVgYjRH024dQy_Kxg8fRfwxH-Y").build()

    # Обработчик для начальной настройки
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthday)],
            INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, interval)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Обработчик для изменения настроек
    change_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('change', change_start)],
        states={
            CHANGE_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_choice)],
            CHANGE_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_birthday)],
            CHANGE_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_interval)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(change_conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
