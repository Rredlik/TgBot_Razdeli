from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton

from database.methods.db_event import create_new_event, add_event_member
from database.methods.db_event import get_event_by_id, get_event_members, \
    create_transaction, add_transaction_members
from handlers.keyboards import btn_create_event
# from handlers.user.dialog import register_dialog_handlers
from loader import bot
from utils.states import Event, EventAddCheck


async def __create_event_msg(msg: Message, state: FSMContext):
    await state.set_state(Event.CreateEvent)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Введите название мероприятия')


async def __event_created(msg: Message, state: FSMContext):
    event_id = await create_new_event(msg.text)
    # user_id = await user_id_by_tg_id(msg.from_user.id)
    # telegram_id =

    await add_event_member(event_id, msg.from_user.id)
    await bot.send_message(chat_id=msg.from_user.id,
                           text=f'Мероприятие создано')
    await state.reset_state()
    await __send_event(msg, event_id)


async def __send_event(msg: Message, event_id=None, state: FSMContext = None):
    if state is not None:
        await state.reset_state()
    event = await get_event_by_id(event_id)
    event_name = event[1]
    event_date = event[2]
    members = await get_event_members(event_id)

    event_message = (f'ID Меропириятия: <code>{event_id}</code>\n'
                     f'Название: {event_name}\n'
                     f'Дата: {event_date}\n'
                     f'Участников: {len(members)}')

    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton('Добавить чек', callback_data=f'addCheck_{event_id}'))
              .add(InlineKeyboardButton('Добавить участника', callback_data=f'addMember_{event_id}'))
              .add(InlineKeyboardButton('Посмотреть чеки', callback_data=f'addMember_{event_id}')))
    await bot.send_message(chat_id=msg.from_user.id,
                           text=event_message, reply_markup=markup)


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
    await bot.send_message(chat_id=call.from_user.id,
                           text=f'Выберите участника, который платил за чек',
                           reply_markup=markup)


async def __addCheck_writeName(call: CallbackQuery, state: FSMContext):
    await state.set_state(EventAddCheck.WriteName)
    user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        data['user_id'] = user_id
    markup = (InlineKeyboardMarkup()
              .add(InlineKeyboardButton(text=f'Отмена', callback_data=f'cancelAddCheck')))
    await bot.send_message(chat_id=call.from_user.id, text=f'Напишите название чека', reply_markup=markup)


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
    user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        members = data['members']

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(text=f'Добавить чек',
                                                             callback_data=f'confirmCheck'))
    for member in members:
        member_id = member['user_id']
        member_login = member['user_login']
        if member_id == user_id:
            member['is_payer'] = not member['is_payer']
        is_payer = '✅' if member['is_payer'] else '❌'
        markup.add(InlineKeyboardButton(text=f'{member_login} {is_payer}',
                                        callback_data=f'changePayerStatus_{member_id}'))

    markup.add(InlineKeyboardButton(text=f'Отмена', callback_data=f'cancelAddCheck'))
    await bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                        reply_markup=markup)


async def __addCheck_confirmCheck(call: CallbackQuery, state: FSMContext):
    # await state.set_state(EventAddCheck.WriteName)
    # user_id = call.data.split('_')[1]
    async with state.proxy() as data:
        user_id = data['user_id']
        event_id = data['event_id']
        transaction_name = data['transaction_name']
        amount = data['amount']
        members = data['members']
    transaction_id = await create_transaction(user_id, event_id, transaction_name, amount)
    members_list = []
    for member in members:
        if member['is_payer']:
            members_list.append(member['user_id'])
    await add_transaction_members(transaction_id, members_list)
    await bot.send_message(chat_id=call.from_user.id, text=f'Чек добавлен!')
    await __send_event(call, event_id)


def register_event_handlers(dp: Dispatcher) -> None:

    # region EVENT
    dp.register_message_handler(__create_event_msg,
                                Text(equals=btn_create_event), state='*')
    dp.register_message_handler(__event_created, content_types=[ContentType.TEXT], state=Event.CreateEvent)
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
                                       state=EventAddCheck.ChooseMember)
    dp.register_callback_query_handler(__addCheck_confirmCheck,
                                       lambda c: c.data == 'confirmCheck',
                                       state=EventAddCheck.ChooseMember)
    # end region ADD CHECK
