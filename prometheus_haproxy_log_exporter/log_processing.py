# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import logging
import threading

from haproxy.line import Line
from prometheus_client import Counter

from .metrics import NAMESPACE

JOURNAL_REGEX = re.compile(
    # Dec  9
    r'\A\w+\s+\d+\s+'
    # 13:01:26
    r'\d+:\d+:\d+\s+'
    # localhost.localdomain haproxy[28029]:
    r'([\.a-zA-Z0-9_-]+)\s+\w+\[\d+\]:\s+',
)


class AbstractLogProcessor(threading.Thread):
    def __init__(self, metric_updaters, *args, **kwargs):
        super(AbstractLogProcessor, self).__init__(*args, **kwargs)

        self.metric_updaters = metric_updaters

        self.processing_errors = Counter(
            'processing_errors_total',
            "Total log lines which could not be processed",
            namespace=NAMESPACE,
        )

    def update_metrics(self, raw_line):
        try:
            raw_line = JOURNAL_REGEX.sub('', raw_line.strip())
            line = Line(raw_line.strip())
        except Exception as e:
            self.processing_errors.inc()
            logging.exception("%s (line parsing error): %s" % (e, raw_line))
            return

        if not line.valid:
            self.processing_errors.inc()
            logging.debug("Failed to parse line: %s" % raw_line)
            return

        try:
            for metric_updater in self.metric_updaters:
                metric_updater(line)
        except Exception as e:
            self.processing_errors.inc()
            logging.exception("%s (error updating metrics): %s" % (e, raw_line))
