from twilio.rest import Client
import os

SID = os.environ.get('TWILIO_ACCOUNT_SID')
Auth_Token = os.environ.get('TWILIO_AUTH_TOKEN')
sender = '+17816536480'
receiver = '639105685214'
cl = Client(SID, Auth_Token)
cl.messages.create(body='Test', from_=sender, to=receiver)
