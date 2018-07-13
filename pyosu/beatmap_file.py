# MIT License

# Copyright (c) 2018 Renondedju

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re

from .base_model import BaseModel

class BeatmapFile(BaseModel):
    """ Beatmap file model.
    
    This model is way heavier than a classic Beatmap object (3Kb to 1Mb) since
    it contains the beatmap file. If you don't really need it, don't use it !
    """

    def __init__(self, api : 'OsuApi', **data):

        super().__init__(api, **data)

        self.content = data.get('content', '')
        self.version = self.parse_version()

    def parse_version(self):

        regex   = r"osu file format v(\d*)"
        matches = re.search(regex, self.content, re.IGNORECASE)

        return int(matches.group(1))