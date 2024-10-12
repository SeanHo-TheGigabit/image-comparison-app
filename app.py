import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import FreeSimpleGUI as sg
import json

captured_image = None
window = None
cap = None


# Function to capture the frame inside the rectangle
def capture_frame(frame, rect):
    x, y, w, h = rect
    return frame[y : y + h, x : x + w]


# Function to compare the captured image with the live frame inside the rectangle
def compare_images(image1, image2):
    # Convert to grayscale for SSIM comparison
    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Compute SSIM
    score, diff = ssim(image1_gray, image2_gray, full=True)
    diff = (diff * 255).astype("uint8")

    print(f"SSIM Score: {score:.4f}")
    return score, diff


# Function to read configuration from JSON file
def read_config(file_path):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config


# Function to write configuration to JSON file
def write_config(file_path, config):
    with open(file_path, "w") as file:
        json.dump(config, file, indent=4)


# Function to handle video capture and drawing
def video_capture():
    global captured_image
    global window
    global cap

    # Read configuration
    config = read_config("config.json")
    top = config.get("top", 0.2)
    right = config.get("right", 0.8)
    bottom = config.get("bottom", 0.8)
    left = config.get("left", 0.2)

    # cap = cv2.VideoCapture(2)
    cap = cv2.VideoCapture(0)

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3000)

    layout = [
        [
            sg.Image(filename="", key="-IMAGE-"),
            sg.Image(filename="", key="-CAPTURED-"),
            sg.Image(filename="", key="-DIFF-"),
            sg.Image(filename="", key="-CURRENTFRAME-"),
        ],
        [
            sg.Button("Capture", key="-CAPTURE-"),
            sg.Button("Compare", key="-COMPARE-"),
            sg.Button("Quit", key="-QUIT-"),
        ],
        [sg.Text("", key="-SSIM-")],
        [sg.Text("Top"), sg.InputText(default_text=str(top), key="-TOP-", size=(5, 1))],
        [
            sg.Text("Right"),
            sg.InputText(default_text=str(right), key="-RIGHT-", size=(5, 1)),
        ],
        [
            sg.Text("Bottom"),
            sg.InputText(default_text=str(bottom), key="-BOTTOM-", size=(5, 1)),
        ],
        [
            sg.Text("Left"),
            sg.InputText(default_text=str(left), key="-LEFT-", size=(5, 1)),
        ],
        [sg.Button("Update Rectangle", key="-UPDATE-")],
    ]

    window = sg.Window("Video Capture", layout, location=(800, 400))

    while True:
        event, values = window.read(timeout=20)
        ret, frame = cap.read()
        if not ret:
            break

        # Update rectangle dimensions based on user input
        if event == "-UPDATE-":
            top = float(values["-TOP-"])
            right = float(values["-RIGHT-"])
            bottom = float(values["-BOTTOM-"])
            left = float(values["-LEFT-"])

            # Update the configuration and write to the JSON file
            config["top"] = top
            config["right"] = right
            config["bottom"] = bottom
            config["left"] = left
            write_config("config.json", config)

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        rect_x = int(left * frame_width)
        rect_y = int(top * frame_height)
        rect_w = int((right - left) * frame_width)
        rect_h = int((bottom - top) * frame_height)
        rect = (rect_x, rect_y, rect_w, rect_h)

        # Draw a rectangle in the middle of the frame
        cv2.rectangle(
            frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2
        )

        # Convert the frame to a format that can be displayed in PySimpleGUI
        imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)

        if event == sg.WIN_CLOSED or event == "-QUIT-":
            print("Closing the window...")
            break

        if event == "-CAPTURE-":
            print("Capturing image...")
            captured_image = capture_frame(frame, rect)
            captured_imgbytes = cv2.imencode(".png", captured_image)[1].tobytes()
            window["-CAPTURED-"].update(data=captured_imgbytes)
            print("Image Captured!")

        if event == "-COMPARE-":
            print("Comparing images...")
            if captured_image is not None:
                live_frame = capture_frame(frame, rect)
                score, diff_image = compare_images(captured_image, live_frame)
                diff_imgbytes = cv2.imencode(".png", diff_image)[1].tobytes()
                live_imgbytes = cv2.imencode(".png", live_frame)[1].tobytes()
                window["-IMAGE-"].update(data=live_imgbytes)
                window["-CURRENTFRAME-"].update(data=live_imgbytes)
                window["-DIFF-"].update(data=diff_imgbytes)
                window["-SSIM-"].update(f"SSIM Score: {score:.4f}")
            else:
                print("No image captured for comparison.")

    print("Closing the window...")
    cap.release()
    print("Releasing the camera...")
    cv2.destroyAllWindows()
    print("Destroy all cv2 window")
    window.close()
    print("Window closed")


# Run the video capture
try:
    video_capture()
except Exception as err:
    print(f"Error: {err}")

    print("Closing the window...")
    cap.release()
    print("Releasing the camera...")
    cv2.destroyAllWindows()
    print("Destroy all cv2 window")
    window.close()
    print("Window closed")
