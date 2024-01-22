# import asyncio
#
# from aiogram import Dispatcher, Bot
# from aiogram.dispatcher import FSMContext
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ContentType
#
# from config import CHANNEL_LINK
# # from database.methods.db_event import check_app, update_app_for_who, update_app_theme, update_app_data
# # from database.methods.user import is_subscriber
# # from handlers.admin.applications import __new_app_attention
# from handlers.msg_text import ANSWERS, themes
# # from handlers.user.register import attention_to_sub
# from utils.methods import send_message
# from utils.states import Dialog
#
#
# async def __firstStep(query: CallbackQuery, state: FSMContext):
#     await state.set_state(Dialog.first_step)
#
#     msg_txt = ("Я смогу найти дело жизни для вас или вашего ребенка всего за 2-3 часа. Вам не придется заполнять "
#                "никаких предварительных анкет или тестов. Вы просто записываетесь ко мне на интервью , "
#                "а я диагностирую ваши природные способности и показываю все возможности их применения на реальном "
#                "рынке. В результате вы получаете план вашей реализации на ближайшие несколько лет, чтобы учиться, "
#                "работать с удовольствием и получать за это достойное вознаграждение. Для кого необходимо выявить "
#                "таланты?")
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Для себя любимого', callback_data='first_step_self'))
#               .add(InlineKeyboardButton('Для ребёнка', callback_data='first_step_child')))
#     await send_message(query, msg_txt, markup)
#
#
# async def __secondStep_self(query: CallbackQuery, state: FSMContext):
#     await state.set_state(Dialog.second_step)
#
#     user_id = query.from_user.id
#     await check_app(user_id)
#     await update_app_for_who(user_id, 'Для себя')
#     msg_txt = "Какую задачу вы бы хотели решить?"
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Найти вдохновение в работе',
#                                         callback_data='second_step_self_1'))
#               .add(InlineKeyboardButton('Сменить профессию',
#                                         callback_data='second_step_self_2'))
#               .add(InlineKeyboardButton('Много увлечений – не знаю, что выбрать',
#                                         callback_data='second_step_self_3'))
#               .add(InlineKeyboardButton('Во что инвестировать время и деньги',
#                                         callback_data='second_step_self_4')))
#     await send_message(query, msg_txt, markup)
#     # await attention_to_sub(query, 'self')
#
#
# async def __secondStep_child(query: CallbackQuery, state: FSMContext):
#     await state.set_state(Dialog.second_step)
#     user_id = query.from_user.id
#     await check_app(user_id)
#     await update_app_for_who(user_id, 'Для ребенка')
#     msg_txt = "Какую задачу вы бы хотели решить?"
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Узнать таланты ребенка',
#                                         callback_data='second_step_child_1'))
#               .add(InlineKeyboardButton('Выбрать профиль класса',
#                                         callback_data='second_step_child_2'))
#               .add(InlineKeyboardButton('Подбор развивающих кружков/секций',
#                                         callback_data='second_step_child_3'))
#               .add(InlineKeyboardButton('Выбор дальнейшего образования колледж/ВУЗ',
#                                         callback_data='second_step_child_4'))
#               .add(InlineKeyboardButton('Подбор подходящих профессий',
#                                         callback_data='second_step_child_5'))
#               .add(InlineKeyboardButton('Выбор специальностей и необходимых ЕГЭ',
#                                         callback_data='second_step_child_6')))
#     await send_message(query, msg_txt, markup)
#     # await attention_to_sub(query, 'child')
#
#
# async def __thirdStep(query: CallbackQuery, state: FSMContext):
#     current_state = await state.get_state()
#     url = f'https://future-mission.ru/'
#     await state.set_state(Dialog.third_step)
#     if current_state == 'Dialog:second_step':
#         msg_txt = ("С радостью помогу вам решить эту задачу. Для этого оставьте заявку. Я свяжусь с вами, "
#                    "и мы обсудим, как можно решить вашу задачу.")
#         theme_data = query.data.split('_')
#         theme = themes[theme_data[2]][int(theme_data[3])]
#         await update_app_theme(query.from_user.id, theme)
#         if theme_data[2] == 'self':
#             url += 'adults'
#         else:
#             url += 'children'
#     else:
#         msg_txt = ("С радостью отвечу на все ваши вопросы. Для этого оставьте заявку. Я свяжусь с вами, "
#                    "и мы обсудим, как можно решить вашу задачу.")
#
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Оставить заявку', callback_data='submit_application'))
#               # .add(InlineKeyboardButton('Часто задаваемые вопросы', callback_data='pop_questions'))
#               .add(InlineKeyboardButton('Узнать об услугах подробнее', url=url)))
#     await send_message(query, msg_txt, markup)
#
#
# # Ответы на вопросы
# async def __popularQuestions(query: CallbackQuery, state: FSMContext):
#     await state.set_state(Dialog.questions)
#     back_btn = 'exit'
#     is_ending = len(query.data.split('_'))
#     if is_ending == 3:
#         await state.reset_state()
#         back_btn = 'exit_ending'
#     msg_txt = "Какой вопрос вас интересует?"
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Где и как проходят занятия?',
#                                         callback_data='pop_question_1'))
#               .add(InlineKeyboardButton('Для какого возраста подходит профориентация подросткам?',
#                                         callback_data='pop_question_2'))
#               .add(InlineKeyboardButton('Кто проводит профориентацию?',
#                                         callback_data='pop_question_3'))
#               .add(InlineKeyboardButton('Нужно ли присутствовать родителю на профориентации для подростков?',
#                                         callback_data='pop_question_4'))
#               .add(InlineKeyboardButton('Что мы получим в результате консультации?',
#                                         callback_data='pop_question_5'))
#               .add(InlineKeyboardButton('Назад в меню',
#                                         callback_data=back_btn)))
#     await send_message(query, msg_txt, markup)
#
#
# async def __questAnswer(query: CallbackQuery):
#     msg_txt = ANSWERS[int(query.data.split('_')[2])]
#     await send_message(query, text=msg_txt)
#
#
# # Узнать подробнее
# async def __learnMore(query: CallbackQuery):
#     msg_txt = ('Более подробную информацию можно получить на сайте https://future-mission.ru/otzyvy-o-konsultaciah\n'
#                'С отзывами можете ознакомиться здесь')
#     await send_message(query, text=msg_txt)
#
#
# # Оставить заявку
# async def __makeApplication(query: CallbackQuery, state: FSMContext):
#     await state.set_state(Dialog.make_application_take_name)
#     # Создать application добавить данные из стейта, вернуть id, записать в стейт
#     msg_txt = 'Хорошо, назовите, пожалуйста, свое имя'
#     await send_message(query, text=msg_txt)
#
#
# async def __makeApplication_takeName(message: Message, state: FSMContext):
#     await state.set_state(Dialog.take_number)
#     name = message.text
#     await update_app_data(message.from_user.id, 'user_name', name)
#     msg_txt = 'Напишите номер телефона'
#     await message.answer(msg_txt)
#
#
# async def __makeApplication_takeNumber(message: Message, state: FSMContext):
#     await state.set_state(Dialog.take_email)
#     number = message.text
#     await update_app_data(message.from_user.id, 'user_number', number)
#     msg_txt = 'Напишите, пожалуйста, вашу электронную почту'
#     await message.answer(msg_txt)
#
#
# async def __makeApplication_takeEmail(message: Message, state: FSMContext):
#     await state.reset_state()
#     email = message.text
#     user_id = message.from_user.id
#     await update_app_data(user_id, 'user_email', email)
#     await update_app_data(user_id, 'is_complete', 1)
#     await update_app_data(user_id, 'in_work', 0)
#     # is_sub = await is_subscriber(user_id)
#     msg_txt = (
#         'Спасибо, ваша заявка отправлена! Я свяжусь с вами в ближайшее время.'
#         'А пока вы можете подписаться на мой канал, где я рассказываю массу интересного.\n\n'
#         'За подписку вы получите от меня подарок в виде полезной пользы 😉\n'
#         f'{CHANNEL_LINK}')
#     await message.answer(msg_txt)
#     await __new_app_attention(message)
#     # Повторная отправка кнопок с вопросами
#     # await asyncio.sleep(5)
#     # await __ending(message)
#
#
# async def __ending(query: Message):
#     msg_txt = "Какой вопрос вас интересует"
#     markup = (InlineKeyboardMarkup()
#               .add(InlineKeyboardButton('Часто задаваемые вопросы', callback_data='pop_questions_ending'))
#               .add(InlineKeyboardButton('Узнать об услугах подробнее', callback_data='learn_more_ending')))
#     await send_message(query, msg_txt, markup)
#
#
# # Добавить напоминание о подписе
# # Предлагаю подписаться на мой телеграмм канал, где я рассказываю
# # примеры из практики и истории ребят и их родителей. За подписку вы получите полезный подарок
# # https://t.me/marinailalova
# #
# # при подписке
# # Спасибо за подписку, получите ваш подарок
# # https://drive.google.com/file/d/1IdVfz1Hf5j2H1uaMpLAT94tMh0rfzl1X/view?usp=sharing
# def register_dialog_handlers(dp: Dispatcher) -> None:
#     dp.register_callback_query_handler(__firstStep, lambda c: c.data == 'first_step', state=None)
#
#     dp.register_callback_query_handler(__secondStep_self, lambda c: c.data == 'first_step_self',
#                                        state=Dialog.first_step)
#     dp.register_callback_query_handler(__secondStep_child, lambda c: c.data == 'first_step_child',
#                                        state=Dialog.first_step)
#
#     dp.register_callback_query_handler(__thirdStep, lambda c: c.data and c.data.startswith('second_step_'),
#                                        state=Dialog.second_step)
#     # Ответы на вопросы
#     dp.register_callback_query_handler(__popularQuestions, lambda c: c.data == 'pop_questions',
#                                        state=Dialog.third_step)
#     dp.register_callback_query_handler(__questAnswer, lambda c: c.data and c.data.startswith('pop_question_'),
#                                        state='*')
#     dp.register_callback_query_handler(__thirdStep, lambda c: c.data == 'exit',
#                                        state=Dialog.questions)
#
#     # Узнать подробнее
#     dp.register_callback_query_handler(__learnMore, lambda c: c.data == 'learn_more',
#                                        state=Dialog.third_step)
#
#     # Оставить заявку
#     dp.register_callback_query_handler(__makeApplication, lambda c: c.data == 'submit_application',
#                                        state=Dialog.third_step)
#     dp.register_message_handler(__makeApplication_takeName, state=Dialog.make_application_take_name,
#                                 content_types=[ContentType.TEXT])
#     dp.register_message_handler(__makeApplication_takeNumber, state=Dialog.take_number,
#                                 content_types=[ContentType.TEXT])
#     dp.register_message_handler(__makeApplication_takeEmail, state=Dialog.take_email,
#                                 content_types=[ContentType.TEXT])
#
#     dp.register_callback_query_handler(__ending, lambda c: c.data == 'exit_ending',
#                                        state=None)
#     dp.register_callback_query_handler(__popularQuestions, lambda c: c.data == 'pop_questions_ending',
#                                        state=None)
#     dp.register_callback_query_handler(__learnMore, lambda c: c.data == 'learn_more_ending',
#                                        state=None)
