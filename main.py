import pytz
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,
    CallbackQueryHandler, CallbackContext)
import os
import db
import math

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DRIVER_GROUP_ID = int(os.getenv("DRIVER_GROUP_ID", "0"))
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "0"))

NAME, PHONE, LOCATION, MAIN_MENU = range(4)
GET_START_LOCATION, GET_DESTINATION, CHOOSE_TARIFF, CONFIRM_ORDER, HELP, SUPPORT, PHONE_EDIT, NAME_SURNAME_EDIT, SETTINGS, PROMOKOD, SETTINGS_LANG = range(
    4, 15)
D_NAME, D_CAR_MODEL, D_CAR_NUMBER = range(15, 18)
ADMIN_MENU, BROADCAST, ADD_PROMO_VALUE = range(18, 21)
EDIT_FARE_SELECT, EDIT_FARE_VALUE = range(21, 23)
SELECT_LANG, ADMIN_ADD_DRIVER_SAVE = range(23, 25)
DRIVER_MENU = 25

LANG_DICT = {
    'uz': {
        'ask_name': "👤 Ism va familiyangizni kiriting:",
        'enter_phone': "📱 Raqamingizni kiriting:",
        'send_phone_btn': "📱 Raqamni yuborish",
        'error_phone': "❌ Raqamni tugma orqali yuboring",
        'send_loc_prompt': "📍 Joylashuvingizni yuboring",
        'send_loc_btn': "📍 Lokatsiya yuborish",
        'error_location': "❌ Tugma orqali location yuboring",
        'reg_success': "✅ Ro‘yxatdan o‘tdingiz!",
        'order_taxi': "🚕 Taxi chaqirish",
        'history': "📜 Mening buyurtmalarim",
        'help': "❓ Yordam",
        'settings': "⚙️ Sozlamalar",
        'back': "⬅️ Orqaga",
        'choose_tariff': "🚕 Tarifni tanlang:",
        'confirm': "✅ Tasdiqlash",
        'cancel': "❌ Bekor qilish",
        'promo': "🎟 Promokod ishlatish",
        'lang_select': "Tilni tanlang / Выберите язык / Select language",
        'request_loc': "📍 Qayerdan olasiz? (Lokatsiya yuboring yoki manzilni yozing)",
        'curr_loc_btn': "📍 Hozirgi joylashuv",
        'change_phone': "📞 Raqamni o'zgartirish",
        'change_name': "👤 Ismni o'zgartirish",
        'enter_new_phone': "📱 Yangi raqamni tugma orqali yuboring:",
        'enter_new_name': "👤 Yangi ism kiriting:",
        'phone_changed': "✅ Telefon raqamingiz muvaffaqiyatli o'zgartirildi!",
        'name_changed': "✅ Ismingiz muvaffaqiyatli o'zgartirildi!",
        'enter_promo': "🎟 Promokod kiriting:",
        'promo_applied': "✅ {discount}% chegirma qo'llanildi!\nYangi narx: {price} so'm",
        'promo_error': "❌ Promokod xato, ishlatilgan yoki muddati o'tgan",
        'help_msg': "Savolingizni yozib qoldiring. Adminlarimiz tez orada javob berishadi.",
        'msg_sent': "✅ Xabaringiz yuborildi. Admin javobini kuting.",
        'd_ask_name': "Haydovchi sifatida ro'yxatdan o'tish uchun ismingizni kiriting:",
        'd_ask_model': "Mashinangiz rusumini kiriting (Masalan: Chevrolet Gentra):",
        'd_ask_number': "Mashina davlat raqamini kiriting (Masalan: 01 A 777 AA):",
        'd_reg_submitted': "✅ Arizangiz adminga yuborildi. Tasdiqlangach, guruh havolasini olasiz.",
        'request_dest': "🏁 Qayerga borasiz? (Iltimos, lokatsiya yuboring)",
        'send_dest_btn': "📍 Manzilni yuborish",
        'distance_text': "📍 Masofa: {dist} km",
        'tariff_ekonom': "🚖 Ekonom ({price} so'm)",
        'tariff_komfort': "✨ Komfort ({price} so'm)",
        'error_dest': "❌ Iltimos, manzilni pastdagi tugma orqali yuboring",
        'order_summary': "📋 **Buyurtmani tasdiqlash:**\n\n🚖 Tarif: {tariff}\n💰 Narxi: {price:,} so'm\n📍 Masofa: {dist} km\n\nTasdiqlaysizmi?",
        'order_sent': "🚀 Buyurtma haydovchilarga yuborildi!",
        'driver_found': "🚖 **Haydovchi topildi!**\n\n👨‍✈️ Haydovchi: {name}\n🚗 Mashina: {model}\n🔢 Raqami: {number}",
        'trip_started': "🚕 Safar boshlandi. Oq yo'l!",
        'trip_finished': "🏁 Manzilga yetib keldingiz. Rahmat!",
        'order_cancelled_driver': "😔 Haydovchi buyurtmani bekor qildi.",
        'no_history': "Sizda hali buyurtmalar yo'q.",
        'history_title': "Sizning oxirgi 5 ta buyurtmangiz:\n\n",
        'change_lang': "🌐 Tilni o'zgartirish",
        'driver_panel': "🚖 Haydovchi paneli",
        'change_status': "🔄 Holatni o'zgartirish",
        'my_stats': "📊 Mening statistikam",
        'exit': "⬅️ Chiqish",
        'online': "🟢 ONLINE",
        'offline': "🔴 OFFLINE",
        'status_changed_online': "✅ Siz online holatga o'tdingiz! Endi buyurtmalarni qabul qila olasiz.",
        'status_changed_offline': "❌ Siz offline holatga o'tdingiz. Buyurtmalar qabul qilinmaydi.",
        'exited_driver': "👋 Haydovchi rejimidan chiqildi.",
        'stats_unavailable': "📊 Statistika hali tayyor emas."
    },
    'ru': {
        'ask_name': "👤 Введите имя и фамилию:",
        'enter_phone': "📱 Введите ваш номер телефона:",
        'send_phone_btn': "📱 Отправить номер",
        'error_phone': "❌ Отправьте номер через кнопку",
        'send_loc_prompt': "📍 Отправьте вашу локацию",
        'send_loc_btn': "📍 Отправить локацию",
        'error_location': "❌ Отправьте локацию через кнопку",
        'reg_success': "✅ Вы успешно зарегистрировались!",
        'order_taxi': "🚕 Заказать такси",
        'history': "📜 Мои заказы",
        'help': "❓ Помощь",
        'settings': "⚙️ Настройки",
        'back': "⬅️ Назад",
        'choose_tariff': "🚕 Выберите тариф:",
        'confirm': "✅ Подтвердить",
        'cancel': "❌ Отмена",
        'promo': "🎟 Использовать промокод",
        'lang_select': "Выберите язык",
        'request_loc': "📍 Откуда вас забрать? (Отправьте локацию или напишите адрес)",
        'curr_loc_btn': "📍 Текущее местоположение",
        'change_phone': "📞 Изменить номер",
        'change_name': "👤 Изменить имя",
        'enter_new_phone': "📱 Отправьте новый номер через кнопку:",
        'enter_new_name': "👤 Введите новое имя:",
        'phone_changed': "✅ Номер телефона успешно изменен!",
        'name_changed': "✅ Имя успешно изменено!",
        'enter_promo': "🎟 Введите промокод:",
        'promo_applied': "✅ {discount}% скидка применена!\nНовая цена: {price} сум",
        'promo_error': "❌ Промокод неверный или истек",
        'help_msg': "Напишите ваш вопрос. Наши админы скоро ответят.",
        'msg_sent': "✅ Ваше сообщение отправлено. Ждите ответа админа.",
        'd_ask_name': "Введите ваше имя для регистрации в качестве водителя:",
        'd_ask_model': "Введите марку вашей машины (Например: Chevrolet Gentra):",
        'd_ask_number': "Введите госномер машины (Например: 01 A 777 AA):",
        'd_reg_submitted': "✅ Ваша заявка отправлена админу. После подтверждения вы получите ссылку на группу.",
        'request_dest': "🏁 Куда поедете? (Пожалуйста, отправьте локацию)",
        'send_dest_btn': "📍 Отправить адрес",
        'distance_text': "📍 Расстояние: {dist} км",
        'tariff_ekonom': "🚖 Эконом ({price} сум)",
        'tariff_komfort': "✨ Комфорт ({price} сум)",
        'error_dest': "❌ Пожалуйста, отправьте адрес через кнопку",
        'order_summary': "📋 **Подтверждение заказа:**\n\n🚖 Тариф: {tariff}\n💰 Цена: {price:,} сум\n📍 Расстояние: {dist} км\n\nПодтверждаете?",
        'order_sent': "🚀 Заказ отправлен водителям!",
        'driver_found': "🚖 **Водитель найден!**\n\n👨‍✈️ Водитель: {name}\n🚗 Машина: {model}\n🔢 Номер: {number}",
        'trip_started': "🚕 Поехали. Счастливого пути!",
        'trip_finished': "🏁 Вы прибыли в пункт назначения. Спасибо!",
        'order_cancelled_driver': "😔 Водитель отменил заказ.",
        'no_history': "У вас пока нет заказов.",
        'history_title': "Ваши последние 5 заказов:\n\n",
        'change_lang': "🌐 Изменить язык",
        'driver_panel': "🚖 Панель водителя",
        'change_status': "🔄 Изменить статус",
        'my_stats': "📊 Моя статистика",
        'exit': "⬅️ Выход",
        'online': "🟢 ONLINE",
        'offline': "🔴 OFFLINE",
        'status_changed_online': "✅ Вы перешли в онлайн-режим! Теперь вы можете принимать заказы.",
        'status_changed_offline': "❌ Вы перешли в офлайн-режим. Заказы не будут поступать.",
        'exited_driver': "👋 Вы вышли из режима водителя.",
        'stats_unavailable': "📊 Статистика пока недоступна."
    },
    'en': {
        'ask_name': "👤 Enter your name and surname:",
        'enter_phone': "📱 Enter your phone number:",
        'send_phone_btn': "📱 Send phone number",
        'error_phone': "❌ Send phone number via button",
        'send_loc_prompt': "📍 Send your location",
        'send_loc_btn': "📍 Send location",
        'error_location': "❌ Send location via button",
        'reg_success': "✅ You have successfully registered!",
        'order_taxi': "🚕 Order Taxi",
        'history': "📜 My Orders",
        'help': "❓ Help",
        'settings': "⚙️ Settings",
        'back': "⬅️ Back",
        'choose_tariff': "🚕 Choose tariff:",
        'confirm': "✅ Confirm",
        'cancel': "❌ Cancel",
        'promo': "🎟 Use Promocode",
        'lang_select': "Select language",
        'request_loc': "📍 Where to pick you up? (Send location or type address)",
        'curr_loc_btn': "📍 Current location",
        'change_phone': "📞 Change phone",
        'change_name': "👤 Change name",
        'enter_new_phone': "📱 Send new phone number via button:",
        'enter_new_name': "👤 Enter new name:",
        'phone_changed': "✅ Phone number changed successfully!",
        'name_changed': "✅ Name changed successfully!",
        'enter_promo': "🎟 Enter promocode:",
        'promo_applied': "✅ {discount}% discount applied!\nNew price: {price} sum",
        'promo_error': "❌ Promocode is invalid or expired",
        'help_msg': "Write your question. Our admins will answer soon.",
        'msg_sent': "✅ Message sent. Please wait for admin reply.",
        'd_ask_name': "Enter your name to register as a driver:",
        'd_ask_model': "Enter your car model (e.g. Chevrolet Gentra):",
        'd_ask_number': "Enter your car plate number (e.g. 01 A 777 AA):",
        'd_reg_submitted': "✅ Your application has been sent to the admin. You will receive a group link once confirmed.",
        'request_dest': "🏁 Where are you going? (Please, send location)",
        'send_dest_btn': "📍 Send destination",
        'distance_text': "📍 Distance: {dist} km",
        'tariff_ekonom': "🚖 Economy ({price} sum)",
        'tariff_komfort': "✨ Comfort ({price} sum)",
        'error_dest': "❌ Please, send the destination via the button",
        'order_summary': "📋 **Order Confirmation:**\n\n🚖 Tariff: {tariff}\n💰 Price: {price:,} sum\n📍 Distance: {dist} km\n\nDo you confirm?",
        'order_sent': "🚀 Order sent to drivers!",
        'driver_found': "🚖 **Driver found!**\n\n👨‍✈️ Driver: {name}\n🚗 Car: {model}\n🔢 Plate: {number}",
        'trip_started': "🚕 Trip started. Have a nice trip!",
        'trip_finished': "🏁 You have arrived. Thank you!",
        'order_cancelled_driver': "😔 The driver cancelled the order.",
        'no_history': "You have no orders yet.",
        'history_title': "Your last 5 orders:\n\n",
        'change_lang': "🌐 Change language",
        'driver_panel': "🚖 Driver Panel",
        'change_status': "🔄 Change status",
        'my_stats': "📊 My statistics",
        'exit': "⬅️ Exit",
        'online': "🟢 ONLINE",
        'offline': "🔴 OFFLINE",
        'status_changed_online': "✅ You are now ONLINE! You can receive orders.",
        'status_changed_offline': "❌ You are now OFFLINE. Orders will not be received.",
        'exited_driver': "👋 Exited driver mode.",
        'stats_unavailable': "📊 Statistics not available yet."
    }
}


