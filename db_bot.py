from dotenv import load_dotenv
import os
import asyncpg

load_dotenv()

db_url = os.getenv('DATABASE_URL')
db_pool = None

async def create_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(db_url)
    print('Database connected successfully!!!!')
