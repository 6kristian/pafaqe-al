#!/usr/bin/env python3
"""Upload leads.clean.json to Firestore as lead_chunks/0000, 0001, ... (new chunks are written first, stale ones removed after).
Local:   pip install firebase-admin ; python upload_leads.py serviceAccount.json
GitHub:  set the FIREBASE_SERVICE_ACCOUNT secret (whole JSON); run without arguments.
NEVER commit the service account file."""
import json, os, sys
import firebase_admin
from firebase_admin import credentials, firestore

if len(sys.argv) > 1:
    cred = credentials.Certificate(sys.argv[1])
else:
    cred = credentials.Certificate(json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT']))
firebase_admin.initialize_app(cred)
db = firestore.client()

rows = json.load(open('leads.clean.json', encoding='utf-8'))['businesses']
if len(rows) < 5000:
    sys.exit(f'Only {len(rows)} leads, refusing to overwrite the live data')
SIZE = 500  # ~150 KB per document, well under Firestore's 1 MiB limit
n = (len(rows) + SIZE - 1) // SIZE

for i in range(n):
    db.collection('lead_chunks').document(f'{i:04d}').set({'rows': rows[i * SIZE:(i + 1) * SIZE]})
for d in db.collection('lead_chunks').stream():
    if int(d.id) >= n:
        d.reference.delete()
print(f'uploaded {len(rows)} leads in {n} chunks')
