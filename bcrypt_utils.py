import datetime
import secrets

import jwt

#JWT
#비밀키, 알고리즘 종류, 유지시간
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
TOKEN_EXPIRE_MIN = 60 # 토큰 유지시간 변경이 필요할 경우 사용.

def get_token(data:dict[str,Any]) -> str:
    # 토큰 시간 설정(1시간으로 설정 함.)
    expire_time = datetime.datetime.now() + datetime.timedelta(minutes=TOKEN_EXPIRE_MIN)
    data.update({'exp':expire_time})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


