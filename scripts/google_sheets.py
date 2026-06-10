import gspread
from google.oauth2.service_account import Credentials


def get_sheet(
    credentials_file: str,
    spreadsheet_name: str,
    worksheet_name: str,
    header: list[str] | None = None,
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
    spreadsheet = client.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(worksheet_name)

    if not sheet.row_values(1):
        sheet.append_row(header)

    return sheet
