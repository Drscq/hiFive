#!/usr/bin/env python3
"""
Test email functionality for Hi5 ETF Reminder - GitHub Actions compatible
"""

import os
import sys
import datetime
from hi5_etf_reminder import send_email_reminder

def test_email():
    """Test sending an email reminder."""
    print("=" * 50)
    print("Testing Hi5 ETF Email Configuration")
    print("=" * 50)
    
    # Check if environment variables are set
    sender = os.getenv("STOCK_EMAIL_SENDER")
    password = os.getenv("STOCK_EMAIL_PASSWORD") 
    receiver = os.getenv("STOCK_EMAIL_RECEIVER")
    
    # GitHub Actions context (if running in GitHub Actions)
    github_event = os.getenv("GITHUB_EVENT")
    github_ref = os.getenv("GITHUB_REF")
    github_sha = os.getenv("GITHUB_SHA")
    
    if github_event:
        print(f"🚀 Running in GitHub Actions")
        print(f"📋 Event: {github_event}")
        print(f"🌿 Branch: {github_ref}")
        print(f"📝 Commit: {github_sha[:8]}..." if github_sha else "unknown")
        print()
    
    print(f"📧 Sender: {sender if sender else '❌ NOT SET'}")
    print(f"🔐 Password: {'✅ SET' if password else '❌ NOT SET'}")
    print(f"📬 Receiver: {receiver if receiver else '❌ NOT SET'}")
    print()
    
    if not all([sender, password, receiver]):
        print("❌ ERROR: Email environment variables not all set.")
        print("\nRequired GitHub Secrets:")
        print("• STOCK_EMAIL_SENDER: Your Gmail address")
        print("• STOCK_EMAIL_PASSWORD: Your Gmail app password")  
        print("• STOCK_EMAIL_RECEIVER: Email to receive notifications")
        print("\nTo set up GitHub Secrets:")
        print("1. Go to your repository Settings")
        print("2. Click 'Secrets and variables' → 'Actions'")
        print("3. Click 'New repository secret' for each variable")
        
        # Exit with error code for GitHub Actions
        sys.exit(1)
    
    print("✅ All email environment variables are set!")
    print("🧪 Sending test email...")
    print()
    
    try:
        # Send test email
        today = datetime.date.today()
        send_email_reminder(999, today)  # Test reminder with number 999
        print("✅ Email test completed successfully!")
        print("📨 Check your inbox for the test email.")
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_email()
