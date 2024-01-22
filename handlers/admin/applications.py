# from aiogram import Dispatcher, Bot
# from aiogram.dispatcher.filters import Text
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
#
# # from database.methods.db_event import get_all_completed_apps, get_one_not_in_work, update_app_data, \
# #     update_app_data_by_id
# from database.methods.db_user import parseAllAdmins
# from filters.main import IsAdmin
# from utils.methods import send_message
# from utils.misc.htms_tags import url


# async def __watch_apps(msg: Message):
#     bot: Bot = msg.bot
#     applications = await get_all_completed_apps()
#     apps_in_work, apps_wait = 0, 0
#     for application in applications:
#         if application[-1] == 1:
#             apps_in_work += 1
#         else:
#             apps_wait += 1
#     msg_text = (f'Заявок ждут обработки: {apps_wait}\n'
#                 f'Заявок обработано: {apps_in_work}\n'
#                 f'Всего заявок: {len(applications)}\n')
#     if apps_wait != 0:
#         markup = (InlineKeyboardMarkup()
#                   .add(InlineKeyboardButton('Показать заявку',
#                                             callback_data='view_app')))
#     else:
#         markup = None
#     await bot.send_message(chat_id=msg.from_user.id,
#                            text=msg_text,
#                            reply_markup=markup)


# async def __view_app(query: CallbackQuery):
#     app = await get_one_not_in_work()
#
#     # user_link = f'[{app[4]}](tg://user?id={str(app[1])})'
#     bot: Bot = query.bot
#     Chat = await bot.get_chat(app[1])
#     user_link = url(app[4], f'{Chat.user_url}')
#     user_name = Chat.username
#     user_name = f'@{user_name}' if user_name is not None else '-'
#     msg_text = (f'Пользователя:  {user_link}\n'
#                 f'Чат: {user_name}\n'
#                 f'Для кого: {app[2]}\n'
#                 f'Тема: {app[3]}\n'
#                 f'Номер телефона: {app[5]}\n'
#                 f'Почта: {app[6]}\n'
#                 f'Дата заявки: {app[7]}')
#
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Закрыть заявку',
#                                         callback_data=f'take_to_work_{app[0]}')))
#
#     await query.bot.send_message(chat_id=query.from_user.id,
#                                  text=msg_text,
#                                  reply_markup=markup)
#
#
# async def __take_app_to_work(query: CallbackQuery):
#     app_id = query.data.split('_')[-1]
#     await update_app_data_by_id(app_id, 'in_work', 1)
#     msg_text = 'Заявка закрыта'
#     await send_message(query, msg_text)
#     await __watch_apps(query)
#
#
# async def __new_app_attention(query: CallbackQuery):
#     msg_text = f'Поступила новая заявка!'
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Посмотреть заявки',
#                                         callback_data='watch_apps')))
#     admins = await parseAllAdmins()
#     for admin in admins:
#         await query.bot.send_message(chat_id=int(admin[0]),
#                                      text=msg_text,
#                                      reply_markup=markup)
#
#
# def _register_applications_handlers(dp: Dispatcher) -> None:
#     dp.register_message_handler(__watch_apps,
#                                 Text(equals="Посмотреть заявки"), IsAdmin(), state='*')
#     dp.register_callback_query_handler(__watch_apps, lambda c: c.data == 'watch_apps', IsAdmin(), state='*')
#     dp.register_callback_query_handler(__view_app, lambda c: c.data == 'view_app', IsAdmin(), state='*')
#     dp.register_callback_query_handler(__take_app_to_work, lambda c: c.data and c.data.startswith('take_to_work_'),
#                                        IsAdmin(), state='*')
    # dp.register_message_handler(send_photo_file_id, IsAdmin(), content_types=ContentType.PHOTO)
