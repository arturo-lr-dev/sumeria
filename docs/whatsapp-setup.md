# WhatsApp Business Cloud API - Setup Guide

This guide will help you set up WhatsApp Business Cloud API integration with your Sumeria Personal Assistant.

## Prerequisites

- A Facebook Business Account
- A verified Meta Business Manager account
- A phone number dedicated to WhatsApp Business (cannot be used with regular WhatsApp)
- Basic understanding of webhooks and APIs

## Table of Contents

1. [Create Meta App](#1-create-meta-app)
2. [Configure WhatsApp Product](#2-configure-whatsapp-product)
3. [Get Access Token and Phone Number ID](#3-get-access-token-and-phone-number-id)
4. [Configure Environment Variables](#4-configure-environment-variables)
5. [Set Up Webhook](#5-set-up-webhook)
6. [Create and Approve Message Templates](#6-create-and-approve-message-templates)
7. [Test Your Integration](#7-test-your-integration)
8. [Production Deployment](#8-production-deployment)

---

## 1. Create Meta App

### Step 1.1: Access Meta for Developers

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "My Apps" in the top right
3. Click "Create App"

### Step 1.2: Choose App Type

1. Select **"Business"** as the app type
2. Click "Next"

### Step 1.3: Provide App Details

1. **Display Name**: Enter a name for your app (e.g., "Sumeria Assistant")
2. **App Contact Email**: Enter your email address
3. **Business Account**: Select your Business Manager account
4. Click "Create App"

### Step 1.4: Confirm Your Account

- You may need to verify your account with a code sent to your email or phone

---

## 2. Configure WhatsApp Product

### Step 2.1: Add WhatsApp to Your App

1. In your app dashboard, find **WhatsApp** in the products list
2. Click "Set up" next to WhatsApp
3. This will add WhatsApp to your app

### Step 2.2: Access WhatsApp API Setup

1. In the left sidebar, click **WhatsApp > API Setup**
2. You should see the WhatsApp Business API setup page

---

## 3. Get Access Token and Phone Number ID

### Step 3.1: Temporary Access Token (for testing)

1. On the API Setup page, you'll see a **"Temporary access token"**
2. Click "Copy" to copy this token
3. **Important**: This token expires in 24 hours - use for testing only

### Step 3.2: Get Phone Number ID

1. On the same page, look for **"Phone number ID"**
2. Copy this ID (looks like: `123456789012345`)
3. This is the ID of the test phone number provided by Meta

### Step 3.3: Get Business Account ID

1. In the left sidebar, click **WhatsApp > Getting Started**
2. Look for "WhatsApp Business Account ID"
3. Copy this ID

### Step 3.4: Get App Secret

1. In the left sidebar, click **Settings > Basic**
2. Find "App Secret" and click "Show"
3. Copy this secret (you'll need it for webhook verification)

---

## 4. Configure Environment Variables

### Step 4.1: Copy Environment Template

```bash
cp .env.example .env
```

### Step 4.2: Edit .env File

Add the following WhatsApp configuration:

```bash
# WhatsApp Business Cloud API
WHATSAPP_ACCESS_TOKEN=your-temporary-access-token-here
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_BUSINESS_ACCOUNT_ID=your-business-account-id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=my-super-secret-verify-token-12345
WHATSAPP_APP_SECRET=your-app-secret-here
WHATSAPP_API_VERSION=v21.0
WHATSAPP_API_BASE_URL=https://graph.facebook.com
```

**Important Notes:**
- Replace `your-temporary-access-token-here` with the token from Step 3.1
- Replace `123456789012345` with your Phone Number ID from Step 3.2
- Replace `your-business-account-id` with your Business Account ID from Step 3.3
- Replace `your-app-secret-here` with your App Secret from Step 3.4
- **Create a random string** for `WHATSAPP_WEBHOOK_VERIFY_TOKEN` (e.g., `my-super-secret-verify-token-12345`)
  - This can be any random string - you'll use it when setting up the webhook
  - Keep it secret and secure!

---

## 5. Set Up Webhook

Webhooks allow you to receive incoming messages from WhatsApp.

### Step 5.1: Run the Webhook Server (Development)

For local development, you need to expose your local server to the internet:

**Option A: Using ngrok (Recommended for testing)**

```bash
# Install ngrok if you don't have it
# Download from https://ngrok.com/

# Start your API server
python -m app.api_server

# In another terminal, start ngrok
ngrok http 8000
```

You'll get a URL like: `https://abcd1234.ngrok.io`

**Option B: Using Cloudflare Tunnel**

```bash
# Install cloudflared
# https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Start your API server
python -m app.api_server

# In another terminal, start tunnel
cloudflared tunnel --url http://localhost:8000
```

### Step 5.2: Configure Webhook in Meta

1. Go to your Meta App Dashboard
2. Click **WhatsApp > Configuration** in the left sidebar
3. Find the "Webhook" section
4. Click "Edit"

**Enter Webhook Details:**
- **Callback URL**: `https://your-ngrok-url.ngrok.io/api/v1/whatsapp/webhook`
  - Replace `your-ngrok-url.ngrok.io` with your actual ngrok/cloudflared URL
- **Verify Token**: Enter the same token you set in `.env` as `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- Click "Verify and Save"

If verification succeeds, you'll see a green checkmark!

### Step 5.3: Subscribe to Webhook Fields

After verification, subscribe to these fields:
- ✅ **messages** (to receive incoming messages)
- ✅ **message_status** (to receive delivery/read receipts)

Click "Save" to save your webhook configuration.

---

## 6. Create and Approve Message Templates

Templates are required for sending messages outside the 24-hour customer service window.

### Step 6.1: Access Message Templates

1. In your Meta App Dashboard, click **WhatsApp > Message Templates**
2. Click "Create Template"

### Step 6.2: Create a Template

**Example Template for Order Confirmation:**

1. **Category**: Select "UTILITY" (for transactional messages)
2. **Name**: `order_confirmation` (lowercase, no spaces)
3. **Languages**: Select "English (US)"
4. **Header** (optional): "Your Order is Confirmed!"
5. **Body**:
   ```
   Hi {{1}}, your order #{{2}} has been confirmed and will be delivered by {{3}}.

   Thank you for your purchase!
   ```
6. **Footer** (optional): "Reply STOP to unsubscribe"
7. **Buttons** (optional): None for this example

8. Click "Submit"

### Step 6.3: Wait for Approval

- Meta reviews templates within **24-48 hours**
- You'll receive an email when your template is approved
- **Only APPROVED templates** can be used to send messages

### Step 6.4: View Template Status

- Templates can have status: **APPROVED**, **PENDING**, or **REJECTED**
- Use the MCP tool `whatsapp_list_templates` to see your templates

---

## 7. Test Your Integration

### Step 7.1: Send Test Message (Text)

```bash
# Run the MCP server
python -m app.main
```

Use the MCP tool to send a test message:

```python
whatsapp_send_text(
    to="+14155552671",  # Use Meta's test number or your own verified number
    text="Hello from Sumeria Assistant! This is a test message.",
    preview_url=False
)
```

**Test Numbers Provided by Meta:**
- Meta provides test numbers in the API Setup page
- You can send up to 5 messages per day to test numbers

### Step 7.2: Send Test Message (Template)

After your template is approved:

```python
whatsapp_send_template(
    to="+14155552671",
    template_name="order_confirmation",
    language="en_US",
    parameters=["John Doe", "12345", "Friday, Jan 15"]
)
```

### Step 7.3: Test Incoming Messages

1. Send a WhatsApp message to your test number
2. Check your webhook server logs
3. You should see the incoming message logged

---

## 8. Production Deployment

### Step 8.1: Get Production Access Token

Temporary tokens expire in 24 hours. For production:

1. Go to **Meta Business Settings** > **System Users**
2. Create a new System User or select existing
3. Click "Generate New Token"
4. Select your app and required permissions:
   - `whatsapp_business_management`
   - `whatsapp_business_messaging`
5. Click "Generate Token"
6. Copy this token and update `WHATSAPP_ACCESS_TOKEN` in `.env`

**This token does not expire** (unless you revoke it).

### Step 8.2: Add Your Own Phone Number

The test number is limited. To add your own:

1. Go to **WhatsApp > Phone Numbers**
2. Click "Add Phone Number"
3. Choose a phone number (must not be used with regular WhatsApp)
4. Verify the number with a code
5. Update `WHATSAPP_PHONE_NUMBER_ID` in `.env`

**Requirements:**
- Number cannot be used with regular WhatsApp
- Must be able to receive SMS or voice calls for verification
- Recommended: Get a dedicated business number

### Step 8.3: Deploy Webhook Server

For production, deploy your webhook server to a public URL with HTTPS:

**Option A: Deploy to Cloud Provider**
- AWS EC2 + Load Balancer
- Google Cloud Run
- Azure App Service
- DigitalOcean Droplet + Nginx

**Option B: Use Serverless**
- AWS Lambda + API Gateway
- Google Cloud Functions
- Azure Functions

**Example Docker Deployment:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
COPY .env .env

CMD ["uvicorn", "app.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t sumeria-api .
docker run -p 8000:8000 sumeria-api
```

### Step 8.4: Update Webhook URL

1. Update webhook URL in Meta Dashboard to your production URL
2. Re-verify the webhook
3. Ensure HTTPS is enabled (required by Meta)

### Step 8.5: Monitor and Scale

- Monitor webhook response times (must respond < 20 seconds)
- Implement proper error handling and logging
- Consider using a message queue for processing (Celery, RabbitMQ, etc.)
- Monitor API rate limits (80 messages/second per phone number)

---

## Troubleshooting

### Issue: Webhook Verification Fails

**Solution:**
- Ensure `WHATSAPP_WEBHOOK_VERIFY_TOKEN` in `.env` matches what you entered in Meta Dashboard
- Check that your webhook server is running and accessible
- Verify the webhook URL is correct (should end with `/webhook`)
- Check server logs for errors

### Issue: Cannot Send Messages

**Solution:**
- Verify `WHATSAPP_ACCESS_TOKEN` is valid and not expired
- Ensure phone number is in E.164 format (+country code + number)
- Check that recipient number has opted in to receive messages
- Verify `WHATSAPP_PHONE_NUMBER_ID` is correct
- Check API response for specific error codes

### Issue: Template Messages Fail

**Solution:**
- Ensure template is APPROVED (check status with `whatsapp_list_templates`)
- Verify template name and language code are correct
- Ensure number of parameters matches template requirements
- Check that parameters are in correct order

### Issue: Incoming Messages Not Received

**Solution:**
- Verify webhook is properly configured and verified in Meta Dashboard
- Check that webhook fields (messages, message_status) are subscribed
- Ensure `WHATSAPP_APP_SECRET` is correct for signature verification
- Check webhook server logs for errors
- Verify webhook server is publicly accessible

### Issue: Signature Verification Fails

**Solution:**
- Ensure `WHATSAPP_APP_SECRET` in `.env` matches your Meta App Secret
- Check that you're using the raw request body for signature verification
- Verify HMAC SHA256 implementation is correct

---

## Rate Limits and Quotas

### Messaging Tier Limits

WhatsApp uses a tiered messaging system:

| Tier | Messages per 24 hours |
|------|----------------------|
| Tier 1 | 1,000 |
| Tier 2 | 10,000 |
| Tier 3 | 100,000 |
| Tier 4 | Unlimited |

**How to Upgrade Tiers:**
- Tier upgrades happen automatically based on message quality and volume
- Poor quality scores can downgrade your tier
- Maintain high message quality (low block/report rates)

### API Rate Limits

- **80 messages per second** per phone number
- Exceeding rate limits results in HTTP 429 errors
- Implement exponential backoff for retries

### Template Message Limits

- **250 template creation requests** per hour per Business Manager
- Unlimited sent template messages (within messaging tier limits)

---

## Best Practices

### 1. Phone Number Format
Always use E.164 format: `+[country code][number]`
```
✅ Correct: +14155552671
❌ Wrong: 4155552671
❌ Wrong: 1-415-555-2671
```

### 2. Opt-In Management
- Always get user consent before sending messages
- Provide clear opt-out instructions
- Honor opt-out requests immediately

### 3. Message Quality
- Send relevant, valuable messages
- Avoid spam or promotional content outside templates
- Respond promptly to customer inquiries

### 4. Template Guidelines
- Use templates for notifications outside 24-hour window
- Keep templates clear and concise
- Follow Meta's template policies
- Test templates before submitting for approval

### 5. Security
- Never commit `.env` file to version control
- Rotate access tokens periodically
- Always verify webhook signatures
- Use HTTPS for all webhook endpoints

---

## Next Steps

- ✅ Complete setup following this guide
- ✅ Test with Meta's test numbers
- ✅ Create and get approval for your message templates
- ✅ Deploy webhook server to production
- ✅ Add your own verified phone number
- ✅ Monitor message quality and delivery rates

For more information, visit:
- [WhatsApp Cloud API Documentation](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [WhatsApp Business Platform](https://business.whatsapp.com/)
- [Meta for Developers](https://developers.facebook.com/)
