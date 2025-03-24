import streamlit as st
import pandas as pd
from io import BytesIO
import requests
import json
from bs4 import BeautifulSoup
from IPython.display import HTML


# JSON 파일에서 법정동 코드 가져오기
def get_dong_codes_for_city(city_name, sigungu_name=None, json_path='korea_region_data.json'):
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        st.error(f"Error: The file at {json_path} was not found.")
        return None, None

    for si_do in data:
        if si_do['si_do_name'] == city_name:
            if sigungu_name and sigungu_name != '전체':
                for sigungu in si_do['sigungu']:
                    if sigungu['sigungu_name'] == sigungu_name:
                        return [sigungu['sigungu_code']], [
                            {'code': dong['code'], 'name': dong['name']} for dong in sigungu['eup_myeon_dong']
                        ]
            else:
                sigungu_codes = [sigungu['sigungu_code'] for sigungu in si_do['sigungu']]
                dong_codes = [
                    {'code': dong['code'], 'name': dong['name']}
                    for sigungu in si_do['sigungu']
                    for dong in sigungu['eup_myeon_dong']
                ]
                return sigungu_codes, dong_codes
    return None, None

def get_vl_list(dong_code):
    headers = {
        'accept': '*/*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDI2MzA5NDAsImV4cCI6MTc0MjY0MTc0MH0.6ybkX7eNOQCpZ7yNzbqV-d8KJ-O2RDRcmLeBf3U-fqg',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://new.land.naver.com/houses?a=VL&b=A1&e=RETAIL',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        # 'cookie': 'NNB=4W7YAA5ZVMPWK; ASID=dd94a0410000018e5520a76800000047; NFS=2; tooltipDisplayed=true; recent_card_list=10225,10221,10295,10252,652,10286,1030,10396,10395; _ga=GA1.1.1501423069.1705550738; _ga_8P4PY65YZ2=GS1.1.1728868272.1.1.1728868278.54.0.0; ba.uuid=c40f8e46-1824-4094-b082-f17ac3e3080b; _gcl_au=1.1.1320614230.1735782083; naverfinancial_CID=6739685caf394e2c9ea8c5d6a7bc3d0b; _tt_enable_cookie=1; _ttp=PIEh2r3cy-6ykpYTyaMm4ftWdLy.tt.1; _ga_Q7G1QTKPGB=GS1.1.1735782082.1.1.1735782151.0.0.0; _fwb=237FOAiAL4reeqTMknBjyjg.1737348126266; nhn.realestate.article.trade_type_cd=A1; SHOW_FIN_BADGE=N; NAC=JtXWBggF6pHy; BNB_FINANCE_HOME_TOOLTIP_MYASSET=true; _ga_451MFZ9CFM=GS1.1.1740713655.3.0.1740713661.0.0.0; page_uid=i9zczlqVN8VsslHoLpVssssstlV-258204; nhn.realestate.article.rlet_type_cd=A01; nhn.realestate.article.ipaddress_city=1100000000; NACT=1; landHomeFlashUseYn=Y; realestate.beta.lastclick.cortar=1174000000; _fwb=237FOAiAL4reeqTMknBjyjg.1737348126266; SRT30=1742604741; SRT5=1742630848; BUC=DgLwt41giN4K07MutHMCBhV2Q-5c-t3Gos_jccnmcgo=; REALESTATE=Sat%20Mar%2022%202025%2017%3A09%3A00%20GMT%2B0900%20(Korean%20Standard%20Time)',
    }

    required_columns = ['articleNo', 'articleName', 'articleStatus', 'realEstateTypeCode', 'realEstateTypeName', 'articleRealEstateTypeCode', 'articleRealEstateTypeName', 'tradeTypeCode', 'tradeTypeName', 'verificationTypeCode', 'floorInfo', 'priceChangeState', 'isPriceModification', 'dealOrWarrantPrc', 'area1', 'area2', 'direction', 'articleConfirmYmd', 'representativeImgUrl', 'representativeImgTypeCode', 'representativeImgThumb', 'siteImageCount', 'articleFeatureDesc', 'tagList', 'buildingName', 'sameAddrCnt', 'sameAddrDirectCnt', 'sameAddrMaxPrc', 'sameAddrMinPrc', 'cpid', 'cpName', 'cpPcArticleUrl', 'cpPcArticleBridgeUrl', 'cpPcArticleLinkUseAtArticleTitleYn', 'cpPcArticleLinkUseAtCpNameYn', 'cpMobileArticleUrl', 'cpMobileArticleLinkUseAtArticleTitleYn', 'cpMobileArticleLinkUseAtCpNameYn', 'latitude', 'longitude', 'isLocationShow', 'realtorName', 'realtorId', 'tradeCheckedByOwner', 'isDirectTrade', 'isInterest', 'isComplex', 'detailAddress', 'detailAddressYn', 'virtualAddressYn', 'isVrExposed', 'elevatorCount']

    try:
        r = requests.get(
            f'https://new.land.naver.com/api/articles?cortarNo={dong_code}&realEstateType=VL&tradeType=A1&priceType=RETAIL',
            headers=headers,
        )
        r.encoding = "utf-8-sig"
        data = r.json()
        
        if 'articleList' in data and isinstance(data['articleList'], list):
            df = pd.DataFrame(data['articleList'])

            for col in required_columns:
                if col not in df.columns:
                    df[col] = None

            return df[required_columns]
        else:
            st.warning(f"No data found for {dong_code}.")
            return pd.DataFrame(columns=required_columns)
    except Exception as e:
        st.error(f"Error fetching data for {dong_code}: {e}")
        return pd.DataFrame(columns=required_columns)

