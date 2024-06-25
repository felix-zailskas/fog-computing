# Edge/Cloud Temperature Regulation Protocol using TCP

This repository contains a client/server module implemented using TCP to regulate the air-conditioning system of an edge device.

## Application Description

The application simulates how a cloud/edge system might control the temperature of an air-conditioning (AC) system. This is done by simulating two sensors, one outside the house and one inside the room. The outside sensor registers the temperature fluctuation of the environment. This is simulated by a random temperature change in the range [-1, 1] at every timestep. The current inside temperature, the outside temperature, and the AC temperature influence the inside temperature. The coefficients of how much each temperature influences the inside temperature can be set variably in the program. The goal of the system is to adjust the AC in such a way as to keep the room at a desired temperature. For this, the temperatures of both sensors are recorded every second, then accumulated every five seconds and sent to the cloud server together with the current AC temperature and the goal temperature. The cloud server then computes an optimal AC temperature based on the available data (a simple calculation in the current implementation) and sends this to the edge client. The client adjusts the AC, and the process is repeated. All communication is done asynchronously; if the connection is lost, packages will be resent until the sending is successful.

## Running the code

To run the code create a virtual environment, and install the dependencies from the `requirements.txt` on both the client and server machine.

```[bash]
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

Next create a copy of the `src/client/.env.template.client` and `src/server/.env.template.server` files. Save them as `src/client/.env` and `src/server/.env`, respectively.
Adjust all values in the `.env` files according to your network setup.

Finally, using the created virtual environments:
On the client machine run

```[bash]
python3 src/client/main.py
```

On the server machine run

```[bash]
python3 src/server/main.py
```

Both services will start up and will be logging their behavior in `stdout` as well as in a file in the `logs/` directory.

## Running the Server in GCP

To run the server part of this application in a cloud environment like GCP do the following:

1. Create a VM and checkout this repository.
2. Make sure that `python` is installed and install all requirements.
3. Create appropriate firewall rules to allow the client application to connect to the VM.
4. Extract the external IP address of the VM and use it as the `HOST` for the client.
5. Use the same `PORT` for both server and client `.env` file.
6. Set the `HOST` for the server to `0.0.0.0/0` (adjust as needed for more security if the network requires it).
7. Run the server code on the VM and the client code locally.
