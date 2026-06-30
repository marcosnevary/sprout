import gspread
from google.oauth2.service_account import Credentials
from src.display import live

def get_sheet(
        credentials_file: str,
        spreadsheet_name: str,
        worksheet_name: str,
        header: list[str] | None = None,
) -> gspread.Worksheet | None:
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]

    try:
        creds = Credentials.from_service_account_file(
            credentials_file,
            scopes=SCOPES,
        )

        client = gspread.authorize(creds)

        spreadsheet = client.open(spreadsheet_name)
        sheet = spreadsheet.worksheet(worksheet_name)

        if not sheet.row_values(1) and header:
            sheet.append_row(header)

        return sheet

    except Exception as e:
        live.console.print(
            f"[yellow]Failed to access Google Sheets: {e!s}[/yellow]",
        )
        return None