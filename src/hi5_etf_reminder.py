"""Utility: 检查 Invesco S&P 500 Equal Weight ETF (RSP) 当日收盘价相对前一交易日是否下跌≥1%。"""

from __future__ import annotations

from typing import Optional
from datetime import date, timedelta
import pandas as pd


def _download_rsp_history():  # pragma: no cover - 简单包装提供可测性
	"""封装 yfinance 下载调用，方便在单元测试中 monkeypatch。"""
	try:
		import yfinance as yf  # 延迟导入
	except Exception:
		return None
	try:
		return yf.download(
			"RSP",
			period="14d",
			interval="1d",
			auto_adjust=False,
			progress=False,
		)
	except Exception:
		return None

def _get_latest_close(df: pd.DataFrame) -> Optional[tuple[float, pd.Timestamp]]:
	"""返回最新 Close 及其时间戳；失败/数据不足返回 None。"""
	if df is None or getattr(df, "empty", True):
		return None

	cols = df.columns
	if "Close" in cols:
		s = df["Close"]
	elif isinstance(cols, pd.MultiIndex):
		# 取末级名为 Close 的第一列
		close_cols = [c for c in cols if isinstance(c, tuple) and c[-1] == "Close"]
		if not close_cols:
			return None
		s = df[close_cols[0]]
	else:
		return None

	s = s.dropna()
	if s.empty:
		return None

	val = s.iloc[-1]
	if isinstance(val, pd.Series):  # 某些 MultiIndex 情况
		val = val.iloc[0]
	try:
		latest_close = float(val)
	except (TypeError, ValueError):
		return None

	idx_val = s.index[-1]
	ts_any = pd.to_datetime(idx_val, errors="coerce")
	if isinstance(ts_any, pd.DatetimeIndex):
		ts = ts_any[0] if len(ts_any) else pd.NaT
	else:
		# already scalar Timestamp / datetime-like
		ts = ts_any  # type: ignore[assignment]
	if not isinstance(ts, pd.Timestamp):
		# fallback convert
		try:
			ts = pd.Timestamp(ts)  # type: ignore[arg-type]
		except Exception:
			return None
	return (latest_close, ts)

def has_rsp_daily_drop_reached_minus_1pct() -> bool:
	"""判断最新交易日开盘价 (Open) 相对前一交易日收盘价 (Close) 是否出现 ≥1% 跳空下跌。

	你最近把 latest_close 改成了 "Start"，推测意图是想用“开盘价”而不是“收盘价”来衡量当日相对前日的跌幅（即检测是否跳空下跌 ≥1%）。

	实现逻辑（Gap Down 判定）：
		prev_close = 前一交易日 Close
		latest_open = 最新交易日 Open（若缺失则回退到最新交易日 Close）
		pct_change = (latest_open - prev_close) / prev_close
		若 pct_change <= -0.01 -> True

	数据来源: yfinance 日线 (未复权)。

	注意:
		1. 只有在最新交易日的开盘数据已经生成后此逻辑才有意义；若在开盘前调用，最新行的 Open 可能不存在或仍是前一日。
		2. 若需要使用收盘对比，请恢复为使用最新 Close。
		3. 异常 / 数据不足均返回 False。

	Returns:
		bool: True 表示最新开盘较前一收盘跳空下跌达到或超过 1%；否则 False。
	"""
	try:
		df = _download_rsp_history()
	except Exception:  # 容错：内部 helper 抛出异常
		return False
	if df is None or df is False or getattr(df, 'empty', True):
		return False

	def _get_series(name: str):
		# 直接列名
		if name in df.columns:
			return df[name]
		# MultiIndex: 寻找末级匹配
		if isinstance(df.columns, pd.MultiIndex):
			for col in df.columns:
				if isinstance(col, tuple) and col[-1] == name:
					return df[col]
		return None

	close_s = _get_series("Close")
	open_s = _get_series("Open")
	if close_s is None:
		return False

	# 清理缺失 close，要求至少两条
	close_s = close_s.dropna()
	if len(close_s) < 2:
		return False

	# 取最后两个索引
	last_two_idx = close_s.index[-2:]
	_prev_series = close_s.loc[last_two_idx[0]]
	if isinstance(_prev_series, (pd.Series, list, tuple)):
		prev_close = float(_prev_series.iloc[0]) if isinstance(_prev_series, pd.Series) else float(_prev_series[0])
	else:
		prev_close = float(_prev_series)
	# latest open 优先；若为缺失或不存在则回退 close
	latest_open_val = None
	if open_s is not None and last_two_idx[-1] in open_s.index:
		_val_candidate = open_s.loc[last_two_idx[-1]]
		if isinstance(_val_candidate, pd.Series):
			_val_candidate = _val_candidate.iloc[0]
		if not pd.isna(_val_candidate):
			latest_open_val = float(_val_candidate)

	_latest_close_candidate = close_s.loc[last_two_idx[-1]]
	if isinstance(_latest_close_candidate, pd.Series):
		_latest_close_candidate = _latest_close_candidate.iloc[0]
	latest_price = latest_open_val if latest_open_val is not None else float(_latest_close_candidate)

	if prev_close <= 0:
		return False

	pct_change = (latest_price - prev_close) / prev_close
	return pct_change <= -0.01


def _today_date() -> date:  # pragma: no cover - 单独封装方便测试 monkeypatch
	"""Return today's date (system local). Isolated for test monkeypatching."""
	return date.today()


def is_third_friday_this_month() -> bool:
	"""判断今天是否为当月的第三个周五 (纯日历计算)。

	规则:
		1. 使用系统本地当前日期 (无时区转换)。
		2. 计算当月第一天开始的第一个周五，然后加 14 天得到第三个周五。
		3. 若今天等于该日期 -> True，否则 False。

	无市场假期调整 (即若第三个周五是假期仍返回 True)。

	Returns:
		bool: True 当且仅当今天是该月第三个周五。
	"""
	today = _today_date()
	first_day = today.replace(day=1)
	# Python: Monday=0 ... Friday=4
	days_until_first_friday = (4 - first_day.weekday()) % 7
	first_friday = first_day + timedelta(days=days_until_first_friday)
	third_friday = first_friday + timedelta(days=14)
	return today == third_friday


def is_last_day_this_month() -> bool:
    """判断今天是否为当月的最后一个自然日。

    规则:
        1. 使用系统本地当前日期 (无时区转换)。
        2. 计算下个月第一天，然后减一天得到本月最后一天。
        3. 若今天等于该日期 -> True，否则 False。

    Returns:
        bool: True 当且仅当今天是该月最后一天。
    """
    today = _today_date()
    if today.month == 12:
        next_month_first_day = today.replace(year=today.year + 1, month=1, day=1)
    else:
        next_month_first_day = today.replace(month=today.month + 1, day=1)
    last_day = next_month_first_day - timedelta(days=1)
    return today == last_day


__all__ = [
	"has_rsp_daily_drop_reached_minus_1pct",
	"is_third_friday_this_month",
	"is_last_day_this_month",
]

