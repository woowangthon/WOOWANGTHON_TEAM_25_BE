from uuid import uuid4
from urllib.parse import urlsplit

from external_api.nts.client import NtsApiError
from external_api.nts.services import lookup_business as lookup_nts
from external_api.ftc.services import lookup_business as lookup_ftc

import logging
logger = logging.getLogger(__name__)

def run_scan(url: str, business_info: dict | None = None) -> dict:
    """
    전체 URL 분석 프로세스를 실행한다.
    """
    business_info = business_info or {}
    logger.debug("business_information : ", business_info, "\n")
    parsed = urlsplit(url)

    domain = parsed.hostname.lower()
    business_number = business_info.get("business_number")
    nts_result = {
        "status": "skipped",
        "business_status": None,
    }

    if business_number:
        try:
            logger.warning(
                "NTS INPUT: %s",
                business_info
            )

            nts_result = lookup_nts(business_number)

            logger.warning(
                "NTS RESULT: %s",
                nts_result
            )
        except (NtsApiError, ValueError):
            nts_result = {
                "status": "unavailable",
                "business_status": None,
            }
    if business_info:
        try:
            ftc_result = lookup_ftc(business_info)
        except Exception as e:
            ftc_result = {
                "status": "error",
                "error": str(e),
            }
    else:
        ftc_result = {
            "status": "skipped",
            "reason": "사업자등록번호가 제공되지 않았습니다.",
        }
    
    reply = {
        "scan_id": str(uuid4()),
        "url": url,
        "domain": domain,
        "status": "received",

        "business_info": business_info,


        "risk_score": None,
        "verdict": "UNDETERMINED",
        "analyses": {
            "nts": nts_result,
            "ftc": {
                "status": ftc_result,
            },
            "ai": {
                "status": "not_configured",
            },
        },
    }
    logger.debug(reply)
    return reply