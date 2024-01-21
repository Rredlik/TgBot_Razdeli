from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_user import isAdmin


async def check_sub():
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton('✅ Проверить подписку',
                                                             callback_data='check_sub'))
    return markup


# async def check_sub_second():
#     markup = InlineKeyboardMarkup().add(InlineKeyboardButton('✅ Проверить подписку',
#                                                              callback_data='check_sub_second'))\
#         .add(InlineKeyboardButton('👩🏼‍💻 Тех. поддержка', url='t.me/skidikis'))
#     return markup


async def to_instruction():
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Далее',
                                                             callback_data='instruction'))
    return markup


# async def sub_succeed_cont():
#     markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Да!',
#                                                              callback_data='sub_succeed_cont'))
#     return markup


btn_create_event = 'Создать мероприятие'
btn_my_events = 'Мои мероприятия'
btn_con_event = 'Присоединиться к мероприятию'
btn_profile = 'Профиль'
async def kb_main_menu(user_id: int):
    markup = (ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
              .add(KeyboardButton(btn_create_event))
              .add(KeyboardButton(btn_my_events))
              .add(KeyboardButton(btn_con_event))
              .add(KeyboardButton(btn_profile)))
    is_admin = await isAdmin(user_id)
    if is_admin:
        (markup
         .add(KeyboardButton('Меню админа')))
    return markup
