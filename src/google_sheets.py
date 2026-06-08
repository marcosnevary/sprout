import gspread
from google.oauth2.service_account import Credentials


def get_sheet(
    credentials_file: str,
    sheet_name: str,
) -> gspread.Spreadsheet:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    creds = Credentials.from_service_account_file(
        credentials_file,
        scopes=SCOPES,
    )

    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1

    if not sheet.row_values(1):
        sheet.append_row(
            [
                "timestamp",
                "sensor_1",
                "sensor_2",
            ],
        )

    return sheet
