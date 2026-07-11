import gspread
from google.oauth2.service_account import Credentials

from video.metadata import VideoMetadata

SCOPES = (
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
)


def ensure_worksheet_header(
    worksheet: gspread.Worksheet,
    header: tuple[str, ...],
) -> None:
    if worksheet.row_values(1):
        return

    worksheet.insert_row(header, index=1)


def save_measurement_to_worksheet(
    timestamp: str,
    sensor_1: float,
    sensor_2: float,
    worksheet: gspread.Worksheet,
) -> None:
    try:
        worksheet.append_row([timestamp, sensor_1, sensor_2])
    except Exception as e:
        print(f"Failed to upload to Google Sheets: {e!s}")


def save_metadata_to_worksheet(
    metadata: VideoMetadata,
    worksheet: gspread.Worksheet,
) -> None:
    try:
        worksheet.append_row(
            [
                metadata.timestamp,
                metadata.filename,
                metadata.duration_seconds,
                metadata.size_mb,
                metadata.width_px,
                metadata.height_px,
                metadata.fps,
            ],
        )
    except Exception as e:
        print(f"Failed to upload to Google Sheets: {e!s}")


def get_worksheet(
    credentials_file: str,
    spreadsheet_name: str,
    worksheet_name: str,
) -> gspread.Worksheet | None:
    try:
        creds = Credentials.from_service_account_file(
            credentials_file,
            scopes=SCOPES,
        )

        client = gspread.authorize(creds)

        spreadsheet = client.open(spreadsheet_name)
        return spreadsheet.worksheet(worksheet_name)

    except Exception as e:
        print(f"Failed to access Google Sheets: {e!s}")


def initialize_worksheet(
    credentials_file: str,
    spreadsheet_name: str,
    worksheet_name: str,
    header: tuple,
) -> gspread.Worksheet | None:
    worksheet = get_worksheet(credentials_file, spreadsheet_name, worksheet_name)

    if worksheet is None:
        return None

    ensure_worksheet_header(worksheet, header)
    return worksheet
