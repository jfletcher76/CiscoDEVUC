import os
from dotenv import load_dotenv
from src import ZoomClient

load_dotenv()

# Constants
zc = ZoomClient(os.getenv("ZOOM_TOKEN"))

meeting_id = input('\nEnter Zoom Meeting ID: ')
# End Constants

# Functions
def get_meeting_recordings(meeting_id :str):
    res = zc.session.get(
        f"https://api.zoom.us/v2/meetings/{meeting_id}/recordings"
    )
    res.raise_for_status()
    return res.json()
# End Function

def main() -> None:
    # Get List of zoom rooms
    recordings = get_meeting_recordings(meeting_id=meeting_id)
    print(recordings)


# Only execute if this is the main script rather than an import
if __name__ ==  "__main__":
    main()