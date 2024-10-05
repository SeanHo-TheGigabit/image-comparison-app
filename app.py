import cv2
from skimage.metrics import structural_similarity as ssim
import numpy as np

captured_image = None

# Function to capture the frame inside the rectangle
def capture_frame(frame, rect):
    x, y, w, h = rect
    return frame[y:y+h, x:x+w]

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

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        print(frame.shape)

        # Draw a rectangle in the middle of the frame
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

        # Show the live video feed
        cv2.imshow('Live Video Feed', frame)

        # Capture frame with 'c' and compare with 'v'
        key = cv2.waitKey(1) & 0xFF

        
        if key == ord('c'):  # Capture
            captured_image = capture_frame(frame, rect)
            cv2.imshow('Captured Image', captured_image)
            print("Image Captured!")

        elif key == ord('v'):  # Compare
            if captured_image is not None:
                live_frame = capture_frame(frame, rect)
                score, diff_image = compare_images(captured_image, live_frame)
                cv2.imshow('Live Image', live_frame)
                cv2.imshow('Difference Image', diff_image)
            else:
                print("No image captured for comparison.")

        elif key == ord('q'):  # Quit
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the video capture
video_capture()
