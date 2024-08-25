from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, or_f

from database.orm_querry import (orm_add_profile, orm_update_description, orm_update_country,
                                 orm_get_profile, orm_update_age, orm_update_gender,
                                 orm_update_city, orm_update_name, orm_update_photo,
                                 orm_rate_profile, orm_count_grades, orm_update_filter_wanted_gender,
                                 orm_get_top)
from keyboards import reply
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from filters.chat_types import ChatTypeFilter
from keyboards.reply import get_keyboard
from keyboards.inline import top_user

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))


class AddProfile(StatesGroup):
    id = State()
    name = State()
    gender = State()
    age = State()
    country = State()
    city = State()
    photography = State()
    change_age = State()
    change_name = State()
    change_gender = State()
    change_country = State()
    change_city = State()
    change_photography = State()
    description = State()
    change_description = State()
    grade = State()
    tg_name = State()
    liked_id = State()
    all_grades = State()
    count_grades = State()
    confirmation = State()
    new_count_grades = State()
    wanted_gender = State()
    report = State()
    confirmation_report = State()
    id_ban = State()
    ban = State()


@user_private_router.message(or_f(CommandStart(), F.text.contains('🔙Главное меню')))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await state.clear()
        await message.answer('''В Monro ты сможешь получить оценку на свои фотографии 📷 от других пользователей.
Не стоит расстраиваться если пользователи ставят вам низкие оценки. Ведь хейтеров всегда хватает 🙃
Ты можешь ознакомиться с правилами🔞 бота нажав на команду /rules''',
                             reply_markup=reply.start_kb)
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.message(AddProfile.id, F.text)
async def add_profile(message: Message, state: FSMContext):
    await state.update_data(id=message.from_user.id)
    await message.answer('Итак... <b>Как тебя зовут?</b> 🙂', reply_markup=get_keyboard(
                                                            f"{message.from_user.first_name}",
                                                            sizes=(1,),
                                                        ))
    await state.set_state(AddProfile.name)


@user_private_router.message(AddProfile.name, F.text)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('<b>Какого ты пола?</b> 👫', reply_markup=get_keyboard(
                                                            f"Мужской",
                                                            "Женский",
                                                            sizes=(1, 1),
                                                        ))
    await state.set_state(AddProfile.gender)


@user_private_router.message(AddProfile.gender, F.text)
async def add_gender(message: Message, state: FSMContext):
    if message.text == 'Мужской' or message.text == 'Женский':
        await state.update_data(gender=message.text)
        await message.answer('<b>Сколько тебе лет?</b> 👶...👨‍🦳', reply_markup=reply.del_kb)
        await state.set_state(AddProfile.age)
    else:
        await message.answer('Выбери свой пол из предложенных кнопок ниже👫')


@user_private_router.message(AddProfile.age, F.text)
async def add_age(message: Message, state: FSMContext):
    try:
        s = int(message.text)
        await state.update_data(age=message.text)
        await message.answer('<b>Из какой ты страны?</b> 🏳️❓', reply_markup=get_keyboard(
                                                                "Не указывать",
                                                                sizes=(1,),
                                                            ))
        await state.set_state(AddProfile.country)
    except:
        await message.answer('Нужно ввести значение в цифрах🔢')


@user_private_router.message(AddProfile.country, F.text)
async def add_country(message: Message, state: FSMContext):
    await state.update_data(country=[message.text, 'Не указана'][message.text == "Не указывать"])
    await message.answer('<b>Из какого ты города?</b> 🌆', reply_markup=get_keyboard(
                                                            "Не указывать",
                                                            sizes=(1,),
                                                        ))
    await state.set_state(AddProfile.city)


@user_private_router.message(AddProfile.city, F.text)
async def add_city(message: Message, state: FSMContext):
    await state.update_data(city=[message.text, 'Не указан'][message.text == "Не указывать"])
    await message.answer('''<b>Отправь свою фотографию</b> 📷.

Помни, фотография не должна содержать контент 18+ и рекламу''', reply_markup=reply.del_kb)
    await state.set_state(AddProfile.photography)


