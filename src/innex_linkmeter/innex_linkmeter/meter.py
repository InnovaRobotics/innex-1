"""Turn message byte counts and times into link rates. No ROS in this module."""

from dataclasses import dataclass

RED = '\033[31m'
RESET = '\033[0m'


def kbps(num_bytes, seconds):
    """Return kilobits per second, with 1 kbps = 1,000 bits per second."""
    if seconds <= 0:
        return 0.0
    return num_bytes * 8 / 1000 / seconds


@dataclass(frozen=True)
class Reading:
    topic_kbps: dict
    total_kbps: float
    average_kbps: float
    limit_kbps: float

    @property
    def over_limit(self):
        return self.average_kbps > self.limit_kbps


class LinkMeter:
    """Count bytes per topic and report the rate since the last reading."""

    def __init__(self, topics, limit_kbps, start):
        self._limit_kbps = limit_kbps
        self._start = start
        self._last = start
        self._window = dict.fromkeys(topics, 0)
        self._total_bytes = 0

    def add(self, topic, num_bytes):
        self._window[topic] += num_bytes
        self._total_bytes += num_bytes

    def read(self, now):
        """Return the rates since the last reading, and the average since the start."""
        window = now - self._last
        topic_kbps = {topic: kbps(n, window) for topic, n in self._window.items()}
        reading = Reading(
            topic_kbps=topic_kbps,
            total_kbps=sum(topic_kbps.values()),
            average_kbps=kbps(self._total_bytes, now - self._start),
            limit_kbps=self._limit_kbps,
        )
        self._window = dict.fromkeys(self._window, 0)
        self._last = now
        return reading


def format_reading(reading, waiting=()):
    """Return the terminal table for a reading, one string per line."""
    width = max([len(t) for t in reading.topic_kbps] + [len('Average since start')])
    lines = [f'{"Topic":<{width}}  {"kbps":>10}']
    for topic, rate in reading.topic_kbps.items():
        rate_text = 'waiting' if topic in waiting else f'{rate:,.1f}'
        lines.append(f'{topic:<{width}}  {rate_text:>10}')
    lines.append(f'{"Total":<{width}}  {reading.total_kbps:>10,.1f}')
    lines.append(f'{"Average since start":<{width}}  {reading.average_kbps:>10,.1f}')
    if reading.over_limit:
        lines.append(
            f'{RED}Over the limit: the average is {reading.average_kbps:,.1f} kbps, '
            f'the limit is {reading.limit_kbps:,.1f} kbps{RESET}')
    return lines
