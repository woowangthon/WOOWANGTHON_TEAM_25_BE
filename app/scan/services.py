
from uuid import uuid4
from urllib.parse import urlsplit
import logging
logger = logging.getLogger(__name__)

from external_api.nts.client import NtsApiError
from external_api.nts.services import lookup_business as lookup_nts
from external_api.ftc.services import lookup_business as lookup_ftc
from risk_engine.services import calculate_risk
from datetime import timedelta
from django.utils import timezone
from .models import ScanCache

CACHE_TTL_HOURS = 24

def get_cached_result(url, business_info):
    # 24시간이 지난 캐시 삭제
    expiration_time = timezone.now() - timedelta(
        hours=CACHE_TTL_HOURS
    )

    ScanCache.objects.filter(
        created_at__lt=expiration_time
    ).delete()

    # 현재 요청의 사업자 정보
    business_name = business_info.get("business_name") or ""
    representative_name = business_info.get("representative_name") or ""
    business_number = business_info.get("business_number") or ""
    address = business_info.get("address") or ""

    # 유효한 캐시 조회
    return ScanCache.objects.filter(
        url=url,
        business_name=business_name,
        representative_name=representative_name,
        business_number=business_number,
        address=address,
    ).first()

def run_scan(url: str, business_info: dict | None = None) -> dict:
    """
    db 기록에 히트 되는지 판단
    """
    logger.debug("========== CACHE DEBUG ==========")
    logger.debug("INPUT URL: %r", url)
    logger.debug("INPUT BUSINESS INFO: %r", business_info)

    logger.debug(
        "CACHE QUERY: %r",
        {
            "url": url,
            "business_name": business_info.get("business_name") or "",
            "representative_name": business_info.get("representative_name") or "",
            "business_number": business_info.get("business_number") or "",
            "address": business_info.get("address") or "",
        }
    )
    for item in ScanCache.objects.all():
        logger.debug(
            "DB CACHE: %r",
            {
                "url": item.url,
                "business_name": item.business_name,
                "representative_name": item.representative_name,
                "business_number": item.business_number,
                "address": item.address,
            }
        )
    cached = get_cached_result(url, business_info)

    if cached:
        logger.debug("CACHE HIT: %s", url)
        return cached.result

    logger.debug("CACHE MISS: %s", url)
        
    """
    전체 URL 분석 프로세스를 실행한다.
    """
    
    business_info = business_info or {}

    parsed = urlsplit(url)
    domain = (parsed.hostname or "").lower()

    business_number = business_info.get("business_number")

    # 공백 문자열 방지
    if isinstance(business_number, str):
        business_number = business_number.strip()

    # 1. NTS 조회
    nts_result = {
        "status": "skipped",
        "business_status": None,
    }

    if business_number:
        try:

            nts_result = lookup_nts(business_number)

            #logger.debug("NTS lookup completed: %s", nts_result)

        except NtsApiError as e:
            logger.exception("NTS API error")

            nts_result = {
                "status": "error",
                "error": "NTS_API_SERVER_ERROR",
            }

        except ValueError:
            nts_result = {
                "status": "error",
                "error": "INVALID_BUSINESS_NUMBER",
            }

    # 2. FTC 조회
    # 사업자번호가 없어도 법인명이 있으면 조회 가능
    try:
        ftc_result = lookup_ftc(business_info)

    except Exception:

        ftc_result = {
            "status": "error",
            "error": "FTC_API_ERROR",
        }

    analyses = {
    "nts": nts_result,
    "ftc": ftc_result,
    "ai": {"status": "not_configured"},
}

    risk_result = calculate_risk(analyses)
    # 3. 최종 응답
    reply = {
        "scan_id": str(uuid4()),
        "url": url,
        "domain": domain,
        "status": "received",

        "business_info": business_info,

    "risk_score": risk_result["risk_score"],
    "verdict": risk_result["verdict"],
    "risk_factors": risk_result["risk_factors"],
    "checked_items": risk_result["checked_items"],

    "analyses": analyses,
    }
    logger.debug("final report %s", reply)
    ScanCache.objects.create(
        url=url,
        business_name=business_info.get("business_name") or "",
        representative_name=business_info.get("representative_name") or "",
        business_number=business_info.get("business_number") or "",
        address=business_info.get("address") or "",
        result=reply
    )

    return reply
