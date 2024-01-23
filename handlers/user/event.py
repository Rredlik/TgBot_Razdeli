from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import create_new_event, add_event_member, get_all_user_events
from database.methods.db_event import get_event_by_id, get_event_members, \
    create_transaction, add_transaction_members
from handlers.keyboards import btn_create_event, btn_con_event, btn_my_events
# from handlers.user.dialog import register_dialog_handlers
from loader import bot
from utils.methods import send_callMessage
from utils.states import Event, EventAddCheck, EventTransactions, EventCalculation


#############################
#############################


async def __create_event_msg(msg: Message, state: FSMContext):
    await state.reset_state()
    await state.set_state(Event.CreateEvent)
    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Отмена', callback_data=f'cancelConnecting')))
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите название мероприятия',
                           reply_markup=markup)


async def __event_created(msg: Message, state: FSMContext):
    event_id = await create_new_event(msg.text)
    # user_id = await user_id_by_tg_id(msg.from_user.id)
    # telegram_id =

    await add_event_member(event_id, msg.from_user.id)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Мероприятие создано')
    await state.reset_state()
    await __send_event(msg, event_id)


###############################

async def __showMyEvents(msg: Message, state: FSMContext):
    await state.reset_state()
    await state.set_state(Event.ShowEvents)
    events = await get_all_user_events(msg.from_user.id)
    markup = InlineKeyboardMarkup()
    for event in events:
        event_id = event[0]
        event_name = event[1]
        markup.add(InlineKeyboardButton(text=f'{event_name}',
                                        callback_data=f'openEvent_{event_id}'))
    markup.add(InlineKeyboardButton('Отмена', callback_data=f'cancelConnecting'))
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Выберите мероприятие, чтобы посмотреть информацию по нему',
                           reply_markup=markup)


async def __openEvent(call: CallbackQuery, state: FSMContext):
    bot.answer_callback_query(call.id)
    await state.reset_state()
    event_id = call.data.split('_')[1]
    await __send_event(call, event_id)


#######################
async def __connectToEvent(msg: Message, state: FSMContext):
    await state.reset_state()
    await state.set_state(Event.ConnectToEvent)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите ID мероприятия\n\n'
                                f'Попросите друзей, присоединившихся к мероприятию, скинуть его ID')


async def __connectedToEvent(msg: Message, state: FSMContext):
    event_id = await get_event_by_id(msg.text)
    if event_id is None or event_id == '':
        markup = (InlineKeyboardMarkup()
                  .add(InlineKeyboardButton('Отмена', callback_data=f'cancelConnecting')))
        await bot.send_message(chat_id=msg.from_user.id,
                               text=f'Не найдено мероприятие с таким ID.\n'
                                    f'Введите еще раз',
                               reply_markup=markup)
    else:
        await state.reset_state()
        await add_event_member(event_id, msg.from_user.id)
        await bot.send_message(chat_id=msg.from_user.id,
                               text=f'Вы присоединились к мероприятию')
        await __send_event(msg, event_id)


#############################
#############################
async def __cancelConnecting(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await send_callMessage(call,
                           text=f'Отмена добавления мероприятия')


async def __cancelAddCheck(call: CallbackQuery, state: FSMContext):
    await state.reset_state()
    event_id = call.data.split('_')[1]
    await send_callMessage(call,
                           text=f'Отмена добавления чека')
    await __send_event(call, event_id)


async def backToEventFromOther(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    await state.reset_state()
    event_id = call.data.split('_')[1]
    await __send_event(call, event_id)


#############################
#############################


async def __send_event(msg: Message, event_id=None, state: FSMContext = None):
    if state is not None:
        await state.reset_state()
    event = await get_event_by_id(event_id)
    event_name = event[1]
    event_date = event[2]
    members = await get_event_members(event_id)

    event_message = (f'Дата создания: {event_date}\n'
                     f'ID мероприятия: <code>{event_id}</code>\n'
                     f'Название: {event_name}\n'
                     f'Участников: {len(members)}')

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Добавить чек', callback_data=f'addCheck_{event_id}'))
              .add(InlineKeyboardButton('Добавить участника', callback_data=f'addMember_{event_id}'))
              .add(InlineKeyboardButton('Посмотреть чеки', callback_data=f'showChecks_{event_id}'))
              .add(InlineKeyboardButton('Расчет', callback_data=f'calculating_{event_id}')))
    await send_callMessage(call=msg, text=event_message, reply_markup=markup)


async def __addCheck_selectMember(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventAddCheck.ChooseMember)
    event_id = call.data.split('_')[1]
    members = await get_event_members(event_id)
    markup = InlineKeyboardMarkup()
    check_members = []
    for member in members:
        check_members.append({
            'user_id': member[0],
            'user_login': member[4],
            'is_payer': True
        })
        member_id = member[0]
        member_login = member[4]
        markup.add(InlineKeyboardButton(text=f'{member_login}',
                                        callback_data=f'addCheckOwner_{member_id}'))
    markup.add(InlineKeyboardButton(text=f'Отмена',
                                    callback_data=f'cancelAddCheck'))
    async with state.proxy() as data:
        data['event_id'] = event_id
        data['members'] = check_members
    await send_callMessage(call,
                           text=f'Выберите участника, который платил за чек',
                           reply_markup=markup)


async def __addCheck_writeName(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventAddCheck.WriteName)
    user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        data['user_id'] = user_id
    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton(text=f'Отмена', callback_data=f'cancelAddCheck')))
    await send_callMessage(call, text=f'Напишите название чека', reply_markup=markup)


