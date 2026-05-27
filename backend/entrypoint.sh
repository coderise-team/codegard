#!/bin/bash
set -e

python - <<'PY'
import os
import sys
import time
import subprocess

import psycopg2


dsn = os.environ.get("DATABASE_URL")
if not dsn:
    print("DATABASE_URL is not set; cannot run migrations.", file=sys.stderr)
    raise SystemExit(1)

# Prevent multiple containers (backend/celery) from running migrations at the
# same time (can cause PostgreSQL DDL race conditions).
lock_id = 742_001_337

deadline = time.time() + 60
while True:
    try:
        conn = psycopg2.connect(dsn)
        break
    except Exception as exc:  # pragma: no cover
        if time.time() >= deadline:
            print(f"DB connection failed while waiting for migration lock: {exc}", file=sys.stderr)
            raise
        time.sleep(1)

conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT pg_advisory_lock(%s)", (lock_id,))
try:
    subprocess.check_call(["python", "django_app/manage.py", "migrate", "--noinput"])
finally:
    try:
        cur.execute("SELECT pg_advisory_unlock(%s)", (lock_id,))
    finally:
        conn.close()
PY

exec "$@"

