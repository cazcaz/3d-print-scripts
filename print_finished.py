# /// script
# dependencies = [
#   "plugp100",
#   "dotenv"
# ]
# ///

import asyncio

from setup_envs import get_envs, Envs
from plug_shutoff import initiate_plug_countdown
from email_results import email_results as send_email

async def shutdown_sequence(envs: Envs):
    await initiate_plug_countdown(envs)
    send_email(envs)

if __name__ == "__main__":
    envs = get_envs()
    if envs == None:
        exit(1)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(shutdown_sequence(envs))
    loop.run_until_complete(asyncio.sleep(0.1))
    loop.close()