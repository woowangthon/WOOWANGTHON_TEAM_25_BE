# external_api/ftc/services.py

import re
import unicodedata

import logging
logger = logging.getLogger(__name__)


from .client import (
    get_business_info,
    get_business_info_by_name,
)


def normalize_name(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"[\s,]", "", value)

    value = value.replace("(주)", "")
    value = value.replace("㈜", "")
    value = value.replace("주식회사", "")

    return value.lower()

def normalize_person_name(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = value.strip()

    # CHANGSEUNGHWAN(장승환) -> 장승환
    korean_name = re.search(r"\(([가-힣]+)\)", value)
    if korean_name:
        value = korean_name.group(1)

    # 공백 제거 및 소문자 변환
    value = re.sub(r"\s+", "", value)

    return value.lower()


def normalize_number(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"\D", "", value)


def normalize_address(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"[,.·]", "", value)

    return value.lower()

def normalize_search_name(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = value.strip()

    # 법인 표기 통일
    value = re.sub(r"^\(주\)", "주식회사", value)
    value = re.sub(r"^㈜", "주식회사", value)

    # 검색어의 공백 제거
    value = re.sub(r"\s+", "", value)

    return value

def extract_region(value):
    """
    시도 + 시군구 추출
    """
    if not value:
        return []

    parts = normalize_address(value).split()

    return parts[:2] if len(parts) >= 2 else parts

def compare_name(input_name, official_name):
    if not input_name or not official_name:
        return "UNKNOWN"

    return (
        "MATCH"
        if normalize_name(input_name) == normalize_name(official_name)
        else "MISMATCH"
    )


def compare_number(input_number, official_number):
    if not input_number or not official_number:
        return "UNKNOWN"

    input_number = normalize_number(input_number)
    official_number = normalize_number(official_number)

    if not input_number or not official_number:
        return "UNKNOWN"

    return (
        "MATCH"
        if input_number == official_number
        else "MISMATCH"
    )

def compare_representative(input_name, official_names):
    if not input_name or not official_names:
        return "UNKNOWN"

    if isinstance(input_name, str):
        input_names = re.split(r"[,，、]", input_name)
    else:
        input_names = input_name

    normalized_inputs = [
        normalize_person_name(name)
        for name in input_names
        if name.strip()
    ]

    normalized_official = [
        normalize_person_name(name)
        for name in official_names
        if name and "*" not in name and "＊" not in name
    ]

    if not normalized_official or not normalized_inputs:
        return "UNKNOWN"

    matched_count = sum(
        name in normalized_official
        for name in normalized_inputs
    )

    if matched_count == len(normalized_inputs):
        return "MATCH"

    if matched_count > 0:
        return "PARTIAL_MATCH"

    return "MISMATCH"

def compare_address(input_address, official_address):
    if not input_address or not official_address:
        return "UNKNOWN"

    input_address = normalize_address(input_address)
    official_address = normalize_address(official_address)
   
    if input_address == official_address:
        return "MATCH"
    if input_address in official_address:
            return "MATCH"

    input_region = extract_region(input_address)
    official_region = extract_region(official_address)

    # 시도 + 시군구 비교
    if input_region == official_region:
        return "PARTIAL_MATCH"

    return "MISMATCH"


def format_candidate(raw_data: dict) -> dict:
    representatives = [
        name.strip()
        for name in (raw_data.get("rprsvNm") or "").split(",")
        if name.strip()
    ]

    return {
        "business_name": raw_data.get("bzmnNm"),
        "representative_names": representatives,
        "business_number": raw_data.get("brno"),
        "corporate_number": raw_data.get("crno"),
        "business_status": raw_data.get("operSttusCdNm"),
        "report_number": raw_data.get("prmmiMnno"),
        "address": raw_data.get("lctnAddr"),
        "road_address": raw_data.get("rnAddr"),
    }


def compare_candidate(business_info, candidate, search_method):
    if search_method == "BUSINESS_NUMBER":
        address_status = "SKIPPED"
    else:
        address_status = compare_address(
            business_info.get("address"),
            candidate.get("address"),
        )

    return {
        "business_name": compare_name(
            business_info.get("business_name"),
            candidate.get("business_name"),
        ),
        "business_number": compare_number(
            business_info.get("business_number"),
            candidate.get("business_number"),
        ),
        "representative_name": compare_representative(
            business_info.get("representative_name"),
            candidate.get("representative_names",[]),
        ),
        "business_address": address_status,
    }


def lookup_business(business_info: dict) -> dict:
    business_info = business_info or {}

    business_number = business_info.get("business_number")
    business_name = business_info.get("business_name")
    business_address = business_info.get("address")
    if isinstance(business_number, str):
        business_number = business_number.strip()

    if isinstance(business_name, str):
        business_name = business_name.strip()

    if isinstance(business_address, str):
        business_address = business_address.strip()

    # 1. 사업자번호 우선 검색
    if business_number:
        raw_items = get_business_info(business_number)
        search_method = "BUSINESS_NUMBER"

    # 2. 사업자번호가 없으면 법인명 검색
    elif business_name:
        search_name = normalize_search_name(business_name)
        raw_items = get_business_info_by_name(search_name)
        search_method = "BUSINESS_NAME"

    else:
        return {
            "status": "skipped",
            "search_method": None,
            "match_status": "UNKNOWN",
            "candidates": [],
        }

    candidates = [
        format_candidate(item)
        for item in raw_items
    ]

    # 3. 검색 결과 없음
    if not candidates:
        return {
            "status": "completed",
            "search_method": search_method,
            "match_status": "NO_MATCH",
            "candidates": [],
        }

    # 4. 법인명 검색일 때 정확한 법인명 후보 우선
    if search_method == "BUSINESS_NAME" and business_name:
        name_matched = [
            candidate
            for candidate in candidates
            if compare_name(
                business_name,
                candidate["business_name"],
            ) == "MATCH"
        ]

        if name_matched:
            candidates = name_matched

    # 5. 법인명 검색일 때 주소로 후보 필터링
    if search_method == "BUSINESS_NAME" and business_address:
        address_matched = [
            candidate
            for candidate in candidates
            if compare_address(
                business_address,
                candidate["address"],
            ) in ("MATCH", "PARTIAL_MATCH")
        ]

        # 주소가 일치하는 후보가 발견된 경우에만 좁힘
        # 모두 불일치하면 원래 후보를 유지
        if address_matched:
            candidates = address_matched

    # 6. 후보가 여러 개면 확정하지 않음
    if len(candidates) > 1:
        candidate_results = []

        for candidate in candidates:
            candidate_result = candidate.copy()
            candidate_result["verification"] = compare_candidate(
                business_info,
                candidate,
                search_method,
            )
            candidate_results.append(candidate_result)

        return {
            "status": "completed",
            "search_method": search_method,
            "match_status": "MULTIPLE_MATCHES",
            "candidates": candidate_results,
        }

    # 7. 후보 하나일 때 최종 정보 비교
    official = candidates[0]

    verification = compare_candidate(
        business_info,
        official,
        search_method,
    )

    return {
        "status": "completed",
        "search_method": search_method,
        "match_status": "SINGLE_CANDIDATE",
        "official_info": official,
        "verification": verification,
    }
