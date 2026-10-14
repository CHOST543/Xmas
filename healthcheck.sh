#!/usr/bin/env bash
# CHOST health check: nginx edge answers, and the panel answers at all (any reply below 500).
curl -fsS -o /dev/null --max-time 4 http://127.0.0.1:8080/healthz || exit 1
code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 6 http://127.0.0.1:8000/api/system)
case "$code" in ""|000|5??) exit 1 ;; esac
exit 0
