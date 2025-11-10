import pyrealsense2 as rs
import numpy as np
import cv2

def run_realsense():
    """
    Initializes and streams both color and depth data from a RealSense camera.
    """
    # --- Setup ---
    # Create a pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()

    # Tell config that we want to stream both depth and color data
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Create an align object
    # rs.align aligns the depth frame to the perspective of the color frame
    align_to = rs.stream.color
    align = rs.align(align_to)
    
    # Start streaming
    print("Starting RealSense pipeline...")
    try:
        profile = pipeline.start(config)
    except Exception as e:
        print(f"Failed to start RealSense pipeline: {e}")
        print("Is the RealSense camera plugged in?")
        return

    try:
        while True:
            # --- Get Frames ---
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            
            # Align the depth frame to the color frame
            aligned_frames = align.process(frames)

            # Get the aligned frames
            depth_frame = aligned_frames.get_depth_frame() 
            color_frame = aligned_frames.get_color_frame()
            
            # Validate that both frames are valid
            if not depth_frame or not color_frame:
                continue
                
            # --- Process Frames ---
            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            
            # Apply a colormap to the depth image for visualization
            # This converts the 16-bit (z16) depth image to an 8-bit (uint8)
            # BGR image that OpenCV can display.
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03), 
                cv2.COLORMAP_JET
            )

            # --- Display Images ---
            # Stack images horizontally (side-by-side)
            images = np.hstack((color_image, depth_colormap))
            
            # Show the combined image in a window
            cv2.namedWindow('RealSense Color and Depth', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense Color and Depth', images)
            
            # Exit the loop when 'q' or 'ESC' is pressed
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                break

    finally:
        # --- Cleanup ---
        print("Stopping RealSense pipeline...")
    pipeline.stop()
    cv2.destroyAllWindows()

def run_webcam():
    """
    Initializes and streams from a normal webcam (RGB only).
    Tries multiple camera indices to find a working one.
    If multiple cameras are found, it asks the user to select one.
    """

    # --- Start Stream ---
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print(f"Error: Failed to open camera at index (it may be in use).")
        return

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            
            # if frame is read correctly ret is True
            if not ret:
                print("Error: Can't receive frame (stream end?). Exiting ...")
                break
                
            # Display the resulting frame
            cv2.imshow('Normal Webcam', frame)
            
            # Exit the loop when 'q' or 'ESC' is pressed
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q') or key == 27:
                break
                
    finally:
        # --- Cleanup ---
        print("Stopping webcam stream...")
        cap.release()
        cv2.destroyAllWindows()

def main():
    """
    Asks the user to select a camera source and runs the corresponding stream.
    """
    print("Please select a camera source:")
    print("  1: Intel RealSense (Color + Depth)")
    print("  2: Normal Webcam (Color only)")
    choice = input("Enter choice (1 or 2): ")
    
    if choice == '1':
        run_realsense()
    elif choice == '2':
        run_webcam()
    else:
        print("Invalid choice. Please run the script again and enter 1 or 2.")

if __name__ == "__main__":
    main()