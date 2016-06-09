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

import tailhead

from ..log_processing import AbstractLogProcessor


class LogFileProcessor(AbstractLogProcessor):
    def __init__(self, metric_updaters, path, *args, **kwargs):
        super().__init__(metric_updaters, *args, **kwargs)
        self.path = path

    def run(self):
        for line in tailhead.follow_path(self.path):
            self.update_metrics(line)
