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

from kafka import KafkaConsumer

from ..log_processing import AbstractLogProcessor


class KafkaProcessor(AbstractLogProcessor):
    def __init__(self, metric_updaters, topic, group, brokers, *args, **kwargs):
        super().__init__(metric_updaters, *args, **kwargs)
        self.topic = topic
        self.group = group
        self.brokers = brokers
        self.should_exit = False

    def run(self):
        consumer = KafkaConsumer(self.topic, bootstrap_servers=self.brokers, group_id=self.group)
        for msg in consumer:
            self.update_metrics(msg.value.decode())
            if self.should_exit:
                consumer.close()
                return
