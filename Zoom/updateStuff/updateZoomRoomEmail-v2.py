import os
from dotenv import load_dotenv
from src import ZoomClient

load_dotenv()

# Constants
zc = ZoomClient(os.getenv("ZOOM_TOKEN"))

zoom_room_name = input('\nEnter Zoom Room Name: ')
new_room_email = input('Enter new calendar email for room: ')
# End Constants

def main() -> None:
    # Get List of zoom rooms
    rooms = zc.list_rooms(zoom_room_name)

    # Extract Room ID
    room = rooms[0]
    room_id = room["room_id"]

    # Query Room for info
    room_info = zc.get_room(
        room_id=room_id
    )

    curr_cal_email = None

    # Get and log current zoom room info
    if room_info["basic"].get("calendar_resource_id"):
        curr_cal_res = zc.get_calendar_resource(
            service_id=id,
            resource_id=room_info["basic"]["calendar_resource_id"]
        )

        curr_cal_email = curr_cal_res["calendar_resource_email"]

    print(f"Current Calendar Email For Room {zoom_room_name}: {curr_cal_email}")

    # Create a calendar resource
    print(f"Creating Calendar Resource: {new_room_email}")
    new_cal_res = zc.create_calendar_resource(
        service_id=id,
        calendar_email=new_room_email
    )

    # Clear current calendar resource from room
    zc.patch_room(
        room_id=room_id,
        data={
            "basic": { "calendar_resource_id": "" }
        }
    )

    # Set calendar resource to the newly created one
    print(f"Assigning Calendar Resource To Room: {zoom_room_name}")
    zc.patch_room(
        room_id=room_id,
        data={
            "basic": { "calendar_resource_id": new_cal_res["calendar_resource_id"] }
        }
    )


# Only execute if this is the main script rather than an import
if __name__ ==  "__main__":
    main()