# /// script
# dependencies = [
#   "dotenv"
# ]
# ///

import os
from getpass import getpass
from dotenv import load_dotenv

REQUIRED_VARS = dict([
    ("tapo_username", "Tapo accout username. This is the email address you use to log in to the Tapo app."),
    ("tapo_password", "Tapo account password. If this contains special characters, it is reccomended to change it to just be letters and numbers"),
    ("tapo_plug_ip", "IP address of the Tapo plug that controls the printer"),
    ("result_gmail", "Gmail address to send results from"),
    ("result_gmail_app_password", "App password for the Gmail account"),
    ("result_recipient_email", "Email address to receive results"),
    ("print_result_path", "Path to read the print result from.")
])

class Envs:
    def __init__(self):
        self.env_dict = {}
        self.env_dict["tapo_username"] = os.getenv("tapo_username")
        self.env_dict["tapo_password"] = os.getenv("tapo_password")
        self.env_dict["tapo_plug_ip"] = os.getenv("tapo_plug_ip")
        self.env_dict["result_gmail"] = os.getenv("result_gmail")
        self.env_dict["result_gmail_app_password"] = os.getenv("result_gmail_app_password")
        self.env_dict["result_recipient_email"] = os.getenv("result_recipient_email")
        self.env_dict["print_result_path"] = os.getenv("print_result_path")
    
    @property
    def tapo_username(self):
        return self.env_dict["tapo_username"]
    
    @property
    def tapo_password(self):
        return self.env_dict["tapo_password"]
    
    @property
    def tapo_plug_ip(self):
        return self.env_dict["tapo_plug_ip"]
    
    @property
    def result_gmail(self):
        return self.env_dict["result_gmail"]
    
    @property
    def result_gmail_app_password(self):
        return self.env_dict["result_gmail_app_password"]
    
    @property
    def result_recipient_email(self):
        return self.env_dict["result_recipient_email"]
    
    @property
    def print_result_path(self):
        return self.env_dict["print_result_path"]

def prompt_for_value(var_name):
    # Mask values that look like passwords or secrets
    print(f"{var_name}: {REQUIRED_VARS[var_name]}")
    if "pass" in var_name or "secret" in var_name or "token" in var_name:
        return getpass(f"Enter value for {var_name}: ")
    return input(f"Enter value for {var_name}: ")


def verify_required_envs():
    load_dotenv()
    for var in REQUIRED_VARS:
        if os.getenv(var) == None:
            print(f"Environment variable '{var}' is not set. Please set it before running the script.")
            return False
    return True

def get_envs() -> Envs:
    load_dotenv()
    if not verify_required_envs():
        return None
    envs = Envs()
    for var in REQUIRED_VARS:
        if envs.env_dict[var] == None:
            print(f"Environment variable '{var}' is not set. Please set it before running the script.")
            return None
    return envs

def main():
    print("=== Environment Setup ===")
    values = {}

    for var in REQUIRED_VARS:
        val = prompt_for_value(var).strip()
        while not val:
            print("Value cannot be empty.")
            val = prompt_for_value(var).strip()
        values[var] = val
        print("\n")

    # Write .env file
    with open(".env", "w") as f:
        for key, val in values.items():
            f.write(f"{key}=\"{val}\"\n")

    print(".env file created successfully.")

if __name__ == "__main__":
    main()
