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

from prometheus_client.exposition import MetricsHandler

index_page = """
<!doctype html>

<html lang="en">
<head>
  <meta charset="utf-8">

  <title>Prometheus HAProxy Log Exporter</title>
</head>

<body>
  <h1>HAProxy Log exporter for Prometheus</h1>

  <p>
    This is a highly configurable exporter for HAProxy.
  </p>

  <a href="/metrics">View metrics</a>

  <h2>Example Configuration</h2>
  <p>
    You must configure Prometheus to scrape the metrics exported here. The port
    is 9129, and the configuration should look something like the example
    below.
  </p>
  <pre><code>
    scrape_configs:
      - job_name: haproxy_log
        target_groups:
          - targets:
            - MACHINE_ADDRESS:9129
  </code></pre>

  <h2>Information</h2>
  <p>
    Copyright (C) 2016  Christopher Baines <mail@cbaines.net><br>
    <a href="/licence">View Licence</a>
  </p>

  <p>
    The source may be obtained from
    <a href="http://git.cbaines.net/prometheus-haproxy-log-exporter/">
    this Git repository</a>
  </p>

  <p>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
  </p>

  <p>
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
  </p>
</body>
</html>
"""


def create_request_handler(licence_location):
    class RequestHandler(MetricsHandler):
        def do_GET(self):
            if self.path == "/metrics":
                return super().do_GET()

            self.send_response(200)
            self.end_headers()

            if self.path == "/licence":
                with open(
                    licence_location,
                    'rb',
                ) as licence:
                    self.wfile.write(licence.read())
            else:
                self.wfile.write(index_page.encode('UTF-8'))

    return RequestHandler
