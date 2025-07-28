"""
This script helps you follow the Hi5 portfolio's DCA/BTD investment rules
outlined on TheMarketMemo's Hi5 page.  According to those rules, the
portfolio consists of five exchange‑traded funds (ETFs)—IWY, RSP, MOAT,
PFF and VNQ—and contributions are made at most three times per month.
Each contribution is split equally among all five ETFs.  The
first contribution is triggered when the equal‑weight S&P 500 index (ETF
symbol RSP) drops at least 1 % on the first trading day of a month; if
that doesn't happen, the first contribution occurs on the third Friday of
the month.  A second contribution is made if RSP subsequently falls at
least 5 % from its price at the beginning of the month.  A third
contribution is made if the market experiences an even more extreme
pullback.  When a contribution occurs, this script sends an email
reminder telling you to buy equal amounts of all five ETFs.  It also
ensures that no more than three reminders are sent per month.

This program is for informational purposes only and does not constitute
financial advice.  Always consult a qualified financial professional
before making investment decisions.
"""

import datetime
import json
import os
import smtplib
import time
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional

import pandas as pd
import yfinance as yf


@dataclass
class ReminderState:
    """Tracks how many reminders have been sent in the current month."""

    year: int
    month: int
    reminders_sent: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "year": self.year,
            "month": self.month,
            "reminders_sent": self.reminders_sent,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, int]) -> "ReminderState":
        return cls(year=d["year"], month=d["month"], reminders_sent=d["reminders_sent"])


STATE_FILE = os.path.join(os.path.dirname(__file__), "hi5_state.json")
ETF_LIST = ["IWY", "RSP", "MOAT", "PFF", "VNQ"]


def load_state(today: datetime.date) -> ReminderState:
    """Load the state from disk or create a new state for the current month."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            state = ReminderState.from_dict(data)
            # Reset state if it's a new month
            if state.year != today.year or state.month != today.month:
                state = ReminderState(year=today.year, month=today.month, reminders_sent=0)
        except Exception:
            # If the file is corrupted, start fresh
            state = ReminderState(year=today.year, month=today.month, reminders_sent=0)
    else:
        state = ReminderState(year=today.year, month=today.month, reminders_sent=0)
    return state


def save_state(state: ReminderState) -> None:
    """Persist the current state to disk."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f)


def is_weekday(date: datetime.date) -> bool:
    """Return True if the date is a weekday (Mon–Fri)."""
    return date.weekday() < 5


def first_trading_day_of_month(date: datetime.date) -> datetime.date:
    """Compute the first weekday (Monday through Friday) in the given month."""
    d = date.replace(day=1)
    while not is_weekday(d):
        d += datetime.timedelta(days=1)
    return d


def third_friday_of_month(date: datetime.date) -> datetime.date:
    """Compute the third Friday of the month for the given date."""
    # Start with the first day of the month
    d = date.replace(day=1)
    friday_count = 0
    while True:
        if d.weekday() == 4:  # 4 corresponds to Friday
            friday_count += 1
            if friday_count == 3:
                return d
        d += datetime.timedelta(days=1)


def fetch_rsp_prices(start_date: datetime.date, end_date: datetime.date) -> Optional[pd.DataFrame]:
    """Fetch daily closing prices for RSP between start_date and end_date.

    Uses yfinance to download historical price data.  Returns None if data
    cannot be fetched (e.g., network problems).
    """
    try:
        ticker = yf.Ticker("RSP")
        df = ticker.history(start=start_date, end=end_date, interval="1d")
        if df.empty:
            return None
        return df
    except Exception:
        return None


def percent_change(current: float, previous: float) -> float:
    """Calculate percent change between two numbers."""
    if previous == 0:
        return 0.0
    return (current - previous) / previous * 100


