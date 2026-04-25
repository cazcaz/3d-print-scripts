# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio

from setup_envs import Envs, get_envs

from plugp100.common.credentials import AuthCredential
from plugp100.discovery.tapo_discovery import TapoDiscovery
from plugp100.new.device_factory import connect, DeviceConnectConfiguration, TapoPlug
from plugp100.new.components.countdown import Countdown as PlugCountdown
from plugp100.new.errors.invalid_authentication import InvalidAuthentication as ia

PLUG_SHUTOFF_COUNTDOWN = 10

# Patch the broken __init__ of InvalidAuthentication to allow it to be raised without arguments
def fixed_init(self, host: str, device_type: str):
    super(ia, self).__init__(
        f"Invalid authentication error for {host}, {device_type}"
    )

ia.__init__ = fixed_init

async def connect_by_ip(credentials: AuthCredential, host: str) -> TapoPlug:
    device_configuration = DeviceConnectConfiguration(host=host, credentials=credentials)
    device = await connect(device_configuration)
    await device.update()
    return device

async def send_shutoff_countdown(plug: TapoPlug):
    countdown_comp = plug.get_component(PlugCountdown)
    if countdown_comp is None:
        countdown_comp = PlugCountdown(plug.client)
        plug.add_component(countdown_comp)
    await countdown_comp.add_countdown_off(PLUG_SHUTOFF_COUNTDOWN)

async def initiate_plug_countdown(envs: Envs):
    credentials = AuthCredential(envs.tapo_username, envs.tapo_password)
    ip = envs.tapo_plug_ip
    device = await connect_by_ip(credentials, ip)
    await send_shutoff_countdown(device)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        exit(1)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(initiate_plug_countdown(envs))
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()