@user_private_router.message(AddProfile.photography, F.photo)
async def add_city(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(photography=message.photo[-1].file_id)
    await message.answer('<b>Отлично</b>, теперь можем начинать 🙃', reply_markup=reply.start_kb)
    data = await state.get_data()
    try:
        await orm_add_profile(session, data)
        await state.clear()
    except Exception as e:
        await message.answer(f'Ошибка: \n{str(e)}, свяжитесь с нами. Опять этот прогер где-то накосячил...')


@user_private_router.message(AddProfile.photography)
async def add_image2(message: Message):
    await message.answer('''<b>Отправь свою фотографию</b> 📷.

Помни, фотография не должна содержать контент 18+ и рекламу''')


@user_private_router.message(or_f(Command('help'), F.text.lower().contains('помощь')))
async def help_for_user(message: Message, state: FSMContext, session: AsyncSession):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await message.answer('''<b>Что умеет бот?</b>🤖

🗒Ты можешь оценивать фотографии других пользователей
🤩Получать оценки от них
💬Завести общение, а может даже и что-то большее 😏
🌇Найти кого нибудь из своего города
🔝Посмотреть кто в топах, а может и оказаться в них

Ну что, приступим?😉''', reply_markup=reply.start_kb)
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.message(or_f(Command('rules'), F.text.lower().contains('правила')))
async def rules(message: Message, state: FSMContext, session: AsyncSession):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await message.answer('''❌ Правила пользования <b>Monro</b> 👇

🔞 Фото содержащие контент 18+ ( эротика, насилие, кровь, педофилия и т.п )
🗣 Фото содержащие матерные слова, высказывания, разжигание международный розни, рассизм
💳 Номера карт на фото ( в целях вашей же безопасности )
📢 Запрещена любая реклама ( сайты, каналы, группы и т.д. )
🌶 Упоминание интима, ссылки на источники по услугам интимного характера''', reply_markup=reply.start_kb)
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.message(or_f(F.text.contains('Мой профиль'), F.text.contains('Назад⬅️2️⃣')))
async def my_profile(message: Message, session: AsyncSession, state: FSMContext):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
👫Пол: <strong>{profile.gender}</strong>
❓Какой пол вы хотите оценивать: <strong>{' '.join(profile.wanted_gender.split()[:-1])}</strong>
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
        round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else str(0)
        }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=get_keyboard(
                'Изменить фото 📷',
                'Изменить возраст 👶...👨‍🦳',
                'Изменить пол 👫',
                'Изменить страну 🏳️',
                'Изменить город 🌇',
                'Изменить имя ⭐️',
                'Далее1️⃣➡️',
                '🔙Главное меню',
                sizes=(3, 3, 2),
            ))
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.message(F.text.contains('Изменить фото 📷'))
async def confirmation(message: Message, state: FSMContext):
    await message.answer('''❗️При замене фото оценка профиля обнуляется❗️\n
<b>Вы уверены?</b>''', reply_markup=get_keyboard(
        'Да✅',
        'Нет❌',
        sizes=(2,),
    ))
    await state.set_state(AddProfile.confirmation)


