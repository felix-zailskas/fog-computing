from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from cloud import compute_ac_adjustment, compute_ac_adjustment_direct
from config import GCLOUD_SERVICE_ACCOUNT_KEY, GCLOUD_SERVICE_ACCOUNT_KEY_ID
from sensors import SensorIn, SensorOut


def simulate_locally(
    goal_temp: float,
    inside_sensor: SensorIn,
    outside_sensor: SensorOut,
    ac_temp: float,
    comm_rounds: int,
    seconds_per_round: int,
    direct_compute: bool = True,
):
    for cloud_comm_round in range(comm_rounds):
        for time_step in range(seconds_per_round):
            outside_sensor.timestep()
            inside_sensor.timestep(outside_sensor.current_temp, ac_temp)
            print(
                f"""
                Current Time Step: {time_step}
                    Inside Temp: {inside_sensor.current_temp:.2f}
                    Outside Temp: {outside_sensor.current_temp:.2f}
                    AC Temp: {ac_temp:.2f}
                    Goal: {goal_temp:.2f}
            """
            )
        if direct_compute:
            ac_temp = compute_ac_adjustment_direct(
                inside_sensor.temp_list,
                outside_sensor.temp_list,
                inside_sensor.temp_outside_factor,
                inside_sensor.temp_ac_factor,
                goal_temp,
            )
        else:
            ac_temp = compute_ac_adjustment(
                inside_sensor.temp_list, outside_sensor.temp_list, ac_temp, goal_temp
            )
        print(f"Talking to the cloud new ac temp is {ac_temp:.2f}")
        inside_sensor.temp_list = []
        outside_sensor.temp_list = []


def simulate_with_cloud(
    goal_temp: float,
    inside_sensor: SensorIn,
    outside_sensor: SensorOut,
    ac_temp: float,
    comm_rounds: int,
    seconds_per_round: int,
):
    service_account_info = {
        "type": "service_account",
        "project_id": "fog-computing-2024",
        "private_key_id": f"{GCLOUD_SERVICE_ACCOUNT_KEY_ID}",
        "private_key": f"-----BEGIN PRIVATE KEY-----\n{GCLOUD_SERVICE_ACCOUNT_KEY}\n-----END PRIVATE KEY-----\n",
        "client_email": "invoke-functions-fog-computing@fog-computing-2024.iam.gserviceaccount.com",
        "client_id": "102093350603936890228",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/invoke-functions-fog-computing%40fog-computing-2024.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }

    url = "https://europe-west1-fog-computing-2024.cloudfunctions.net/compute_ac_adjustment"

    creds = service_account.IDTokenCredentials.from_service_account_info(
        service_account_info,
        target_audience=url,
    )

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    authed_session = AuthorizedSession(creds)

    for cloud_comm_round in range(comm_rounds):
        for time_step in range(seconds_per_round):
            outside_sensor.timestep()
            inside_sensor.timestep(outside_sensor.current_temp, ac_temp)
            print(
                f"""
                Current Time Step: {time_step}
                    Inside Temp: {inside_sensor.current_temp:.2f}
                    Outside Temp: {outside_sensor.current_temp:.2f}
                    AC Temp: {ac_temp:.2f}
                    Goal: {goal_temp:.2f}
            """
            )

        body = {
            "inside_temps": inside_sensor.temp_list,
            "outside_temps": outside_sensor.temp_list,
            "ac_temp": ac_temp,
            "goal_temp": goal_temp,
        }

        # TODO: while trying to send the sensors need to keep producing
        # perhaps add the payload to an async queue
        while True:
            print("Sending request to cloud...")
            response = authed_session.post(url, json=body, headers=headers)
            print(f"Response with status code {response.status_code}")
            if response.status_code == 200:
                response = response.json()
                ac_temp = response["ac_temp"]
                print(f"New AC temp is {ac_temp}")
                inside_sensor.temp_list = []
                outside_sensor.temp_list = []
                break


if __name__ == "__main__":
    goal_temp = 21.0
    outside_sensor = SensorOut(starting_temp=19.0)
    inside_sensor = SensorIn(
        starting_temp=19.0, temp_outside_factor=0.5, temp_ac_factor=0.8
    )
    ac_temp = 20.0

    # simulate_locally(goal_temp, inside_sensor, outside_sensor, ac_temp, 10, 3, True)
    simulate_with_cloud(goal_temp, inside_sensor, outside_sensor, ac_temp, 10, 3)
