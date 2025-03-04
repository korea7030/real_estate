import PublicDataReader as pdr
import pandas as pd
import json

# 공공데이터 API 설정
service_key = 'WTYVEWrqH1fJhKBvkhv23qngA0cPgTV6vM4JijusQLrDNgBVdtyg3GJyxDtu085xaAliU0/jui5z2VFRU+2zXQ=='  # 여기에 API 키를 입력하세요.
api = pdr.TransactionPrice(service_key)

# 시도, 시군구, 읍면동 코드 가져오기
df = pdr.code_bdong()

# 데이터 확인
print(df.head())

# JSON 구조로 변환
def build_region_hierarchy(df):
    result = []

    # 시도 기준 그룹화
    sido_grouped = df.groupby(['시도코드', '시도명'])
    for (sido_code, sido_name), sido_df in sido_grouped:
        sigungu_list = []

        # 시군구 기준 그룹화
        sigungu_grouped = sido_df.groupby(['시군구코드', '시군구명'])
        for (sigungu_code, sigungu_name), sigungu_df in sigungu_grouped:
            eup_myeon_dong_list = []

            # 읍면동 추가
            for _, row in sigungu_df.iterrows():
                eup_myeon_dong_list.append({
                    "code": row['법정동코드'],
                    "name": row['읍면동명']
                })

            sigungu_list.append({
                "sigungu_code": sigungu_code,
                "sigungu_name": sigungu_name,
                "eup_myeon_dong": eup_myeon_dong_list
            })

        result.append({
            "si_do_code": sido_code,
            "si_do_name": sido_name,
            "sigungu": sigungu_list
        })

    return result

# JSON 생성
region_json = build_region_hierarchy(df)

# JSON 파일로 저장
with open('korea_region_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(region_json, json_file, ensure_ascii=False, indent=4)

print("JSON 파일이 생성되었습니다.")


