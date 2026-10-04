# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio

from setup_envs import Envs, get_envs

from plugp100.common.credentials import AuthCredential
from plugp100.discovery import (
    DiscoveredDevice,
    TapoDiscovery,
    connect_discovered_device,
)
from plugp100.devices.plug import TapoPlug
from plugp100.components.countdown import Countdown as PlugCountdown

PLUG_SHUTOFF_COUNTDOWN = 10
PRINTER_PLUG_MAC = "8C-86-DD-2B-8B-F8"

def normalize_mac(mac: str) -> str:
    return mac.replace(":", "").replace("-", "").strip().upper()

async def discover_plugs() -> list[DiscoveredDevice]:
    discovered_devices = await TapoDiscovery.scan()
    return [
        device
        for device in discovered_devices
        if (device.device_type or "").upper() == "SMART.TAPOPLUG"
    ]

async def discover_plug() -> DiscoveredDevice:
    plugs = await discover_plugs()
    if not plugs:
        raise RuntimeError("No Tapo smart plugs found on the local network.")
    target_mac = normalize_mac(PRINTER_PLUG_MAC)
    matches = [device for device in plugs if normalize_mac(device.mac or "") == target_mac]
    if not matches:
        found = ", ".join(device.mac or "unknown MAC" for device in plugs)
        raise RuntimeError(
            f"Printer plug {PRINTER_PLUG_MAC} was not found. Discovered plug MACs: {found}"
        )
    if len(matches) > 1:
        raise RuntimeError(f"Multiple discovered plugs reported printer MAC {PRINTER_PLUG_MAC}.")
    return matches[0]

async def connect_to_plug(credentials: AuthCredential) -> TapoPlug:
    discovered = await discover_plug()
    device = await connect_discovered_plug(discovered, credentials)
    if not isinstance(device, TapoPlug):
        raise RuntimeError(f"Discovered device at {discovered.ip} is not a Tapo plug.")
    await device.update()
    return device

async def connect_discovered_plug(
    discovered: DiscoveredDevice, credentials: AuthCredential
) -> TapoPlug:
    device = await connect_discovered_device(discovered, credentials)
    if not isinstance(device, TapoPlug):
        raise RuntimeError(f"Discovered device at {discovered.ip} is not a Tapo plug.")
    return device

async def send_shutoff_countdown(plug: TapoPlug):
    countdown_comp = plug.get_component(PlugCountdown)
    if countdown_comp is None:
        countdown_comp = PlugCountdown(plug.client)
        plug.add_component(countdown_comp)
    await countdown_comp.add_countdown_off(PLUG_SHUTOFF_COUNTDOWN)

async def initiate_plug_countdown(envs: Envs):
    credentials = AuthCredential(envs.tapo_username, envs.tapo_password)
    device = await connect_to_plug(credentials)
    await send_shutoff_countdown(device)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        exit(1)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(initiate_plug_countdown(envs))
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()