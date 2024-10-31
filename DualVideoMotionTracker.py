import cv2
import numpy as np
import pandas as pd

# Initialize lists to store the clicked points
left_points = []
right_points = []

# Colors for the points
colors = [(255, 0, 0), (202, 51, 255), (0, 0, 255)]

def add_point(points, x, y, label):
    """
    Adds a point to the list if there are less than 3 points.
    
    Args:
        points (list): List to which the point is added.
        x (int): X coordinate of the point.
        y (int): Y coordinate of the point.
        label (str): Label to identify the point (e.g., "Left" or "Right").
    
    Outputs:
        Prints the added point and its coordinates.
    """
    if len(points) < 3:
        points.append((x, y))
        print(f"{label} Point {len(points)}: ({x}, {y})")

def add_special_point(points, label, value):
    """
    Adds a special point (with specific value) to the list if there are less than 3 points.
    
    Args:
        points (list): List to which the point is added.
        x (int): X coordinate related to the special point.
        label (str): Label to identify the point (e.g., "Left" or "Right").
        value (tuple): The special value to be added to the points list.
    
    Outputs:
        Prints the added special point and its value.
    """
    if len(points) < 3:
        points.append(value)
        print(f"{label} Point {len(points)}: {value}")

def handle_click(event, x, y, frame, left_points, right_points):
    """
    Handles mouse click events, adding points to left or right points list based on click position.
    
    Args:
        event (int): The type of mouse event (e.g., cv2.EVENT_LBUTTONDOWN).
        x (int): X coordinate of the mouse click.
        y (int): Y coordinate of the mouse click.
        frame (numpy.ndarray): The video frame where the click is detected.
        left_points (list): List of points on the left side.
        right_points (list): List of points on the right side.
    
    Outputs:
        Calls functions to add points or handle overlay clicks based on click position.
    """
    frame_width = frame.shape[1] // 2
    frame_height = frame.shape[0]

    if event == cv2.EVENT_LBUTTONDOWN:
        if y < frame_height:  # Click is in the video frame
            if x < frame_width:  # Left half of the frame
                add_point(left_points, x, y, "Left")
            else:  # Right half of the frame
                add_point(right_points, x - frame_width, y, "Right")
        else:  # Click is in the overlay
            handle_overlay_click(x, frame_width, left_points, right_points)

def handle_overlay_click(x, frame_width, left_points, right_points):
    """
    Determines which side of the overlay was clicked and handles the click accordingly.
    
    Args:
        x (int): X coordinate of the mouse click.
        frame_width (int): Half of the frame width.
        left_points (list): List of points on the left side.
        right_points (list): List of points on the right side.
    
    Outputs:
        Calls function to handle button clicks on the overlay.
    """
    button_width = frame_width // 4
    if x < frame_width:  # Left side of the overlay
        handle_button_click(x, button_width, left_points, "Left")
    else:  # Right side of the overlay
        handle_button_click(x - frame_width, button_width, right_points, "Right")

def handle_button_click(x, button_width, points, label):
    """
    Handles clicks on specific buttons within the overlay and performs corresponding actions.
    
    Args:
        x (int): X coordinate of the mouse click within the overlay section.
        button_width (int): Width of each button section in the overlay.
        points (list): List of points to modify.
        label (str): Label to identify the point (e.g., "Left" or "Right").
    
    Outputs:
        Adds special points or deletes the last point based on click position.
    """
    if x < button_width:
        add_special_point(points, label, (-1, -1))
    elif x < 2 * button_width:
        add_special_point(points, label, (-2, -2))
    elif x < 3 * button_width:
        for _ in range(3):
            add_special_point(points, label, (0, 0))
    else:
        if points:
            points.pop()
            print(f"Last {label.lower()} point deleted")

def mouse_callback(event, x, y, flags, param):
    """
    Callback function for mouse events. Directs handling of click events based on position.
    
    Args:
        event (int): The type of mouse event (e.g., cv2.EVENT_LBUTTONDOWN).
        x (int): X coordinate of the mouse click.
        y (int): Y coordinate of the mouse click.
        flags (int): Flags for the mouse event (not used here).
        param (dict): Dictionary containing frame and overlay information.
    
    Outputs:
        Calls the handle_click function with appropriate parameters.
    """
    handle_click(event, x, y, param['frame'], left_points, right_points)


