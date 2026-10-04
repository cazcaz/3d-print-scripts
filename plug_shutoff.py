# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio

from setup_envs import Envs, get_envs

from plugp100.common.credentials import AuthCredential
from plugp100.discovery.tapo_discovery import DiscoveredDevice, TapoDiscovery
from plugp100.new.device_factory import (
    DeviceConnectConfiguration,
    TapoPlug,
    connect,
)
from plugp100.new.components.countdown import Countdown as PlugCountdown
from plugp100.new.errors.invalid_authentication import InvalidAuthentication as ia

PLUG_SHUTOFF_COUNTDOWN = 10

# Patch the broken __init__ of InvalidAuthentication to allow it to be raised without arguments
def fixed_init(self, host: str, device_type: str):
    super(ia, self).__init__(
        f"Invalid authentication error for {host}, {device_type}"
    )

ia.__init__ = fixed_init

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
    if len(plugs) > 1:
        found = ", ".join(f"{device.device_model} ({device.ip})" for device in plugs)
        raise RuntimeError(f"Found multiple Tapo smart plugs; refusing to choose: {found}")
    return plugs[0]

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
    try:
        device = await discovered.get_tapo_device(credentials)
    except Exception as error:
        if str(error) != "Failed to determine the right tapo protocol":
            raise
        schema = discovered.mgt_encrypt_schm
        port = schema.http_port if schema and schema.http_port else 80
        configuration = DeviceConnectConfiguration(
            host=discovered.ip,
            port=port,
            credentials=credentials,
            device_type=discovered.device_type,
        )
        device = await connect(configuration)
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