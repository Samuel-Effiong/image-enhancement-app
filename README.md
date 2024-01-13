# image-enhancement-app
A desktop application built using PyQt5 to enhance the quality of a image using deep learning models
Certainly! Below is a comprehensive README for your project:

---

# Thera - Image Processing Application

## Overview

Thera is an image processing application developed in Python using the PyQt6 library. This desktop application provides users with tools to view, resize, and manipulate images. Thera incorporates advanced image enlargement techniques, utilizing the LapSRN deep learning model for superior image upscaling.

## Features

### 1. Image Viewing and Navigation

Thera allows users to view images in a user-friendly interface. Key features include:

- **Opening Images:** Users can open images of various formats, such as JPEG, PNG, GIF, SVG, and more.

- **Image Navigation:** Navigate through a folder of images with forward and backward options.

- **Renaming:** Rename images directly within the application.

### 2. Image Resizing

Thera offers advanced image resizing capabilities, allowing users to upscale images using different interpolation methods:

- **Bilinear:** Smooth and fast resizing suitable for most images.
  
- **Cubic:** Higher-quality resizing with more computational cost.

- **Lanczos:** Best quality resizing with increased computational complexity.

- **Super Resolution (Experimental):** Utilizes the LapSRN deep learning model for enhanced image upscaling. Note: This feature is experimental and computationally intensive.

### 3. Enlargement Dialog

The enlargement dialog allows users to customize the resizing process:

- **Method Selection:** Choose the interpolation method for resizing.

- **Scaling Factor:** Select from predefined scaling factors (X2, X4, X8) to adjust the image size.

- **Image Size Preview:** Preview the initial and final image sizes before processing.

- **Save To:** Specify the location to save the resized image.

### 4. About Dialog

The about dialog provides information about the developer and the application:

- **Developer Details:** Name, email, and contact information.

- **Profile Image:** A visual representation of the developer.

- **Introduction:** A brief introduction about the developer and the motivation behind building the application.

## Getting Started

### Prerequisites

- Python 3.x
- PyQt6
- OpenCV (cv2)
- Numpy
- [LapSRN Models](#) (Download and place them in the `models` directory)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your_username/thera.git
cd thera
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python controller.py
```

## Known Issues

- **Super Resolution Warning:** The Super Resolution feature is experimental and may be resource-intensive. It is advisable to use it cautiously.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize the content based on your specific project details and requirements. If you have any specific sections you would like to add or modify, please let me know!
