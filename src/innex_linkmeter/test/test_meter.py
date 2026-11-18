from innex_linkmeter.meter import format_reading, kbps, LinkMeter, RED
import pytest


def test_kbps_counts_8_bits_per_byte_and_1000_bits_per_kilobit():
    assert kbps(1000, 1.0) == pytest.approx(8.0)
    assert kbps(500_000, 2.0) == pytest.approx(2000.0)


def test_kbps_is_zero_when_no_time_has_passed():
    assert kbps(1000, 0.0) == 0.0


def test_reading_gives_each_topic_its_rate_over_the_last_window():
    meter = LinkMeter(['/a', '/b'], limit_kbps=3600.0, start=0.0)
    meter.add('/a', 1000)
    meter.add('/a', 1000)
    meter.add('/b', 250)
    reading = meter.read(now=1.0)
    assert reading.topic_kbps == {'/a': pytest.approx(16.0), '/b': pytest.approx(2.0)}
    assert reading.total_kbps == pytest.approx(18.0)


def test_each_reading_starts_a_new_window():
    meter = LinkMeter(['/a'], limit_kbps=3600.0, start=0.0)
    meter.add('/a', 1000)
    meter.read(now=1.0)
    meter.add('/a', 3000)
    assert meter.read(now=3.0).topic_kbps['/a'] == pytest.approx(12.0)


def test_average_covers_everything_since_the_start():
    meter = LinkMeter(['/a'], limit_kbps=3600.0, start=10.0)
    meter.add('/a', 1000)
    meter.read(now=11.0)
    meter.read(now=12.0)
    assert meter.read(now=14.0).average_kbps == pytest.approx(2.0)


def test_over_limit_compares_the_average_not_the_last_second():
    meter = LinkMeter(['/a'], limit_kbps=10.0, start=0.0)
    meter.read(now=9.0)
    meter.add('/a', 10_000)
    reading = meter.read(now=10.0)
    assert reading.total_kbps == pytest.approx(80.0)
    assert reading.average_kbps == pytest.approx(8.0)
    assert not reading.over_limit


def test_table_lists_each_topic_and_the_totals():
    meter = LinkMeter(['/a', '/b'], limit_kbps=3600.0, start=0.0)
    meter.add('/a', 1000)
    lines = format_reading(meter.read(now=1.0), waiting=['/b'])
    assert lines[1].split() == ['/a', '8.0']
    assert lines[2].split() == ['/b', 'waiting']
    assert lines[3].split() == ['Total', '8.0']
    assert not any(RED in line for line in lines)


def test_table_warns_in_red_over_the_limit():
    meter = LinkMeter(['/a'], limit_kbps=1.0, start=0.0)
    meter.add('/a', 1000)
    lines = format_reading(meter.read(now=1.0))
    assert lines[-1].startswith(RED)
    assert 'Over the limit' in lines[-1]
