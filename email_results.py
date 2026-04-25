# /// script
# dependencies = [
#   "dotenv"
# ]
# ///

import smtplib
import os

from setup_envs import Envs, get_envs
from email.message import EmailMessage

class PrintDetails:
    def __init__(self, result_path: str):
        self._path = result_path
        self.is_valid = False
        self.parse_result()
    
    def parse_result(self):
        result_dict = {}
        try:
            with open(self._path, "r") as f:
                for line in f:
                    parts = line.strip().split(",")
                    for part in parts:
                        key_val = part.strip().split("=")
                        print(part)
                        result_dict[key_val[0]] = key_val[1]
        except:
            print(f"Could not open results file at {self._path}")
            return
        
        try:
            self._print_status = result_dict["STATUS"]
            self._print_time = result_dict["TIME"]
            self._print_name = result_dict["NAME"]
            self.is_valid = True
        except:
            print("Could not parse results")

        try:
            os.remove(self._path)
        except:
            print("Could not remove old results path")
    
    @property
    def print_status(self) -> str:
        return self._print_status
    
    @property
    def print_time(self) -> str:
        return self._print_time
    
    @property
    def print_name(self) -> str:
        return self._print_name

def format_seconds(value: str | int) -> str:
    total = int(value)
    hours, rem = divmod(total, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def send_result_email(result: PrintDetails, envs: Envs):
    email = envs.result_gmail
    email_password = envs.result_gmail_app_password
    recipient_email = envs.result_recipient_email

    msg = EmailMessage()
    msg["Subject"] = f"3D Print {result.print_name} Completed"
    msg["From"] = email
    msg["To"] = recipient_email
    msg.set_content(
        f"Status: {result.print_status}\n"
        f"Total print time: {format_seconds(result.print_time)}"
    )
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(email, email_password)
        smtp.send_message(msg)

def email_results(envs: Envs):
    results = PrintDetails(envs.print_result_path)
    if not results.is_valid:
        return
    send_result_email(results, envs)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        exit(1)
    email_results(envs)
    
    
