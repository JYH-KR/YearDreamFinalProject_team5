import os
from datetime import date
from urllib.parse import quote_plus

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text, create_engine

'''
cctv.csv 데이터를 safety_facilities 테이블에 넣는다.
경로 : data/
파일명 : cctv.csv
comment : cctv 파일에는 좌표가 있기 때문에 주소로 좌표 변경하는 작업 없이 바로 넣는다.
          비슷한 위치의 cctv는 중복이 아닌 수량을 묶어서 데이터에 넣는다.
          
실행 : python -m scripts.load_cctv
'''

# 접속정보
id = os.getenv("DB_ID")
pw = quote_plus(os.getenv("DB_PW"))
host = os.getenv("DB_URL")
port = os.getenv("DB_PORT")
database = os.getenv("DATABASE")

url = f'mysql+pymysql://{id}:{pw}@{host}:{port}/{database}'

load_dotenv()
engine = create_engine(url)

df = pd.read_csv("data/cctv.csv", encoding="cp949")
df.columns = df.columns.str.strip() # 컬럼의 공백 제거
df = df[df["시군구명"] == "영등포구"]
df = df.rename(columns={"X좌표(WSG)" : "lat", "Y좌표(WSG)":"lng"})
df = df.dropna(subset=["lat", "lng"]) # 좌표가 없는 데이터는 삭제 한다.

before = len(df)

# 위도 경도가 같은 데는 그룹화 하여 수량으로 체크
# 주소의 경우 첫번재 값을 대표주소로 사용.
# 수량은 모두 더함.
# 데이터 기준일자는 제일 최신날짜로 적용.
df = (
        df.groupby(["lat", "lng"], as_index=False)
        .agg(address=("안심주소", "first"),
             qty=("수량", "sum"),
             base_date=("데이터기준일자", "max")
             )
      )

rows = [{
    "type": "C",
    "address": r["address"],
    "qty": int(r["qty"]),
    "lat": float(r["lat"]),
    "lng": float(r["lng"]),
    "base_date": r["base_date"],
    "ins_dt": date.today(),
    "ins_nm": "system",
} for _, r in df.iterrows()]

sql = text("""
    INSERT INTO safety_facilities (type, address, lat, lng, base_date, ins_dt, ins_nm)
    VALUES (:type, :address, :lat, :lng, :base_date, :ins_dt, :ins_nm)
""")

with engine.begin() as conn:
    conn.execute(text("DELETE FROM safety_facilities WHERE type = 'C'"))
    conn.execute(sql, rows)

print(f"원본 {before}줄 → 중복 제거 후 {len(rows)}곳 적재")
