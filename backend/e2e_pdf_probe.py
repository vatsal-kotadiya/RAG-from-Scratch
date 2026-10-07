"""Probe: upload a 2-page PDF, verify page_count + page citations, then clean up."""
import json
import time
import urllib.request
import uuid

BASE = "http://127.0.0.1:8000"

boundary = "----" + uuid.uuid4().hex
with open("data/uploads/probe_handbook.pdf", "rb") as f:
    data = f.read()
pre = (
    "--" + boundary + '\r\nContent-Disposition: form-data; name="file"; '
    'filename="probe_handbook.pdf"\r\nContent-Type: application/pdf\r\n\r\n'
).encode()
body = pre + data + ("\r\n--" + boundary + "--\r\n").encode()
req = urllib.request.Request(
    BASE + "/api/documents/upload", data=body,
    headers={"Content-Type": "multipart/form-data; boundary=" + boundary},
)
up = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
doc_id = up["id"]
for _ in range(24):
    time.sleep(5)
    d = json.loads(urllib.request.urlopen(BASE + f"/api/documents/{doc_id}", timeout=15).read().decode())
    if d["status"] in ("READY", "FAILED"):
        break
print("doc:", d["filename"], "pages:", d["page_count"], "chunks:", d["chunk_count"], d["status"], d["error_message"])

q = json.dumps({
    "question": "How long can books be borrowed?",
    "document_ids": [doc_id], "top_k": 5,
}).encode()
req = urllib.request.Request(BASE + "/api/chat", data=q, headers={"Content-Type": "application/json"})
ans = json.loads(urllib.request.urlopen(req, timeout=180).read().decode())
print("SOURCES:", json.dumps(ans["sources"], indent=1))

urllib.request.urlopen(urllib.request.Request(BASE + f"/api/documents/{doc_id}", method="DELETE"), timeout=30)
print("deleted probe doc")
