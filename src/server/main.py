import asyncio
import struct

from config import HOST, PORT

from server import compute_ac_adjustment


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"Connected to {addr}")

    try:
        while True:
            print("Waiting for incoming data")
            incoming_data = await reader.read(16)
            if not incoming_data:
                print("No data received, reset connection.")
                break

            incoming_data = struct.unpack("ffff", incoming_data)
            print(f"Received data from {addr}: {incoming_data}")
            new_ac_temp = compute_ac_adjustment(*incoming_data)

            print(f"Sending new AC temp: {new_ac_temp}")
            data_to_send = struct.pack("f", new_ac_temp)
            writer.write(data_to_send)
            await writer.drain()

    except asyncio.CancelledError:
        print(f"Connection to {addr} closed.")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"Serving on {addr}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
