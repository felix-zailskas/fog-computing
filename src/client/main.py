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
import socket
import struct

from config import (
    AC_START_TEMP,
    GOAL_TEMP,
    HOST,
    INSIDE_FACTOR,
    OUTSIDE_FACTOR,
    PORT,
    SECONDS_PER_ROUND,
    STARTING_TEMP,
)

from client.util import SensorIn, SensorOut
from logger.logger import FileAndStoudLogger

logger = FileAndStoudLogger(
    f"Client-{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}",
    "../../logs/client/",
)


def compute_mean(values: list[float]) -> float:
    return sum(values) / len(values)


async def produce_data(
    inside_sensor: SensorIn,
    outside_sensor: SensorOut,
    ac_temp: float,
    queue: asyncio.Queue,
):
    while True:
        logger.info(f"Producing {SECONDS_PER_ROUND} more data samples...")
        for _ in range(SECONDS_PER_ROUND):
            outside_sensor.timestep()
            inside_sensor.timestep(outside_sensor.current_temp, ac_temp)

        data = [
            compute_mean(inside_sensor.temp_list),  # inside_temps
            compute_mean(outside_sensor.temp_list),  # outside_temps
            ac_temp,
            GOAL_TEMP,
        ]

        inside_sensor.temp_list = []
        outside_sensor.temp_list = []

        await queue.put(data)
        await asyncio.sleep(SECONDS_PER_ROUND)


async def send_data(queue: asyncio.Queue):
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Establishing connection to server
            try:
                logger.info(f"Trying to connect to {HOST}:{PORT}")
                s.connect((HOST, PORT))
                logger.info(f"Connection to {HOST}:{PORT} established")
            except ConnectionRefusedError as e:
                logger.info(f"Connection to {HOST}:{PORT} not possible. Retrying in 5s")
                logger.info(
                    f"Currently {queue.qsize()} packages in the queue to be send"
                )
                await asyncio.sleep(5)
                continue

            while True:
                item = await queue.get()
                if item is None:
                    logger.info("Found None, stopping process")
                    return
                # There is data to send
                logger.info(f"Consumer: Processing item {item}")
                try:
                    logger.info("Converting data to bytes")
                    data_to_send = struct.pack("ffff", *item)
                    s.sendall(data_to_send)
                    logger.info(f"Sending data: {item}")
                    # Get answer
                    data_received = s.recv(4)
                    if data_received:
                        new_ac_temp = struct.unpack("f", data_received)[0]
                        ac_temp = new_ac_temp
                        logger.info(
                            f"Received new AC temp. Changing from {ac_temp:.2f} to {new_ac_temp:.2f}."
                        )
                    else:
                        logger.info(
                            f"No data received from server. Restarting connection and resending package"
                        )
                        await queue.put(None)
                        queue._queue.rotate(1)
                        queue._queue[0] = item
                        break
                # TODO: Check for correct Exceptions
                except Exception as e:
                    logger.info(f"Connection lost. Err: {str(e)}")
                    logger.info("Restarting connection and resending package")
                    await queue.put(None)
                    queue._queue.rotate(1)
                    queue._queue[0] = item
                    break


async def main():
    outside_sensor = SensorOut(starting_temp=STARTING_TEMP)
    inside_sensor = SensorIn(
        starting_temp=STARTING_TEMP,
        temp_outside_factor=OUTSIDE_FACTOR,
        temp_ac_factor=INSIDE_FACTOR,
    )
    ac_temp = AC_START_TEMP

    queue = asyncio.Queue()
    produce_task = asyncio.create_task(
        produce_data(inside_sensor, outside_sensor, ac_temp, queue)
    )
    consumer_task = asyncio.create_task(send_data(queue))

    await asyncio.gather(produce_task, consumer_task)
    await queue.join()

    await queue.put(None)


if __name__ == "__main__":
    asyncio.run(main())
