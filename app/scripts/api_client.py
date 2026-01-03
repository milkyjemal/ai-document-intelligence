import requests

url = "http://127.0.0.1:8000/v1/extractions"

with open("samples/TFF-BOL-Form.pdf", "rb") as f:
    files = {"file": ("TFF-BOL-Form.pdf", f, "application/pdf")}
    data = {"schema": "bol_v1"}
    r = requests.post(url, data=data, files=files)

print("Status:", r.status_code)
print("X-Request-Id:", r.headers.get("X-Request-Id"))
print("Response:", r.json())
