import os
import re
from datetime import date
from urllib.parse import quote_plus

import pandas as pd
import httpx
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

'''
streetlamp.csv 데이터를 safety_facilities 테이블에 넣는다.
경로 : data/
파일명 : streetlamp.csv
comment : 가로등 파일에는 좌표가 없기때문에 해당 주소를 kakao map API를 통해 좌표값을 가져온다.

실행 : python -m scripts.load_streetlight
'''

load_dotenv()

# 접속정보
id = os.getenv("DB_ID")
pw = quote_plus(os.getenv("DB_PW"))
host = os.getenv("DB_URL")
port = os.getenv("DB_PORT")
database = os.getenv("DATABASE")

url = f'mysql+pymysql://{id}:{pw}@{host}:{port}/{database}'

engine = create_engine(url)
kakao_key = os.getenv("KAKAO_KEY")
cache = {}

def geocode(addr):
    if addr in cache:
        return cache[addr]
    for q in (addr, re.sub(r"(로|길)(\d)", r"\1 \2", addr)):   # '영신로139-5' → '영신로 139-5'
        res = httpx.get(
            "https://dapi.kakao.com/v2/local/search/address.json",
            params={"query": q},
            headers={"Authorization": f"KakaoAK {kakao_key}"},
        )
        docs = res.json().get("documents", [])
        time.sleep(0.05)
        if docs:
            cache[addr] = (float(docs[0]["y"]), float(docs[0]["x"]))   # y=위도, x=경도
            return cache[addr]
    cache[addr] = (None, None)
    return cache[addr]

df = pd.read_csv("data/streetlamp.csv", encoding="cp949")
df.columns = df.columns.str.strip()

rows, failed = [], []
for i, r in df.iterrows():
    lat, lng = geocode(r["위치"])
    if lat is None:
        failed.append(r["위치"])
        continue
    rows.append({
        "type": "S",
        "address": r["위치"],
        "qty": int(r["조명수량"]),
        "lat": lat,
        "lng": lng,
        "base_date": r["데이터기준일자"],
        "ins_dt": date.today(),
        "ins_nm": "system",
    })
    if (i + 1) % 200 == 0:
        print(f"  {i + 1}건 처리 중...")

sql = text("""
     INSERT INTO safety_facilities (type, address, qty, lat, lng, base_date, ins_dt, ins_nm)
    VALUES (:type, :address, :qty, :lat, :lng, :base_date, :ins_dt, :ins_nm)
""")

with engine.begin() as conn:
    conn.execute(text("DELETE FROM safety_facilities WHERE type = 'S'"))
    conn.execute(sql, rows)

print(f"적재 {len(rows)}건, 좌표 실패 {len(failed)}건")
for a in failed[:10]:
    print("  실패:", a)