def get_l(context):
    lang = context.user_data.get('lang', 'uz')
    return LANG_DICT.get(lang, LANG_DICT['uz'])


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if user_id == ADMIN_ID:
        context.user_data['lang'] = 'uz'
        update.message.reply_text("👋 Xush kelibsiz, hurmatli Admin!")
        return admin_panel(update, context)

    driver = db.get_driver_full_info(user_id)
    if driver and driver[0]:
        is_active = db.is_active_driver(user_id)
        if is_active:
            context.user_data['is_driver'] = True
            context.user_data['lang'] = 'uz'
            update.message.reply_text(f"👋 Xush kelibsiz, haydovchi {driver[0]}!")
            return driver_menu(update, context)
        else:
            update.message.reply_text("⏳ Ariza tekshirilmoqda. Admin tasdiqlashini kuting.")
            return ConversationHandler.END

    if user:
        lang = user[6] if len(user) > 6 else 'uz'
        context.user_data['lang'] = lang
        context.user_data['name'] = user[1]
        context.user_data['phone'] = user[2]
        return main_menu(update, context)

    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
            InlineKeyboardButton("🇺🇸 English", callback_data='lang_en')
        ]
    ]
    update.message.reply_text(
        "Tilni tanlang / Выберите язык / Select language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_LANG


def set_lang(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    lang = data.split('_')[1]

    context.user_data['lang'] = lang
    L = get_l(context)

    query.edit_message_text(L.get('ask_name'))
    return NAME


def get_name(update: Update, context: CallbackContext):
    L = get_l(context)

    context.user_data["name"] = update.message.text

    update.message.reply_text(
        L.get('enter_phone'),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(L.get('send_phone_btn'), request_contact=True)]],
            resize_keyboard=True)
    )
    return PHONE


