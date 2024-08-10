import os
import time

import pyautogui as pag
import requests
from PIL import Image

import directKeys


BAD_APPLE_FRAMES_FOLDER = "bad_apple_frames"
RENDERED_FRAMES_SAVE_FOLDER = "spray_paint_bad_apple_frames"
DISCORD_WEBHOOK_ALERT_URL = "URL"

DRAWING_WIDTH_SIZE = 12
FRAME_TOP_LEFT_COORDINATE = (703, 373)
COOLDOWN_BETWEEN_FRAMES = 5


def get_colors(img: Image, new_img_height: int) -> dict:
    """
    Get the colors from the image and their coordinates

    :param img: Frame to get the colors of.
    :param new_img_height: New image height in pixels to downscale the image.
    :return: dict in format of {"0": [(x1, y1), ...)], "255": [(x2, y2), ...]}
    """
    reference = Image.open(img).convert("L")  # Convert to grayscale
    width_percentage = (new_img_height / float(reference.size[1]))  # Get width percentage to keep aspect ratio
    new_img_width = int((float(reference.size[0]) * float(width_percentage)))  # Calculate new width
    reference = reference.resize((new_img_width, new_img_height), Image.NEAREST)  # Resize image to new dimensions

    img_color_coordinates = {"0": [], "255": []}

    # Loop through each pixel in order of left-to-right, top-to-bottom
    for y in range(new_img_height):
        for x in range(new_img_width):
            current_pixel = (x, y)
            current_color = reference.getpixel(current_pixel)

            # Determine if the pixel is white or black based on its brightness value
            if int(current_color) > 127:
                img_color_coordinates["255"].append(current_pixel)

            else:
                img_color_coordinates["0"].append(current_pixel)
    return img_color_coordinates


def image_to_game_coordinates(screen_start_coordinate: tuple, skip_by_count: int | float, img_coordinate: tuple) -> tuple:
    """
    Convert the coordinates from the image into screen coordinates

    :param screen_start_coordinate: Screen coordinate of where the top left corner of the frame will be.
    :param skip_by_count: Every how many pixels does it skip on the screen to place the next color.
    :param img_coordinate: The coordinate of the pixels in the image.
    :return: A tuple of a coordinate on the screen.
    """

    """
    e.g.
    screen_start_coordinates = (500, 500)
    skip_by_count = 10
    img_coordinates = (10, 5)

    Black pixel at `(10, 5)` in the image will be placed onto `(600, 550)` on the screen
    """

    screen_x, screen_y = screen_start_coordinate
    img_x, img_y = img_coordinate
    return screen_x + (img_x * skip_by_count), screen_y + (img_y * skip_by_count)


def log_frame(frame_no: str) -> None:
    """
    Logs which frame was just finished

    :param frame_no: Frame number
    :return: None
    """

    with open("lastframe.txt", "w") as f:
        # Writes in the format of 0001
        f.write(f"{int(frame_no):04d}")


def read_last_frame() -> str:
    """
    Read what was the last frame drawn

    :return: str of the last frame drawn in format of 0001
    """
    with open("lastframe.txt", "r") as f:
        return f.read()


def clear_all() -> None:
    """
    Creates a new layer, then deletes the last layer

    :return: None
    """

    # Create new layer
    directKeys.rblx_click((1777, 854))
    time.sleep(0.1)

    # Delete current layer
    directKeys.rblx_click((1858, 857))
    time.sleep(0.1)

    # Confirm deletion of current layer
    directKeys.rblx_click((1066, 604))
    time.sleep(0.1)


def change_color_rgb(rgb: tuple) -> None:
    """
    Change the color using RGB values on the spray paint color on the bottom left

    :param rgb: tuple of rgb value
    :return: None
    """
    rgb = [str(value) for value in rgb]  # Convert each value to string in order for pyautogui to type it
    r, g, b = rgb

    # Change red value
    directKeys.rblx_click((107, 1022))
    pag.write(r)
    directKeys.press(0x1C)

    # Change green value
    directKeys.rblx_click((190, 1022))
    pag.write(g)
    directKeys.press(0x1C)

    # Change blue value
    directKeys.rblx_click((268, 1022))
    pag.write(b)
    directKeys.press(0x1C)

    time.sleep(0.2)


def change_color_click(coordinate: tuple[int, int]) -> None:
    """
    Change color by just clicking on the color picker

    :param coordinate: Coordinate of the color on the color picker
    :return:
    """
    directKeys.rblx_click(coordinate)
    time.sleep(0.1)


def exit_if_roblox_disconnected() -> None:
    """
    Check if the Roblox client has disconnected from the server, send an alert, kill the Roblox process,
    put system to sleep, and terminate code.

    :return: None
    """

    # Check of the trophy button is visible
    if pag.pixelMatchesColor(1842, 15, (255, 255, 255)):
        return

    requests.post(
        DISCORD_WEBHOOK_ALERT_URL,
        data={"content": "Roblox has disconnected"}
    )

    os.system("taskkill /f /im RobloxPlayerBeta.exe")  # Kill Roblox process
    time.sleep(10)
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Put to sleep mode
    exit()


if __name__ == "__main__":
    time.sleep(3)

    # There are 6572 frames in Bad Apple
    # Check if all the frames are finished
    while len(os.listdir(BAD_APPLE_FRAMES_FOLDER)) <= 6572:
        exit_if_roblox_disconnected()
        timer_start = time.time()
        last_frame_done = read_last_frame()

        new_frame_number = f"{(int(last_frame_done) + 1):04d}"
        colors = get_colors(f"{BAD_APPLE_FRAMES_FOLDER}/frame_{new_frame_number}.png", DRAWING_WIDTH_SIZE)

        change_color_click((301, 961))  # Change to black
        for coordinate in colors["0"]:
            directKeys.rblx_click(image_to_game_coordinates(FRAME_TOP_LEFT_COORDINATE, 1290 / (DRAWING_WIDTH_SIZE * 3), coordinate))

        change_color_click((71, 779))  # Change to white
        for coordinate in colors["255"]:
            directKeys.rblx_click(image_to_game_coordinates(FRAME_TOP_LEFT_COORDINATE, 1290 / (DRAWING_WIDTH_SIZE * 3), coordinate))

        # Save frame
        pag.screenshot(f"{RENDERED_FRAMES_SAVE_FOLDER}/frame_{new_frame_number}.png")
        log_frame(new_frame_number)
        clear_all()

        timer_end = time.time()
        time_taken_seconds = int(timer_end) - int(timer_start)
        print(f"Created frame #{new_frame_number} in {time_taken_seconds}s ({time_taken_seconds / 60}m)")

        time.sleep(COOLDOWN_BETWEEN_FRAMES)
