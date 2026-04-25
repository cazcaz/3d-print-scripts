# 3D Printing Scripts
---
## Brief
Python scripts for Klipper to call at the end of a 3D print. This is to do things like:
- Send an email with reports of the print status, like time taken, filament used, Klipper status
- Find the 3D printer Tapo plug, and send it a countdown sequence to turn off the printer

## Setup 
- Clone the repo
- Install python3
- Install pipx
- Run `pipx run setup_envs.py` to initialise environment variables
- Run `pipx run print_finished.py` to verify all works correctly

NOTE: If there is a warning about auth errors, the `plugp100` needs to be manually updated in the environment it is installed in. This involves changing `super.init()` to `super().__init__()` in the auth.

- Update Klipper to output the print status to a file that will be read by the script
- Update Klipper to call the script on completion