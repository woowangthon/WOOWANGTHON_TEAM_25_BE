from uuid import uuid4
from urllib.parse import urlsplit

from tax_api.nts.services import lookup_business
from tax_api.nts.client import NtsApiError


import logging
logger = logging.getLogger(__name__)

def run_scan(url: str, business_info: dict | None = None) -> dict:
    """
    전체 URL 분석 프로세스를 실행한다.
    """
    business_info = business_info or {}

    parsed = urlsplit(url)

    domain = parsed.hostname.lower()
    business_number = business_info.get("business_number")
    nts_result = {
        "status": "skipped",
        "business_status": None,
    }

    if business_number:
        try:
            nts_result = lookup_business(business_number)
        except (NtsApiError, ValueError):
            nts_result = {
                "status": "unavailable",
                "business_status": None,
            }
    return {
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
                "status": "not_configured",
            },
            "ai": {
                "status": "not_configured",
            },
        },
    }