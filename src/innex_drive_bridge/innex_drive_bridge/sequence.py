# Copyright 2026 Leo-P-1109
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Reserve persistent sequence ranges to avoid reuse after a host restart."""

import fcntl
import os
from pathlib import Path


class SequenceCounter:
    """Hold a process lock and reserve ranges before any frame is sent."""

    def __init__(self, state_path=None, block_size=65536):
        """Use volatile numbering only for dry-run or isolated test sessions."""
        if not 1 <= block_size < 0x80000000:
            raise ValueError('Invalid sequence reservation size')
        self.file = None
        self.block_size = block_size
        self.remaining = block_size
        self.current = 0
        if state_path is None:
            return
        path = Path(state_path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        created = False
        try:
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
            created = True
        except FileExistsError:
            fd = os.open(path, os.O_RDWR)
        self.file = os.fdopen(fd, 'r+')
        try:
            fcntl.flock(self.file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            text = self.file.read().strip()
            if not created:
                if not text.isdecimal() or not 0 <= int(text) <= 0xFFFFFFFF:
                    raise ValueError('Invalid sequence state; do not reset it blindly')
                self.current = int(text)
            self._reserve()
        except BaseException:
            self.close()
            raise

    def _reserve(self):
        """Persist the next unused range before returning a sequence in it."""
        if self.file is not None:
            self.file.seek(0)
            self.file.write(str((self.current + self.block_size) & 0xFFFFFFFF) + '\n')
            self.file.truncate()
            self.file.flush()
            os.fsync(self.file.fileno())
        self.remaining = self.block_size

    def take(self):
        """Return a new sequence with uint32 wraparound."""
        if self.remaining == 0:
            self._reserve()
        value = self.current
        self.current = (value + 1) & 0xFFFFFFFF
        self.remaining -= 1
        return value

    def close(self):
        """Release the exclusive state-file lock."""
        if self.file is not None:
            self.file.close()
            self.file = None
