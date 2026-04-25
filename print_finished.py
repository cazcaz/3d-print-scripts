# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio
import logging
import smtplib

from email.message import EmailMessage

from setup_envs import get_envs, Envs
from plugp100.common.credentials import AuthCredential
from plugp100.discovery.tapo_discovery import TapoDiscovery
from plugp100.new.device_factory import connect, DeviceConnectConfiguration, TapoPlug
from plugp100.new.components.countdown import Countdown as PlugCountdown
from plugp100.new.errors.invalid_authentication import InvalidAuthentication as ia

# Patch the broken __init__ of InvalidAuthentication to allow it to be raised without arguments
def fixed_init(self, host: str, device_type: str):
    super(ia, self).__init__(
        f"Invalid authentication error for {host}, {device_type}"
    )

ia.__init__ = fixed_init

class PrintDetails:
    def __init__(self, result_path: str):
        self.path = result_path
    
    def parse_result(self):
        print("not implemented")

async def connect_by_ip(credentials: AuthCredential, host: str) -> TapoPlug:
    device_configuration = DeviceConnectConfiguration(host=host, credentials=credentials)
    device = await connect(device_configuration)
    await device.update()
    return device

async def set_countdown(plug: TapoPlug):
    countdown_comp = plug.get_component(PlugCountdown)
    if countdown_comp is None:
        countdown_comp = PlugCountdown(plug.client)
        plug.add_component(countdown_comp)
    await countdown_comp.add_countdown_off(10)

def send_result_email(result: PrintDetails, envs: Envs):
    email = envs.result_gmail
    email_password = envs.result_gmail_app_password
    recipient_email = envs.result_recipient_email

    msg = EmailMessage()
    msg["Subject"] = "Hello from Python"
    msg["From"] = email
    msg["To"] = recipient_email
    msg.set_content("This is a test email sent from my Python script.")
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(email, email_password)
        smtp.send_message(msg)

async def shutdown_sequence(print_result: PrintDetails, envs: Envs):
    credentials = AuthCredential(envs.tapo_username, envs.tapo_password)
    ip = envs.tapo_plug_ip
    device = await connect_by_ip(credentials, ip)
    send_result_email(print_result, envs)
    await set_countdown(device)

def search_print_results(envs: Envs) -> PrintDetails:
    result_path = envs.print_result_path
    return PrintDetails(result_path)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        print("Environment variables not set correctly. Please run the setup_envs.py script.")
        exit(1)
    print_result = search_print_results(envs)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(shutdown_sequence(print_result, envs))
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()