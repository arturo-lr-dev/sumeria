# Gmail Setup Guide

This guide will help you configure Gmail OAuth2 authentication for the Sumeria Personal Assistant.

## Prerequisites

- A Google account with Gmail access
- Python 3.10+ installed
- Access to Google Cloud Console

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it something like "Sumeria Personal Assistant"

## Step 2: Enable Gmail API

1. In your Google Cloud project, go to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click on "Gmail API" and click **Enable**

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace)
3. Fill in the required fields:
   - **App name**: Sumeria Personal Assistant
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes**
6. Add these scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
7. Click **Save and Continue**
8. On the **Test users** page, add your Gmail address as a test user
9. Click **Save and Continue**

## Step 4: Create OAuth2 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Choose **Desktop app** as application type
4. Name it "Sumeria Desktop Client"
5. Click **Create**
6. Click **Download JSON** to download your credentials
7. Save the file as `credentials.json` in the project root directory

## Step 5: Configure Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and update:
   ```env
   GMAIL_CREDENTIALS_FILE=credentials.json
   GMAIL_DEFAULT_ACCOUNT=your-email@gmail.com
   ```

## Step 6: First Authentication

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server for the first time:
   ```bash
   python -m app.main
   ```

3. When you first use a Gmail tool, it will:
   - Open your browser
   - Ask you to sign in to your Google account
   - Request permission to access Gmail
   - Show a warning that the app is not verified (this is normal for development)
   - Click **Advanced** > **Go to Sumeria Personal Assistant (unsafe)**
   - Grant the requested permissions

4. After authorization, a token will be saved in `tokens/token_{your-email}.json`

## Multiple Accounts

The system supports multiple Gmail accounts:

### Adding Additional Accounts

Use the `add_gmail_account` tool:
```python
# This will trigger OAuth flow for the new account
add_gmail_account(account_id="second-email@gmail.com")
```

### Using Specific Accounts

All Gmail tools accept an `account_id` parameter:
```python
# Send from specific account
send_email(
    to=["recipient@example.com"],
    subject="Hello",
    body_text="Test email",
    account_id="second-email@gmail.com"
)

# Search in specific account
search_emails(
    query="from:someone@example.com",
    account_id="work-email@gmail.com"
)
```

### Default Account

Set a default account to use when `account_id` is not specified:
```python
set_default_gmail_account(account_id="primary@gmail.com")
```

Or set it in `.env`:
```env
GMAIL_DEFAULT_ACCOUNT=primary@gmail.com
```

### List Authenticated Accounts

```python
list_gmail_accounts()
# Returns: {"accounts": ["email1@gmail.com", "email2@gmail.com"], "default_account": "email1@gmail.com"}
```

## Token Storage

- Tokens are stored in the `tokens/` directory
- Each account has its own token file: `token_{account_id}.json`
- Tokens are automatically refreshed when they expire
- Keep these files secure and add `tokens/` to `.gitignore`

## Security Notes

1. **Never commit credentials**:
   - Add `credentials.json` to `.gitignore`
   - Add `tokens/` directory to `.gitignore`
   - Keep `.env` file private

2. **Token file security**:
   - Token files contain access credentials
   - Protect them like passwords
   - If compromised, revoke access in Google Account settings

3. **Scopes**:
   - Only request scopes you need
   - Current scopes allow read, send, and modify (labels)
   - Don't use `gmail.full-control` unless absolutely necessary

## Troubleshooting

### "Access blocked: This app's request is invalid"
- Make sure you added your email as a test user in OAuth consent screen
- Verify the OAuth client is for "Desktop app" type

### "Token has been expired or revoked"
- Delete the token file in `tokens/` directory
- Re-authenticate by running a Gmail tool

### "Credentials file not found"
- Make sure `credentials.json` is in the project root
- Check the path in your `.env` file

### Browser doesn't open for authentication
- The OAuth URL will be printed in the console
- Copy and paste it into your browser manually

## Production Deployment

For production use:

1. Submit your app for OAuth verification in Google Cloud Console
2. Update the OAuth consent screen to "Production"
3. Use more secure token storage (encrypted database, secrets manager)
4. Implement proper error handling and logging
5. Set up monitoring for API quota limits

## API Quotas

Gmail API has usage limits:
- **Free tier**: 1 billion quota units per day
- **Send email**: 100 units per message
- **Get message**: 5 units per message
- **List messages**: 5 units per request

Monitor your usage in Google Cloud Console under **APIs & Services** > **Dashboard**.
