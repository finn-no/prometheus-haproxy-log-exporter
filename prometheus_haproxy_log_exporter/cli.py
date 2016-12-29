#!/usr/bin/python3

# Copyright (C) 2016  Christopher Baines <mail@cbaines.net>
#
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

import logging
import configargparse

from os.path import join, dirname, normpath
from http.server import HTTPServer

from . import __version__
from . import metrics
from .exposition import create_request_handler


def get_argument_parser():
    p = configargparse.ArgParser(
        prog="prometheus-haproxy-log-exporter",
    )

    p.add(
        '--version',
        action='version',
        version=__version__,
        help="Show the version",
    )

    p.add(
        '-v',
        '--verbose',
        help="Enable debug logging",
        action="store_true"
    )

    p.add(
        '-c',
        '--config',
        is_config_file=True,
        help="config file path",
        env_var='CONFIG',
    )

    p.add(
        '--port',
        default='9129',
        help="Port on which to expose metrics",
        type=int,
        env_var='PORT',
    )
    p.add(
        '--host',
        default='0.0.0.0',
        help="Host on which to expose metrics",
        env_var='HOST',
    )

    p.add(
        '--licence-location',
        default=join(dirname(dirname(normpath(__file__))), 'LICENSE'),
        help="The location of the licence, linked to through the web interface",
        env_var='LICENCE_LOCATION',
    )

    # Processor arguments
    processor = p.add_mutually_exclusive_group(required=True)
    processor.add_argument(
        '-f',
        '--file',
        help="read logs from a log file",
        dest='file',
        env_var='LOG_FILE',
    )
    processor.add_argument(
        '-j',
        '--journal',
        help="read logs from systemd journal",
        dest='journal',
        const="haproxy.service",
        nargs='?',
        action='store',
        env_var='JOURNAL_UNIT',
    )
    processor.add_argument(
        '-s',
        '--stdin',
        help="read logs from stdin",
        dest='stdin',
        action='store_true',
        env_var='STDIN',
    )
    processor.add_argument(
        '-k',
        '--kafka',
        help="fread log rom kafka brokers host:port[,host:port...]",
        dest='kafka',
        env_var='KAFKA_BROKERS',
    )
    p.add(
        '--topic',
        help="kafka topic to consume",
        dest='kafka_topic',
        env_var='KAFKA_TOPIC',
    )
    p.add(
        '--group',
        help="kafka consumer group",
        dest='kafka_group',
        env_var='KAFKA_GROUP',
    )

    p.add(
        '--enabled-metrics',
        nargs='+',
        default=(
            [
                'requests_total',
                'bytes_read_total',
                'backend_queue_length',
                'server_queue_length',
            ] +
            list(metrics.TIMERS.keys())
        ),
        choices=(
            [
                'requests_total',
                'bytes_read_total',
                'backend_queue_length',
                'server_queue_length',
            ] +
            list(metrics.TIMERS.keys())
        ),
        help="Comma separated list of timers to export",
        env_var='ENABLED_TIMERS',
    )

    for counter in (
        metrics.bytes_read_total,
        metrics.requests_total,
    ):
        name_with_hyphens = counter.__name__.replace('_', '-')

        p.add(
            '--%s-labels' % name_with_hyphens,
            nargs='+',
            default=['status_code', 'backend_name', 'server_name'],
            choices=metrics.REQUEST_LABELS,
            help="Labels to use for %s" % counter.__name__,
            env_var='%s_LABELS' % counter.__name__.upper(),
        )

    for timer_name, (_, documentation) in metrics.TIMERS.items():
        p.add_argument(
            '--%s-labels' % timer_name.replace('_', '-'),
            nargs='+',
            default=[],
            choices=metrics.REQUEST_LABELS,
            help="Labels for the %s timer" % timer_name,
            env_var='%s_LABELS' % timer_name.upper(),
        )

        p.add_argument(
            '--%s-buckets' % timer_name.replace('_', '-'),
            nargs='+',
            default=metrics.DEFAULT_TIMER_BUCKETS,
            help="Labels for the %s metric" % timer_name,
            env_var='%s_BUCKETS' % timer_name.upper(),
        )

    for queue_histogram in (
        metrics.backend_queue_length,
        metrics.server_queue_length,
    ):
        name_with_hyphens = queue_histogram.__name__.replace('_', '-')

        p.add_argument(
            '--%s-labels' % name_with_hyphens,
            nargs='+',
            default=[],
            choices=metrics.REQUEST_LABELS,
            help="Labels for the %s metric" % queue_histogram.__name__,
            env_var='%s_LABELS' % queue_histogram.__name__.upper(),
        )

        p.add_argument(
            '--%s-buckets' % name_with_hyphens,
            nargs='+',
            default=metrics.DEFAULT_QUEUE_LENGTH_BUCKETS,
            help="Labels for the %s metric" % queue_histogram.__name__,
            env_var='%s_BUCKETS' % queue_histogram.__name__.upper(),
        )

    return p


def create_log_processor(options, error):
    metric_updaters = []

    for timer_name in metrics.TIMERS.keys():
        if timer_name not in options.enabled_metrics:
            continue

        labelnames = getattr(options, '%s_labels' % timer_name)
        buckets = getattr(options, '%s_buckets' % timer_name)

        metric_updaters.append(
            metrics.timer(timer_name, labelnames, buckets),
        )

    for counter in (
        metrics.bytes_read_total,
        metrics.requests_total,
    ):
        if counter.__name__ not in options.enabled_metrics:
            continue

        labelnames = getattr(options, '%s_labels' % counter.__name__)

        metric_updaters.append(counter(labelnames))

    for queue_histogram in (
        metrics.backend_queue_length,
        metrics.server_queue_length,
    ):
        if queue_histogram.__name__ not in options.enabled_metrics:
            continue

        labelnames = getattr(options, '%s_labels' % queue_histogram.__name__)
        buckets = getattr(options, '%s_buckets' % queue_histogram.__name__)

        metric_updaters.append(queue_histogram(labelnames, buckets))

    if options.stdin:
        from .stdin import StdinProcessor

        log_processor = StdinProcessor(metric_updaters)
    elif options.journal:
        from .journal import JournalProcessor

        log_processor = JournalProcessor(
            metric_updaters=metric_updaters,
            unit=options.journal,
        )
    elif options.file:
        from .file import LogFileProcessor

        log_processor = LogFileProcessor(
            metric_updaters=metric_updaters,
            path=options.file,
        )
    elif options.kafka:
        from .kafka import KafkaProcessor

        log_processor = KafkaProcessor(
            metric_updaters=metric_updaters,
            topic=options.kafka_topic,
            group=options.kafka_group,
            brokers=options.kafka
        )

    return log_processor


def main():
    p = get_argument_parser()
    options = p.parse_args()

    logging.basicConfig(level=logging.DEBUG if options.verbose else logging.INFO)

    logging.info(p.format_values())

    log_processor = create_log_processor(options, p.error)
    log_processor.start()

    host = options.host
    port = options.port

    httpd = HTTPServer(
        (host, port),
        create_request_handler(options.licence_location),
    )

    logging.info("Listing on port %s:%d" % (host, port))

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    log_processor.stop()
