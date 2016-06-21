#!/usr/bin/env python
# -*- coding: utf-8

import threading
import time
from unittest.mock import MagicMock

import pytest

from prometheus_haproxy_log_exporter.file.log_file_processor import LogFileProcessor

@pytest.fixture()
def updater_mock():
    return MagicMock()


def test_follow(tmpfile, updater_mock, log_content):
    tmp = tmpfile.open('w')
    log_processor = LogFileProcessor(
        metric_updaters=[updater_mock],
        path=str(tmpfile),
    )
    lp = threading.Thread(target=log_processor.run)
    lp.start()
    time.sleep(1)
    for line in log_content.splitlines(keepends=True):
        tmp.write(line)
        time.sleep(0)
    tmp.close()
    time.sleep(1)
    log_processor.should_exit = True
    lp.join()
    assert updater_mock.call_count == 13
