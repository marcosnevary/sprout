def invert_sensor_values(sensor_1: float, sensor_2: float) -> tuple[float, float]:
    return 1023 - sensor_1, 1023 - sensor_2
