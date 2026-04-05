import os
from sqlalchemy import create_engine, text

def test_db_connection():
    user = os.getenv("DB_USER")
    pw = os.getenv("DB_PASSWORD")
    db = os.getenv("DB_NAME")
    host = os.getenv("DB_HOST", "localhost")
    
    DATABASE_URL = f"postgresql://{user}:{pw}@{host}:5432/{db}"
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Простейший запрос к БД
            result = conn.execute(text("SELECT 1"))
            assert result.fetchone()[0] == 1
            print("✅ Тест пройден: База данных отвечает!")
    except Exception as e:
        print(f"❌ Тест провален: {e}")
        exit(1)

if __name__ == "__main__":
    test_db_connection()