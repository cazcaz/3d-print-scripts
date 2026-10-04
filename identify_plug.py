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
from plugp100.errors.invalid_authentication import InvalidAuthentication


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
        schema = plug.mgt_encrypt_schm
        security = (
            f"{schema.encrypt_type} v{schema.lv}, port {schema.http_port}, "
            f"HTTPS {schema.is_support_https}"
            if schema
            else "security metadata unavailable"
        )
        print(
            f"{index}. {plug.device_model}  MAC: {plug.mac}  IP: {plug.ip}  "
            f"Security: {security}"
        )

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
    try:
        device = await connect_discovered_plug(selected_plug, credentials)
    except InvalidAuthentication:
        print(
            "The plug rejected all supported authentication handshakes. "
            "Check that .env contains the Tapo account email and password "
            "used for this plug. Do not share those values."
        )
        return
    except Exception as error:
        print(f"Could not connect to the selected plug: {error}")
        return
    await device.update()
    await send_shutoff_countdown(device)
    print(
        f"Scheduled {selected_plug.device_model} ({selected_plug.mac}) to turn off "
        f"in {PLUG_SHUTOFF_COUNTDOWN} seconds."
    )


if __name__ == "__main__":
    asyncio.run(identify_plug())