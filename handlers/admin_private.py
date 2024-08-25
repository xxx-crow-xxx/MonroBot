from aiogram.types import Message
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_querry import orm_get_profile, orm_delete_report, orm_check_report, orm_ban
from filters.chat_types import ChatTypeFilter, IsAdmin
from handlers.user_private import AddProfile
from keyboards.reply import get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_keyboard(
    "Заблокировать пользователя❌",
    "Разблокировать пользователя✅",
    'Просмотреть жалобу🧐',
    placeholder="Выберите действие",
    sizes=(2, 1),
)


@admin_router.message(Command("admin"))
async def what_do_you_do(message: Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@admin_router.message(F.text.contains('Просмотреть жалобу🧐'))
async def check_report(message: Message, session: AsyncSession, state: FSMContext):
    try:
        report = await orm_check_report(session)
        profile = await orm_get_profile(session, report.report_id)
        await state.update_data(id=profile.id)
        await message.answer_photo(
                profile.photography,
                caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
{profile.id}
❌Жалоба: {report.report}''',
                reply_markup=get_keyboard(
                    'Заблокировать пользователя❌',
                    'Тут всё в порядке👍',
                    sizes=(1, 1)
                ))
        await orm_delete_report(session, report.id, report.report_id)
        await state.set_state(AddProfile.confirmation_report)
    except:
        await message.answer('На данный момент жалоб нет🧐')


@admin_router.message(AddProfile.confirmation_report, F.text)
async def confirmation_report(message: Message, session: AsyncSession, state: FSMContext):
    if message.text == 'Заблокировать пользователя❌' or message.text == 'Тут всё в порядке👍':
        if message.text == 'Заблокировать пользователя❌':
            data = await state.get_data()
            await orm_ban(session, data['id'], 'block')
            await message.answer('Пользователь успешно заблокирован✅')
            await state.clear()
            await what_do_you_do(message)
        else:
            await state.clear()
            await what_do_you_do(message)
    elif message.text == "Разблокировать пользователя✅":
        data = await state.get_data()
        await orm_ban(session, data['id'], 'lock')
        await message.answer('Пользователь успешно раблокирован✅')
        await state.clear()
        await what_do_you_do(message)
    else:
        await message.answer('Воспользуйтесь кнопками ниже')


@admin_router.message(F.text.contains("Заблокировать пользователя"))
async def ban(message: Message, state: FSMContext):
    await message.answer("Введите id пользователя которого вы хотите заблокировать")
    await state.update_data(ban='block')
    await state.set_state(AddProfile.id_ban)


@admin_router.message(F.text.contains("Разблокировать пользователя"))
async def lock_user(message: Message, state: FSMContext):
    await message.answer("Введите id пользователя которого вы хотите разблокировать")
    await state.update_data(ban='lock')
    await state.set_state(AddProfile.id_ban)


@admin_router.message(AddProfile.id_ban, F.text)
async def ban_account(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(id=message.text)
    data = await state.get_data()
    profile = await orm_get_profile(session, data['id'])
    if profile:
        await message.answer_photo(
            profile.photography,
            caption=f'''⭐️Имя: <strong>{profile.name}, {profile.age}</strong> лет\n
👫Пол: <strong>{profile.gender}</strong>
🌆Страна: <strong>{profile.country}</strong> 
🌇Город: <strong>{profile.city}</strong>
{profile.description}
Средняя оценка: <strong>{
            round(profile.all_grades / profile.count_grades, 2) if profile.count_grades != 0 else 0
            }</strong>
Количество оценок: <strong>{profile.count_grades}</strong>''',
            reply_markup=get_keyboard(
                'Заблокировать пользователя❌',
                "Разблокировать пользователя✅",
                'Тут всё в порядке👍',
                sizes=(2, 1),
            ))
        await state.set_state(AddProfile.confirmation_report)
    else:
        await message.answer('Пользователя с таким ID не найдено')
        await state.clear()
        await what_do_you_do(message)

