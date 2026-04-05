import os
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    hostname = Column(String, nullable=False)
    ip_address = Column(String)
    device_type = Column(String)

# Получение данных из ENV
user = os.getenv("DB_USER")
pw = os.getenv("DB_PASSWORD")
db = os.getenv("DB_NAME")
host = os.getenv("DB_HOST", "db")

DATABASE_URL = f"postgresql://{user}:{pw}@{host}:5432/{db}"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    retries = 5
    while retries > 0:
        try:
            Base.metadata.create_all(engine)
            print("БАЗА ДАННЫХ: Таблицы успешно созданы/проверены.")
            break
        except OperationalError:
            retries -= 1
            print(f"БАЗА ДАННЫХ: Ожидание готовности Postgres... (осталось попыток: {retries})")
            time.sleep(3) # Ждем 3 секунды перед следующей попыткой
    else:
        print("ОШИБКА: Не удалось подключиться к базе данных после нескольких попыток.")