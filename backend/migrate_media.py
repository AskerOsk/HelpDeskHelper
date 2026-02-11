import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    """Добавление полей для медиа в таблицу messages"""
    conn = psycopg2.connect(
        user=os.getenv('DB_USER', 'postgres'),
        host=os.getenv('DB_HOST', '127.0.0.1'),
        database=os.getenv('DB_NAME', 'sulpak_helpdesk'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        port=int(os.getenv('DB_PORT', '5432'))
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        print('Проверка и добавление полей для медиа...')

        # Проверяем существует ли колонка media_type
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='messages' AND column_name='media_type';
        """)

        if not cursor.fetchone():
            print('Добавление колонки media_type...')
            cursor.execute('ALTER TABLE messages ADD COLUMN media_type VARCHAR(20);')
            print('✓ Колонка media_type добавлена')
        else:
            print('✓ Колонка media_type уже существует')

        # Проверяем media_url
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='messages' AND column_name='media_url';
        """)

        if not cursor.fetchone():
            print('Добавление колонки media_url...')
            cursor.execute('ALTER TABLE messages ADD COLUMN media_url TEXT;')
            print('✓ Колонка media_url добавлена')
        else:
            print('✓ Колонка media_url уже существует')

        # Проверяем media_file_id
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='messages' AND column_name='media_file_id';
        """)

        if not cursor.fetchone():
            print('Добавление колонки media_file_id...')
            cursor.execute('ALTER TABLE messages ADD COLUMN media_file_id VARCHAR(255);')
            print('✓ Колонка media_file_id добавлена')
        else:
            print('✓ Колонка media_file_id уже существует')

        print('\n✅ Миграция успешно завершена!')
        print('Теперь система поддерживает фото и видео от пользователей.')

        cursor.close()
        conn.close()

    except Exception as e:
        print(f'❌ Ошибка миграции: {e}')
        cursor.close()
        conn.close()
        exit(1)


if __name__ == "__main__":
    print('=== Миграция базы данных для поддержки медиа ===\n')
    migrate_database()

