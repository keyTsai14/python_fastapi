from sqlalchemy.exc import InternalError, OperationalError
from sqlalchemy import create_engine, text

from api.models.task import Base
from api.db import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

"""
DBマイグレーション用のスクリプトを作成  
"""

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?charset=utf8"
DEMO_DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/demo?charset=utf8"

engine = create_engine(DEMO_DB_URL, echo=True)


def database_exists():
    # 接続を試みることでdemoデータベースが存在を確認
    try:
        engine.connect()
        return True
    except (InternalError, OperationalError) as e:
        print(e)
        print("Database does not exist.")
        return False


def create_database():
    if not database_exists():
        root = create_engine(DB_URL, echo=True)
        with root.connect() as conn:
            conn.execute(text("CREATE DATABASE demo"))
        print("Database created.")
    Base.metadata.create_all(bind=engine)
    print("Table created.")


if __name__ == '__main__':
    create_database()
