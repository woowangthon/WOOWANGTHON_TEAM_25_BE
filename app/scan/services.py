from uuid import uuid4
from urllib.parse import urlsplit

import logging
logger = logging.getLogger(__name__)

def run_scan(url: str) -> dict:
    """
    전체 URL 분석 프로세스를 실행한다.
    """
    #logger.info("Starting scan process")


    parsed = urlsplit(url)

    domain = parsed.hostname.lower()
    #logger.debug("Parsed domain: %s", domain)
    #scan_id = str(uuid4())

        # logger.debug("Generated scan_id: %s", scan_id)
        # logger.info("Scan process completed")
    return {
        "scan_id": str(uuid4()),
        "url": url,
        "domain": domain,
        "status": "received",
        "risk_score": None,
        "verdict": "UNDETERMINED",
        "analyses": {
            "nts": {
                "status": "not_configured",
            },
            "ftc": {
                "status": "not_configured",
            },
            "ai": {
                "status": "not_configured",
            },
        },
    }