def get_phone(update: Update, context: CallbackContext):
    L = get_l(context)

    if not update.message.contact:
        update.message.reply_text(L.get('error_phone'))
        return PHONE

    context.user_data["phone"] = update.message.contact.phone_number

    update.message.reply_text(
        L.get('send_loc_prompt'),
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(L.get('send_loc_btn'), request_location=True)]],
            resize_keyboard=True
        ))
    return LOCATION


def get_location(update: Update, context: CallbackContext):
    L = get_l(context)
    if not update.message.location:
        update.message.reply_text(L.get('error_location'))
        return LOCATION

    loc = update.message.location
    db.add_user(
        update.effective_user.id,
        context.user_data["name"],
        context.user_data["phone"],
        loc.latitude, loc.longitude,
        context.user_data.get('lang', 'uz')
    )

    update.message.reply_text(L.get('reg_success'))
    return main_menu(update, context)


def main_menu(update: Update, context: CallbackContext):
    L = get_l(context)
    keyboard = [
        [L['order_taxi']],
        [L['history']],
        [L['help'], L['settings']]
    ]

    text = "Menu:"
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(text, reply_markup=markup)
    return MAIN_MENU


def main_menu_select(update: Update, context: CallbackContext):
    text = update.message.text
    L = get_l(context)

    if text == L['order_taxi']:
        return request_taxi(update, context)
    if text == L['history']:
        return show_history(update, context)
    if text == L['help']:
        return help_command(update, context)
    if text == L['settings']:
        return settings(update, context)
    return MAIN_MENU


