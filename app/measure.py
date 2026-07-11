from config.app import DATA_PATH, SPREADSHEET_NAME
from config.measurement import MEASUREMENT_CONFIG, MEASUREMENT_HEADER
from devices.sensor import Sensor
from storage.csv import initialize_csv, save_measurement_to_csv
from storage.google_sheets import initialize_worksheet, save_measurement_to_worksheet
from utils.measurements import invert_sensor_values
from utils.time import countdown, current_timestamp


def main() -> None:
    sensor = Sensor(
        serial_port=MEASUREMENT_CONFIG.serial_port,
        command=MEASUREMENT_CONFIG.command,
        baud_rate=MEASUREMENT_CONFIG.baud_rate,
    )

    file_path = initialize_csv(
        data_path=DATA_PATH,
        filename=MEASUREMENT_CONFIG.measurements_filename,
        header=MEASUREMENT_HEADER,
    )

    worksheet = initialize_worksheet(
        credentials_file="credentials.json",
        spreadsheet_name=SPREADSHEET_NAME,
        worksheet_name=MEASUREMENT_CONFIG.measurements_worksheet_name,
        header=MEASUREMENT_HEADER,
    )

    for i in range(MEASUREMENT_CONFIG.max_measurements):
        sensor_1, sensor_2 = sensor.measure()
        sensor_1, sensor_2 = invert_sensor_values(sensor_1, sensor_2)
        timestamp = current_timestamp()

        print(f"[{timestamp}] Measurement {i + 1}: {sensor_1}, {sensor_2}")

        save_measurement_to_csv(
            timestamp,
            sensor_1,
            sensor_2,
            file_path,
        )

        if worksheet:
            save_measurement_to_worksheet(
                timestamp,
                sensor_1,
                sensor_2,
                worksheet,
            )

        countdown(
            MEASUREMENT_CONFIG.interval_between_measurements,
            "Time until next measurement",
        )


if __name__ == "__main__":
    main()