def should_trigger_first_reminder(today: datetime.date, rsp_prices: pd.DataFrame) -> bool:
    """Determine whether the first reminder should be triggered.

    The first reminder fires when the RSP ETF drops at least 1 % on the first
    trading day of the month.  The drop is measured as the percentage change
    between the close of the first trading day and the previous trading day.
    """
    # Determine the first trading day of the month
    first_trade_day = first_trading_day_of_month(today)
    if today != first_trade_day:
        return False

    # Extract two consecutive rows around the first trading day
    # We need the previous close (last row before first_trade_day) and the
    # close on the first_trade_day
    try:
        idx = rsp_prices.index.get_loc(pd.Timestamp(first_trade_day))
        if idx == 0:
            return False
        prev_close = float(rsp_prices.iloc[idx - 1]["Close"])
        current_close = float(rsp_prices.iloc[idx]["Close"])
        change_pct = percent_change(current_close, prev_close)
        return change_pct <= -1.0
    except (KeyError, IndexError):
        return False


def should_trigger_second_reminder(
    start_of_month_price: float, current_price: float
) -> bool:
    """Trigger the second reminder when RSP falls at least 5 % from the month start."""
    drop_pct = percent_change(current_price, start_of_month_price)
    return drop_pct <= -5.0


def send_email_reminder(reminder_number: int, today: datetime.date) -> None:
    """Send a reminder email to buy equal amounts of all ETFs."""
    try:
        # Get email configuration from environment variables
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("STOCK_EMAIL_SENDER")
        sender_password = os.getenv("STOCK_EMAIL_PASSWORD")
        receiver_email = os.getenv("STOCK_EMAIL_RECEIVER")
        
        if not all([sender_email, sender_password, receiver_email]):
            print(f"[{today}] Warning: Email configuration incomplete. Using print instead.")
            print_reminder(reminder_number, today)
            return
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = f"Hi5 ETF Investment Reminder #{reminder_number} - {today}"
        
        # Create email body
        body = f"""
Hi5 ETF Investment Reminder #{reminder_number}
Date: {today}

It's time to buy equal amounts of these five ETFs:
• IWY (iShares Russell Top 200 Growth ETF)
• RSP (Invesco S&P 500 Equal Weight ETF)
• MOAT (VanEck Morningstar Wide Moat ETF)
• PFF (iShares Preferred & Income Securities ETF)
• VNQ (Vanguard Real Estate Index Fund ETF)

Investment Strategy:
- Split your investment equally among all five ETFs
- This follows the Hi5 portfolio DCA/BTD strategy
- Maximum 3 reminders per month

Reminder: This is for informational purposes only and does not constitute 
financial advice. Always consult a qualified financial professional 
before making investment decisions.

Happy investing!
        """
        
        message.attach(MIMEText(body, "plain"))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
            
        print(f"[{today}] Email reminder #{reminder_number} sent successfully to {receiver_email}")
        
    except Exception as e:
        print(f"[{today}] Error sending email: {e}")
        print(f"[{today}] Falling back to print reminder:")
        print_reminder(reminder_number, today)


def print_reminder(reminder_number: int, today: datetime.date) -> None:
    """Print a reminder to buy equal amounts of all ETFs (fallback method)."""
    print(
        f"[{today}] Reminder #{reminder_number}: Time to buy equal amounts of these five ETFs: "
        f"{', '.join(ETF_LIST)}."
    )