def settings(update: Update, context: CallbackContext):
    L = get_l(context)
    keyboard = [[L['change_phone']], [L['change_name']], [L['change_lang']], [L['back']]]

    text = L['settings']
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    update.message.reply_text(text, reply_markup=markup)
    return SETTINGS


def settings_select_menu(update: Update, context: CallbackContext):
    text = update.message.text
    L = get_l(context)

    if text == L['change_phone']:
        update.message.reply_text(L['enter_new_phone'], reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(L['send_phone_btn'], request_contact=True)], [L['back']]], resize_keyboard=True))
        return PHONE_EDIT

    if text == L['change_name']:
        update.message.reply_text(L['enter_new_name'],
                                  reply_markup=ReplyKeyboardMarkup([[L['back']]], resize_keyboard=True))
        return NAME_SURNAME_EDIT

    if text == L['change_lang']:
        keyboard = [
            [InlineKeyboardButton("🇺🇿 Uz", callback_data="setlang_uz"),
             InlineKeyboardButton("🇷🇺 Ru", callback_data="setlang_ru"),
             InlineKeyboardButton("🇺🇸 En", callback_data="setlang_en")]
        ]
        update.message.reply_text(L['lang_select'], reply_markup=InlineKeyboardMarkup(keyboard))
        return SETTINGS_LANG

    if text == L['back']:
        return main_menu(update, context)
    return SETTINGS


def update_language(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    new_lang = query.data.split("_")[1]
    context.user_data['lang'] = new_lang
    db.update_user_lang(update.effective_user.id, new_lang)

    query.message.reply_text("✅ OK!")
    return settings(update, context)


def edit_phone(update: Update, context: CallbackContext):
    L = get_l(context)
    if update.message.text == L['back']:
        return settings(update, context)
    if not update.message.contact:
        update.message.reply_text(L['error_phone'])
        return PHONE_EDIT

    db.edit_phone(update.message.contact.phone_number, update.effective_user.id)
    update.message.reply_text(L['phone_changed'])
    return settings(update, context)


def edit_name(update: Update, context: CallbackContext):
    L = get_l(context)
    if update.message.text == L['back']:
        return settings(update, context)
    db.edit_name(update.message.text, update.effective_user.id)
    update.message.reply_text(L['name_changed'])
    return settings(update, context)


def request_taxi(update: Update, context: CallbackContext):
    L = get_l(context)
    update.message.reply_text(L['request_loc'], reply_markup=ReplyKeyboardMarkup(
        [[KeyboardButton(L['curr_loc_btn'], request_location=True)], [KeyboardButton(L['back'])]],
        resize_keyboard=True))
    return GET_START_LOCATION


def promokod_check(update: Update, context: CallbackContext):
    L = get_l(context)
    user_promokod = update.message.text.upper()
    promo_data = db.check_promo_db(user_promokod)

    if promo_data:
        discount = int(promo_data[0])
        old_price = int(context.user_data.get('final_price', 0))
        new_price = int(old_price * (100 - discount) / 100)

        context.user_data['final_price'] = new_price
        context.user_data['promo_applied'] = True

        db.use_promo_db(user_promokod)

        update.message.reply_text(L['promo_applied'].format(discount=discount, price=new_price))
    else:
        update.message.reply_text(L['promo_error'])

    return confirm_order(update, context)


def driver_start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    lang = context.user_data.get('lang', 'uz')
    L = LANG_DICT[lang]

    driver_info = db.get_driver_full_info(user_id)

    if driver_info and driver_info[0]:
        is_active = db.is_active_driver(user_id)
        if is_active:
            update.message.reply_text(f"👋 Xush kelibsiz, haydovchi {driver_info[0]}!")
            return driver_menu(update, context)
        else:
            update.message.reply_text("⏳ Ariza tekshirilmoqda. Admin tasdiqlashini kuting.")
            return ConversationHandler.END
    else:
        update.message.reply_text(L['d_ask_name'])
        return D_NAME


def get_d_name(update: Update, context: CallbackContext):
    L = get_l(context)
    context.user_data['d_name'] = update.message.text
    update.message.reply_text(L['d_ask_model'])
    return D_CAR_MODEL


def get_d_model(update: Update, context: CallbackContext):
    L = get_l(context)
    context.user_data['d_model'] = update.message.text
    update.message.reply_text(L['d_ask_number'])
    return D_CAR_NUMBER


def finish_driver_reg(update: Update, context: CallbackContext):
    L = get_l(context)
    user_id = update.effective_user.id
    name = context.user_data.get('d_name')
    model = context.user_data.get('d_model')
    number = update.message.text

    db.add_pending_driver(user_id, name, model, number)

    admin_text = (
        f"🆕 **Yangi haydovchi murojaati:**\n\n"
        f"Ism: {name}\nMashina: {model}\nRaqam: {number}\nID: `{user_id}`"
    )

    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"verify_{user_id}")
        ]])
    )

    update.message.reply_text(L['d_reg_submitted'])
    return ConversationHandler.END


def driver_menu(update: Update, context: CallbackContext):
    L = get_l(context)
    user_id = update.effective_user.id
    driver_info = db.get_driver_full_info(user_id)

    status = L['online'] if db.is_active_driver(user_id) else L['offline']

    keyboard = [
        [L['change_status']],
        [L['my_stats']],
        [L['exit']]
    ]

    update.message.reply_text(
        f"🚖 **{L['driver_panel']}**\n\n"
        f"👤 {driver_info[0]}\n"
        f"🚗 {driver_info[1]} | {driver_info[2]}\n"
        f"📊 Holat: {status}\n\n"
        f"Buyurtmalarni qabul qilish uchun guruhda faol bo'ling.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        parse_mode='Markdown'
    )
    return DRIVER_MENU


