import os
from getpass import getpass

REQUIRED_VARS = dict([
    ("tapo_username", "Tapo accout username. This is the email address you use to log in to the Tapo app."),
    ("tapo_password", "Tapo account password. If this contains special characters, it is reccomended to change it to just be letters and numbers"),
    ("tapo_plug_ip", "IP address of the Tapo plug that controls the printer"),
    ("result_gmail", "Gmail address to send results from"),
    ("result_gmail_app_password", "App password for the Gmail account"),
    ("result_recipient_email", "Email address to receive results"),
    ("print_result_path", "Path to read the print result from.")
])

def prompt_for_value(var_name):
    # Mask values that look like passwords or secrets
    print(f"{var_name}: {REQUIRED_VARS[var_name]}")
    if "pass" in var_name or "secret" in var_name or "token" in var_name:
        return getpass(f"Enter value for {var_name}: ")
    return input(f"Enter value for {var_name}: ")

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
