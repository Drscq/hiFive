import pandas as pd
import pytest

import hi5_etf_reminder as mod


def test__download_rsp_history():
    df = mod._download_rsp_history()
    assert isinstance(df, pd.DataFrame)
    assert "Close" in df.columns
    assert len(df) > 0

def test_has_rsp_daily_drop_reached_minus_1pct():
    res = mod.has_rsp_daily_drop_reached_minus_1pct()
    assert isinstance(res, bool)


def test__get_latest_close():
    df = mod._download_rsp_history()
    res = mod._get_latest_close(df)
    if res is not None:
        latest_close, ts = res
        assert isinstance(latest_close, float)
        # ts 可为 NaT，但类型应是 pd.Timestamp
        assert isinstance(ts, pd.Timestamp)
        print(f"Latest close price: {latest_close} at {ts}")


@pytest.mark.parametrize(
    "fake_today, expected",
    [
        (pd.Timestamp("2025-09-19").date(), True),  # 2025-09 third Friday
        (pd.Timestamp("2025-09-12").date(), False),
        (pd.Timestamp("2025-09-26").date(), False),
        (pd.Timestamp("2025-03-21").date(), True),  # 2025-03 third Friday
        (pd.Timestamp("2025-03-14").date(), False),
    ],
)
def test_is_third_friday_this_month(monkeypatch, fake_today, expected):
    monkeypatch.setattr(mod, "_today_date", lambda: fake_today)
    assert mod.is_third_friday_this_month() is expected


@pytest.mark.parametrize(
    "fake_today, expected",
    [
        (pd.Timestamp("2025-09-30").date(), True),  # last day Sept
        (pd.Timestamp("2025-09-29").date(), False),
        (pd.Timestamp("2024-02-29").date(), True),  # leap year Feb
        (pd.Timestamp("2025-02-28").date(), True),  # non-leap Feb
        (pd.Timestamp("2025-02-27").date(), False),
        (pd.Timestamp("2025-04-30").date(), True),  # 30-day month
        (pd.Timestamp("2025-04-29").date(), False),
    ],
)
def test_is_last_day_this_month(monkeypatch, fake_today, expected):
    monkeypatch.setattr(mod, "_today_date", lambda: fake_today)
    assert mod.is_last_day_this_month() is expected

def test_is_third_friday_this_month_real_date():
    # 仅打印结果，实际日期会变化
    res = mod.is_third_friday_this_month()
    print(f"Today is {mod._today_date()}, is third Friday this month? {res}")