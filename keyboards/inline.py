from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


top_user = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🥇',
            callback_data='top_1'
        ),
        InlineKeyboardButton(
            text='🥈',
            callback_data='top_2'
        ),
        InlineKeyboardButton(
            text='🥉',
            callback_data='top_3'
        )
    ]
])



