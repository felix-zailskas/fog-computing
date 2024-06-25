import random


class SensorOut:
    current_temp: float
    temp_list: list[float]

    def __init__(self, starting_temp: float = 19.0) -> None:
        self.current_temp = starting_temp
        self.temp_list = [self.current_temp]

    def timestep(self) -> None:
        temp_delta = random.uniform(-1, 1)
        self.current_temp += temp_delta
        self.temp_list.append(self.current_temp)


class SensorIn:
    current_temp: float
    temp_list: list[float]
    temp_outside_factor: float
    temp_ac_factor: float

    def __init__(
        self,
        starting_temp: float = 19.0,
        temp_outside_factor: float = 0.5,
        temp_ac_factor: float = 0.5,
    ) -> None:
        self.current_temp = starting_temp
        self.temp_list = [self.current_temp]
        self.temp_outside_factor = temp_outside_factor
        self.temp_ac_factor = temp_ac_factor

    def timestep(self, temp_outside: float, temp_ac: float) -> None:
        self.current_temp = (
            self.current_temp
            + self.temp_outside_factor * temp_outside
            + self.temp_ac_factor * temp_ac
        ) / (1 + self.temp_outside_factor + self.temp_ac_factor)
        self.temp_list.append(self.current_temp)
