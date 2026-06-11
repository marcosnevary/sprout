from scripts.video_metadata import upload_video_metadata_to_google_sheets
from src.camera_recorder import CameraRecorder
from src.soil_moisture_sensor import SoilMoistureSensor


def soil_moisture_loop(
    soil_moisture_sensor: SoilMoistureSensor,
    max_measurements: int,
) -> None:
    for i in range(max_measurements):
        soil_moisture_sensor.trigger_measurement()
        if i < max_measurements - 1:
            soil_moisture_sensor.wait_until_next_measurement()


def video_loop(
    recorder: CameraRecorder,
    max_recordings: int,
    video_metadata_sheet: object,
) -> None:
    for i in range(max_recordings):
        recorder.record_video()
        if i < max_recordings - 1:
            recorder.wait_until_next_recording()
        upload_video_metadata_to_google_sheets(video_metadata_sheet)
