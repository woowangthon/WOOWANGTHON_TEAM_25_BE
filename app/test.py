import os
import requests

url = "https://api.odcloud.kr/api/nts-businessman/v1/status"

key = "72e6bf8caf7ff5cf174799cd81d6d35550c0101de8f4562d9665f609b18cddd2"

response = requests.post(
    url,
    params={"serviceKey": key},
    json={"b_no": ["1208800767"]},
    timeout=10
)

print(response.status_code)
print(response.text)
print("===== NTS API DEBUG =====")
print("HTTP STATUS:", response.status_code)
print("REQUEST URL:", response.request.url.split("?")[0])
print("CONTENT TYPE:", response.headers.get("Content-Type"))
print("RESPONSE BODY:", response.text)
print("=========================")