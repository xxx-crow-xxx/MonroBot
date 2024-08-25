from sqlalchemy import delete, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Profile, NewGrade, Report


async def orm_add_report(session: AsyncSession, data: dict):
    obj = (Report(
        id=data['id'],
        report_id=data['liked_id'],
        report=data['report']
    ))
    session.add(obj)
    await session.commit()


async def orm_check_report(session: AsyncSession):
    query = select(Report).order_by(func.random()).limit(1)
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_report(session: AsyncSession, profile_id: str, report_id: str):
    query = delete(Report).where(Report.id == profile_id).where(Report.report_id == report_id)
    await session.execute(query)
    await session.commit()


async def orm_get_top(session: AsyncSession):
    query = select(Profile).order_by(Profile.count_grades.desc()).limit(3)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_add_grade(session: AsyncSession, data: dict):
    obj = (NewGrade(
        id_user=data['id'],
        liked_id=data['liked_id'],
        grade=data['grade'],
        user_name=data['user_name']
    ))
    session.add(obj)
    await session.commit()


async def orm_update_new_count_grade(session: AsyncSession, profile_id: str, new_count_grades: str):
    query = update(NewGrade).values(new_count_grades=new_count_grades).where(
        NewGrade.liked_id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_get_grade(session: AsyncSession, profile_id: int):
    query = select(NewGrade).join(Profile, NewGrade.liked_id == Profile.id).where(Profile.id == profile_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_delete_grade(session: AsyncSession, profile_id: int, id_all):
    query = delete(NewGrade).where(NewGrade.id_user == profile_id).where(NewGrade.id_all == id_all)
    await session.execute(query)
    await session.commit()


async def orm_add_profile(session: AsyncSession, data: dict):
    obj = (Profile(
        id=data['id'],
        name=data['name'],
        gender=data['gender'],
        age=data['age'],
        country=data['country'],
        city=data['city'],
        photography=data['photography']
    ))
    session.add(obj)
    await session.commit()


async def orm_delete_profile(session: AsyncSession, profile_id: str):
    query = delete(Profile).where(Profile.id == profile_id)
    await session.execute(query)
    await session.commit()


async def orm_get_random_profile(session: AsyncSession, profile_id: int):
    query = select(Profile).order_by(func.random()).limit(1).where(Profile.id != str(profile_id)).where(
        Profile.ban == 'lock')
    result = await session.execute(query)
    return result.scalar()


async def orm_get_random_profile_man(session: AsyncSession, profile_id: int):
    query = select(Profile).order_by(func.random()).limit(1).where(Profile.id != str(profile_id)).where(
        Profile.gender == 'Мужской').where(Profile.ban == 'lock')
    result = await session.execute(query)
    return result.scalar()


async def orm_get_random_profile_woman(session: AsyncSession, profile_id: int):
    query = select(Profile).order_by(func.random()).limit(1).where(Profile.id != str(profile_id)).where(
        Profile.gender == 'Женский').where(Profile.ban == 'lock')
    result = await session.execute(query)
    return result.scalar()


async def orm_get_profiles(session: AsyncSession):
    query = select(Profile)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_profile(session: AsyncSession, profile_id: int):
    query = select(Profile).where(Profile.id == str(profile_id))
    result = await session.execute(query)
    return result.scalar()


async def orm_rate_profile(session: AsyncSession, profile_id: str, new_grade: int):
    query = update(Profile).values(all_grades=new_grade).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_count_grades(session: AsyncSession, profile_id: str, new_count_grades: int):
    query = update(Profile).values(count_grades=new_count_grades).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_age(session: AsyncSession, profile_id: int, new_age: str):
    query = update(Profile).values(age=new_age).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_gender(session: AsyncSession, profile_id: int, new_gender: str):
    query = update(Profile).values(gender=new_gender).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_country(session: AsyncSession, profile_id: int, new_country: str):
    query = update(Profile).values(country=new_country).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_city(session: AsyncSession, profile_id: int, new_city: str):
    query = update(Profile).values(city=new_city).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_name(session: AsyncSession, profile_id: int, new_name: str):
    query = update(Profile).values(name=new_name).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_photo(session: AsyncSession, profile_id: int, new_photo: str):
    query = update(Profile).values(photography=new_photo).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_description(session: AsyncSession, profile_id: int, new_description: str):
    query = update(Profile).values(description=new_description).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_update_filter_wanted_gender(session: AsyncSession, profile_id: int, wanted_gender: str):
    query = update(Profile).values(wanted_gender=wanted_gender).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()


async def orm_ban(session: AsyncSession, profile_id: str, ban: str):
    query = update(Profile).values(ban=ban).where(Profile.id == str(profile_id))
    await session.execute(query)
    await session.commit()
