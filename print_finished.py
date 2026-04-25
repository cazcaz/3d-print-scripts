# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio
import logging
import smtplib
import os

from dotenv import load_dotenv

from email.message import EmailMessage

from plugp100.common.credentials import AuthCredential
from plugp100.discovery.tapo_discovery import TapoDiscovery
from plugp100.new.device_factory import connect, DeviceConnectConfiguration, TapoPlug
from plugp100.new.components.countdown import Countdown as PlugCountdown

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

def get_credentials() -> AuthCredential:
    username = os.getenv("tapo_username")
    password = os.getenv("tapo_password")
    if username == None:
        print("Username is unset. Set 'tapo_username' environment variable")
        return None
    if password == None:
        print("Password is unset. Set 'tapo_password' environment variable")
        return None
    return AuthCredential(username, password)

def get_tapo_plug_ip() -> str:
    ip = os.getenv("tapo_plug_ip")
    if ip == None:
        print("Tapo plug ip is unset. Set 'tapo_plug_ip' environment variable")
    return ip

async def set_countdown(plug: TapoPlug):
    countdown_comp = plug.get_component(PlugCountdown)
    if countdown_comp is None:
        countdown_comp = PlugCountdown(plug.client)
        plug.add_component(countdown_comp)
    await countdown_comp.add_countdown_off(10)

def send_result_email(result: PrintDetails):
    email = os.getenv("result_gmail")
    email_password = os.getenv("result_gmail_app_password")
    recipient_email = os.getenv("result_recipient_email")

    msg = EmailMessage()
    msg["Subject"] = "Hello from Python"
    msg["From"] = email
    msg["To"] = recipient_email
    msg.set_content("This is a test email sent from my Python script.")
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(email, email_password)
        smtp.send_message(msg)

async def shutdown_sequence(print_result: PrintDetails):
    load_dotenv()
    credentials = get_credentials()
    if credentials == None:
        return 1
    ip = get_tapo_plug_ip()
    if ip == None:
        return 1
    device = await connect_by_ip(credentials, ip)
    send_result_email(print_result)
    await set_countdown(device)

def search_print_results():
    result_path = os.getenv("print_result_path")
    return PrintDetails("")

if __name__ == "__main__":
    print_result = search_print_results()
    loop = asyncio.new_event_loop()
    loop.run_until_complete(shutdown_sequence(print_result))
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()