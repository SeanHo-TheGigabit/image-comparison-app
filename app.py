import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import FreeSimpleGUI as sg
import json
import os
from datetime import datetime

captured_image = None
window = None
color_window = None
cap = None
similarity_threshold = 0.5  # Default threshold value
auto_compare = False  # Auto-compare mode flag
diff_scale_factor = 1.0  # Default scale factor for difference image
live_scale_factor = 1.0  # Default scale factor for live frame
stream_width = 640  # Default stream width
stream_height = 480  # Default stream height


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


# Function to resize image based on scale factor
def resize_image(image, scale_factor):
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


# Function to handle video capture and drawing
def video_capture():
    global captured_image
    global window
    global color_window
    global cap
    global similarity_threshold
    global auto_compare
    global diff_scale_factor
    global live_scale_factor
    global stream_width
    global stream_height

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
        captured_image = cv2.imread("sample/sample_capture.png")
        print("No captured image found or file is empty.")
        print("Loaded sample image for comparison.")

    layout = [
        [
            sg.Button("Quit App", key="-QUIT-"),
        ],
        [
            sg.Column(
                [
                    [
                        sg.Frame(
                            "Stream Settings",
                            [
                                [
                                    sg.Text(f"Stream Width:  ", key="-WIDTH-TEXT-"),
                                    sg.Slider(
                                        range=(320, 1920),
                                        orientation="h",
                                        resolution=1,
                                        size=(20, 15),
                                        default_value=stream_width,
                                        key="-WIDTH-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                ],
                                [
                                    sg.Text(f"Stream Height: ", key="-HEIGHT-TEXT-"),
                                    sg.Slider(
                                        range=(240, 1080),
                                        orientation="h",
                                        resolution=1,
                                        size=(20, 15),
                                        default_value=stream_height,
                                        key="-HEIGHT-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                ],
                            ],
                        ),
                    ],
                    [
                        sg.Frame(
                            "Camera and Rectangle Settings",
                            [
                                [
                                    sg.Text("Select Camera"),
                                    sg.Combo(
                                        ["Camera 0", "Camera 1"],
                                        default_value="Camera 0",
                                        key="-CAMERA-",
                                        readonly=True,
                                    ),
                                    sg.Button("Apply Camera", key="-APPLY-CAMERA-"),
                                ],
                                [
                                    sg.Text("Top"),
                                    sg.Slider(
                                        range=(0, 1),
                                        orientation="h",
                                        resolution=0.01,
                                        size=(20, 15),
                                        default_value=top,
                                        key="-TOP-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                    sg.Text("Bottom"),
                                    sg.Slider(
                                        range=(0, 1),
                                        orientation="h",
                                        resolution=0.01,
                                        size=(20, 15),
                                        default_value=bottom,
                                        key="-BOTTOM-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                ],
                                [
                                    sg.Text("Left"),
                                    sg.Slider(
                                        range=(0, 1),
                                        orientation="h",
                                        resolution=0.01,
                                        size=(20, 15),
                                        default_value=left,
                                        key="-LEFT-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                    sg.Text("Right   "),
                                    sg.Slider(
                                        range=(0, 1),
                                        orientation="h",
                                        resolution=0.01,
                                        size=(20, 15),
                                        default_value=right,
                                        key="-RIGHT-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                ],
                                [sg.Button("Save Config", key="-SAVE-CONFIG-")],
                            ],
                        ),
                    ],
                    [
                        sg.Frame(
                            "Similarity and Scaling",
                            [
                                [
                                    sg.Text(
                                        "Similarity               : 0.00%",
                                        key="-SSIM-",
                                        font=("Helvetica", 16),
                                    )
                                ],
                                [
                                    sg.Text(
                                        f"Current Threshold : {similarity_threshold*100:.2f}%",
                                        key="-CURRENT-THRESHOLD-",
                                        font=("Helvetica", 16),
                                    ),
                                ],
                                [
                                    sg.Text(
                                        "Similarity Decision: ",
                                        key="-DECISION-",
                                        font=("Helvetica", 16),
                                        background_color="red",
                                    ),
                                ],
                                [
                                    sg.Text("Similarity Threshold"),
                                    sg.Slider(
                                        range=(0, 1),
                                        resolution=0.01,
                                        orientation="h",
                                        size=(20, 15),
                                        default_value=similarity_threshold,
                                        key="-THRESHOLD-",
                                        enable_events=True,  # Enable events for live update
                                    ),
                                ],
                                [
                                    sg.Text("Live Image Scaling"),
                                    sg.Button("+", key="-LIVEFRAME-PLUS-"),
                                    sg.Button("-", key="-LIVEFRAME-MINUS-"),
                                ],
                                [
                                    sg.Text("Compare Scaling   "),
                                    sg.Button("+", key="-DIFF-PLUS-"),
                                    sg.Button("-", key="-DIFF-MINUS-"),
                                ],
                            ],
                        ),
                    ],
                ]
            ),
            sg.Column(
                [
                    [
                        sg.Frame(
                            "Actions",
                            [
                                [
                                    sg.Button(
                                        "Capture Reference",
                                        key="-CAPTURE-",
                                        size=(20, 1),
                                    ),
                                ],
                                [
                                    sg.Button(
                                        "Single Compare", key="-COMPARE-", size=(20, 1)
                                    ),
                                    sg.Button(
                                        "Enable/Disable Auto Compare",
                                        key="-AUTO-COMPARE-",
                                    ),
                                ],
                            ],
                        ),
                    ],
                    [
                        sg.Frame(
                            "Important Info",
                            [
                                [
                                    sg.Text(
                                        "Capture new reference image if you change the stream or rectangle size to avoid stream fail.",
                                        font=("Helvetica", 12),
                                        size=(42, 2),
                                    )
                                ],
                            ],
                        ),
                    ],
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

    color_layout = [
        [
            sg.Text(
                "Similarity Color",
                key="-COLOR-TEXT-",
                size=(20, 1),
                font=("Helvetica", 12),
            )
        ],
        [sg.Text("", size=(40, 20), key="-COLOR-BLOCK-", background_color="red")],
    ]

    window = sg.Window(
        "Video Capture", layout, location=(0, 0)
    )  # Set location to top-left corner
    color_window = sg.Window(
        "Similarity Color", color_layout, location=(300, 0)
    )  # Adjust location as needed

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
            diff_image_resized = resize_image(diff_image, diff_scale_factor)
            live_frame_resized = resize_image(live_frame, diff_scale_factor)
            diff_imgbytes = cv2.imencode(".png", diff_image_resized)[1].tobytes()
            live_imgbytes = cv2.imencode(".png", live_frame_resized)[1].tobytes()
            window["-CURRENTFRAME-"].update(data=live_imgbytes)
            window["-DIFF-"].update(data=diff_imgbytes)
            window["-SSIM-"].update(
                f"Similarity               : {similarity_percentage:.2f}%"
            )

            # Determine similarity decision
            decision = "Similar" if score >= similarity_threshold else "Dissimilar"
            color = "green" if score >= similarity_threshold else "red"
            window["-DECISION-"].update(f"Similarity Decision: {decision}")
            window["-DECISION-"].update(background_color=color)

            # Update color window
            color_window["-COLOR-BLOCK-"].update(background_color=color)
            color_window["-COLOR-TEXT-"].update(f"Similarity Color: {color}")

        else:
            print("No image captured for comparison.")

    # Default camera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_height)

    while True:
        event, values = window.read(timeout=20)
        color_event, color_values = color_window.read(timeout=20)
        ret, frame = cap.read()
        if not ret:
            break

        # Update rectangle dimensions based on user input
        if event in ["-TOP-", "-RIGHT-", "-BOTTOM-", "-LEFT-"]:
            top = float(values["-TOP-"])
            right = float(values["-RIGHT-"])
            bottom = float(values["-BOTTOM-"])
            left = float(values["-LEFT-"])

        # Save configuration to file
        if event == "-SAVE-CONFIG-":
            config["top"] = top
            config["right"] = right
            config["bottom"] = bottom
            config["left"] = left
            write_config("config.json", config)

        # Update similarity threshold live
        if event == "-THRESHOLD-":
            similarity_threshold = float(values["-THRESHOLD-"])
            window["-CURRENT-THRESHOLD-"].update(
                f"Current Threshold : {similarity_threshold*100:.2f}%"
            )

        # Update camera based on user input
        if event == "-APPLY-CAMERA-":
            selected_camera = values["-CAMERA-"]
            camera_index = 0 if selected_camera == "Camera 0" else 1
            cap.release()
            cap = cv2.VideoCapture(camera_index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_height)

        # Handle scaling events
        if event == "-DIFF-PLUS-":
            diff_scale_factor += 0.1
        if event == "-DIFF-MINUS-":
            diff_scale_factor = max(0.1, diff_scale_factor - 0.1)
        if event == "-LIVEFRAME-PLUS-":
            live_scale_factor += 0.1
        if event == "-LIVEFRAME-MINUS-":
            live_scale_factor = max(0.1, live_scale_factor - 0.1)

        # Update the captured image if it exists
        if event == "-DIFF-PLUS-" or event == "-DIFF-MINUS-":
            if captured_image is not None:
                captured_image_resized = resize_image(captured_image, diff_scale_factor)
                captured_imgbytes = cv2.imencode(".png", captured_image_resized)[
                    1
                ].tobytes()
                window["-CAPTURED-"].update(data=captured_imgbytes)

        # Update stream width and height
        if event == "-WIDTH-":
            stream_width = int(values["-WIDTH-"])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_width)
        if event == "-HEIGHT-":
            stream_height = int(values["-HEIGHT-"])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_height)

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
        frame_resized = resize_image(frame, live_scale_factor)
        imgbytes = cv2.imencode(".png", frame_resized)[1].tobytes()
        window["-IMAGE-"].update(data=imgbytes)

        if event == sg.WIN_CLOSED or event == "-QUIT-" or color_event == sg.WIN_CLOSED:
            print("Closing the window...")
            break

        if event == "-CAPTURE-":
            print("Capturing image...")
            captured_image = capture_frame(frame, rect)
            captured_image_resized = resize_image(captured_image, diff_scale_factor)
            captured_imgbytes = cv2.imencode(".png", captured_image_resized)[
                1
            ].tobytes()
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
    color_window.close()
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
    color_window.close()
    print("Window closed")
