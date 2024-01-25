from typing import Final
from aiogram.dispatcher.filters.state import StatesGroup, State


class Register(StatesGroup):
    WaitLogin: Final = State()
    SucceedSub: Final = State()


class Event(StatesGroup):
    CreateEvent: Final = State()
    ConnectToEvent: Final = State()
    ShowEvents: Final = State()


class EventAddCheck(StatesGroup):
    ChooseMember: Final = State()
    WriteName: Final = State()
    WriteAmount: Final = State()
    ChoosePayers: Final = State()


class EventTransactions(StatesGroup):
    SelectTransaction: Final = State()
    OpenTransaction: Final = State()


class EventMembers(StatesGroup):
    ShowAllMembers: Final = State()
    AddNewMember: Final = State()
    AddNewMemberBotName: Final = State()
    AddNewMemberUserID: Final = State()



class EventCalculation(StatesGroup):
    Calculate: Final = State()


class ADPosting(StatesGroup):
    WriteText: Final = State()
    CheckPost: Final = State()
    SendPost: Final = State()


class AddAdmin(StatesGroup):
    TakeUserId: Final = State()

