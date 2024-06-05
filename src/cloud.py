import numpy as np


def compute_ac_adjustment_direct(
    inside_temps: list[float],
    outside_temps: list[float],
    alpha: float,
    beta: float,
    goal_temp: float,
) -> float:
    inside_avg = np.array(inside_temps).mean()
    outside_avg = np.array(outside_temps).mean()

    new_ac_temp = (
        (goal_temp * (1 + alpha + beta)) - alpha * outside_avg - inside_avg
    ) / beta

    return new_ac_temp


def compute_ac_adjustment(
    inside_temps: list[float],
    outside_temps: list[float],
    ac_temp: float,
    goal_temp: float,
) -> float:
    inside_avg = np.array(inside_temps).mean()
    outside_avg = np.array(outside_temps).mean()

    if inside_avg < goal_temp - 1:
        if outside_avg < goal_temp:
            ac_temp += 2
        else:
            ac_temp += 1
    elif inside_avg > goal_temp + 1:
        if outside_avg < goal_temp:
            ac_temp -= 1
        else:
            ac_temp -= 2

    # Cap the max difference between ac and goal temperature
    threshold = 5
    if abs(goal_temp - ac_temp) > threshold:
        if goal_temp - ac_temp < 0:
            ac_temp = goal_temp + threshold
        else:
            ac_temp = goal_temp - threshold

    return ac_temp
