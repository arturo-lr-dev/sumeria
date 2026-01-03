# Apple Calendar (iCloud) Setup Guide

This guide will help you configure Apple Calendar integration using CalDAV protocol for the Sumeria MCP Server.

## Prerequisites

- Apple ID with iCloud account
- iCloud Calendar enabled

## Step 1: Generate App-Specific Password

Apple requires app-specific passwords for third-party applications accessing iCloud services.

1. Go to [Apple ID Account Page](https://appleid.apple.com/)
2. Sign in with your Apple ID
3. In the **Security** section, click **App-Specific Passwords**
4. Click the **+** button or "Generate an app-specific password"
5. Enter a label (e.g., "Sumeria Calendar")
6. Copy the generated password (format: `xxxx-xxxx-xxxx-xxxx`)
7. **Important**: Save this password securely - you won't be able to see it again!

## Step 2: Find Your CalDAV Server URL

For iCloud Calendar, the CalDAV URL is:
```
https://caldav.icloud.com
```

For other CalDAV providers, consult your provider's documentation.

## Step 3: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Apple Calendar (CalDAV) Configuration
APPLE_CALENDAR_URL=https://caldav.icloud.com
APPLE_CALENDAR_USERNAME=your.apple.id@icloud.com
APPLE_CALENDAR_PASSWORD=xxxx-xxxx-xxxx-xxxx

# Optional: Customize credential storage location
# APPLE_CALENDAR_TOKENS_DIR=tokens/apple_calendar
```

**Security Note**:
- Use the app-specific password, NOT your main Apple ID password
- Never commit `.env` to version control
- Keep credentials secure and private

## Step 4: Test Connection

Test the integration with a simple command:

```python
# List your calendars
calendar_list_calendars(provider="apple")

# Create a test event
calendar_create_event(
    summary="Test Event",
    start_datetime="2026-01-15T10:00:00",
    end_datetime="2026-01-15T11:00:00",
    provider="apple"
)
```

## Step 5: Find Calendar IDs

iCloud uses specific calendar IDs. To find your calendar IDs:

```python
# List all calendars and their IDs
result = calendar_list_calendars(provider="apple")

# Result will show calendars like:
# - id: "work"
# - id: "personal"
# - id: "family"
```

Use these IDs when creating or listing events:

```python
calendar_create_event(
    summary="Work Meeting",
    start_datetime="2026-01-15T14:00:00",
    end_datetime="2026-01-15T15:00:00",
    calendar_id="work",
    provider="apple"
)
```

## CalDAV Protocol Information

### What is CalDAV?

CalDAV is a web-based protocol for accessing and managing calendar data. It's supported by:
- Apple iCloud Calendar
- Google Calendar
- Microsoft Exchange
- Nextcloud
- Many other calendar services

### How It Works

1. Sumeria uses the `caldav` Python library
2. Communicates with the CalDAV server using HTTP/HTTPS
3. Uses iCalendar format for event data
4. Supports all standard calendar operations

## Differences from Google Calendar

| Feature | Google Calendar | Apple Calendar (CalDAV) |
|---------|-----------------|-------------------------|
| Authentication | OAuth 2.0 | App-specific password |
| Protocol | REST API | CalDAV (WebDAV) |
| Multi-account | Full support | Full support |
| Event URLs | HTML links | Not available |
| Free/Busy | Native API | CalDAV query |
| Attachments | Full support | Limited |

## Troubleshooting

### "No credentials available"
- Check that environment variables are set correctly
- Verify `.env` file is in the correct location
- Ensure credentials are not quoted in `.env`

### "Connection failed"
- Verify your Apple ID and app-specific password
- Make sure iCloud Calendar is enabled in your Apple ID settings
- Check that CalDAV URL is correct: `https://caldav.icloud.com`

### "Calendar not found"
- Use `calendar_list_calendars(provider="apple")` to find calendar IDs
- iCloud calendar IDs may be different from their display names
- Use "primary" to access the default calendar

### "Authentication error"
- Regenerate your app-specific password
- Delete stored credentials: `rm ~/.sumeria/tokens/apple_calendar/credentials_*.json`
- Make sure you're using the app-specific password, not your main password

### "Event creation failed"
- Verify datetime format: ISO 8601 (2026-01-15T10:00:00)
- Check that end time is after start time
- Ensure calendar_id exists and is writable

## Rate Limits

iCloud CalDAV has conservative rate limits:
- Approximately **240 requests per hour** per account
- Stricter than Google Calendar
- The server implements retry logic to handle rate limiting

**Best Practices**:
- Batch operations when possible
- Cache calendar lists locally
- Avoid frequent polling for changes

## Multi-Account Support

Like Google Calendar, Apple Calendar supports multiple accounts:

```bash
# In .env, set primary account
APPLE_CALENDAR_USERNAME=primary@icloud.com
APPLE_CALENDAR_PASSWORD=xxxx-xxxx-xxxx-xxxx

# For additional accounts, use account_id parameter
calendar_create_event(
    summary="Event",
    start_datetime="2026-01-15T10:00:00",
    end_datetime="2026-01-15T11:00:00",
    provider="apple",
    account_id="secondary@icloud.com"
)
```

Credentials for each account are stored separately.

## Security Best Practices

1. **Use app-specific passwords**: Never use your main Apple ID password
2. **Revoke unused passwords**: Periodically review and revoke old app passwords
3. **Secure credentials**: Store in `.env`, never in code or version control
4. **Monitor access**: Check Apple ID security settings for active app passwords
5. **Rotate regularly**: Generate new app-specific passwords periodically

## Alternative CalDAV Providers

This integration works with any CalDAV-compatible server. Just change the URL:

### Nextcloud
```bash
APPLE_CALENDAR_URL=https://nextcloud.example.com/remote.php/dav
```

### Baikal
```bash
APPLE_CALENDAR_URL=https://baikal.example.com/dav.php
```

### Radicale
```bash
APPLE_CALENDAR_URL=https://radicale.example.com
```

Consult your provider's documentation for the correct CalDAV URL.

## Additional Resources

- [iCloud CalDAV Documentation](https://developer.apple.com/library/archive/documentation/DataManagement/Conceptual/CalendarStoreProg/Introduction/Introduction.html)
- [CalDAV Protocol Specification (RFC 4791)](https://tools.ietf.org/html/rfc4791)
- [iCalendar Format (RFC 5545)](https://tools.ietf.org/html/rfc5545)
- [Apple ID App-Specific Passwords](https://support.apple.com/en-us/HT204397)

## Comparison: When to Use Which Provider

### Use Google Calendar if:
- You need HTML event links
- You want OAuth 2.0 authentication
- You need higher API rate limits
- You want better third-party integration

### Use Apple Calendar if:
- You're already in the Apple ecosystem
- You prefer CalDAV standard protocol
- You want cross-platform compatibility
- You use other CalDAV-compatible tools

Both providers are fully supported and offer the same core functionality in Sumeria.
