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
- The shutoff script discovers the Tapo plug on the local network; no plug IP is required. Run it from a device on the same LAN as the plug.
- To identify the printer's plug, run `python3 identify_plug.py`, select one discovered plug, and confirm only when the printer is idle. Note the MAC address of the plug that turns off.

- Update Klipper to output the print status to a file that will be read by the script
- Update Klipper to call the script on completion