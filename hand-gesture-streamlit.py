import streamlit as st
import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import numpy as np
from PIL import Image
import time

# Page configuration
st.set_page_config(
    page_title="Hand Gesture Presentation",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'imgNumber' not in st.session_state:
    st.session_state.imgNumber = 0
if 'annotations' not in st.session_state:
    st.session_state.annotations = [[]]
if 'annotationNumber' not in st.session_state:
    st.session_state.annotationNumber = -1
if 'annotationStart' not in st.session_state:
    st.session_state.annotationStart = False
if 'buttonPressed' not in st.session_state:
    st.session_state.buttonPressed = False
if 'buttonCounter' not in st.session_state:
    st.session_state.buttonCounter = 0
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

# Constants
WIDTH, HEIGHT = 1280, 720
GESTURE_THRESHOLD = 500
BUTTON_DELAY = 10
HS, WS = 100, 170

# Sidebar
st.sidebar.title("🎯 Gesture Controls")
st.sidebar.markdown("""
### Hand Gestures:
- 👍 **Thumb Only**: Previous slide
- 🤙 **Pinky Only**: Next slide
- ✌️ **Index + Middle**: Show pointer
- ☝️ **Index Only**: Draw
- 🤟 **Index + Middle + Ring**: Erase last
- 🤘 **Index + Pinky**: Erase all
""")

folder_path = st.sidebar.text_input("Presentation Folder", "Presentation Dummy")
gesture_threshold = st.sidebar.slider("Gesture Threshold", 300, 700, GESTURE_THRESHOLD)

# Main title
st.title("👋 Hand Gesture Presentation Controller")

# Get presentation images
if os.path.exists(folder_path):
    path_images = sorted(os.listdir(folder_path), key=len)
    path_images = [img for img in path_images if img.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not path_images:
        st.error("No images found in the presentation folder!")
        st.stop()
else:
    st.error(f"Folder '{folder_path}' not found!")
    st.stop()

# Navigation buttons
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("⬅️ Previous"):
        if st.session_state.imgNumber > 0:
            st.session_state.imgNumber -= 1
            st.session_state.annotations = [[]]
            st.session_state.annotationNumber = -1

with col2:
    if st.button("➡️ Next"):
        if st.session_state.imgNumber < len(path_images) - 1:
            st.session_state.imgNumber += 1
            st.session_state.annotations = [[]]
            st.session_state.annotationNumber = -1

with col3:
    if st.button("🗑️ Clear Annotations"):
        st.session_state.annotations = [[]]
        st.session_state.annotationNumber = -1

with col4:
    st.metric("Slide", f"{st.session_state.imgNumber + 1} / {len(path_images)}")

with col5:
    camera_toggle = st.checkbox("📷 Enable Camera", value=st.session_state.camera_active)
    st.session_state.camera_active = camera_toggle

# Display columns
display_col1, display_col2 = st.columns([2, 1])

# Placeholder for video and slide
video_placeholder = display_col2.empty()
slide_placeholder = display_col1.empty()
status_placeholder = st.empty()

# Initialize hand detector
detector = HandDetector(detectionCon=0.5, maxHands=1)

# Camera processing
if st.session_state.camera_active:
    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    
    stframe = st.empty()
    
    # Run camera loop
    while st.session_state.camera_active:
        success, img = cap.read()
        if not success:
            st.error("Failed to access camera")
            break
        
        img = cv2.flip(img, 1)
        
        # Load current slide
        path_full_image = os.path.join(folder_path, path_images[st.session_state.imgNumber])
        img_current = cv2.imread(path_full_image)
        
        if img_current is None:
            st.error(f"Failed to load image: {path_images[st.session_state.imgNumber]}")
            break
        
        # Hand detection
        hands, img = detector.findHands(img)
        cv2.line(img, (0, gesture_threshold), (WIDTH, gesture_threshold), (0, 255, 0), 10)
        
        gesture_detected = "None"
        
        if hands and not st.session_state.buttonPressed:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            cx, cy = hand['center']
            lmList = hand['lmList']
            
            # Calculate index finger position
            xVal = int(np.interp(lmList[8][0], [WIDTH // 2, WIDTH], [0, WIDTH]))
            yVal = int(np.interp(lmList[8][1], [150, HEIGHT - 150], [0, HEIGHT]))
            indexFinger = (xVal, yVal)
            
            if cy <= gesture_threshold:
                # Gesture 1 - Left (Thumb only)
                if fingers == [1, 0, 0, 0, 0]:
                    gesture_detected = "Previous Slide"
                    if st.session_state.imgNumber > 0:
                        st.session_state.buttonPressed = True
                        st.session_state.annotations = [[]]
                        st.session_state.annotationNumber = -1
                        st.session_state.annotationStart = False
                        st.session_state.imgNumber -= 1
                
                # Gesture 2 - Right (Pinky only)
                if fingers == [0, 0, 0, 0, 1]:
                    gesture_detected = "Next Slide"
                    if st.session_state.imgNumber < len(path_images) - 1:
                        st.session_state.buttonPressed = True
                        st.session_state.annotations = [[]]
                        st.session_state.annotationNumber = -1
                        st.session_state.annotationStart = False
                        st.session_state.imgNumber += 1
            
            # Gesture 3 - Show Pointer
            if fingers == [0, 1, 1, 0, 0]:
                gesture_detected = "Pointer"
                cv2.circle(img_current, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            
            # Gesture 4 - Draw
            if fingers == [0, 1, 0, 0, 0]:
                gesture_detected = "Drawing"
                if not st.session_state.annotationStart:
                    st.session_state.annotationStart = True
                    st.session_state.annotationNumber += 1
                    st.session_state.annotations.append([])
                cv2.circle(img_current, indexFinger, 12, (0, 0, 255), cv2.FILLED)
                st.session_state.annotations[st.session_state.annotationNumber].append(indexFinger)
            else:
                st.session_state.annotationStart = False
            
            # Gesture 5 - Erase last
            if fingers == [0, 1, 1, 1, 0]:
                gesture_detected = "Erase Last"
                if st.session_state.annotations:
                    st.session_state.annotations.pop(-1)
                    st.session_state.annotationNumber -= 1
                    st.session_state.buttonPressed = True
            
            # Gesture 6 - Erase All
            if fingers == [0, 1, 0, 0, 1]:
                gesture_detected = "Erase All"
                st.session_state.annotations = [[]]
                st.session_state.annotationNumber = -1
                st.session_state.annotationStart = False
        
        # Button press delay
        if st.session_state.buttonPressed:
            st.session_state.buttonCounter += 1
            if st.session_state.buttonCounter > BUTTON_DELAY:
                st.session_state.buttonCounter = 0
                st.session_state.buttonPressed = False
        
        # Draw annotations
        for i in range(len(st.session_state.annotations)):
            for j in range(len(st.session_state.annotations[i])):
                if j != 0:
                    cv2.line(img_current, 
                            st.session_state.annotations[i][j-1], 
                            st.session_state.annotations[i][j], 
                            (0, 0, 200), 12)
        
        # Add webcam thumbnail to slide
        img_small = cv2.resize(img, (WS, HS))
        h, w, _ = img_current.shape
        img_current[0:HS, w-WS:w] = img_small
        
        # Display
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            img_current_rgb = cv2.cvtColor(img_current, cv2.COLOR_BGR2RGB)
            slide_placeholder.image(img_current_rgb, use_container_width=True, caption=f"Slide {st.session_state.imgNumber + 1}/{len(path_images)}")
        
        with col_right:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            video_placeholder.image(img_rgb, use_container_width=True, caption="Camera Feed")
        
        status_placeholder.info(f"🎯 Gesture Detected: **{gesture_detected}**")
        
        # Small delay to reduce CPU usage
        time.sleep(0.03)
    
    cap.release()
else:
    # Display slide without camera
    path_full_image = os.path.join(folder_path, path_images[st.session_state.imgNumber])
    img_current = cv2.imread(path_full_image)
    
    if img_current is not None:
        # Draw annotations
        for i in range(len(st.session_state.annotations)):
            for j in range(len(st.session_state.annotations[i])):
                if j != 0:
                    cv2.line(img_current, 
                            st.session_state.annotations[i][j-1], 
                            st.session_state.annotations[i][j], 
                            (0, 0, 200), 12)
        
        img_current_rgb = cv2.cvtColor(img_current, cv2.COLOR_BGR2RGB)
        slide_placeholder.image(img_current_rgb, use_container_width=True, caption=f"Slide {st.session_state.imgNumber + 1}/{len(path_images)}")
        status_placeholder.info("📷 Enable camera to use hand gestures")
    else:
        st.error(f"Failed to load image: {path_images[st.session_state.imgNumber]}")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit • Hand tracking powered by CVZone")