import os
import sys

# Set this file as the realtive path
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
# Append parent directory to the path to import from sibling package
module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)

import asyncio
import datetime
import struct

from config import HOST, PORT

from logger.logger import FileAndStoudLogger
from server.util import compute_ac_adjustment

logger = FileAndStoudLogger(
    f"Server-{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}",
    "../../logs/server/",
)


LAST_AC_TEMP_OUT = None
LAST_AC_TEMP_LOCK = asyncio.Lock()


async def write_last_ac_temp_out(new_value):
    global LAST_AC_TEMP_OUT
    async with LAST_AC_TEMP_LOCK:
        LAST_AC_TEMP_OUT = new_value


async def read_last_ac_temp_out():
    global LAST_AC_TEMP_OUT
    async with LAST_AC_TEMP_LOCK:
        return LAST_AC_TEMP_OUT


async def handle_client(
    reader: asyncio.streams.StreamReader, writer: asyncio.streams.StreamWriter
):
    addr = writer.get_extra_info("peername")
    logger.info(f"Connected to {addr[0]}:{addr[1]}")

    try:
        last_ac_temp = await read_last_ac_temp_out()
        if last_ac_temp is not None:
            logger.info(
                f"Previous data package containing AC temp {last_ac_temp} will be resend now."
            )
            data_to_send = struct.pack("f", last_ac_temp)
            writer.write(data_to_send)
            await writer.drain()
        await write_last_ac_temp_out(None)

        while True:
            logger.info("Waiting for incoming data")
            incoming_data = await reader.read(16)
            if not incoming_data:
                logger.info("Invalid package received, resetting connection.")
                break

            incoming_data = struct.unpack("ffff", incoming_data)
            logger.info(
                f"Received data from {addr[0]}:{addr[1]}. Package: {incoming_data}"
            )
            new_ac_temp = compute_ac_adjustment(*incoming_data)
            await write_last_ac_temp_out(new_ac_temp)
            logger.info(f"Sending new AC temp: {new_ac_temp}")
            data_to_send = struct.pack("f", new_ac_temp)
            writer.write(data_to_send)
            await writer.drain()

    except asyncio.CancelledError:
        logger.info(f"Connection to {addr[0]}:{addr[1]} closed.")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    logger.info(f"Serving on {addr[0]}:{addr[1]}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
