import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np
import FreeSimpleGUIWeb as sg

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

# Function to handle video capture and drawing
def video_capture():
    global captured_image
    global window
    global cap

    # cap = cv2.VideoCapture(2)
    cap = cv2.VideoCapture(0)

    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3000)

    # Define the rectangle dimensions (centered on screen)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    rect_w, rect_h = 200, 200  # Rectangle dimensions
    rect_x = (frame_width - rect_w) // 2
    rect_y = (frame_height - rect_h) // 2
    rect = (rect_x, rect_y, rect_w, rect_h)

    layout = [
        [sg.Image(filename="", key="-IMAGE-"), sg.Image(filename="", key="-CAPTURED-"), sg.Image(filename="", key="-DIFF-"), sg.Image(filename="", key="-CURRENTFRAME-")],
        [sg.Button("Capture", key="-CAPTURE-"), sg.Button("Compare", key="-COMPARE-"), sg.Button("Quit", key="-QUIT-")],
        [sg.Text("", key="-SSIM-")]
    ]

    window = sg.Window("Video Capture", layout, location=(800, 400), web_port=8080, web_start_browser=True)

    while True:
        event, values = window.read(timeout=20)
        ret, frame = cap.read()
        if not ret:
            break

        # Draw a rectangle in the middle of the frame
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

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

