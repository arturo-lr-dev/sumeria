# Google Calendar Setup Guide

This guide will help you configure Google Calendar integration for the Sumeria MCP Server.

## Prerequisites

- Google account with Google Calendar access
- Google Cloud Project (can be the same one used for Gmail)

## Step 1: Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services** > **Library**
4. Search for "Google Calendar API"
5. Click **Enable**

## Step 2: Create OAuth 2.0 Credentials

### If you already have credentials from Gmail setup:

You can reuse the same OAuth credentials file. Just make sure the Google Calendar API is enabled in your project.

### If you need new credentials:

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - User Type: External (or Internal for Google Workspace)
   - Add your email as a test user
   - Required scopes are automatically added
4. Choose **Desktop app** as the application type
5. Give it a name (e.g., "Sumeria Google Calendar")
6. Click **Create**
7. Download the credentials JSON file
8. Save it to a secure location (e.g., `~/.sumeria/google_calendar_credentials.json`)

## Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Google Calendar Configuration
GOOGLE_CALENDAR_CREDENTIALS_FILE=/path/to/google_calendar_credentials.json

# Optional: Customize token storage location
# GOOGLE_CALENDAR_TOKENS_DIR=tokens/google_calendar

# Optional: Set default account
# GOOGLE_CALENDAR_DEFAULT_ACCOUNT=your.email@gmail.com
```

## Step 4: First-Time Authentication

The first time you use a Google Calendar tool, you'll be prompted to authenticate:

1. A browser window will open automatically
2. Sign in with your Google account
3. Review and accept the requested permissions:
   - View and manage your calendars
   - View and manage events
4. After authorization, the token will be saved locally
5. Future requests will use the saved token (auto-refreshed when expired)

## Step 5: Multi-Account Support

Sumeria supports multiple Google Calendar accounts:

### Adding Additional Accounts

When calling calendar tools, specify the `account_id` parameter:

```python
# First account (will trigger auth flow)
calendar_create_event(
    summary="Meeting",
    start_datetime="2026-01-15T10:00:00",
    end_datetime="2026-01-15T11:00:00",
    provider="google",
    account_id="primary.account@gmail.com"
)

# Second account (will trigger auth flow)
calendar_create_event(
    summary="Personal event",
    start_datetime="2026-01-15T14:00:00",
    end_datetime="2026-01-15T15:00:00",
    provider="google",
    account_id="secondary.account@gmail.com"
)
```

### Token Storage

Each account's token is stored separately:
```
~/.sumeria/tokens/google_calendar/
├── token_primary_account_at_gmail_com.json
└── token_secondary_account_at_gmail_com.json
```

## Step 6: Verify Setup

Test the integration with a simple command:

```python
# List your calendars
calendar_list_calendars(provider="google")

# Create a test event
calendar_create_event(
    summary="Test Event",
    start_datetime="2026-01-15T10:00:00",
    end_datetime="2026-01-15T11:00:00",
    provider="google"
)
```

## Troubleshooting

### "Credentials file not found"
- Check that the path in `GOOGLE_CALENDAR_CREDENTIALS_FILE` is correct
- Ensure the file exists and has proper read permissions

### "OAuth2 flow failed"
- Make sure you've enabled Google Calendar API in your project
- Check that your OAuth consent screen is configured
- Add your email as a test user if using External user type

### "Token refresh failed"
- Delete the token file: `rm ~/.sumeria/tokens/google_calendar/token_*.json`
- Re-authenticate by running any calendar command

### "Permission denied"
- Ensure you granted all requested permissions during OAuth flow
- Check that the OAuth scopes in settings.py include:
  - `https://www.googleapis.com/auth/calendar`
  - `https://www.googleapis.com/auth/calendar.events`

## API Limits

Google Calendar API has the following limits:
- **Quota**: 1,000,000 requests per day
- **Rate limit**: ~10 requests per second per user
- **Batch requests**: Up to 50 operations per batch

The Sumeria server implements automatic retry with exponential backoff to handle rate limits gracefully.

## Security Best Practices

1. **Protect your credentials file**: Never commit it to version control
2. **Use environment variables**: Keep sensitive paths in `.env`
3. **Rotate tokens**: Delete old tokens periodically if accounts are no longer used
4. **Review OAuth scopes**: Only grant necessary permissions
5. **Monitor API usage**: Check Google Cloud Console for unusual activity

## Additional Resources

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [API Rate Limits](https://developers.google.com/calendar/api/guides/quota)
