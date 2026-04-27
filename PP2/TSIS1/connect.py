import psycopg2
from config import DB_CONFIG
 
 
def get_connection():
    """Возвращает новое соединение с PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)
 
 
def init_db():
    """
    Создаёт таблицы и процедуры, если они ещё не существуют.
    Читает schema.sql и procedures.sql и выполняет их.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                for sql_file in ("schema.sql", "procedures.sql"):
                    try:
                        with open(sql_file, "r", encoding="utf-8") as f:
                            cur.execute(f.read())
                        print(f"[OK] {sql_file} выполнен.")
                    except FileNotFoundError:
                        print(f"[WARN] {sql_file} не найден, пропускаем.")
    finally:
        conn.close()
 