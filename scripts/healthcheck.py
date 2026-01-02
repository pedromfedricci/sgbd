#!/usr/bin/env python3

import sys
import urllib.request

URL = "http://localhost:8000/health"
TIMEOUT = 2

try:
    with urllib.request.urlopen(URL, timeout=TIMEOUT) as resp:
        if resp.status != 200:
            sys.exit(1)
except Exception:
    sys.exit(1)