def driver_menu_select(update: Update, context: CallbackContext):
    text = update.message.text
    L = get_l(context)

    if text == L['change_status']:
        user_id = update.effective_user.id
        is_active = db.is_active_driver(user_id)

        if is_active:
            db.update_driver_status(user_id, 'jarayonda')
            update.message.reply_text(L['status_changed_offline'])
        else:
            db.update_driver_status(user_id, 'aktiv')
            update.message.reply_text(L['status_changed_online'])

        return DRIVER_MENU

    elif text == L['my_stats']:
        update.message.reply_text(L['stats_unavailable'])
        return DRIVER_MENU

    elif text == L['exit']:
        update.message.reply_text(
            L['exited_driver'],
            reply_markup=ReplyKeyboardMarkup([[L['order_taxi']]], resize_keyboard=True)
        )
        return ConversationHandler.END

    return DRIVER_MENU


def help_command(update: Update, context: CallbackContext):
    L = get_l(context)
    update.message.reply_text(
        L['help_msg'],
        reply_markup=ReplyKeyboardMarkup([[L['back']]], resize_keyboard=True)
    )
    return SUPPORT


def forward_to_admin(update: Update, context: CallbackContext):
    L = get_l(context)
    if update.message.text == L['back']:
        return main_menu(update, context)

    user = update.effective_user
    admin_msg = f"🆘 **Yangi murojaat!**\n👤 Kimdan: {user.full_name}\n🆔 ID: {user.id}\n\nXabar: {update.message.text}"

    context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=admin_msg, parse_mode='Markdown')
    update.message.reply_text(L['msg_sent'])
    return main_menu(update, context)


def admin_reply_handler(update: Update, context: CallbackContext):
    if not update.message.reply_to_message:
        return

    original_message = update.message.reply_to_message
    text_to_parse = original_message.text or original_message.caption

    if not text_to_parse or "🆔 ID:" not in text_to_parse:
        return

    try:
        parts = text_to_parse.split("🆔 ID: ")
        user_id_str = parts[1].split()[0].strip('`')
        user_id = int(user_id_str)

        admin_reply = update.message.text

        context.bot.send_message(
            chat_id=user_id,
            text=f"👨‍💻 **Admin javobi:**\n\n{admin_reply}",
            parse_mode='Markdown'
        )
        update.message.reply_text(f"✅ Javob yuborildi (ID: {user_id})")

    except Exception as e:
        update.message.reply_text(f"❌ Xatolik: {e}")


def get_start_location(update: Update, context: CallbackContext):
    L = get_l(context)

    if update.message.text == L['back']:
        return main_menu(update, context)

    if update.message.location:
        context.user_data['pickup_lat'] = update.message.location.latitude
        context.user_data['pickup_lon'] = update.message.location.longitude
    else:
        context.user_data['pickup_text'] = update.message.text

    update.message.reply_text(
        L['request_dest'],
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton(L['send_dest_btn'], request_location=True)],
             [KeyboardButton(L['back'])]],
            resize_keyboard=True
        )
    )
    return GET_DESTINATION


