import os
import re
import requests
# $env:NTS_SERVICE_KEY = "발급받은 인증키" 
# docker run --rm -it `
#   -p 8000:8000 `
#   -e NTS_SERVICE_KEY="$env:NTS_SERVICE_KEY" `

nts_api = "72e6bf8caf7ff5cf174799cd81d6d35550c0101de8f4562d9665f609b18cddd2"
API_URL = (
    "https://api.odcloud.kr/api/nts-businessman/v1/status"
)


class NtsApiError(Exception):
    pass


def get_business_status(business_number: str) -> dict:
    # 사업자등록번호에서 하이픈 제거
    business_number = re.sub(r"\D", "", business_number)

    if len(business_number) != 10:
        raise ValueError("사업자등록번호는 10자리여야 합니다.")

    #service_key = os.environ.get("NTS_SERVICE_KEY") # $env:NTS_SERVICE_KEY = "발급받은 인증키" 
    service_key = nts_api
    if not service_key:
        raise NtsApiError("국세청 API 인증키가 설정되지 않았습니다.")

    payload = {
        "b_no": [business_number]
    }

    try:
        # print("[NTS] 함수 진입", flush=True)
        # print("[NTS] 사업자번호:", business_number, flush=True)
        # print("[NTS] 인증키 존재:", bool(service_key), flush=True)
        # print("[NTS] API 요청 시작", flush=True)
        response = requests.post(
            API_URL,
            params={"serviceKey": service_key},
            json=payload,
            timeout=10
        )
        # print("[NTS] 요청 완료", flush=True)
        # #print("[NTS] 소요 시간:", time.time() - start, flush=True)
        # print("[NTS] HTTP STATUS:", response.status_code, flush=True)
        # print("[NTS] RESPONSE:", response.text, flush=True)
        # print("RAW:", response.content[:500])
        # print("TEXT:", response.text[:500])
        # print("JSON:", response.json())


        response.raise_for_status()
        result = response.json()
        # print("NTS RESULT:", result)

    except requests.RequestException as e:
        raise NtsApiError(f"국세청 API 요청 실패: {e}") from e

    except ValueError as e:
        raise NtsApiError("국세청 API 응답 JSON 파싱 실패") from e

    data = result.get("data", [])

    if not data:
        raise NtsApiError("국세청 API 응답에 조회 데이터가 없습니다.")

    return data[0]