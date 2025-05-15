FastAPI Drag-and-Drop File Uploader

A modern file upload system with drag-and-drop interface, file gallery, and responsive design.
![Screenshot (195)](https://github.com/user-attachments/assets/aff68568-fb7d-47d8-b1de-9db61f23321d)

## Features

- Drag-and-drop file upload interface
- Responsive design that works on mobile and desktop
- File gallery showing all uploaded files
- Progress indicators during upload
- Unique filenames to prevent conflicts
- File type icons and size information
- Download functionality for all files

## Requirements

- Python 3.7+
- FastAPI
- Uvicorn

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fastapi-file-uploader.git
cd fastapi-file-uploader
2. Install dependencies:
pip install fastapi uvicorn python-multipart
3.Run the application:
uvicorn main:app --reload
4.Open your browser at:
http://localhost:8000
The application will automatically create an uploads directory where all files are stored.