def get_destination_and_show_tariffs(update: Update, context: CallbackContext):
    L = get_l(context)

    if update.message.text == L['back']:
        return request_taxi(update, context)

    if update.message.location:
        dest_lat = update.message.location.latitude
        dest_lon = update.message.location.longitude
        context.user_data['destination_lat'] = dest_lat
        context.user_data['destination_lon'] = dest_lon

        start_lat = context.user_data.get('pickup_lat')
        start_lon = context.user_data.get('pickup_lon')

        if start_lat:
            distance = calculate_distance(start_lat, start_lon, dest_lat, dest_lon)
        else:
            distance = 5.0

        context.user_data['distance'] = distance

        price_ekonom = get_fare(distance, "ekonom")
        price_komfort = get_fare(distance, "comfort")

        context.user_data['price_ekonom'] = price_ekonom
        context.user_data['price_komfort'] = price_komfort

        keyboard = [
            [KeyboardButton(L['tariff_ekonom'].format(price=f"{price_ekonom:,}"))],
            [KeyboardButton(L['tariff_komfort'].format(price=f"{price_komfort:,}"))],
            [KeyboardButton(L['back'])]
        ]

        update.message.reply_text(
            f"{L['distance_text'].format(dist=round(distance, 1))}\n\n{L['choose_tariff']}",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CHOOSE_TARIFF

    update.message.reply_text(L['error_dest'])
    return GET_DESTINATION


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def get_fare(distance, tariff_type):
    base, per_km = db.get_fare_settings(tariff_type)
    if distance <= 3:
        total = base
    else:
        total = base + (distance - 3) * per_km
    return int(round(total / 500) * 500)


def confirm_order(update: Update, context: CallbackContext):
    L = get_l(context)

    text = update.message.text if update.message else ""

    if text == L.get('promo'):
        return promokod_first_check(update, context)

    if text == L.get('back'):
        return request_taxi(update, context)

    if not context.user_data.get('promo_applied'):
        if any(x in text for x in ["Ekonom", "Эконом", "Economy"]):
            context.user_data['selected_tariff'] = "Ekonom"
            context.user_data['final_price'] = context.user_data['price_ekonom']
        elif any(x in text for x in ["Komfort", "Комфорт", "Comfort"]):
            context.user_data['selected_tariff'] = "Komfort"
            context.user_data['final_price'] = context.user_data['price_komfort']

    if 'selected_tariff' not in context.user_data:
        update.message.reply_text(f"⚠️ {L['choose_tariff']}")
        return CHOOSE_TARIFF

    summary = (
        f"📋 **{L['confirm'].replace('✅ ', '')}:**\n\n"
        f"🚖 Tarif: {context.user_data['selected_tariff']}\n"
        f"💰 Narxi: {context.user_data['final_price']:,} so'm\n"
        f"📍 Masofa: {round(context.user_data['distance'], 1)} km\n\n"
        f"Buyurtma berishni tasdiqlaysizmi?"
    )

    keyboard = [
        [InlineKeyboardButton(L['confirm'], callback_data="final_confirm")],
        [InlineKeyboardButton(L['promo'], callback_data="use_promo")],
        [InlineKeyboardButton(L['cancel'], callback_data="cancel_order")]
    ]

    update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    return CONFIRM_ORDER


def promokod_first_check(update: Update, context: CallbackContext):
    L = get_l(context)
    update.message.reply_text(L['enter_promo'])
    return PROMOKOD


def send_to_driver(update: Update, context: CallbackContext):
    L = get_l(context)
    u = context.user_data

    db.add_order(update.effective_user.id, u.get('pickup_lat'), u.get('pickup_lon'),
                 u.get('destination_lat'), u.get('destination_lon'),
                 u.get('selected_tariff'), u.get('final_price'))

    nav_url = f"https://yandex.com/maps/?rtext=~{u.get('pickup_lat')},{u.get('pickup_lon')}&rtt=auto"
    driver_text = (
        f"🚕 **YANGI BUYURTMA!**\n\n"
        f"👤 Mijoz: {u.get('name')}\n"
        f"📞 Tel: {u.get('phone')}\n"
        f"💰 Narxi: {u.get('final_price', 0):,} so'm\n"
        f"🚖 Tarif: {u.get('selected_tariff')}\n"
    )

    keyboard = [
        [InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_{update.effective_user.id}")],
        [InlineKeyboardButton("🧭 Navigator", url=nav_url)]
    ]

    context.bot.send_message(
        chat_id=DRIVER_GROUP_ID,
        text=driver_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    update.message.reply_text(L['order_sent'])

    context.user_data['promo_applied'] = False
    return main_menu(update, context)


def show_history(update: Update, context: CallbackContext):
    L = get_l(context)
    lang = context.user_data.get('lang', 'uz')

    orders = db.show_history_db(update.effective_user.id)

    if not orders:
        update.message.reply_text(L['no_history'])
        return MAIN_MENU

    status_map = {
        'jarayonda': {'uz': 'Kutilmoqda', 'ru': 'В ожидании', 'en': 'Pending'},
        'Haydovchi qabul qildi': {'uz': 'Haydovchi yo\'lda', 'ru': 'Водитель едет', 'en': 'Driver on way'},
        'Yo\'lda': {'uz': 'Safar davom etmoqda', 'ru': 'В пути', 'en': 'In trip'},
        'Yakunlandi': {'uz': 'Tugallangan', 'ru': 'Завершено', 'en': 'Completed'},
        'Bekor qilindi': {'uz': 'Bekor qilingan', 'ru': 'Отменено', 'en': 'Cancelled'}
    }

    msg = f"📜 **{L['history_title']}**\n\n"
    for order in orders:
        status_raw = order[2]
        status_translated = status_map.get(status_raw, {}).get(lang, status_raw)

        msg += f"🚖 {order[0]} | 💰 {order[1]:,} so'm\n"
        msg += f"Status: *{status_translated}*\n"
        msg += f"Sana: {order[3]}\n"
        msg += "----------------------------\n"

    update.message.reply_text(msg, parse_mode='Markdown')
    return MAIN_MENU


def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    user_id = update.effective_user.id

    query.answer()

    if data == "final_confirm":
        query.edit_message_reply_markup(reply_markup=None)
        return send_to_driver(update, context)

    if data == "use_promo":
        L = get_l(context)
        query.message.reply_text(L['enter_promo'])
        return PROMOKOD

    if data == "cancel_order":
        query.edit_message_text("❌")
        return main_menu(update, context)

    if data.startswith("setlang_"):
        new_lang = data.split("_")[1]
        context.user_data['lang'] = new_lang
        db.update_user_lang(user_id, new_lang)
        query.answer(f"Language updated to {new_lang.upper()}")
        return settings(update, context)

    parts = data.split("_")
    if len(parts) < 2:
        return

    action = parts[0]
    target_id = parts[1]

    if action == "verify":
        db.update_driver_status(target_id, 'aktiv')
        d_user = db.get_user(int(target_id))
        d_lang = d_user[6] if d_user else 'uz'

        group_link = "https://t.me/+57wd-B4YIF81OWFi"
        msg = {
            'uz': f"🎉 Tabriklaymiz! Arizangiz tasdiqlandi.\n\nHaydovchilar guruhi: {group_link}",
            'ru': f"🎉 Поздравляем! Ваша заявка одобрена.\n\nГруппа для водителей: {group_link}",
            'en': f"🎉 Congratulations! Your application has been approved.\n\nDriver group: {group_link}"
        }
        context.bot.send_message(chat_id=int(target_id), text=msg.get(d_lang, msg['uz']))
        query.edit_message_text(f"✅ Haydovchi (ID: {target_id}) tasdiqlandi.")
        return

    customer_id = int(target_id)
    customer = db.get_user(customer_id)
    c_lang = customer[6] if customer else 'uz'
    L_c = LANG_DICT[c_lang]

    if action == "accept":
        if not db.is_active_driver(user_id):
            query.answer("❌ Faqat tasdiqlangan haydovchilar qabul qilishi mumkin", show_alert=True)
            return

        driver_info = db.get_driver_full_info(user_id)
        d_name, d_model, d_number = driver_info

        db.update_order_status(customer_id, "Haydovchi qabul qildi")
        context.bot.send_message(
            chat_id=customer_id,
            text=L_c['driver_found'].format(name=d_name, model=d_model, number=d_number),
            parse_mode='Markdown'
        )

        keyboard = [
            [InlineKeyboardButton("✅ Mijozni oldim", callback_data=f"picked_{customer_id}")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_{customer_id}")]
        ]
        query.edit_message_text(
            text=query.message.text + f"\n\n🚖 Qabul qildi: {d_name}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    elif action == "picked":
        db.update_order_status(customer_id, "Yo'lda")
        context.bot.send_message(chat_id=customer_id, text=L_c['trip_started'])
        keyboard = [[InlineKeyboardButton("🏁 Yetib keldik", callback_data=f"finish_{customer_id}")]]
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

    elif action == "finish":
        db.update_order_status(customer_id, "Yakunlandi")
        context.bot.send_message(chat_id=customer_id, text=L_c['trip_finished'])
        query.edit_message_text(text=query.message.text + "\n\n✅ YAKUNLANDI")

    elif action == "cancel":
        db.update_order_status(customer_id, "Bekor qilindi")
        context.bot.send_message(chat_id=customer_id, text=L_c['order_cancelled_driver'])
        query.edit_message_text(text="❌ Bekor qilindi")


def admin_panel(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    u_count, o_count = db.get_stats()
    msg = f"👨‍✈️ **Admin Panel**\n\n👥 Foydalanuvchilar: {u_count}\n📦 Buyurtmalar: {o_count}"

    keyboard = [
        ["💰 Tarif narxlari", "📢 Xabar yuborish"],
        ["🎟 Promokod qo'shish", "📊 Batafsil statistika"],
        ["🆕 Haydovchi qo'shish", "⬅️ Orqaga"]
    ]
    update.message.reply_text(msg, parse_mode='Markdown',
                              reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return ADMIN_MENU


def show_detailed_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    daily_data = db.get_daily_stats()

    if not daily_data:
        update.message.reply_text("📊 Hozircha ma'lumotlar yo'q.")
        return ADMIN_MENU

    msg = "📊 **Oxirgi 7 kunlik statistika:**\n\n"
    grand_total_money = 0

    for day, count, money in daily_data:
        money_val = money or 0
        msg += f"📅 {day}\n"
        msg += f"✅ Buyurtmalar: {count} ta\n"
        msg += f"💰 Daromad: {money_val:,} so'm\n"
        msg += "----------------------------\n"
        grand_total_money += money_val

    msg += f"\n📈 **Umumiy haftalik daromad:** {grand_total_money:,} so'm"

    update.message.reply_text(msg, parse_mode='Markdown')
    return ADMIN_MENU


def broadcast_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Yubormoqchi bo'lgan xabaringizni yozing:",
        reply_markup=ReplyKeyboardMarkup([["⬅️ Orqaga"]], resize_keyboard=True)
    )
    return BROADCAST


def send_broadcast(update: Update, context: CallbackContext):
    if update.message.text == "⬅️ Orqaga":
        return admin_panel(update, context)

    users = db.get_all_user_ids()
    text = update.message.text
    count = 0

    for uid in users:
        try:
            context.bot.send_message(chat_id=uid, text=f"📢 **Xabar:**\n\n{text}", parse_mode='Markdown')
            count += 1
        except:
            continue

    update.message.reply_text(f"✅ Xabar {count} ta foydalanuvchiga yuborildi.")
    return admin_panel(update, context)


def admin_fare_menu(update: Update, context: CallbackContext):
    keyboard = [["Ekonom narxini o'zgartirish"], ["Komfort narxini o'zgartirish"], ["⬅️ Orqaga"]]
    update.message.reply_text(
        "Qaysi tarif narxini o'zgartiramiz?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return EDIT_FARE_SELECT


def ask_new_fare(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "⬅️ Orqaga":
        return admin_panel(update, context)

    context.user_data['editing_tariff'] = 'ekonom' if "Ekonom" in text else 'comfort'

    update.message.reply_text(
        "Yangi narxlarni quyidagi formatda yuboring:\n`asosiy_narx per_km` \n\n"
        "Masalan: `7000 2500` \n\nBekor qilish uchun: /cancel",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([["⬅️ Orqaga"]], resize_keyboard=True)
    )
    return EDIT_FARE_VALUE


def save_new_fare(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "⬅️ Orqaga":
        return admin_panel(update, context)

    try:
        base, per_km = map(int, text.split())
        tariff = context.user_data['editing_tariff']

        db.update_fare(tariff, base, per_km)

        update.message.reply_text(f"✅ {tariff.capitalize()} narxlari yangilandi!")
        return admin_panel(update, context)
    except (ValueError, IndexError):
        update.message.reply_text(
            "❌ Xato format. Iltimos raqamlarni probel bilan yuboring: `7000 2500`"
        )
        return EDIT_FARE_VALUE


def add_promo_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Yangi promokodni yuboring: `KOD FOIZ LIMIT` (Masalan: TAXI20 15 100)",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([["⬅️ Orqaga"]], resize_keyboard=True)
    )
    return ADD_PROMO_VALUE


def add_promo_save(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "⬅️ Orqaga":
        return admin_panel(update, context)

    try:
        parts = text.split()
        if len(parts) < 3:
            raise ValueError

        code = parts[0].upper()
        percentage = int(parts[1])
        max_uses = int(parts[2])

        db.add_promocode_db(code, percentage, max_uses)

        update.message.reply_text(f"✅ Promokod saqlandi: {code} ({percentage}%)")
        return admin_panel(update, context)
    except (IndexError, ValueError):
        update.message.reply_text(
            "❌ Xato format. Qayta urinib ko'ring: `KOD FOIZ LIMIT` (Masalan: TAXI20 15 100)"
        )
        return ADD_PROMO_VALUE


def admin_add_driver_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Yangi haydovchi ma'lumotlarini yuboring:\n"
        "Format: `ID ISM MASHINA RAQAM`\n\n"
        "Misol: `12345678 Ali GENTRA 01A777AA`",
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([["⬅️ Orqaga"]], resize_keyboard=True)
    )
    return ADMIN_ADD_DRIVER_SAVE


def admin_add_driver_save(update: Update, context: CallbackContext):
    text = update.message.text
    if text == "⬅️ Orqaga":
        return admin_panel(update, context)

    try:
        parts = text.split(maxsplit=3)
        if len(parts) < 4:
            raise ValueError

        tg_id = int(parts[0])
        name = parts[1]
        model = parts[2]
        number = parts[3]

        db.admin_add_driver_db(tg_id, name, model, number)

        update.message.reply_text(
            f"✅ **Muvaffaqiyatli!**\n\n"
            f"🆔 ID: `{tg_id}`\n"
            f"👤 Ism: {name}\n"
            f"🚘 Mashina: {model}\n"
            f"🔢 Raqam: {number}",
            parse_mode='Markdown'
        )

        try:
            context.bot.send_message(
                chat_id=tg_id,
                text="🎉 Admin sizni haydovchi sifatida tizimga qo'shdi!\nEndi guruhda buyurtmalarni qabul qilishingiz mumkin."
            )
        except Exception:
            update.message.reply_text("⚠️ Xabar haydovchiga yetkazilmadi (bot bloklangan bo'lishi mumkin).")

        return admin_panel(update, context)

    except (ValueError, IndexError):
        update.message.reply_text(
            "❌ **Xato format!**\n\nIltimos, ma'lumotlarni quyidagi ko'rinishda yuboring:\n"
            "`ID ISM MASHINA RAQAM`",
            parse_mode='Markdown'
        )
        return ADMIN_ADD_DRIVER_SAVE


def cancel_action(update: Update, context: CallbackContext):
    update.message.reply_text("🚫 Amallar bekor qilindi.")
    return admin_panel(update, context)


def main():
    db.create_all_tables()

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('driver', driver_start)
        ],
        states={
            SELECT_LANG: [CallbackQueryHandler(set_lang, pattern="^lang_")],
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE: [MessageHandler(Filters.contact | (Filters.text & ~Filters.command), get_phone)],
            LOCATION: [MessageHandler(Filters.location, get_location)],

            D_NAME: [MessageHandler(Filters.text & ~Filters.command, get_d_name)],
            D_CAR_MODEL: [MessageHandler(Filters.text & ~Filters.command, get_d_model)],
            D_CAR_NUMBER: [MessageHandler(Filters.text & ~Filters.command, finish_driver_reg)],
            DRIVER_MENU: [MessageHandler(Filters.text & ~Filters.command, driver_menu_select)],

            MAIN_MENU: [MessageHandler(Filters.text & ~Filters.command, main_menu_select)],

            GET_START_LOCATION: [MessageHandler(Filters.location | Filters.text, get_start_location)],
            GET_DESTINATION: [MessageHandler(Filters.location | Filters.text, get_destination_and_show_tariffs)],
            CHOOSE_TARIFF: [MessageHandler(Filters.text & ~Filters.command, confirm_order)],

            CONFIRM_ORDER: [
                CallbackQueryHandler(button_handler, pattern="^(final_confirm|use_promo|cancel_order)$"),
                MessageHandler(Filters.regex(r"(🎟|Promokod)"), promokod_first_check),
                MessageHandler(Filters.regex(r"(✅|Tasdiqlash|Подтвердить|Confirm)"), send_to_driver),
                MessageHandler(Filters.regex(r"(❌|Bekor|Отмена|Cancel)"), main_menu),
            ],

            PROMOKOD: [MessageHandler(Filters.text & ~Filters.command, promokod_check)],
            SUPPORT: [MessageHandler(Filters.text & ~Filters.command, forward_to_admin)],
            SETTINGS: [MessageHandler(Filters.text & ~Filters.command, settings_select_menu)],
            SETTINGS_LANG: [CallbackQueryHandler(update_language, pattern="^setlang_")],
            PHONE_EDIT: [MessageHandler(Filters.contact | Filters.text, edit_phone)],
            NAME_SURNAME_EDIT: [MessageHandler(Filters.text, edit_name)],

            ADMIN_MENU: [
                MessageHandler(Filters.regex('^📊'), show_detailed_stats),
                MessageHandler(Filters.regex('^💰'), admin_fare_menu),
                MessageHandler(Filters.regex('^📢'), broadcast_start),
                MessageHandler(Filters.regex('^🎟'), add_promo_start),
                MessageHandler(Filters.regex('^⬅️'), main_menu),
                MessageHandler(Filters.regex('^🆕'), admin_add_driver_start),
            ],
            ADMIN_ADD_DRIVER_SAVE: [
                MessageHandler(Filters.text & ~Filters.command, admin_add_driver_save)
            ],
            EDIT_FARE_SELECT: [MessageHandler(Filters.text, ask_new_fare)],
            EDIT_FARE_VALUE: [MessageHandler(Filters.text, save_new_fare)],
            BROADCAST: [MessageHandler(Filters.text, send_broadcast)],
            ADD_PROMO_VALUE: [MessageHandler(Filters.text, add_promo_save)],
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('cancel', cancel_action)]
    )

    dp.add_handler(conv)
    dp.add_handler(CallbackQueryHandler(button_handler, pattern="^(accept_|picked_|finish_|cancel_|verify_|setlang_)"))
    dp.add_handler(MessageHandler(Filters.reply & Filters.chat(chat_id=ADMIN_GROUP_ID), admin_reply_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()