async def __addCheck_writeAmount(msg: Message, state: FSMContext):
    await state.set_state(EventAddCheck.WriteAmount)
    async with state.proxy() as data:
        data['transaction_name'] = msg.text
    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton(text=f'Отмена', callback_data=f'cancelAddCheck')))
    await bot.send_message(chat_id=msg.from_user.id, text=f'Напишите стоимость чека', reply_markup=markup)


async def __addCheck_choosePayers(msg: Message, state: FSMContext):
    await state.set_state(EventAddCheck.ChoosePayers)
    async with state.proxy() as data:
        data['amount'] = msg.text
        members = data['members']
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Добавить чек',
                                                             callback_data=f'confirmCheck'))
    for member in members:
        member_id = member['user_id']
        member_login = member['user_login']
        is_payer = '✅' if member['is_payer'] else '❌'
        markup.add(InlineKeyboardButton(text=f'{member_login} {is_payer}',
                                        callback_data=f'changePayerStatus_{member_id}'))
    markup.add(InlineKeyboardButton(text=f'Отмена',
                                    callback_data=f'cancelAddCheck'))
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Нажмите на участника, который не должен платить за этот чек. '
                                f'Если готовы добавить чек нажмите "Добавить чек"',
                           reply_markup=markup)


async def __addCheck_changePayerStatus(call: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        members = data['members']

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Добавить чек',
                                                             callback_data=f'confirmCheck'))
    for member in members:
        member_id = member['user_id']
        member_login = member['user_login']
        if str(member_id) == str(user_id):
            member['is_payer'] = not member['is_payer']
        is_payer = '✅' if member['is_payer'] else '❌'
        markup.add(InlineKeyboardButton(text=f'{member_login} {is_payer}',
                                        callback_data=f'changePayerStatus_{member_id}'))
    async with state.proxy() as data:
        data['members'] = members
    markup.add(InlineKeyboardButton(text=f'Отмена', callback_data=f'cancelAddCheck'))
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=markup)


async def __addCheck_confirmCheck(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        user_id = data['user_id']
        event_id = data['event_id']
        transaction_name = data['transaction_name']
        amount = data['amount']
        members = data['members']
    await state.reset_state()
    transaction_id = await create_transaction(user_id, event_id, transaction_name, amount)
    members_list = []
    for member in members:
        if member['is_payer']:
            members_list.append(member['user_id'])
    await add_transaction_members(transaction_id, members_list)
    await send_callMessage(call, text=f'Чек добавлен!\n\n'
                                      f'{transaction_name}\n'
                                      f'Сумма: {amount}')
    await __send_event(call, event_id)


#############################
#############################


def register_event_handlers(dp: Dispatcher) -> None:
    # region EVENT
    ## create event
    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)

    ## my events
    dp.register_message_handler(__showMyEvents,
                                Text(equals=btn_my_events), state='*')
    dp.register_callback_query_handler(__openEvent,
                                       lambda c: c.data and c.data.startswith('openEvent_'), state=Event.ShowEvents)
    ## connect to event
    dp.register_message_handler(__connectToEvent,
                                Text(equals=btn_con_event), state='*')
    dp.register_message_handler(__connectedToEvent, content_types=[ContentType.TEXT], state=Event.ConnectToEvent)
    dp.register_callback_query_handler(__cancelConnecting,
                                       lambda c: c.data == 'cancelConnecting',
                                       state='*')
    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data and c.data.startswith('backToEvent_'),
                                       state=EventTransactions.SelectTransaction)
    dp.register_callback_query_handler(backToEventFromOther,
                                       lambda c: c.data and c.data.startswith('backToEvent_'),
                                       state=EventCalculation.Calculate)
    # end region EVENT

    # region ADD CHECK
    dp.register_callback_query_handler(__addCheck_selectMember,
                                       lambda c: c.data and c.data.startswith('addCheck_'), state=None)
    dp.register_callback_query_handler(__addCheck_writeName,
                                       lambda c: c.data and c.data.startswith('addCheckOwner_'),
                                       state=EventAddCheck.ChooseMember)
    dp.register_message_handler(__addCheck_writeAmount,
                                content_types=[ContentType.TEXT], state=EventAddCheck.WriteName)
    dp.register_message_handler(__addCheck_choosePayers,
                                content_types=[ContentType.TEXT], state=EventAddCheck.WriteAmount)
    dp.register_callback_query_handler(__addCheck_changePayerStatus,
                                       lambda c: c.data and c.data.startswith('changePayerStatus_'),
                                       state=EventAddCheck.ChoosePayers)
    dp.register_callback_query_handler(__addCheck_confirmCheck,
                                       lambda c: c.data == 'confirmCheck',
                                       state=EventAddCheck.ChoosePayers)
    # end region ADD CHECK
