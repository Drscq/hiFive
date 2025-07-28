#!/usr/bin/env python3
"""
Test email functionality for Hi5 ETF Reminder
"""

import os
from hi5_etf_reminder import send_email_reminder
import datetime

def test_email():
    """Test sending an email reminder."""
    print("Testing email functionality...")
    
    # Check if environment variables are set
    sender = os.getenv("STOCK_EMAIL_SENDER")
    password = os.getenv("STOCK_EMAIL_PASSWORD") 
    receiver = os.getenv("STOCK_EMAIL_RECEIVER")
    
    print(f"Sender: {sender}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    print(f"Receiver: {receiver}")
    
    if not all([sender, password, receiver]):
        print("\n❌ Email environment variables not all set.")
        print("Set them with:")
        print('export STOCK_EMAIL_SENDER="your.email@gmail.com"')
        print('export STOCK_EMAIL_PASSWORD="your-app-password"')
        print('export STOCK_EMAIL_RECEIVER="your.email@gmail.com"')
        return
    
    print("\n✅ All email environment variables are set.")
    print("Sending test email...")
    
    # Send test email
    today = datetime.date.today()
    send_email_reminder(999, today)  # Test reminder with number 999

if __name__ == "__main__":
    test_email()
