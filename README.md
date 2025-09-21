# Project Setup & Gesture Guide

This project allows you to control a presentation using hand gestures captured by your webcam. It uses computer vision to recognize specific hand poses to navigate slides, point, draw, and erase, offering an interactive and touch-free presentation experience.

---

## 📋 Features

-   **Slide Navigation**: Move forward and backward through your slides.
-   **Virtual Pointer**: Use your hand as a laser pointer.
-   **Live Annotation**: Draw on slides to emphasize points.
-   **Undo & Erase**: Remove annotations individually or all at once.

---

## 🛠️ Initialization & Prerequisites

Before you begin, you must have the required software and files set up.

### 1. Required Libraries
Make sure you have Python installed. You will also need to install the following libraries:

-   **OpenCV (`opencv-python`)**: Used to access the **camera** and process images.
-   **NumPy**: Used for creating and managing the **list** of finger states and other numerical operations.
-   **MediaPipe**: The core library for **hand gesture recognition**.

You can install all required libraries with a single command:
```bash
pip install opencv-python numpy mediapipe
```
---

## 📁 Presentation Folder Setup

You must have a **folder containing your presentation slides**. Before running the program, export each slide as a separate image file in **JPG or PNG format** and place them all together in one directory. The program will load these images in alphanumeric order.

---

## 🖐️ Gesture Guide

The control system works by identifying which of your fingers are extended. The state of your hand is read as a list of five numbers (`[0,0,0,0,0]`), where each number represents a finger.

-   **`1`** means the finger is **Open** (extended).
-   **`0`** means the finger is **Close** (curled).

The list index corresponds to your fingers as follows:

`[ 1:Thumb, 2:Index, 3:Middle, 4:Ring, 5:Pinkie ]`

### Control Commands

Here are all the specific commands and the hand gestures that trigger them.

#### 1. Next / Previous Slide
Used to navigate through your presentation images.
-   **Next Slide**: Extend only your **Pinkie** finger.
    -   `[0, 0, 0, 0, 1]`
-   **Previous Slide**: Extend only your **Thumb**.
    -   `[1, 0, 0, 0, 0]`

#### 2. Pointer
Activates a virtual pointer on the screen that follows your hand.
-   **Activate Pointer**: Extend your **Index and Middle fingers** (Peace Sign).
    -   `[0, 1, 1, 0, 0]`

#### 3. Draw
Allows you to draw on the slide to highlight areas of interest.
-   **Activate Drawing**: Extend only your **Index finger**.
    -   `[0, 1, 0, 0, 0]`

#### 4. Undo
Removes the last drawing you made on the slide.
-   **Activate Undo**: Extend your **Index, Middle, and Ring fingers**.
    -   `[0, 1, 1, 1, 0]`

#### 5. Erase All
Clears all drawings from the current slide.
-   **Activate Erase All**: Extend your **Index and Pinkie fingers** ("Rock On" sign).
    -   `[0, 1, 0, 0, 1]`
