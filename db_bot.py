from dotenv import load_dotenv
import os
import asyncpg
from schemas import (
    GET_USER_QUERY,
    UPDATE_SCORE_QUERY,
    CREATE_USER_QUERY
)

load_dotenv()

db_url = os.getenv('DATABASE_URL')
db_pool = None

async def create_db_pool(): 
    global db_pool
    db_pool = await asyncpg.create_pool(db_url)
    print('Database connected successfully!!!!')

MILESTONES = {
    "Human":(0, 99),
    "Guardian":(100, 199),
    "Saiyan":(200, 299),
    "Demon":(300, 399),
    "Kai":(400, 499),
    "Destroyer":(500, 599),
    "Angel":(600, float("inf"))
}
# ---------------------------|Helper functions to interract with the db|------------------------------
async def get_user(user_id):
    user_id=str(user_id)
    async with db_pool.acquire() as conn:
        return await conn.fetchrow(GET_USER_QUERY, user_id)

async def create_user(user_id, score=0, role="Human"):
    user_id=str(user_id)
    async with db_pool.acquire() as conn:
        return await conn.execute(CREATE_USER_QUERY, user_id, score, role)
    
async def update_user(user_id, score, role):
    user_id=str(user_id)
    async with db_pool.acquire() as conn:
        return await conn.execute(UPDATE_SCORE_QUERY, score, role, user_id)

def get_role_from_points(score:float) -> str:
    for role, (min_score, max_score) in MILESTONES.items():
        if min_score <=score <= max_score:
            return role
    return "Human"    
# ---------------------------|Functions the can be used on the bot|------------------------------
async def add_points(user_id, points_to_add):
    user_id=str(user_id)
    user = await get_user(user_id)
    
    if not user:
        return await create_user(user_id, score=points_to_add) # The database already have default value for role=Human
    
    new_score=user['score'] + points_to_add
    new_role = get_role_from_points(new_score)
    
    await update_user(user['id'], new_score, new_role)
    
    return new_score, new_role