# 아파트 코드 리스트 가져오기
def get_apt_list(dong_code):
    down_url = f'https://new.land.naver.com/api/regions/complexes?cortarNo={dong_code}&realEstateType=A1&order='
    referer_url = f"https://new.land.naver.com/complexes/102378?a=APT&b=A1&e=RETAIL"

    header = {
        "Accept-Encoding": "gzip",
        "Host": "new.land.naver.com",
        "Referer": referer_url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    required_columns = ['complexNo', 'complexName', 'buildYear', 'totalHouseholdCount', 'areaSize', 'price', 'address', 'floor']
    try:
        r = requests.get(down_url, headers=header)
        r.encoding = "utf-8-sig"
        data = r.json()

        if 'complexList' in data and isinstance(data['complexList'], list):
            df = pd.DataFrame(data['complexList'])

            for col in required_columns:
                if col not in df.columns:
                    df[col] = None

            return df[required_columns]
        else:
            st.warning(f"No data found for {dong_code}.")
            return pd.DataFrame(columns=required_columns)

    except Exception as e:
        st.error(f"Error fetching data for {dong_code}: {e}")
        return pd.DataFrame(columns=required_columns)


def format_amount(amount):
    if amount >= 1_0000_0000:  # 억 단위 이상
        billions = amount // 1_0000_0000  # 억 단위
        remainder = amount % 1_0000_0000  # 나머지 금액
        if remainder > 0:
            remainder_million = remainder // 10_000  # 만 단위 추출
            return f"{billions}억 {remainder_million:,}만"
        else:
            return f"{billions}억"
    elif amount >= 10_000:  # 만 단위 이상
        return f"{amount // 10_000}만"
    else:  # 만 단위 미만
        return f"{amount:,}원"


def get_vl_details(vl_code):
    headers = {
        'accept': '*/*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3NDI2MzA5NDAsImV4cCI6MTc0MjY0MTc0MH0.6ybkX7eNOQCpZ7yNzbqV-d8KJ-O2RDRcmLeBf3U-fqg',
        'priority': 'u=1, i',
        'referer': f'https://new.land.naver.com/houses?a=VL&e=RETAIL&articleNo={vl_code}',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        # 'cookie': 'NNB=4W7YAA5ZVMPWK; ASID=dd94a0410000018e5520a76800000047; NFS=2; tooltipDisplayed=true; recent_card_list=10225,10221,10295,10252,652,10286,1030,10396,10395; _ga=GA1.1.1501423069.1705550738; _ga_8P4PY65YZ2=GS1.1.1728868272.1.1.1728868278.54.0.0; ba.uuid=c40f8e46-1824-4094-b082-f17ac3e3080b; _gcl_au=1.1.1320614230.1735782083; naverfinancial_CID=6739685caf394e2c9ea8c5d6a7bc3d0b; _tt_enable_cookie=1; _ttp=PIEh2r3cy-6ykpYTyaMm4ftWdLy.tt.1; _ga_Q7G1QTKPGB=GS1.1.1735782082.1.1.1735782151.0.0.0; _fwb=237FOAiAL4reeqTMknBjyjg.1737348126266; nhn.realestate.article.trade_type_cd=A1; SHOW_FIN_BADGE=N; NAC=JtXWBggF6pHy; BNB_FINANCE_HOME_TOOLTIP_MYASSET=true; _ga_451MFZ9CFM=GS1.1.1740713655.3.0.1740713661.0.0.0; page_uid=i9zczlqVN8VsslHoLpVssssstlV-258204; nhn.realestate.article.rlet_type_cd=A01; nhn.realestate.article.ipaddress_city=1100000000; NACT=1; landHomeFlashUseYn=Y; realestate.beta.lastclick.cortar=1174000000; _fwb=237FOAiAL4reeqTMknBjyjg.1737348126266; SRT30=1742604741; REALESTATE=Sat%20Mar%2022%202025%2017%3A09%3A00%20GMT%2B0900%20(Korean%20Standard%20Time); SRT5=1742632297; BUC=mhRD9Z3IIXEGy1XxiChff8bhoV9smvxeWaDDEGE3-fI=',
    }
    
    try:
        details_url = f'https://new.land.naver.com/api/articles/{vl_code}'
        # 기본 정보 가져오기
        r_details = requests.get(details_url, headers=headers)
        r_details.encoding = "utf-8-sig"

        vl_detail = r_details.json().get('articleDetail')
        vl_detail['link'] = f'https://new.land.naver.com/houses?articleNo={vl_code}'
        return vl_detail
        

    except Exception as e:
        st.error(f"Error fetching details for {vl_code}: {e}")
        return []
# 아파트 코드로 상세 정보 가져오기
def get_apt_details(apt_code):
    direction_dict = {
        'WW': '서향',
        'EE': '동향',
        'ES': '남동향',
        'EN': '북동향',
        'NN': '북향',
        'WS': '남서향',
        'SS': '남향',
        'WN': '북서향'
    }
    details_url = f'https://fin.land.naver.com/complexes/{apt_code}?tab=complex-info'
    article_url = f'https://fin.land.naver.com/complexes/{apt_code}?tradeTypes=A1&tab=article'
    front_api_url = 'https://fin.land.naver.com/front-api/v1/complex/article/list?complexNumber={}&userChannelType=PC&page={}'

    header = {
        "Accept-Encoding": "gzip",
        "Host": "fin.land.naver.com",
        "Referer": "https://fin.land.naver.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    try:
        # 기본 정보 가져오기
        r_details = requests.get(details_url, headers=header)
        r_details.encoding = "utf-8-sig"
        soup_details = BeautifulSoup(r_details.content, 'html.parser')
        
        apt_name_tag = soup_details.find('span', class_='ComplexSummary_name__vX3IN')
        apt_name = apt_name_tag.text.strip() if apt_name_tag else 'Unknown'
        detail_dict = {'complexNo': apt_code, 'complexName': apt_name}
        
        detail_items = soup_details.find_all('li', class_='DataList_item__T1hMR')
        for item in detail_items:
            term = item.find('div', class_='DataList_term__Tks7l').text.strip()
            definition = item.find('div', class_='DataList_definition__d9KY1').text.strip()
            if term in ['공급면적', '전용면적', '해당면적 세대수', '현관구조', '방/욕실', '위치', '사용승인일', '세대수', '난방', '주차', '전기차 충전시설', '용적률/건폐율', '관리사무소 전화', '건설사']:
                detail_dict[term] = definition

        # 매물 정보 가져오기
        # r_article = requests.get(article_url, headers=header)
        # r_article.encoding = "utf-8-sig"
        # soup_article = BeautifulSoup(r_article.content, 'html.parser')
        
        listings = []
        # for item in soup_article.find_all('li', class_='ComplexArticleItem_item__L5o7k'):
        #     listing = {}
        #     name_tag = item.find('span', class_='ComplexArticleItem_name__4h3AA')
        #     listing['매물명'] = name_tag.text.strip() if name_tag else 'Unknown'
        #     # article_prefix_url = item.find('a', class_='ComplexArticleItem_link___vfQz').get('href') if item.find('a', class_='ComplexArticleItem_link___vfQz') else None
        #     # print(name_tag.text.strip(), article_prefix_url)
        #     # article_no = article_prefix_url.split('/')[-1] if article_prefix_url else ''
        #     # detail_dict['articleNo'] = article_no

        #     price_tag = item.find('span', class_='ComplexArticleItem_price__DFeIb')
        #     listing['거래방식'] = price_tag.text.strip().split(' ')[0] if price_tag else 'Unknown'
        #     listing['매매가'] = price_tag.text.strip().split(' ')[1] if price_tag else 'Unknown'
            
        #     summary_items = item.find_all('li', class_='ComplexArticleItem_item-summary__oHSwl')
        #     if len(summary_items) >= 4:
        #         listing['면적'] = summary_items[1].text.strip() if len(summary_items) >= 1 else 'Unknown'
        #         listing['층수'] = summary_items[2].text.strip() if len(summary_items) >= 2 else 'Unknown'
        #         listing['방향'] = summary_items[3].text.strip() if len(summary_items) >= 3 else 'Unknown'
            
        #     image_tag = item.find('img')
        #     listing['이미지'] = image_tag['src'] if image_tag else 'No image'
        #     comment_tag = item.find('p', class_='ComplexArticleItem_comment__zN_dK')
        #     listing['코멘트'] = comment_tag.text.strip() if comment_tag else 'No comment'

        # 매물 front-api
        has_next = True
        article_listing = []
        page = 0
        temp_article_listing = {}

        while has_next:
            r_front_article = requests.get(front_api_url.format(apt_code, page), headers=header)
            front_response = front_result = r_front_article.json()
            # print(r_front_article.json().get('result'))
            front_result = front_response.get('result')
            has_next = front_result.get('hasNextPage')
            front_list = front_result.get('list')

            for f_l in front_list:
                article_info = f_l.get('representativeArticleInfo')
                duplicate_article_info = f_l.get('duplicatedArticlesInfo')
                article_name = article_info.get('complexName') + ' ' + article_info.get('dongName')
                exclusive_space_info = str(article_info.get('spaceInfo').get('exclusiveSpace')) + article_info.get('spaceInfo').get('nameType')
                supply_space_info = str(article_info.get('spaceInfo').get('supplySpace')) + article_info.get('spaceInfo').get('nameType')
                
                if article_info.get('tradeType') == 'A1':
                    temp_article_listing['매물명'] = article_name
                    temp_article_listing['거래방식'] = '매매'
                    temp_article_listing['층수'] = article_info.get('articleDetail').get('floorInfo') + '층'
                    temp_article_listing['면적'] = exclusive_space_info + '㎡' + '(' + supply_space_info + ')'
                    temp_article_listing['코멘트'] = article_info.get('articleDetail').get('articleFeatureDescription')
                    direction_info = article_info.get('articleDetail').get('direction')
                    temp_article_listing['방향'] = direction_dict.get(direction_info)

                    if duplicate_article_info:
                        article_info_list = duplicate_article_info.get('articleInfoList')
                        for a_i in article_info_list:
                            price_info = a_i.get('priceInfo').get('dealPrice')
                            article_detail = a_i.get('articleDetail')
                            broker_info = a_i.get('brokerInfo')
                            media_info = a_i.get('articleMediaDto')
                            # print('!!!!!!!! ', article_name, '1!!!!!!!!!!!!!!!!!!!!!', price_info)
                            temp_article_listing['매매가'] = format_amount(price_info)
                            temp_article_listing['매물link'] = 'https://fin.land.naver.com/articles/'+article_detail.get('articleNumber')
                            temp_article_listing['중개업체'] = broker_info.get('brokerageName')
                            temp_article_listing['이미지'] = media_info.get('imageUrl')
                            combined_listing = {**detail_dict, **temp_article_listing}
                            article_listing.append(combined_listing)
                    else:
                        price_info = article_info.get('priceInfo').get('dealPrice')
                        temp_article_listing['매매가'] = format_amount(price_info)
                        temp_article_listing['매물link'] = 'https://fin.land.naver.com/articles/'+article_info.get('articleNumber')
                        temp_article_listing['중개업체'] = article_info.get('brokerageName')
                        temp_article_listing['이미지'] = article_info.get('articleMediaDto').get('imageUrl')
                        combined_listing = {**detail_dict, **temp_article_listing}
                        article_listing.append(combined_listing)

            if has_next:
                page += 1

        # combined_listing = {**detail_dict, **article_listing}

        # listings.append(combined_listing)
        
        return article_listing
    
    except Exception as e:
        st.error(f"Error fetching details for {apt_code}: {e}")
        return []

def make_clickable(row):
    return f'<a href="https://fin.land.naver.com/articles/{row["articleNumber"]}" target="_blank">{row["complexNo"]}</a>'

def wrap_url_with_a_tag(url):
    return f'<a href="{url}">link</a>'

# 아파트 정보를 수집하는 함수(네이버)
def naver_collect_apt_info_for_city(city_name, sigungu_name, dong_name, dong_code, property_type):
    all_apt_data = []
    all_vl_data = []
    # 수집 중 표시를 위한 placeholder
    placeholder = st.empty()

    placeholder.write(f"{dong_name} ({dong_code}) - 수집중입니다.")
    if property_type == 'APT':
        apt_codes = get_apt_list(dong_code)

        if not apt_codes.empty:
            for _, apt_info in apt_codes.iterrows():
                apt_code = apt_info['complexNo']
                apt_name = apt_info['complexName']
                placeholder.write(f"{apt_name} ({apt_code}) - 수집중입니다.")
                listings = get_apt_details(apt_code)
                
                if listings:
                    for listing in listings:
                        listing['dong_code'] = dong_code
                        listing['dong_name'] = dong_name
                        all_apt_data.append(listing)
        else:
            st.warning(f"No apartment codes found for {dong_code}")
    else:
        vl_codes = get_vl_list(dong_code)

        if not vl_codes.empty:
            for _, vl_info in vl_codes.iterrows():
                vl_code = vl_info['articleNo']
                vl_name = vl_info['articleName']

                placeholder.write(f'{vl_name} ({vl_code}) - 수집중입니다.')

                vl_details = get_vl_details(vl_code)

                if vl_details:
                    all_vl_data.append(vl_details)

    # 수집이 완료된 후, 수집 중 메시지를 지우기
    placeholder.empty()

    if all_vl_data:
        required_columns = ['articleNo', 'articleName', 'cortarNo', 'totalDongCount', 'buildingTypeName', 'realestateTypeName', 'tradeTypeName',  'cityName', 'divisionName', 
                            'sectionName', 'walkingTimeToNearSubway', 'grandPlanList', 'detailAddress', 'exposureAddress', 'roomCount', 'bathroomCount', 'moveInTypeName', 'moveInDiscussionPossibleYN',
                            'articleFeatureDescription', 'detailDescription', 'parkingCount', 'parkingPerHouseholdCount', 'parkingPossibleYN', 'floorLayerName', 'lawUsage', 'tagList', 'link']
        final_df = pd.DataFrame(all_vl_data)
        final_df = final_df[required_columns]
        link_col = final_df.pop('link')
        final_df.insert(1, 'link', link_col)
        # 엑셀 파일로 저장
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False)
        output.seek(0)

        st.write("빌라 정보 수집 완료:")
        st.dataframe(
            final_df,
            column_config={
                'link': st.column_config.LinkColumn('link')
            },
            hide_index=True
        )

        # 엑셀 파일 다운로드 버튼
        st.download_button(
            label="Download Excel",
            data=output,
            file_name=f"{city_name}_{sigungu_name}_apartments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # CSV 파일 다운로드 버튼
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{city_name}_{sigungu_name}_apartments.csv",
            mime="text/csv"
        )
    else:
        st.write("No data to save.")

    if all_apt_data:
        final_df = pd.DataFrame(all_apt_data)
        final_df['si_do_name'] = city_name
        final_df['sigungu_name'] = sigungu_name
        final_df['dong_name'] = dong_name if dong_name else '전체'
        final_df.pop('complexName')

        link_col = final_df.pop('매물link')
        final_df.insert(1, '매물link', link_col)
        price_col = final_df.pop('매매가')
        final_df.insert(2, '매매가', price_col)
        complex_col = final_df.pop('매물명')
        final_df.insert(3, '매물명', complex_col)
        broker_col = final_df.pop('중개업체')
        final_df.insert(4, '중개업체', broker_col)

        # 데이터프레임 결과 출력
        st.write("아파트 정보 수집 완료:")
        st.dataframe(
            final_df,
            column_config={
                '매물link': st.column_config.LinkColumn('매물link'),
                '이미지': st.column_config.LinkColumn('이미지')
            },
            hide_index=True
        )

        # 엑셀 파일로 저장
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            final_df.to_excel(writer, index=False)
        output.seek(0)

        # 엑셀 파일 다운로드 버튼
        st.download_button(
            label="Download Excel",
            data=output,
            file_name=f"{city_name}_{sigungu_name}_apartments.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # CSV 파일 다운로드 버튼
        csv = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{city_name}_{sigungu_name}_apartments.csv",
            mime="text/csv"
        )
    else:
        st.write("No data to save.")

headers = {
    'accept': '*/*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE3MzY1ODM4NzksImV4cCI6MTczNjU5NDY3OX0.XV1X7-GSDPmLpxImFrhxRiATwoW1w2eHEuV_FCqRfp8',
    'priority': 'u=1, i',
    'referer': 'https://new.land.naver.com/',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

naver_district_url = 'https://new.land.naver.com/api/regions/list?cortarNo={}'

@st.cache_data
def get_sido_list():
    response = requests.get(naver_district_url.format('0000000000'), headers=headers)
    if response.status_code == 200:
        data = response.json().get('regionList', [])
        sido_dict = {item['cortarName']: item['cortarNo'] for item in data}
        return sido_dict
    else:
        st.error('시/도 데이터를 가져오는데 실패했습니다.')
        return {}

@st.cache_data
def get_sigungu_list(sido_cortar_no):
    url = f'https://new.land.naver.com/api/regions/list?cortarNo={sido_cortar_no}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('regionList', [])
        sigungu_dict = {item["cortarName"]: item["cortarNo"] for item in data}
        return sigungu_dict
    else:
        st.error("군/구 데이터를 가져오는 데 실패했습니다.")
        return {}
    
@st.cache_data
def get_eup_myeon_dong_list(gu_cortar_no):
    url = f'https://new.land.naver.com/api/regions/list?cortarNo={gu_cortar_no}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json().get('regionList', [])
        eup_myeon_dong_dict = {item["cortarName"]: item["cortarNo"] for item in data}
        return eup_myeon_dong_dict
    else:
        st.error("읍/면/동 데이터를 가져오는 데 실패했습니다.")
        return {}


# Streamlit 앱 실행
st.title("아파트 정보 수집기")

# 시/도 선택
sido_dict = get_sido_list()
sido_list = list(sido_dict.keys())

selected_sido = st.selectbox("시/도 선택", ["선택하세요"] + sido_list)

if selected_sido and selected_sido != "선택하세요":
    # 선택된 시/도의 cortarNo 값을 가져옴
    sido_cortar_no = sido_dict[selected_sido]

    # 군/구 리스트 불러오기
    sigungu_dict = get_sigungu_list(sido_cortar_no)
    sigungu_list = list(sigungu_dict.keys())

    selected_sigungu = st.selectbox("군/구 선택", ["선택하세요"] + sigungu_list)

    if selected_sigungu and selected_sigungu != "선택하세요":
        sigungu_cortar_no = sigungu_dict[selected_sigungu]
        eup_myeon_dong_dict = get_eup_myeon_dong_list(sigungu_cortar_no)
        eup_myeon_dong_list = list(eup_myeon_dong_dict.keys())

        selected_eup_myeon_dong = st.selectbox("읍/면/동 선택", ["선택하세요"] + eup_myeon_dong_list)

        if selected_eup_myeon_dong and selected_eup_myeon_dong != "선택하세요":
            property_type = st.radio("매물 종류 선택", ["APT", "VL"], index=0)

            st.success(f"선택한 지역: {selected_sido} > {selected_sigungu} > {selected_eup_myeon_dong}")
            st.write(f"선택한 매물 유형: {property_type}")

            if st.button("정보 수집 시작"):
                naver_collect_apt_info_for_city(selected_sido, selected_sigungu, selected_eup_myeon_dong, eup_myeon_dong_dict[selected_eup_myeon_dong], property_type)