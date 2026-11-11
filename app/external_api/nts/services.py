from .client import get_business_status
import logging
logger = logging.getLogger(__name__)

def lookup_business(business_number: str) -> dict:
    logger.warning(
        "NTS BUSINESS NUMBER: %s",
        business_number
    )
    
    raw_data = get_business_status(business_number)
    logger.warning(
        "NTS RAW RESULT: %s",
        raw_data
    )
    status_code = raw_data.get("b_stt_cd")

    status_mapping = {
        "01": "ACTIVE",
        "02": "SUSPENDED",
        "03": "CLOSED",
    }

    business_status = status_mapping.get(
        status_code,
        "UNKNOWN"
    )

    return {
        "status": "completed",
        "business_number": raw_data.get("b_no"),
        "business_status": status_mapping.get(
            status_code, "UNKNOWN"
        ),
        "business_status_code": status_code,
        "business_status_description": raw_data.get("b_stt"),
        "tax_type": raw_data.get("tax_type"),
        "tax_type_code": raw_data.get("tax_type_cd"),
        "closed_date": raw_data.get("end_dt") or None,
    }