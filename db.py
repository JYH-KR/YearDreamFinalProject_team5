import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv() #.env 파일 내용을 불러옴

# 접속정보
id = os.getenv("DB_ID")
pw = quote_plus(os.getenv("DB_PW"))
host = os.getenv("DB_URL")
port = os.getenv("DB_PORT")
database = os.getenv("DATABASE")

url = f'mysql+pymysql://{id}:{pw}@{host}:{port}/{database}'

# 엔진 생성
engine = create_engine(url=url, echo=True)

# 세션 준비
session = sessionmaker(bind=engine)

# 세션을 사용자에게 전달
def get_conn():
    return session()
