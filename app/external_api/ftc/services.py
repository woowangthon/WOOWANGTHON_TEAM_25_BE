# external_api/ftc/services.py

import re
import unicodedata

from .client import (
    get_business_info,
    get_business_info_by_name,
)


def normalize_name(value: str | None) -> str:
    if not value:
        return ""

    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", "", value)

    # 법인 표기 통일
    value = value.replace("(주)", "")
    value = value.replace("㈜", "")
    value = value.replace("주식회사", "")

    return value.lower()


def normalize_number(value: str | None) -> str:
    if not value:
        return ""

    return re.sub(r"\D", "", value)


def compare_name(input_name, official_name):
    if not input_name or not official_name:
        return "UNKNOWN"

    return (
        "MATCH"
        if normalize_name(input_name) == normalize_name(official_name)
        else "MISMATCH"
    )


def compare_representative(input_name, official_names):
    if not input_name or not official_names:
        return "UNKNOWN"

    normalized_names = [
        normalize_name(name)
        for name in official_names
    ]

    return (
        "MATCH"
        if normalize_name(input_name) in normalized_names
        else "MISMATCH"
    )


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
    }


def lookup_business(business_info: dict) -> dict:
    business_number = business_info.get("business_number")
    business_name = business_info.get("business_name")
    representative_name = business_info.get("representative_name")

    # 1. 사업자번호 우선 검색
    if business_number:
        raw_items = get_business_info(business_number)
        search_method = "BUSINESS_NUMBER"

    # 2. 사업자번호가 없으면 상호명 검색
    elif business_name:
        raw_items = get_business_info_by_name(business_name)
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

    # 검색 결과 없음
    if not candidates:
        return {
            "status": "completed",
            "search_method": search_method,
            "match_status": "NO_MATCH",
            "candidates": [],
        }

    # 3. 상호명 검색에서 대표자명으로 후보 필터링
    if search_method == "BUSINESS_NAME" and representative_name:
        filtered = [
            candidate
            for candidate in candidates
            if compare_representative(
                representative_name,
                candidate["representative_names"],
            ) == "MATCH"
        ]

        if filtered:
            candidates = filtered

    # 4. 최종 후보가 여러 개면 확정하지 않음
    if len(candidates) > 1:
        return {
            "status": "completed",
            "search_method": search_method,
            "match_status": "MULTIPLE_MATCHES",
            "candidates": candidates,
        }

    # 5. 후보 하나일 때 정보 비교
    official = candidates[0]

    verification = {
        "business_name": compare_name(
            business_name,
            official["business_name"],
        ),
        "representative_name": compare_representative(
            representative_name,
            official["representative_names"],
        ),
        "business_number": (
            "UNKNOWN"
            if not business_number
            else (
                "MATCH"
                if normalize_number(business_number)
                == normalize_number(official["business_number"])
                else "MISMATCH"
            )
        ),
    }

    return {
        "status": "completed",
        "search_method": search_method,
        "match_status": "SINGLE_CANDIDATE",
        "official_info": official,
        "verification": verification,
    }