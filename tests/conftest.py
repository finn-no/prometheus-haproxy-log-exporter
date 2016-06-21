#!/usr/bin/env python
# -*- coding: utf-8
import pytest

LOG_CONTENT = """\
Jun  9 12:31:39 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42563 [09/Jun/2016:12:31:39.908] cache.api.finn.no-tls cache.api.finn.no-backend/apicache3.finn.no 0/0/1/1/2 200 1771 - - ---- 1/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:39 softwarelb1-prod1.z01.finn.no haproxy[11066]: 127.0.0.1:42563 [09/Jun/2016:12:31:39.900] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 8/1/11 1752 -- 0/0/0/0/0 0/0
Jun  9 12:31:40 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:55104 [09/Jun/2016:12:31:40.048] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/1/0/1 200 1777 - - ---- 2/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:40 softwarelb3-prod1.z01.finn.no haproxy[31506]: 127.0.0.1:55104 [09/Jun/2016:12:31:40.043] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 5/1/8 1758 -- 0/0/0/0/0 0/0
Jun  9 12:31:41 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42568 [09/Jun/2016:12:31:41.913] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/0/2/2 200 1777 - - ---- 1/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:41 softwarelb1-prod1.z01.finn.no haproxy[11061]: 127.0.0.1:42568 [09/Jun/2016:12:31:41.903] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 9/1/12 1758 -- 0/0/0/0/0 0/0
Jun  9 12:31:42 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:55111 [09/Jun/2016:12:31:42.045] cache.api.finn.no-tls cache.api.finn.no-backend/apicache3.finn.no 0/0/0/1/1 200 1771 - - ---- 2/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:42 softwarelb3-prod1.z01.finn.no haproxy[31502]: 127.0.0.1:55111 [09/Jun/2016:12:31:42.037] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 8/1/10 1752 -- 0/0/0/0/0 0/0
Jun  9 12:31:43 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42573 [09/Jun/2016:12:31:43.916] cache.api.finn.no-tls cache.api.finn.no-backend/apicache3.finn.no 0/0/1/1/2 200 1771 - - ---- 1/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:43 softwarelb1-prod1.z01.finn.no haproxy[11060]: 127.0.0.1:42573 [09/Jun/2016:12:31:43.906] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 10/1/13 1752 -- 0/0/0/0/0 0/0
Jun  9 12:31:44 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:55116 [09/Jun/2016:12:31:44.047] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/1/1/2 200 1777 - - ---- 1/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:44 softwarelb3-prod1.z01.finn.no haproxy[31502]: 127.0.0.1:55116 [09/Jun/2016:12:31:44.039] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 8/1/11 1758 -- 0/0/0/0/0 0/0
Jun  9 12:31:45 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42578 [09/Jun/2016:12:31:45.914] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/1/1/2 200 1777 - - ---- 1/1/0/1/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:45 softwarelb1-prod1.z01.finn.no haproxy[11066]: 127.0.0.1:42578 [09/Jun/2016:12:31:45.907] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 6/1/9 1758 -- 0/0/0/0/0 0/0
Jun  9 12:31:46 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:55121 [09/Jun/2016:12:31:46.051] cache.api.finn.no-tls cache.api.finn.no-backend/apicache3.finn.no 0/0/0/2/2 200 1771 - - ---- 1/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:46 softwarelb3-prod1.z01.finn.no haproxy[31504]: 127.0.0.1:55121 [09/Jun/2016:12:31:46.042] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 8/1/11 1752 -- 0/0/0/0/0 0/0
Jun  9 12:31:46 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:50672 [09/Jun/2016:12:31:46.565] statistics statistics/<STATS> 0/0/0/0/0 200 1715 - - LR-- 1/1/0/0/0 0/0 "GET /statistics;csv HTTP/1.1"
Jun  9 12:31:47 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42585 [09/Jun/2016:12:31:47.915] cache.api.finn.no-tls cache.api.finn.no-backend/apicache3.finn.no 0/0/0/1/1 200 1771 - - ---- 2/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:47 softwarelb1-prod1.z01.finn.no haproxy[11060]: 127.0.0.1:42585 [09/Jun/2016:12:31:47.910] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 5/1/7 1752 -- 0/0/0/0/0 0/0
Jun  9 12:31:47 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:33906 [09/Jun/2016:12:31:47.988] statistics statistics/<STATS> 0/0/0/0/0 200 1714 - - LR-- 1/1/0/0/0 0/0 "GET /statistics;csv HTTP/1.1"
Jun  9 12:31:48 softwarelb3-prod1.z01.finn.no haproxy[31501]: 127.0.0.1:55128 [09/Jun/2016:12:31:48.045] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/1/1/2 200 1777 - - ---- 2/1/0/0/0 0/0 "GET / HTTP/1.1"
Jun  9 12:31:48 softwarelb3-prod1.z01.finn.no haproxy[31504]: 127.0.0.1:55128 [09/Jun/2016:12:31:48.036] cache.api.finn.no-tls-termination~ cache.api.finn.no-tls-termination/cache.api.finn.no-tls-frontend 8/1/10 1758 -- 0/0/0/0/0 0/0
Jun  9 12:31:49 softwarelb1-prod1.z01.finn.no haproxy[11058]: 127.0.0.1:42592 [09/Jun/2016:12:31:49.916] cache.api.finn.no-tls cache.api.finn.no-backend/apicache4.finn.no 0/0/1/1/2 200 1777 - - ---- 2/1/0/0/0 0/0 "GET / HTTP/1.1"
"""


@pytest.fixture()
def log_content():
    return LOG_CONTENT


@pytest.fixture()
def tmpfile(tmpdir):
    tmpfile = tmpdir.join("haproxy.log")
    return tmpfile


@pytest.fixture()
def logfile(tmpfile):
    tmpfile.write(LOG_CONTENT)
    return tmpfile
