import os
import re
import requests
import logging
logger = logging.getLogger(__name__)
ftc_key = "72e6bf8caf7ff5cf174799cd81d6d35550c0101de8f4562d9665f609b18cddd2"

BASE_URL = (
    "https://apis.data.go.kr/1130000/MllBs_2Service/"
)

BUSINESS_NUMBER_URL = BASE_URL + "getMllBsBiznoInfo_2"
BUSINESS_NAME_URL = BASE_URL + "getMllBsCoNmInfo_2"


class FtcApiError(Exception):
    pass


def _request(api_url: str, search_params: dict) -> list:
    #service_key = os.getenv("FTC_SERVICE_KEY")

    service_key = ftc_key
    if not service_key:
        raise FtcApiError("공정위 API 인증키가 설정되지 않았습니다.")

    params = {
        "serviceKey": service_key,
        "pageNo": 1,
        "numOfRows": 10,
        "resultType": "json",
        **search_params,
    }

    try:
        response = requests.get(
            api_url,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        result = response.json()

    except requests.RequestException as e:
        raise FtcApiError(f"공정위 API 요청 실패: {e}") from e

    except ValueError as e:
        raise FtcApiError("공정위 API JSON 파싱 실패") from e

    # API 오류 응답 확인
    if "OpenAPI_ServiceResponse" in result:
        error = result["OpenAPI_ServiceResponse"].get(
            "cmmMsgHeader", {}
        )
        raise FtcApiError(
            error.get("returnAuthMsg")
            or error.get("errMsg")
            or "공정위 API 오류"
        )

    if result.get("resultCode") != "00":
        raise FtcApiError(
            f"공정위 API 오류: {result.get('resultMsg')}"
        )

    logger.warning(
    "FTC total=%s, returned=%s",
    result.get("totalCount"),
    len(result.get("items", [])),
)

    return result.get("items", [])

def get_business_info(business_number: str) -> list:
    business_number = re.sub(r"\D", "", business_number)

    if len(business_number) != 10:
        raise ValueError("사업자등록번호는 10자리여야 합니다.")

    return _request(
        BUSINESS_NUMBER_URL,
        {"brno": business_number},
    )


def get_business_info_by_name(business_name: str) -> list:
    business_name = business_name.strip()

    if not business_name:
        raise ValueError("상호명을 입력해야 합니다.")

    return _request(
        BUSINESS_NAME_URL,
        {"bzmnNm": business_name},
    )