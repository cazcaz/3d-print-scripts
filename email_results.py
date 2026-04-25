# /// script
# dependencies = [
#   "dotenv"
# ]
# ///

import smtplib

from setup_envs import Envs, get_envs
from email.message import EmailMessage

class PrintDetails:
    def __init__(self, result_path: str):
        self.path = result_path
    
    def parse_result(self):
        print("not implemented")

def fetch_print_results(envs: Envs) -> PrintDetails:
    result_path = envs.print_result_path
    print("not implemented")
    return None

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

def email_results(envs: Envs):
    results = fetch_print_results(envs)
    if results == None:
        return
    send_result_email(envs)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        exit(1)
    email_results(envs)
    
    
