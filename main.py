import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from typing import List
import uuid
from pathlib import Path

app = FastAPI()

# Configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    file_urls = []
    for file in files:
        try:
            # Generate unique filename
            file_ext = Path(file.filename).suffix
            new_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, new_filename)
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            file_urls.append(f"/files/{new_filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading {file.filename}: {str(e)}")
    
    return {"message": "Files uploaded successfully", "file_urls": file_urls}

@app.get("/files/")
async def list_files():
    files = []
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            files.append({
                "name": filename,
                "url": f"/files/{filename}",
                "size": os.path.getsize(file_path)
            })
    return {"files": files}

@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>File Upload</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <style>
            .dropzone {
                border: 2px dashed #ccc;
                border-radius: 6px;
                padding: 20px;
                text-align: center;
                transition: all 0.3s;
            }
            .dropzone.active {
                border-color: #4CAF50;
                background-color: #f8f8f8;
            }
            .file-item {
                transition: all 0.2s;
            }
            .file-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            @media (max-width: 640px) {
                .file-grid {
                    grid-template-columns: repeat(1, minmax(0, 1fr));
                }
            }
        </style>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold text-center mb-8">Drag & Drop File Upload</h1>
            
            <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8">
                <div id="dropzone" class="dropzone">
                    <div class="text-center">
                        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                        <h3 class="mt-2 text-lg font-medium text-gray-900">Drag and drop files here</h3>
                        <p class="mt-1 text-sm text-gray-500">or click to select files</p>
                    </div>
                    <input type="file" id="fileInput" class="hidden" multiple>
                </div>
                <div class="mt-4 flex justify-between items-center">
                    <button id="uploadBtn" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50" disabled>Upload Files</button>
                    <div id="fileCount" class="text-sm text-gray-500">0 files selected</div>
                </div>
                <div id="progressContainer" class="mt-4 hidden">
                    <div class="w-full bg-gray-200 rounded-full h-2.5">
                        <div id="progressBar" class="bg-blue-600 h-2.5 rounded-full" style="width: 0%"></div>
                    </div>
                    <div id="progressText" class="text-sm text-gray-600 mt-1">Uploading: 0%</div>
                </div>
            </div>
            
            <h2 class="text-2xl font-semibold mb-4">Uploaded Files</h2>
            <div id="fileGallery" class="file-grid grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <!-- Files will be loaded here -->
            </div>
        </div>

        <script>
            const dropzone = document.getElementById('dropzone');
            const fileInput = document.getElementById('fileInput');
            const uploadBtn = document.getElementById('uploadBtn');
            const fileCount = document.getElementById('fileCount');
            const progressContainer = document.getElementById('progressContainer');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            const fileGallery = document.getElementById('fileGallery');
            
            let files = [];
            
            // Load files on page load
            window.addEventListener('DOMContentLoaded', async () => {
                await loadFiles();
            });
            
            // Drag and drop events
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, preventDefaults, false);
            });
            
            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, highlight, false);
            });
            
            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, unhighlight, false);
            });
            
            function highlight() {
                dropzone.classList.add('active');
            }
            
            function unhighlight() {
                dropzone.classList.remove('active');
            }
            
            dropzone.addEventListener('drop', handleDrop, false);
            dropzone.addEventListener('click', () => fileInput.click());
            
            fileInput.addEventListener('change', handleFiles);
            
            function handleDrop(e) {
                const dt = e.dataTransfer;
                const newFiles = dt.files;
                handleFiles({ target: { files: newFiles } });
            }
            
            function handleFiles(e) {
                files = Array.from(e.target.files);
                updateFileCount();
                fileInput.value = '';
            }
            
            function updateFileCount() {
                fileCount.textContent = `${files.length} file${files.length !== 1 ? 's' : ''} selected`;
                uploadBtn.disabled = files.length === 0;
            }
            
            uploadBtn.addEventListener('click', uploadFiles);
            
            async function uploadFiles() {
                if (files.length === 0) return;
                
                const formData = new FormData();
                files.forEach(file => formData.append('files', file));
                
                progressContainer.classList.remove('hidden');
                progressBar.style.width = '0%';
                progressText.textContent = 'Uploading: 0%';
                
                try {
                    const xhr = new XMLHttpRequest();
                    xhr.open('POST', '/upload/', true);
                    
                    xhr.upload.onprogress = (e) => {
                        if (e.lengthComputable) {
                            const percent = Math.round((e.loaded / e.total) * 100);
                            progressBar.style.width = `${percent}%`;
                            progressText.textContent = `Uploading: ${percent}%`;
                        }
                    };
                    
                    xhr.onload = async () => {
                        if (xhr.status === 200) {
                            progressText.textContent = 'Upload complete!';
                            setTimeout(() => {
                                progressContainer.classList.add('hidden');
                            }, 2000);
                            files = [];
                            updateFileCount();
                            await loadFiles();
                        } else {
                            progressText.textContent = 'Upload failed. Please try again.';
                        }
                    };
                    
                    xhr.send(formData);
                } catch (error) {
                    console.error('Upload error:', error);
                    progressText.textContent = 'Upload failed. Please try again.';
                }
            }
            
            async function loadFiles() {
                try {
                    const response = await fetch('/files/');
                    const data = await response.json();
                    
                    fileGallery.innerHTML = '';
                    
                    if (data.files.length === 0) {
                        fileGallery.innerHTML = '<p class="text-gray-500 col-span-full text-center py-8">No files uploaded yet.</p>';
                        return;
                    }
                    
                    data.files.forEach(file => {
                        const fileExt = file.name.split('.').pop().toLowerCase();
                        let icon = '📄';
                        
                        if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(fileExt)) {
                            icon = '🖼️';
                        } else if (['pdf'].includes(fileExt)) {
                            icon = '📕';
                        } else if (['doc', 'docx'].includes(fileExt)) {
                            icon = '📝';
                        } else if (['xls', 'xlsx'].includes(fileExt)) {
                            icon = '📊';
                        } else if (['zip', 'rar', '7z'].includes(fileExt)) {
                            icon = '🗜️';
                        }
                        
                        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                        
                        const fileElement = document.createElement('div');
                        fileElement.className = 'file-item bg-white rounded-lg shadow-sm p-4 flex flex-col';
                        fileElement.innerHTML = `
                            <div class="text-4xl text-center mb-2">${icon}</div>
                            <div class="text-sm font-medium text-gray-900 truncate">${file.name}</div>
                            <div class="text-xs text-gray-500 mt-1">${sizeMB} MB</div>
                            <a href="${file.url}" class="mt-2 text-sm text-blue-600 hover:text-blue-800" download>Download</a>
                        `;
                        fileGallery.appendChild(fileElement);
                    });
                } catch (error) {
                    console.error('Error loading files:', error);
                    fileGallery.innerHTML = '<p class="text-red-500 col-span-full text-center py-8">Error loading files. Please refresh the page.</p>';
                }
            }
        </script>
    </body>
    </html>
    """