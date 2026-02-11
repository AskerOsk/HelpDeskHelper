import psycopg2
from psycopg2 import sql


def create_database():
    """Создание базы данных"""
    # Подключаемся к базе postgres для создания новой базы
    conn = psycopg2.connect(
        user='postgres',
        host='127.0.0.1',
        database='postgres',
        password='postgres',
        port=5432
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Проверяем, существует ли база данных
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = 'sulpak_helpdesk'"
        )

        if cursor.fetchone():
            print('✓ База данных sulpak_helpdesk уже существует')
        else:
            # Создаём базу данных
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier('sulpak_helpdesk')
            ))
            print('✓ База данных sulpak_helpdesk успешно создана')

        cursor.close()
        conn.close()
        print('\nТеперь можно запускать сервер: python server.py')

    except Exception as e:
        print(f'Ошибка: {e}')
        cursor.close()
        conn.close()
        exit(1)


if __name__ == "__main__":
    create_database()

