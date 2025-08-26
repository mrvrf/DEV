import aiosqlite
from datetime import datetime

DATABASE_PLAYERS = 'players.db'
DATABASE_GVG = 'gvg.db'

async def initialize_db():
    async with aiosqlite.connect(DATABASE_PLAYERS) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS players (
                UserID TEXT PRIMARY KEY,
                Name TEXT NOT NULL,
                DisplayName TEXT NOT NULL
            )
        ''')
        await db.commit()

    async with aiosqlite.connect(DATABASE_GVG) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS gvg (
                UserID TEXT PRIMARY KEY
            )
        ''')
        await db.commit()

async def upsert_player(user_id: str, name: str, display_name: str):
    async with aiosqlite.connect(DATABASE_PLAYERS) as db:
        await db.execute('''
            INSERT INTO players (UserID, Name, DisplayName)
            VALUES (?, ?, ?)
            ON CONFLICT(UserID) DO UPDATE SET
                Name=excluded.Name,
                DisplayName=excluded.DisplayName
        ''', (user_id, name, display_name))
        await db.commit()

async def update_gvg_presence(role_members, voice_channel_members, column_name: str):
    async with aiosqlite.connect(DATABASE_GVG) as db:
        async with db.execute("PRAGMA table_info(gvg)") as cursor:
            columns = [column[1] for column in await cursor.fetchall()]
            if column_name not in columns:
                print(f"Adding column: {column_name}")
                await db.execute(f'ALTER TABLE gvg ADD COLUMN "{column_name}" TEXT')
        
        for member in role_members:
            presence = "SIM" if member in voice_channel_members else "NAO"
            try:
                print(f"Updating presence for {member.id}: {presence}")
                await db.execute(f'''
                    INSERT INTO gvg (UserID, "{column_name}")
                    VALUES (?, ?)
                    ON CONFLICT(UserID) DO UPDATE SET
                        "{column_name}"=excluded."{column_name}"
                ''', (str(member.id), presence))
            except Exception as e:
                print(f"Error inserting/updating presence: {e}")
        await db.commit()

async def update_user_response(user_id: str, column_name: str, response: str):
    async with aiosqlite.connect(DATABASE_GVG) as db:
        try:
            await db.execute(f'''
                UPDATE gvg
                SET "{column_name}" = ?
                WHERE UserID = ?
            ''', (response, user_id))
        except Exception as e:
            print(f"Error updating user response: {e}")
        await db.commit()

async def get_user_profile(user_id: str):
    async with aiosqlite.connect(DATABASE_GVG) as db:
        async with db.execute('''
            SELECT * FROM gvg WHERE UserID = ?
        ''', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                columns = [description[0] for description in cursor.description]
                profile = dict(zip(columns, row))
                return profile
            return None