def daily_check() -> None:
    """
    Run this function daily to evaluate whether a contribution should be made.

    The logic implements the Hi5 trading rules:
      1. On the first trading day of the month, if RSP drops 1 % or more from the
         previous trading day, send the first reminder.
      2. If the first reminder hasn't been sent and it's the third Friday of the
         month, send the first reminder regardless of market movement.
      3. After the first reminder has been sent, if RSP falls 5 % or more from
         the start‐of‐month price, send the second reminder.

    Each reminder advises buying all five ETFs in equal dollar amounts.
    """
    today = datetime.date.today()
    state = load_state(today)
    print(f"[{today}] Daily check: Current state - Year: {state.year}, Month: {state.month}, Reminders sent: {state.reminders_sent}")
    
    # Only run checks on weekdays
    if not is_weekday(today):
        print(f"[{today}] Today is not a weekday. Skipping check.")
        return

    # Load RSP price data from the last 30 days to ensure we have enough history
    start_of_month = today.replace(day=1)
    # We'll fetch from the last day of the previous month to today
    fetch_start = start_of_month - datetime.timedelta(days=5)
    rsp_data = fetch_rsp_prices(fetch_start, today + datetime.timedelta(days=1))
    if rsp_data is None or rsp_data.empty:
        # If we can't fetch data, skip the check for today
        print(f"[{today}] Could not fetch RSP price data. Skipping check.")
        return

    print(f"[{today}] Fetched RSP data: {len(rsp_data)} rows from {rsp_data.index[0].date()} to {rsp_data.index[-1].date()}")

    # Determine the first trading day of the current month
    first_trade_day = first_trading_day_of_month(today)

    # Compute the start of month price (close on the first trading day)
    start_price = None
    if pd.Timestamp(first_trade_day) in rsp_data.index:
        start_price = float(rsp_data.loc[pd.Timestamp(first_trade_day)]["Close"])
        print(f"[{today}] Start of month price (first trading day {first_trade_day}): ${start_price:.2f}")

    # Check if we need to trigger the first reminder
    if state.reminders_sent == 0:
        print(f"[{today}] No reminders sent yet this month. Checking first reminder conditions.")
        
        # Condition 1: first trading day drop of at least 1 %
        if should_trigger_first_reminder(today, rsp_data):
            print(f"[{today}] First trading day drop condition met!")
            state.reminders_sent += 1
            send_email_reminder(state.reminders_sent, today)
            save_state(state)
            return

        # Condition 2: fallback on the third Friday if condition 1 never occurred
        third_friday = third_friday_of_month(today)
        if today == third_friday:
            print(f"[{today}] Third Friday condition met!")
            state.reminders_sent += 1
            send_email_reminder(state.reminders_sent, today)
            save_state(state)
            return
            
        print(f"[{today}] No first reminder conditions met. Third Friday is {third_friday}.")
        
    # After the first reminder, check for second reminder conditions
    elif state.reminders_sent == 1 and start_price is not None:
        print(f"[{today}] First reminder already sent. Checking second reminder conditions.")
        
        # Get current closing price (most recent available)
        current_price = float(rsp_data.iloc[-1]["Close"])
        print(f"[{today}] Current price: ${current_price:.2f}")
        
        if should_trigger_second_reminder(start_price, current_price):
            print(f"[{today}] Second reminder condition met (5% drop from start of month)!")
            state.reminders_sent += 1
            send_email_reminder(state.reminders_sent, today)
            save_state(state)
            return
            
        drop_pct = percent_change(current_price, start_price)
        print(f"[{today}] Current drop from start of month: {drop_pct:.2f}% (need -5.0% for second reminder)")
        
    elif state.reminders_sent >= 2:
        print(f"[{today}] Maximum reminders ({state.reminders_sent}) already sent this month.")
    
    else:
        print(f"[{today}] No conditions met for reminders.")

    # Additional reminders (e.g., for extreme conditions) could be implemented here


def main() -> None:
    """Entry point: run the daily check once (designed for GitHub Actions)."""
    print(f"Hi5 ETF Reminder check started at {datetime.datetime.now()}")
    daily_check()
    print(f"Hi5 ETF Reminder check completed at {datetime.datetime.now()}")


def main_loop() -> None:
    """Alternative entry point: run a loop that performs the daily check at 15:30 local time."""
    # Track the last day on which we performed the daily check to avoid
    # triggering multiple reminders in a single day.
    last_checked_date: Optional[datetime.date] = None
    print("Starting Hi5 ETF Reminder loop. Checking daily at 15:30 local time.")
    
    while True:
        now = datetime.datetime.now()
        today_date = now.date()
        # Run the daily check at 15:30 (3:30 PM) local time.  This time is
        # approximately half an hour before the US market close, allowing you to
        # place an order before the day ends.  Adjust the hour and minute
        # values below if you'd like a different reminder time.
        if now.hour == 15 and now.minute == 30 and last_checked_date != today_date:
            daily_check()
            last_checked_date = today_date
        time.sleep(30)


if __name__ == "__main__":
    main()