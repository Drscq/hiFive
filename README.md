# Hi5 ETF Reminder - GitHub Actions Setup

This document explains how to set up the Hi5 ETF Reminder to run automatically using GitHub Actions and send email notifications.

## Features

- **Automated Daily Checks**: Runs every weekday at 3:30 PM UTC (30 minutes before US market close)
- **Email Notifications**: Sends Gmail notifications instead of console output
- **State Persistence**: Maintains reminder state across runs using GitHub Actions cache
- **Manual Triggers**: Can be triggered manually from GitHub Actions tab

## Usage

1. How to activate the venv
```
cd /hiFive
source venv/bin/activate
pytest -s
```

## Setup Instructions

### 1. Repository Setup

1. Create a new GitHub repository
2. Upload these files to your repository:
   - `hi5_etf_reminder.py` (main script)
   - `requirements.txt` (Python dependencies)
   - `.github/workflows/hi5_daily_check.yml` (GitHub Actions workflow)

### 2. Email Configuration

You need to set up Gmail app passwords and configure GitHub secrets:

#### Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Save this password (you'll need it for GitHub secrets)

#### GitHub Secrets Setup

Go to your repository → Settings → Secrets and variables → Actions, then add these secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `STOCK_EMAIL_SENDER` | Your Gmail address | `your.email@gmail.com` |
| `STOCK_EMAIL_PASSWORD` | Gmail app password | `abcd efgh ijkl mnop` |
| `STOCK_EMAIL_RECEIVER` | Email to receive notifications | `your.email@gmail.com` |

### 3. Workflow Schedule

The workflow runs automatically:
- **Time**: 3:30 PM UTC (15:30)
- **Days**: Monday to Friday (weekdays only)
- **Timezone Note**: 3:30 PM UTC = 10:30 AM EST / 11:30 AM EDT

You can adjust the schedule by editing the cron expression in `.github/workflows/hi5_daily_check.yml`:

```yaml
schedule:
  - cron: '30 15 * * 1-5'  # 30 minutes, 15 hours, any day, any month, Mon-Fri
```

### 4. Manual Testing

You can manually trigger the workflow:

1. Go to your repository on GitHub
2. Click "Actions" tab
3. Select "Hi5 ETF Daily Check" workflow
4. Click "Run workflow" button

## How It Works

### Hi5 Investment Rules

The script implements the Hi5 portfolio strategy:

1. **First Reminder**: Triggered when:
   - RSP drops 1%+ on the first trading day of the month, OR
   - It's the third Friday of the month (fallback)

2. **Second Reminder**: Triggered when:
   - RSP falls 5%+ from the start-of-month price

3. **Maximum**: 3 reminders per month

### Email Content

Email notifications include:
- Reminder number and date
- List of five ETFs to buy (IWY, RSP, MOAT, PFF, VNQ)
- Investment strategy notes
- Financial disclaimer

### State Management

The script maintains state using:
- `hi5_state.json` file with reminder count per month
- GitHub Actions cache for persistence across runs
- Automatic reset at the beginning of each month

## Troubleshooting

### Email Issues

If emails aren't being sent:

1. **Check GitHub Secrets**: Ensure all three email secrets are set correctly
2. **Verify App Password**: Make sure you're using an app password, not your regular Gmail password
3. **Check Logs**: View the GitHub Actions logs for error messages

### Workflow Issues

If the workflow doesn't run:

1. **Repository Activity**: GitHub disables workflows after 60 days of repository inactivity
2. **Permissions**: Ensure GitHub Actions are enabled for your repository
3. **Branch**: Make sure the workflow file is in the default branch (usually `main`)

### Testing Locally

To test the script locally with email:

```bash
# Set environment variables
export STOCK_EMAIL_SENDER="your.email@gmail.com"
export STOCK_EMAIL_PASSWORD="your-app-password"
export STOCK_EMAIL_RECEIVER="your.email@gmail.com"

# Run the script
python hi5_etf_reminder.py
```

## File Structure

```
hiFive/
├── .github/
│   └── workflows/
│       └── hi5_daily_check.yml    # GitHub Actions workflow
├── hi5_etf_reminder.py            # Main script
├── requirements.txt               # Python dependencies
├── hi5_state.json                 # State file (auto-generated)
└── README.md                      # This file
```

## Security Notes

- **Never commit passwords** or secrets to your repository
- Use GitHub secrets for all sensitive information
- App passwords are safer than regular passwords for automated scripts
- The script only reads public market data from Yahoo Finance

## Customization

### Changing the Schedule

Edit the cron expression in the workflow file:
- `0 14 * * 1-5` = 2:00 PM UTC
- `0 20 * * 1-5` = 8:00 PM UTC (3:00 PM EST/4:00 PM EDT)

### Adding More ETFs

Edit the `ETF_LIST` in `hi5_etf_reminder.py`:

```python
ETF_LIST = ["IWY", "RSP", "MOAT", "PFF", "VNQ", "NEW_ETF"]
```

### Changing Thresholds

Modify the percentage thresholds in the respective functions:
- `should_trigger_first_reminder()`: Currently -1%
- `should_trigger_second_reminder()`: Currently -5%

## Support

For issues or questions:
1. Check the GitHub Actions logs for error details
2. Verify your email configuration
3. Test the script locally first
4. Review the Hi5 investment strategy documentation

---

**Disclaimer**: This tool is for informational purposes only and does not constitute financial advice. Always consult a qualified financial professional before making investment decisions.
