from pathlib import Path
import pandas as pd

base_dir = Path(__file__).resolve().parent
file_path1 = base_dir / 'data' / 'cctv.csv'
new_file_path = base_dir / 'data' / 'cctv_utf8.csv'

# 💡 encoding='utf-8' 또는 encoding='utf-8-sig' 로 변경!
df1 = pd.read_csv(file_path1, encoding='utf-8')
df1.to_csv(new_file_path, index=False, encoding='utf-8-sig')
# streetlamp 위치 정보 좌표가 아니라 실제 좌표로 변경 어려움 
print("CCTV CSV 파일 변환 완료!")