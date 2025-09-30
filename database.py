import asyncpg
import logging
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None

    async def init_db(self):
        """Initializes the database connection pool and creates tables if they don't exist."""
        try:
            self.pool = await asyncpg.create_pool(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            async with self.pool.acquire() as connection:
                await self._create_tables(connection)
            logger.info("Database connection pool created successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    async def _create_tables(self, connection):
        """Creates the necessary tables in the database."""
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                points BIGINT DEFAULT 0,
                trees INT DEFAULT 0,
                level INT DEFAULT 1,
                energy INT DEFAULT 100,
                total_taps BIGINT DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        logger.info("Table 'users' checked/created.")

    async def close(self):
        """Closes the database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed.")

    async def register_user(self, user_id, username, first_name, last_name):
        """Registers a new user or updates their info if they already exist."""
        query = '''
            INSERT INTO users (user_id, username, first_name, last_name)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (user_id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name;
        '''
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query, user_id, username, first_name, last_name)
            return True
        except Exception as e:
            logger.error(f"Error registering user {user_id}: {e}")
            return False

    async def get_user_progress(self, user_id):
        """Retrieves a user's progress from the database."""
        query = 'SELECT * FROM users WHERE user_id = $1;'
        try:
            async with self.pool.acquire() as connection:
                user_data = await connection.fetchrow(query, user_id)
            return dict(user_data) if user_data else None
        except Exception as e:
            logger.error(f"Error getting progress for user {user_id}: {e}")
            return None

# Create a single instance of the Database class
db = Database()
