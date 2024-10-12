import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import FreeSimpleGUI as sg
import json
import os
from datetime import datetime

captured_image = None
window = None
cap = None
similarity_threshold = 0.5  # Default threshold value
auto_compare = False  # Auto-compare mode flag


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
    default_config = {"top": 0.2, "right": 0.8, "bottom": 0.8, "left": 0.2}
    try:
        with open(file_path, "r") as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        config = default_config
        write_config(file_path, config)
    return config


# Function to write configuration to JSON file
def write_config(file_path, config):
    with open(file_path, "w") as file:
        json.dump(config, file, indent=4)


# Function to generate a unique filename
def generate_filename(prefix="capture", ext=".png"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}{ext}"


# Function to handle video capture and drawing
def video_capture():
    global captured_image
    global window
    global cap
    global similarity_threshold
    global auto_compare

    # Read configuration
    config = read_config("config.json")
    top = config.get("top", 0.2)
    right = config.get("right", 0.8)
    bottom = config.get("bottom", 0.8)
    left = config.get("left", 0.2)

    # Read captured image if it exists and is not empty
    if (
        os.path.exists("captured_image.png")
        and os.path.getsize("captured_image.png") > 0
    ):
        captured_image = cv2.imread("captured_image.png")
        print("Captured image loaded successfully.")
    else:
        print("No captured image found or file is empty.")

    # cap = cv2.VideoCapture(2)
    cap = cv2.VideoCapture(0)

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3000)

    layout = [
        [
            sg.Button("Quit App", key="-QUIT-"),
        ],
        [
            sg.Column(
                [
                    [
                        sg.Button("Capture Reference", key="-CAPTURE-"),
                    ],
                    [
                        sg.Button("Single Compare", key="-COMPARE-"),
                        sg.Button("Enable/Disable Auto Compare", key="-AUTO-COMPARE-"),
                    ],
                    [sg.Text("Similarity: 0.00%", key="-SSIM-")],
                    [sg.Text("Similarity Decision: ", key="-DECISION-")],
                    [
                        sg.Text("Top"),
                        sg.Slider(
                            range=(0, 1),
                            resolution=0.1,
                            orientation="h",
                            size=(20, 15),
                            default_value=top,
                            key="-TOP-",
                        ),
                    ],
                    [
                        sg.Text("Right"),
                        sg.Slider(
                            range=(0, 1),
                            resolution=0.1,
                            orientation="h",
                            size=(20, 15),
                            default_value=right,
                            key="-RIGHT-",
                        ),
                    ],
                    [
                        sg.Text("Bottom"),
                        sg.Slider(
                            range=(0, 1),
                            resolution=0.1,
                            orientation="h",
                            size=(20, 15),
                            default_value=bottom,
                            key="-BOTTOM-",
                        ),
                    ],
                    [
                        sg.Text("Left"),
                        sg.Slider(
                            range=(0, 1),
                            resolution=0.1,
                            orientation="h",
                            size=(20, 15),
                            default_value=left,
                            key="-LEFT-",
                        ),
                    ],
                    [sg.Button("Update Rectangle", key="-UPDATE-")],
                    [
                        sg.Text("Similarity Threshold"),
                        sg.Slider(
                            range=(0, 1),
                            resolution=0.01,
                            orientation="h",
                            size=(20, 15),
                            default_value=similarity_threshold,
                            key="-THRESHOLD-",
                        ),
                    ],
                    [sg.Button("Update Threshold", key="-APPLY-THRESHOLD-")],
                ]
            ),
            sg.Column(
                [
                    [sg.Image(filename="", key="-IMAGE-")],
                    [sg.Text("Live Frame")],
                ]
            ),
        ],
        [
            sg.Column(
                [
                    [sg.Image(filename="", key="-CAPTURED-")],
                    [sg.Text("Captured Image")],
                ]
            ),
            sg.Column(
                [
                    [sg.Image(filename="", key="-DIFF-")],
                    [sg.Text("Difference Image")],
                ]
            ),
            sg.Column(
                [
                    [sg.Image(filename="", key="-CURRENTFRAME-")],
                    [sg.Text("Current Frame")],
                ]
            ),
        ],
    ]

    window = sg.Window("Video Capture", layout, location=(800, 400))

    # Initialize Setup
    event, values = window.read(timeout=20)
    if capture_frame is not None:
        window["-CAPTURED-"].update(
            data=cv2.imencode(".png", captured_image)[1].tobytes()
        )

    def run_comparison():
        if captured_image is not None:
            live_frame = capture_frame(frame, rect)
            score, diff_image = compare_images(captured_image, live_frame)
            similarity_percentage = score * 100
            diff_imgbytes = cv2.imencode(".png", diff_image)[1].tobytes()
            live_imgbytes = cv2.imencode(".png", live_frame)[1].tobytes()
            window["-CURRENTFRAME-"].update(data=live_imgbytes)
            window["-DIFF-"].update(data=diff_imgbytes)
            window["-SSIM-"].update(f"Similarity: {similarity_percentage:.2f}%")

            # Determine similarity decision
            decision = "Similar" if score >= similarity_threshold else "Dissimilar"
            print("similarity_threshold", similarity_threshold)
            window["-DECISION-"].update(f"Similarity Decision: {decision}")
        else:
            print("No image captured for comparison.")

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

        # Update similarity threshold based on user input
        if event == "-APPLY-THRESHOLD-":
            similarity_threshold = float(values["-THRESHOLD-"])

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

            # Save the captured image to a file
            filename = "captured_image.png"
            cv2.imwrite(filename, captured_image)
            print(f"Image saved as {filename}")

        if event == "-COMPARE-":
            print("Comparing images...")
            run_comparison()

        if event == "-AUTO-COMPARE-":
            auto_compare = not auto_compare
            if auto_compare:
                print("Auto-compare mode enabled.")
            else:
                print("Auto-compare mode disabled.")

        if auto_compare:
            run_comparison()

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
