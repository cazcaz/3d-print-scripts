# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio

from setup_envs import get_envs
from plug_shutoff import (
    PLUG_SHUTOFF_COUNTDOWN,
    connect_discovered_plug,
    discover_plugs,
    send_shutoff_countdown,
)
from plugp100.common.credentials import AuthCredential


async def identify_plug():
    envs = get_envs()
    if envs is None:
        return

    plugs = await discover_plugs()
    if not plugs:
        print("No Tapo smart plugs found. Run this on the same LAN as the plugs.")
        return

    print("Discovered Tapo plugs:")
    for index, plug in enumerate(plugs, start=1):
        print(f"{index}. {plug.device_model}  MAC: {plug.mac}  IP: {plug.ip}")

    selection = input("Enter the number of one plug to test, or q to quit: ").strip()
    if selection.lower() == "q":
        return
    if not selection.isdigit() or not 1 <= int(selection) <= len(plugs):
        print("Invalid selection; no plug was changed.")
        return

    selected_plug = plugs[int(selection) - 1]
    confirmation = input(
        "Ensure the printer is idle. Type POWER OFF to schedule this plug to turn off: "
    ).strip()
    if confirmation != "POWER OFF":
        print("Cancelled; no plug was changed.")
        return

    credentials = AuthCredential(envs.tapo_username, envs.tapo_password)
    device = await connect_discovered_plug(selected_plug, credentials)
    await device.update()
    await send_shutoff_countdown(device)
    print(
        f"Scheduled {selected_plug.device_model} ({selected_plug.mac}) to turn off "
        f"in {PLUG_SHUTOFF_COUNTDOWN} seconds."
    )


if __name__ == "__main__":
    asyncio.run(identify_plug())