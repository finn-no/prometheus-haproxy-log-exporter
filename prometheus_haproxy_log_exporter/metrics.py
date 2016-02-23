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

import itertools

from prometheus_client import Counter, Histogram

NAMESPACE = 'haproxy_log'

TIMERS = {
    'request_wait_milliseconds': (
        'time_wait_request',
        "Time spent waiting for the client to send the full HTTP request (Tq in HAProxy)",
    ),
    'server_tcp_connection_establish_milliseconds': (
        'time_connect_server',
        "Time in milliseconds to connect to the final server (Tc in HAProxy)",
    ),
    'request_queued_milliseconds': (
        'time_wait_queues',
        "Time that the request spend on HAProxy queues (Tw in HAProxy)",
    ),
    'response_processing_milliseconds': (
        'time_wait_response',
        "Time waiting the downstream server to send the full HTTP response (Tr in HAProxy)",
    ),
    'session_duration_milliseconds': (
        'total_time',
        "Time between accepting the HTTP request and sending back the HTTP response (Tt in HAProxy)",
    ),
}

TIMER_ABORT_COUNTERS = {
    'request_wait_milliseconds': (  # Tq
        'request_abort_total',
        "Count of connections aborted before a complete request was received",
    ),
    'server_tcp_connection_establish_milliseconds': (  # Tc
        'request_pre_server_connection_abort',
        "Count of connections aborted before a connection to a server was established",
    ),
    'request_queued_milliseconds': (  # Tw
        'request_pre_queue_abort_total',
        "Count of connections aborted before reaching the queue",
    ),
    'response_processing_milliseconds': (  # Tr
        'request_response_abort_total',
        "Count of connections for which the last response header from the server was never received",
    ),
}

TIMER_NAMES = TIMERS.keys()

# These are attributes associated with each line processed, which can be used
# as labels on metrics
REQUEST_LABELS = (
    'status_code',
    'frontend_name',
    'backend_name',
    'server_name',
    'http_request_path',
    'http_request_method',
    'client_ip',
    'client_port',
)

# These are the default buckets for the Prometheus python client, adjusted to
# be in milliseconds
DEFAULT_TIMER_BUCKETS = (
    5, 10, 25,
    50, 75, 100, 250,
    500, 750, 1000, 2500,
    5000, 7500, 10000, float('inf'),
)


DEFAULT_QUEUE_LENGTH_BUCKETS = tuple(itertools.chain(
    range(0, 10),
    (20, 30, 40, 60, 100, float('inf')),
))


def requests_total(labelnames):
    requests_total = Counter(
        'requests_total',
        "Total processed requests",
        namespace=NAMESPACE,
        labelnames=labelnames,
    )

    if len(labelnames) == 0:
        def observe(line):
            requests_total.inc()
    else:
        def observe(line):
            requests_total.labels({
                label: getattr(line, label)
                for label in labelnames
            }).inc()

    return observe


def timer(timer_name, labelnames, buckets):
    attribute, documentation = TIMERS[timer_name]

    all_labelnames = labelnames

    if timer_name == 'session_duration_milliseconds':
        all_labelnames = labelnames + ['logasap']

    histogram = Histogram(
        timer_name,
        documentation=documentation,
        namespace=NAMESPACE,
        labelnames=tuple(all_labelnames),
        buckets=buckets,
    )

    if timer_name == 'session_duration_milliseconds':
        def observe(line):
            raw_value = getattr(line, attribute)

            label_values = {
                label: getattr(line, label)
                for label in labelnames
            }

            if raw_value.startswith('+'):
                label_values['logasap'] = True
                value = float(raw_value[1:])
            else:
                label_values['logasap'] = False
                value = float(raw_value)

            histogram.labels(label_values).observe(value)
    else:
        abort_counter_name, abort_counter_documentation = TIMER_ABORT_COUNTERS[timer_name]

        abort_counter = Counter(
            abort_counter_name,
            abort_counter_documentation,
            namespace=NAMESPACE,
            labelnames=labelnames,
        )

        if len(labelnames) == 0:
            def observe(line):
                value = float(getattr(line, attribute))

                if value == -1:
                    abort_counter.inc()
                else:
                    histogram.observe(value)
        else:
            def observe(line):
                value = float(getattr(line, attribute))

                label_values = {
                    label: getattr(line, label)
                    for label in labelnames
                }

                if value == -1:
                    abort_counter.labels(label_values).inc()
                else:
                    histogram.labels(label_values).observe(value)

    return observe


def bytes_read_total(labelnames):
    counter = Counter(
        'bytes_read_total',
        "Bytes read total",
        namespace=NAMESPACE,
        labelnames=labelnames,
    )

    if len(labelnames) == 0:
        def observe(line):
            counter.inc()
    else:
        def observe(line):
            counter.labels({
                label: getattr(line, label)
                for label in labelnames
            }).inc()

    return observe


def backend_queue_length(labelnames, buckets):
    histogram = Histogram(
        'backend_queue_length',
        "Requests processed before this one in the backend queue",
        namespace=NAMESPACE,
        labelnames=tuple(labelnames),
        buckets=buckets,
    )

    if len(labelnames) == 0:
        def observe(line):
            histogram.observe(line.queue_backend)
    else:
        def observe(line):
            histogram.labels({
                label: getattr(line, label)
                for label in labelnames
            }).observe(line.queue_backend)

    return observe


def server_queue_length(labelnames, buckets):
    histogram = Histogram(
        'server_queue_length',
        "Length of the server queue when the request was received",
        namespace=NAMESPACE,
        labelnames=tuple(labelnames),
        buckets=buckets,
    )

    if len(labelnames) == 0:
        def observe(line):
            histogram.observe(line.queue_server)
    else:
        def observe(line):
            histogram.labels({
                label: getattr(line, label)
                for label in labelnames
            }).observe(line.queue_server)

    return observe
