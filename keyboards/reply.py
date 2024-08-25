
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder


start_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Оценивать📝')],
    [KeyboardButton(text='Мой профиль😎'),
     KeyboardButton(text='Кто меня оценил🔎')],
    [KeyboardButton(text='ТОП🏆')]],
                    resize_keyboard=True,
                    input_field_placeholder='Выбери пункт меню😉')

del_kb = ReplyKeyboardRemove()


def get_keyboard(
        *btns: str,
        placeholder: str = None,
        request_contact: int = None,
        request_location: int = None,
        sizes: tuple = (2,),
):

    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):

        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
        resize_keyboard=True, input_field_placeholder=placeholder)
