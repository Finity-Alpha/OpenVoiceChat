import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
server_url = os.environ.get("TWILIO_SERVER_URL")
client = Client(account_sid, auth_token)

call = client.calls.create(
    url=server_url.replace("wss", "https") + "/twiml",
    to=os.environ.get("MY_NUMBER"),
    from_=os.environ.get("TWILIO_NUMBER"),
)

print(call.sid)
