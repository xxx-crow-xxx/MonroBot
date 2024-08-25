from aiogram import Router, F

from aiogram.types import Message
from aiogram.filters import or_f

from database.orm_querry import (orm_get_random_profile, orm_rate_profile,
                                 orm_count_grades, orm_get_profile, orm_get_grade,
                                 orm_add_grade, orm_update_new_count_grade,
                                 orm_delete_grade, orm_get_random_profile_man,
                                 orm_get_random_profile_woman, orm_add_report)
from handlers.user_private import AddProfile
from keyboards import reply
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext

from filters.chat_types import ChatTypeFilter
from keyboards.reply import get_keyboard

user_assessment_router = Router()
user_assessment_router.message.filter(ChatTypeFilter(["private"]))


@user_assessment_router.message(or_f(F.text.contains('Оценивать'), F.text.contains('➡️Пропустить')))
async def grade(message: Message, session: AsyncSession, state: FSMContext):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        if profile.wanted_gender == 'Без разницы 👫':
            profile = await orm_get_random_profile(session, message.from_user.id)
        elif profile.wanted_gender == 'Мужской 👨‍🦱':
            profile = await orm_get_random_profile_man(session, message.from_user.id)
        else:
            profile = await orm_get_random_profile_woman(session, message.from_user.id)
        if profile:
            await state.update_data(liked_id=profile.id)
            await state.update_data(all_grades=profile.all_grades)
            await state.update_data(count_grades=profile.count_grades + 1)
            await state.update_data(id=message.from_user.id)
            await message.answer_photo(
                profile.photography,
                caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
*При оценке 7+ этому пользователю будет виден ваш профиль''',
                reply_markup=get_keyboard(
                    '1',
                    '2',
                    '3',
                    '4',
                    '5',
                    '6',
                    '7',
                    '8',
                    '9',
                    '10',
                    '➡️Пропустить',
                    '🔙Главное меню',
                    'Пожаловаться❌',
                    sizes=(5, 5, 3),
                ))
            await state.set_state(AddProfile.grade)
        else:
            await message.answer('''На данный момент анкеты закончились 😢.
Зови своих друзей, а они позовут своих и анкет станет на столько 🙌 много,
что больше это сообщение никто не увидит 🙃''')
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)


@user_assessment_router.message(AddProfile.grade, F.text)
async def next_grade(message: Message, session: AsyncSession, state: FSMContext):
    if message.text == 'Пожаловаться❌':
        await message.answer('🤔 Опишите жалобу текстом или воспользуйтесь кнопками ниже',
                             reply_markup=get_keyboard(
                                 '🔞 контент',
                                 'Реклама📣',
                                 'Мошенничество💳',
                                 sizes=(2, 1)
                             ))
        await state.set_state(AddProfile.report)
    else:
        try:
            s = int(message.text)
            if 0 < s < 11:
                await state.update_data(grade=message.text)
                await state.update_data(user_name=message.from_user.username)
                data = await state.get_data()
                await orm_add_grade(session, data)
                grade_info = await orm_get_grade(session, data['liked_id'])
                await state.update_data(new_count_grades=grade_info.new_count_grades + 1)
                if grade_info.new_count_grades == 1 or grade_info.new_count_grades % 10 == 0:
                    await message.bot.send_message(data['liked_id'], 'Тебя кто-то оценил, давай посмотрим кто это 🙃')
                data = await state.get_data()
                await orm_update_new_count_grade(session, data['liked_id'], data['new_count_grades'])
                await orm_rate_profile(session, data['liked_id'], int(data['grade']) + int(data['all_grades']))
                await orm_count_grades(session, data['liked_id'], int(data['count_grades']))
                await state.clear()
                await grade(message, session, state)
            else:
                await message.answer('❌Принимаются оценки от <b>1</b> до <b>10</b>❌')
        except:
            await message.answer('Нужно ввести оценку от 1 до 10')


@user_assessment_router.message(AddProfile.report, F.text)
async def save_report(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(report=message.text)
    data = await state.get_data()
    await message.answer('Жалоба отправлена на рассмотрение🧐')
    await orm_add_report(session, data)
    await state.clear()
    await grade(message, session, state)


@user_assessment_router.message(F.text.contains('Кто меня оценил'))
async def new_grades(message: Message, session: AsyncSession):
    try:
        new_grade = await orm_get_grade(session, message.from_user.id)
        liked_profile = await orm_get_profile(session, new_grade.id_user)
        await orm_update_new_count_grade(session, new_grade.liked_id, new_grade.new_count_grades - 1)
        await message.answer_photo(
            liked_profile.photography,
            caption=f'''🗒Вас оценил(а):\n
{['👩‍🦳', '👨‍🦱'][liked_profile.gender == 'Мужской']} {
            [liked_profile.name, '@'+new_grade.user_name][new_grade.grade >= 7]
            }
⭐️Оценка: {new_grade.grade}/10
🔞Возраст: {liked_profile.age}
🌆Страна: {liked_profile.country}
🌇Город: {liked_profile.city}
{liked_profile.description}''')
        await orm_delete_grade(session, new_grade.id_user, new_grade.id_all)
    except:
        await message.answer('Тебя пока никто не оценил')


@user_assessment_router.message()
async def help_for_you(message: Message, state: FSMContext, session: AsyncSession):
    profile = await orm_get_profile(session, message.from_user.id)
    if profile and profile.ban != 'block':
        await message.answer('🆘Если возникли вопросы воспользуйся коммандой /help', reply_markup=reply.start_kb)
    elif profile and profile.ban == 'block':
        await message.answer('Вы были заблокированы за нарушение правил👿')
    else:
        await message.answer('<b>Для начала нужно зарегистрироваться</b> 🙂', reply_markup=get_keyboard(
            "Начать регистрацию",
            sizes=(1,),
        ))
        await state.set_state(AddProfile.id)