@user_private_router.message(AddProfile.confirmation, F.text)
async def new_photography(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Да✅':
        await message.answer('''<b>Пришли своё фото</b> 📷\n
Помни, фотография не должна содержать контент 18+ и рекламу''', reply_markup=get_keyboard(
            'Оставить текущее',
            sizes=(1,),
        ))
        await state.update_data(id=message.from_user.id)
        await state.set_state(AddProfile.change_photography)
    else:
        await state.clear()
        await my_profile(message, session, state)


@user_private_router.message(AddProfile.change_photography, F.photo)
async def change_photography(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(change_photography=message.photo[-1].file_id)
    data = await state.get_data()
    await orm_update_photo(session, data['id'], str(data['change_photography']))
    await orm_rate_profile(session, str(data['id']), 0)
    await orm_count_grades(session, str(data['id']), 0)
    await message.answer('<b>Фото успешно изменено 👌</b>')
    await state.clear()
    await my_profile(message, session, state)


@user_private_router.message(AddProfile.change_photography)
async def add_image2(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Оставить текущее':
        await state.clear()
        await my_profile(message, session)
    else:
        await message.answer('''<b>Нужно отправить свою фотографию</b> 📷.\n
Помни, фотография не должна содержать контент 18+ и рекламу''')


@user_private_router.message(F.text.contains('Изменить возраст 👶...👨‍🦳'))
async def new_age(message: Message, state: FSMContext):
    await message.answer('Укажи новый возраст 😉')
    await state.set_state(AddProfile.change_age)


@user_private_router.message(AddProfile.change_age, F.text)
async def change_age(message: Message, state: FSMContext, session: AsyncSession):
    try:
        s = int(message.text)
        await state.update_data(change_age=message.text)
        data = await state.get_data()
        await orm_update_age(session, message.from_user.id, str(data['change_age']))
        await message.answer('<b>Возраст успешно изменён</b> 👌')
        await state.clear()
        await my_profile(message, session, state)
    except:
        await message.answer('<b>Нужно ввести число</b>')


@user_private_router.message(F.text.contains('Изменить пол 👫'))
async def new_gender(message: Message, state: FSMContext):
    await message.answer('Укажи свой пол 👫', reply_markup=get_keyboard(
                                                            f"Мужской",
                                                            "Женский",
                                                            sizes=(1, 1),
                                                        ))
    await state.set_state(AddProfile.change_gender)


@user_private_router.message(AddProfile.change_gender, F.text)
async def change_gender(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Мужской' or message.text == 'Женский':
        await state.update_data(change_gender=message.text)
        data = await state.get_data()
        await orm_update_gender(session, message.from_user.id, str(data['change_gender']))
        await message.answer('<b>Пол успешно изменён</b> 👌')
        await state.clear()
        await my_profile(message, session, state)
    else:
        await message.answer('Выбери свой пол из предложенных кнопок ниже👫')


@user_private_router.message(F.text.contains('Изменить страну 🏳️'))
async def new_country(message: Message, state: FSMContext):
    await message.answer('Из какой ты страны? 🏳️❓', reply_markup=get_keyboard(
                                                                "Не указывать",
                                                                sizes=(1,),
                                                            ))
    await state.set_state(AddProfile.change_country)


@user_private_router.message(AddProfile.change_country, F.text)
async def change_gender(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(change_country=[message.text, 'Не указана'][message.text == "Не указывать"])
    data = await state.get_data()
    await orm_update_country(session, message.from_user.id, str(data['change_country']))
    await message.answer('<b>Страна успешно изменена</b> 👌')
    await state.clear()
    await my_profile(message, session, state)


@user_private_router.message(F.text.contains('Изменить город 🌇'))
async def new_city(message: Message, state: FSMContext):
    await message.answer('Из какого ты города? 🌆', reply_markup=get_keyboard(
                                                            "Не указывать",
                                                            sizes=(1,),
                                                        ))
    await state.set_state(AddProfile.change_city)


@user_private_router.message(AddProfile.change_city, F.text)
async def change_city(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(change_city=[message.text, 'Не указана'][message.text == "Не указывать"])
    data = await state.get_data()
    await orm_update_city(session, message.from_user.id, str(data['change_city']))
    await message.answer('<b>Город успешно изменен</b> 👌')
    await state.clear()
    await my_profile(message, session, state)


@user_private_router.message(F.text.contains('Изменить имя ⭐️'))
async def new_name(message: Message, state: FSMContext):
    await message.answer('Укажи новое имя ⭐️', reply_markup=get_keyboard(
                                                            f"{message.from_user.first_name}",
                                                            sizes=(1,),
                                                        ))
    await state.set_state(AddProfile.change_name)


@user_private_router.message(AddProfile.change_name, F.text)
async def change_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(change_name=message.text)
    data = await state.get_data()
    await orm_update_name(session, message.from_user.id, str(data['change_name']))
    await message.answer('<b>Имя успешно изменено</b> 👌')
    await state.clear()
    await my_profile(message, session, state)


@user_private_router.message(or_f(F.text.contains('Мой профиль'), F.text.contains('Далее1️⃣➡️')))
async def my_profile_two(message: Message, session: AsyncSession, state: FSMContext):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
👫Пол: <strong>{profile.gender}</strong>
❓Какой пол вы хотите оценивать: <strong>{' '.join(profile.wanted_gender.split()[:-1])}</strong>
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
        round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
        }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=get_keyboard(
                'Добавить описание ✏️',
                'Фильтры 📝',
                'Назад⬅️2️⃣',
                '🔙Главное меню',
                sizes=(2, 2),
            ))
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.message(F.text.contains('Добавить описание ✏️'))
async def new_description(message: Message, state: FSMContext):
    await message.answer('✏️ Напиши что нибудь о себе, но помни описание не может превышать длину в <b>255</b>',
                         reply_markup=get_keyboard(
                             'Оставить пустым',
                             sizes=(1,),
                         ))
    await state.set_state(AddProfile.change_description)


@user_private_router.message(AddProfile.change_description, F.text)
async def change_description(message: Message, state: FSMContext, session: AsyncSession):
    if len(message.text) <= 255:
        await state.update_data(change_description=[f'\n✏️: {message.text}\n', ''][message.text == 'Оставить пустым'])
        data = await state.get_data()
        await orm_update_description(session, message.from_user.id, str(data['change_description']))
        await message.answer('<b>Описание успешно изменено</b> 👌')
        await state.clear()
        await my_profile_two(message, session, state)
    else:
        await message.answer('❌ Описание не может превышать длину в <b>255</b> символов')


@user_private_router.message(F.text.contains('Фильтры 📝'))
async def wanted_gender(message: Message, state: FSMContext):
    await message.answer('Выбери пол, который ты хочешь оценивать',
                         reply_markup=get_keyboard(
                             'Мужской 👨‍🦱',
                             'Женский 👩‍🦳',
                             'Без разницы 👫',
                             sizes=(2, 1),
                         ))
    await state.set_state(AddProfile.wanted_gender)


@user_private_router.message(AddProfile.wanted_gender, F.text)
async def change_wanted_gender(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == 'Мужской 👨‍🦱' or message.text == 'Женский 👩‍🦳' or message.text == 'Без разницы 👫':
        await state.update_data(wanted_gender=message.text)
        data = await state.get_data()
        await orm_update_filter_wanted_gender(session, message.from_user.id, str(data['wanted_gender']))
        await message.answer('<b>Фильтры успешно изменены</b> 👌')
        await state.clear()
        await my_profile_two(message, session, state)
    else:
        await message.answer('Выбери фильтр из предложенных кнопок ниже👫')


@user_private_router.message(F.text.contains('ТОП'))
async def top(message: Message, session: AsyncSession, state: FSMContext):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        tops = await orm_get_top(session)
        profile = tops[0]
        await message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
    round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
    }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=top_user)
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_private_router.callback_query(or_f(F.data == 'top_1', F.data == 'top_2', F.data == 'top_3'))
async def top1(callback: CallbackQuery, session: AsyncSession):
    data = callback.data
    tops = await orm_get_top(session)
    if data == 'top_1':
        await callback.message.delete()
        await callback.answer()
        profile = tops[0]
        await callback.message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
    round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
    }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=top_user)
    elif data == 'top_2':
        await callback.message.delete()
        await callback.answer()
        profile = tops[1]
        await callback.message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
    round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
    }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=top_user)
    elif data == 'top_3':
        await callback.message.delete()
        await callback.answer()
        profile = tops[2]
        await callback.message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
    round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
    }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=top_user)