def init_overlay(frame_width):
    """
    Initialize an overlay with predefined buttons and labels, including separation lines between buttons.

    Args:
        frame_width (int): The width of the frame where the overlay will be applied.

    Returns:
        numpy.ndarray: An overlay image with labeled buttons.
    """
    overlay = np.zeros((75, frame_width, 3), dtype=np.uint8)
    button_size = frame_width // 8
    labels = ["No detect (Top)", "Feeding (Top)", "None (Top)", "Del (Top)",
              "No detect (Lat.)", "Feeding (Lat.)", "None (Lat.)", "Del (Lat.)"]

    for i, label in enumerate(labels):
        # Draw the button background
        cv2.rectangle(overlay, (i * button_size, 0), ((i + 1) * button_size, 50), (255, 255, 255), -1)
        # Draw the label text
        cv2.putText(overlay, label, (i * button_size + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        # Draw the separation line, except after the last button
        if i < len(labels) - 1:
            cv2.line(overlay, ((i + 1) * button_size, 0), ((i + 1) * button_size, 50), (0, 0, 0), 4)
    
    cv2.rectangle(overlay, (0, 52), (frame_width, 75), (255, 255, 255), -1)
    
    return overlay

def setup_window(frac):
    """
    Set up the window for displaying video frames.

    Args:
        frac (float): Scale factor for resizing the video frame.
    """
    cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Frame", int(720 * frac) * 2, int(480 * frac + 75))

def process_videos(video_path_top, video_path_lat, output_excel, start_frame_top=0, start_frame_lat=0, frac=0.8):
    """
    Process video streams, capture points of interest from mouse clicks, and save to an Excel file.

    Args:
        video_path_top (str): Path to the top view video file.
        video_path_lat (str): Path to the lateral view video file.
        output_excel (str): Output path for the Excel file to save captured points.
        start_frame_top (int): Start frame number for the top view video.
        start_frame_lat (int): Start frame number for the lateral view video.
        frac (float): Scale factor for resizing the video frame.
    """
    # Open the video files
    cap_top, cap_lat = cv2.VideoCapture(video_path_top), cv2.VideoCapture(video_path_lat)
    if not cap_top.isOpened() or not cap_lat.isOpened():
        print("Error: Could not open one or both video files.")
        return
    
    # Set the starting frame for both videos
    cap_top.set(cv2.CAP_PROP_POS_FRAMES, start_frame_top)
    cap_lat.set(cv2.CAP_PROP_POS_FRAMES, start_frame_lat)
    
    # Set up the window for displaying video frames
    setup_window(frac)
    
    # Initialize the overlay with buttons
    overlay = init_overlay(int(720 * frac) * 2)
    
    # List to store all clicked points
    all_points = []

    while True:
        # Read frames from both videos
        ret_top, frame_top = cap_top.read()
        ret_lat, frame_lat = cap_lat.read()
        if not ret_top or not ret_lat:
            break

        # Resize frames
        frame_top = cv2.resize(frame_top, (int(720 * frac), int(480 * frac)))
        frame_lat = cv2.resize(frame_lat, (int(720 * frac), int(480 * frac)))
        
        # Combine frames from top and lateral views horizontally
        combined_frame = np.hstack((frame_top, frame_lat))
        
        # Add the overlay to the combined frame
        display_frame = np.vstack((combined_frame, overlay))
        
        # Set mouse callback for capturing points
        cv2.setMouseCallback("Frame", mouse_callback, {'frame': combined_frame, 'overlay': overlay})
        
        # Display frame and wait for user to click points
        while len(left_points) < 3 or len(right_points) < 3:
            temp_display_frame = display_frame.copy()
            
            # Draw clicked points on the display frame
            for i, point in enumerate(left_points):
                cv2.circle(temp_display_frame, point, 5, colors[i], -1)
                cv2.putText(temp_display_frame, f"({point[0]}, {point[1]})", (80*i, int(480 * frac) + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.3, colors[i], 1)
            for i, point in enumerate(right_points):
                cv2.circle(temp_display_frame, (point[0] + int(720 * frac), point[1]), 5, colors[i], -1)
                cv2.putText(temp_display_frame, f"({point[0]}, {point[1]})", (int(720 * frac) + 80*i, int(480 * frac) + 65), cv2.FONT_HERSHEY_SIMPLEX, 0.3, colors[i], 1)
            
            # Show the frame
            cv2.imshow("Frame", temp_display_frame)

            # Check for 'ESC' key press to exit
            if cv2.waitKey(1) & 0xFF == 27:
                # Release video capture objects and destroy windows
                cap_top.release()
                cap_lat.release()
                cv2.destroyAllWindows()

                # Save captured points to an Excel file
                df = pd.DataFrame(all_points)
                df.to_csv(output_excel, index=False)
                print(f"Data saved to {output_excel}")
                return

        # Store and print the clicked points, then clear for the next frame
        current_points = {
            'Left Point 1': left_points[0] if len(left_points) > 0 else (np.nan, np.nan),
            'Left Point 2': left_points[1] if len(left_points) > 1 else (np.nan, np.nan),
            'Left Point 3': left_points[2] if len(left_points) > 2 else (np.nan, np.nan),
            'Right Point 1': right_points[0] if len(right_points) > 0 else (np.nan, np.nan),
            'Right Point 2': right_points[1] if len(right_points) > 1 else (np.nan, np.nan),
            'Right Point 3': right_points[2] if len(right_points) > 2 else (np.nan, np.nan)
        }
        all_points.append(current_points)
        print("Clicked points for the current frame:", left_points + right_points)
        
        # Clear the points for the next frame
        left_points.clear()
        right_points.clear()

    # Release video capture objects and destroy windows after processing all frames
    cap_top.release()
    cap_lat.release()
    cv2.destroyAllWindows()

    # Save captured points to an Excel file
    df = pd.DataFrame(all_points)
    df.to_csv(output_excel, index=False)
    print(f"Data saved to {output_excel}")
