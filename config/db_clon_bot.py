from aiogram.types.input_file import FSInputFile
from datetime import datetime, date
from local_db_ import DB_CONFIG
from decimal import Decimal
from psycopg2 import sql
from aiogram import Bot
import psycopg2
import environ
import asyncio
import json
import os
env = environ.Env()
env.read_env()

CHAT_ID = env.int('CHAT_ID')
BOT_TOKEN = env.str('BOT_TOKEN')

def serialize_value(value):
    """
    JSON serializatsiyasini qo'llab-quvvatlash uchun qiymatni string yoki float formatiga o'zgartirish.
    """
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d %H:%M:%S')  # Datetime formatini stringga aylantirish
    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')  # Date formatini stringga aylantirish
    if isinstance(value, Decimal):
        return float(value)  # Decimal obyektini float formatiga aylantirish
    return value

async def fetch_table_data(table_name, cursor):
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
    rows = cursor.fetchall()  # Jadvaldagi barcha qatorlar
    columns = [desc[0] for desc in cursor.description]  # Ustun nomlari
    serialized_rows = [
        [serialize_value(value) for value in row] for row in rows
    ]
    return {table_name: {"columns": columns, "rows": serialized_rows}}


async def send_file():
    bot = Bot(token=BOT_TOKEN)

    today = datetime.now().strftime("%Y-%m-%d")
    
    # Ma'lumotlar bazasi ulanishi va kursori


    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Jadval nomlarini olish
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()

        # Asinxron ma'lumotlarni olish
        tasks = []
        for table in tables:
            table_name = table[0]
            tasks.append(fetch_table_data(table_name, cursor))

        # Barcha jadvallardan ma'lumotlarni olish
        results = await asyncio.gather(*tasks)

        # Har bir jadvalni alohida faylda saqlash
        for result in results:
            for table_name, table_data in result.items():
                file_path = f"/tmp/{table_name}_backup_{today}.json"  # Har bir jadval uchun fayl nomi
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(table_data, file, indent=4, ensure_ascii=False)
                
                # Faylni yuborish
                document = FSInputFile(file_path)
                await bot.send_document(chat_id=CHAT_ID, document=document)

    except Exception as e:
        print(f"Xato yuz berdi: {e}")
    finally:
        if conn:
            conn.close()  # Ulanishni yopish

        # Zaxira fayllarini o'chirish
        for result in results:
            for table_name, _ in result.items():
                file_path = f"/tmp/{table_name}_backup_{today}.json"
                if os.path.exists(file_path):
                    os.remove(file_path)

asyncio.run(send_file())




# DB_CONFIG = {
#     "dbname": "myproject",
#     "user": "myprojectuser",
#     "password": "password",
#     "host": "localhost",
#     "port": "5432",
# }

# # JSON faylini deserializatsiya qilish
# def deserialize_value(value, value_type):
#     """
#     JSONdan o'qilgan qiymatni kerakli formatga deserializatsiya qilish.
#     """
#     if value_type == 'datetime':
#         return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
#     if value_type == 'date':
#         return datetime.strptime(value, '%Y-%m-%d').date()
#     if value_type == 'decimal':
#         return Decimal(value)
#     return value

# async def load_json_data(file_path, cursor):
#     # JSON faylini o'qish
#     with open(file_path, "r", encoding="utf-8") as file:
#         data = json.load(file)

#     for table_name, table_data in data.items():
#         columns = table_data["columns"]
#         rows = table_data["rows"]

#         # Ustun nomlarini va ma'lumotlarni formatlash
#         for row in rows:
#             # Har bir qiymatni kerakli turga aylantirish (masalan: datetime, date, decimal)
#             for i, value in enumerate(row):
#                 if isinstance(value, str):
#                     if ' ' in value and ':' in value:  # Datetime formatini tekshirish
#                         row[i] = deserialize_value(value, 'datetime')
#                     elif '-' in value:  # Date formatini tekshirish
#                         row[i] = deserialize_value(value, 'date')
#                     elif value.replace('.', '', 1).isdigit():  # Decimal formatini tekshirish
#                         row[i] = deserialize_value(value, 'decimal')

#         # PostgreSQL ga kiritish
#         placeholders = ', '.join(['%s'] * len(columns))  # %s uchun joy saqlash
#         insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
#             sql.Identifier(table_name),
#             sql.SQL(', ').join(map(sql.Identifier, columns)),
#             sql.SQL(placeholders)
#         )

#         # Qatorlarni kiritish
#         for row in rows:
#             cursor.execute(insert_query, row)
            
#         print(f"{table_name} jadvali yuklandi.")

# async def upload_json_to_postgresql():
#     bot = Bot(token=BOT_TOKEN)
#     today = datetime.now().strftime("%Y-%m-%d")

#     try:
#         conn = psycopg2.connect(**DB_CONFIG)
#         cursor = conn.cursor()

#         # JSON fayllarini topish
#         json_files = [f for f in os.listdir("/tmp") if f.endswith(f"backup_{today}.json")]
#         if not json_files:
#             print(f"Bugungi fayllar topilmadi: {today}")
#             return

#         # Har bir faylni yuklash
#         for file_path in json_files:
#             await load_json_data(f"/tmp/{file_path}", cursor)
#             print(f"{file_path} fayli yuklandi.")

#         conn.commit()  # O'zgarishlarni ma'lumotlar bazasiga saqlash

#     except Exception as e:
#         print(f"Xato yuz berdi: {e}")
#     finally:
#         if conn:
#             conn.close()  # Ulanishni yopish

# asyncio.run(upload_json_to_postgresql())