
# risk_engine/services.py

def _add_factor(factors, checked_items, name, result, points, reason):
    """
    검증 결과에 따라 위험 점수를 추가한다.
    """
    if result == "UNKNOWN" or result is None:
        return 0

    checked_items.append(name)

    if result == "MISMATCH":
        factors.append({
            "code": name.upper() + "_MISMATCH",
            "name": name,
            "result": result,
            "points": points,
            "reason": reason,
        })
        return points

    return 0


def _check_nts(nts_result, factors, checked_items):
    """
    국세청 사업자 상태 확인
    """
    if not isinstance(nts_result, dict):
        return 0

    if nts_result.get("status") != "completed":
        return 0

    business_status = nts_result.get("business_status")

    if not business_status:
        return 0

    checked_items.append("nts_business_status")

    status_text = str(business_status).strip()

    # 비정상 사업자 상태
    abnormal_keywords = ("폐업", "휴업", "말소", "등록취소")

    if any(keyword in status_text for keyword in abnormal_keywords):
        factors.append({
            "code": "ABNORMAL_BUSINESS_STATUS",
            "name": "사업자 상태",
            "result": "MISMATCH",
            "points": 30,
            "reason": f"사업자 상태가 정상적이지 않습니다: {status_text}",
        })
        return 30

    return 0


def _check_ftc(ftc_result, factors, checked_items):
    """
    공정거래위원회 검증 결과 확인
    """
    if not isinstance(ftc_result, dict):
        return 0

    if ftc_result.get("status") != "completed":
        return 0

    match_status = ftc_result.get("match_status")

    # 검색은 성공했지만 일치하는 업체가 없는 경우
    if match_status == "NO_MATCH":
        checked_items.append("ftc_business_lookup")

        factors.append({
            "code": "FTC_NO_MATCH",
            "name": "공정위 업체 조회",
            "result": "NO_MATCH",
            "points": 30,
            "reason": "공정거래위원회 통신판매사업자 정보에서 일치하는 업체를 찾지 못했습니다.",
        })

        return 30

    # 여러 후보가 발견된 경우
    if match_status == "MULTIPLE_MATCHES":
        checked_items.append("ftc_business_lookup")
        return 0

    official_info = ftc_result.get("official_info") or {}
    verification = ftc_result.get("verification")

    if not isinstance(verification, dict):
        verification = official_info.get("verification")

    if not isinstance(verification, dict):
        return 0

    score = 0

    score += _add_factor(
        factors,
        checked_items,
        "business_number",
        verification.get("business_number"),
        40,
        "사업자등록번호가 공식 정보와 일치하지 않습니다.",
    )

    score += _add_factor(
        factors,
        checked_items,
        "business_name",
        verification.get("business_name"),
        25,
        "상호명이 공식 정보와 일치하지 않습니다.",
    )

    score += _add_factor(
        factors,
        checked_items,
        "representative_name",
        verification.get("representative_name"),
        15,
        "대표자 이름이 공식 정보와 일치하지 않습니다.",
    )

    return score


def calculate_risk(analyses: dict) -> dict:
    """
    NTS, FTC 분석 결과를 종합하여 위험도를 계산한다.

    반환:
        risk_score: 0~100
        verdict: 최종 판정
        risk_factors: 위험 판단 근거
        checked_items: 실제 검증한 항목
    """
    analyses = analyses or {}

    factors = []
    checked_items = []

    nts_result = analyses.get("nts", {})
    ftc_result = analyses.get("ftc", {})

    score = 0

    score += _check_nts(
        nts_result,
        factors,
        checked_items,
    )

    score += _check_ftc(
        ftc_result,
        factors,
        checked_items,
    )

    score = min(score, 100)

    # 검증 가능한 항목이 하나도 없으면 판정 보류
    if not checked_items:
        verdict = "INSUFFICIENT_DATA"

    elif score >= 50:
        verdict = "HIGH_RISK"

    elif score >= 20:
        verdict = "CAUTION"

    else:
        verdict = "LOW_RISK"

    return {
        "risk_score": score,
        "verdict": verdict,
        "risk_factors": factors,
        "checked_items": checked_items,
    }
