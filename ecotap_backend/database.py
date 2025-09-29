import aiosqlite
import os
from datetime import datetime
from config import DBConfig, GameConfig

class Database:
    def __init__(self):
        self.db_path = DBConfig.PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
    async def init_db(self):
        """Создает таблицы в базе данных"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id INTEGER PRIMARY KEY,
                    points INTEGER DEFAULT 0,
                    trees INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    experience INTEGER DEFAULT 0,
                    energy INTEGER DEFAULT 100,
                    last_energy_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_taps INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            await db.commit()
        print("Database initialized successfully")
    
    async def _restore_energy(self, db, user_id):
        """Восстанавливает энергию на основе времени"""
        cursor = await db.execute(
            "SELECT energy, last_energy_update FROM user_progress WHERE user_id = ?", 
            (user_id,)
        )
        result = await cursor.fetchone()
        
        if not result:
            return
            
        current_energy, last_update_str = result
        
        if current_energy >= GameConfig.MAX_ENERGY:
            return
            
        # Парсим время
        try:
            last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00'))
        except:
            last_update = datetime.now()
            
        now = datetime.now()
        time_diff = (now - last_update).total_seconds()
        energy_restored = int(time_diff // GameConfig.ENERGY_RESTORE_TIME)
        
        if energy_restored > 0:
            new_energy = min(current_energy + energy_restored, GameConfig.MAX_ENERGY)
            await db.execute('''
                UPDATE user_progress 
                SET energy = ?, last_energy_update = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_energy, user_id))
    
    async def register_user(self, user_id, username=None, first_name=None, last_name=None):
        """Регистрирует нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if await cursor.fetchone():
                return False
            
            await db.execute('''
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            
            await db.execute('''
                INSERT INTO user_progress (user_id, energy)
                VALUES (?, ?)
            ''', (user_id, GameConfig.MAX_ENERGY))
            
            await db.commit()
            return True
    
    async def get_user_progress(self, user_id):
        """Получает прогресс пользователя с восстановлением энергии"""
        async with aiosqlite.connect(self.db_path) as db:
            await self._restore_energy(db, user_id)
            
            cursor = await db.execute('''
                SELECT points, trees, level, experience, energy, total_taps
                FROM user_progress 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = await cursor.fetchone()
            
            if result:
                return {
                    'points': result[0],
                    'trees': result[1], 
                    'level': result[2],
                    'experience': result[3],
                    'energy': result[4],
                    'total_taps': result[5]
                }
            return None
    
    async def update_taps(self, user_id, taps_count=1):
        """Обновляет прогресс и возвращает новые данные"""
        async with aiosqlite.connect(self.db_path) as db:
            await self._restore_energy(db, user_id)
            
            cursor = await db.execute("SELECT energy FROM user_progress WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            
            if not result or result[0] < taps_count:
                return None  # Недостаточно энергии
            
            points_gained = taps_count * GameConfig.POINTS_PER_TAP
            experience_gained = taps_count
            
            await db.execute('''
                UPDATE user_progress 
                SET points = points + ?, 
                    experience = experience + ?,
                    energy = energy - ?,
                    total_taps = total_taps + ?,
                    last_energy_update = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (points_gained, experience_gained, taps_count, taps_count, user_id))
            
            # Проверяем деревья
            cursor = await db.execute("SELECT points, experience, level FROM user_progress WHERE user_id = ?", (user_id,))
            result = await cursor.fetchone()
            current_points, current_exp, current_level = result
            
            if current_points >= GameConfig.POINTS_PER_TREE:
                new_trees = current_points // GameConfig.POINTS_PER_TREE
                remaining_points = current_points % GameConfig.POINTS_PER_TREE
                
                await db.execute('''
                    UPDATE user_progress 
                    SET trees = trees + ?, points = ?
                    WHERE user_id = ?
                ''', (new_trees, remaining_points, user_id))
            
            # Система уровней (100 XP = уровень)
            new_level = (current_exp // 100) + 1
            if new_level > current_level:
                await db.execute("UPDATE user_progress SET level = ? WHERE user_id = ?", (new_level, user_id))
            
            await db.commit()
            return await self.get_user_progress(user_id)

db = Database()
