import cv2
import sys

def run_webcam():
    """
    Initializes and streams from a normal webcam (RGB only).
    Tries multiple camera indices to find a working one.
    If multiple cameras are found, it asks the user to select one.
    """
    cap = None
    found_cam_index = -1
    available_indices = []

    # Try camera indices from 0 to 4 to find all working ones
    print("Searching for a working webcam...")
    for i in range(5):
        # We explicitly use the V4L2 backend on Linux, but CAP_ANY is more cross-platform.
        # Let's try CAP_ANY first.
        cap_test_any = cv2.VideoCapture(i, cv2.CAP_ANY)
        
        if cap_test_any.isOpened():
            print(f"Success: Found a working camera at index {i}.")
            available_indices.append(i)
            # Release it, we're just checking
            cap_test_any.release()
        else:
            # Try V4L2 backend specifically if CAP_ANY failed, as per your error logs
            cap_test_v4l = cv2.VideoCapture(i, cv2.CAP_V4L2)
            if cap_test_v4l.isOpened():
                print(f"Success: Found a working camera at index {i} (using V4L2).")
                available_indices.append(i)
                cap_test_v4l.release()


    # --- Selection Logic ---
    if len(available_indices) == 0:
        print("Error: Could not open any webcam. Tried indices 0-4.")
        print("Please ensure your webcam is connected and drivers are installed.")
        return
    elif len(available_indices) == 1:
        # Only one camera found, use it
        found_cam_index = available_indices[0]
    else:
        # Multiple cameras found, ask the user to choose
        print("\nFound multiple cameras. Please choose:")
        # Use a set to show unique indices, in case CAP_ANY and CAP_V4L2 found the same one
        unique_indices = sorted(list(set(available_indices))) 
        for idx in unique_indices:
            print(f"  {idx}: Camera at index {idx}")
        
        try:
            choice_str = input("Enter camera index: ")
            choice_int = int(choice_str)
            
            if choice_int in unique_indices:
                found_cam_index = choice_int
            else:
                print("Invalid selection. Exiting.")
                return
        except ValueError:
            print("Invalid input. Please enter a number. Exiting.")
            return

    # --- Start Stream ---
    print(f"Starting webcam stream from index {found_cam_index}...")
    # Use CAP_ANY to be safe, but you could also use found_cam_index directly
    cap = cv2.VideoCapture(found_cam_index) 
    
    if not cap.isOpened():
        print(f"Error: Failed to open camera at index {found_cam_index} (it may be in use).")
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

if __name__ == "__main__":
    run_webcam()