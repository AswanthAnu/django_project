from django.conf import settings
import os
from twilio.rest import Client


ACCOUNT_SID = 'AC158fc54ebc80234dce390049a8f81b04'
AUTH_TOKEN =  '0a27a968a60bfdbb872c7fd6fd7cc10b'
SERVICES = 'VA0dd91b528f43b0e713f211f2332e4007'

# class MessageHandler:

#     phone_number = None
#     otp = None

#     def __init__(self, phone_number, otp) :
#         self.phone_number = phone_number
#         self.otp = otp 

#     def send_otp_on_phone(self):
#         client = Client(account_sid, auth_token)
#         message = client.messages.create(
#                                 body=f'Welcome to pepper, your OTP to login is {self.otp} ',
#                                 from_='+15806708494',
#                                 to= self.phone_number,
#                             )

#         print(message.sid)

