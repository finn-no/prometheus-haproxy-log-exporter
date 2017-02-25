#!/usr/bin/env python
# -*- coding: utf-8

from haproxy.line import Line
from prometheus_client import REGISTRY

from prometheus_haproxy_log_exporter.log_processing import JOURNAL_REGEX
from prometheus_haproxy_log_exporter.metrics import timer, DEFAULT_TIMER_BUCKETS


def test_timer(log_content):
    expected = {
        "haproxy_log_session_duration_milliseconds_count": {
            "cache.api.finn.no-backend": 11.0,
            "statistics": 2.0
        },
        "haproxy_log_session_duration_milliseconds_sum": {
            "cache.api.finn.no-backend": 19.0,
            "statistics": 0.0
        }
    }
    t = timer("session_duration_milliseconds", ["frontend_name", "backend_name"], DEFAULT_TIMER_BUCKETS)
    for raw_line in log_content.splitlines():
        raw_line = JOURNAL_REGEX.sub('', raw_line.strip())
        line = Line(raw_line.strip())
        if line.valid:
            t(line)
    for metric in REGISTRY.collect():
        for name, labels, value in metric.samples:
            if name in expected:
                assert value == expected[name][labels["backend_name"]]
