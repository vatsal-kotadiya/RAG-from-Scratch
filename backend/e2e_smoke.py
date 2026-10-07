"""End-to-end smoke test: upload policy doc -> wait READY -> ask -> print answer."""
import json
import time
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"

print("health:", urllib.request.urlopen(BASE + "/api/health", timeout=15).read().decode())

boundary = "----" + uuid.uuid4().hex
with open("evaluation_dataset/company_policy.txt", "rb") as f:
    data = f.read()
pre = (
    "--" + boundary + '\r\nContent-Disposition: form-data; name="file"; '
    'filename="company_policy.txt"\r\nContent-Type: text/plain\r\n\r\n'
).encode()
body = pre + data + ("\r\n--" + boundary + "--\r\n").encode()
req = urllib.request.Request(
    BASE + "/api/documents/upload", data=body,
    headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
)
up = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
print("upload:", up["id"], up["status"])
doc_id = up["id"]

for _ in range(30):
    time.sleep(5)
    d = json.loads(urllib.request.urlopen(BASE + f"/api/documents/{doc_id}", timeout=15).read().decode())
    print("status:", d["status"], "chunks:", d["chunk_count"], d["error_message"] or "")
    if d["status"] in ("READY", "FAILED"):
        break

q = json.dumps({
    "question": "What is the minimum attendance requirement?",
    "document_ids": [doc_id], "top_k": 5,
}).encode()
req = urllib.request.Request(BASE + "/api/chat", data=q, headers={"Content-Type": "application/json"})
ans = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
print("ANSWER:", ans["answer"][:400])
print("SOURCES:", json.dumps(ans["sources"], indent=1)[:800])
print("META:", ans["retrieval_metadata"], ans["provider"])
