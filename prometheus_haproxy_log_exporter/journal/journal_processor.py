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

from systemd import journal

from ..log_processing import AbstractLogProcessor


class JournalProcessor(AbstractLogProcessor):
    def __init__(self, unit, *args, **kwargs):
        super(JournalProcessor, self).__init__(*args, **kwargs)

        self.unit = unit
        self.should_exit = False

    def run(self):
        with journal.Reader() as j:
            j.add_match(_SYSTEMD_UNIT=self.unit)

            j.seek_tail()
            j.get_previous()

            while True:
                if self.should_exit:
                    return
                for entry in j:
                    self.update_metrics(entry['MESSAGE'])
                j.wait()
