import tkinter as tk
from tkinter import filedialog
import firebase_admin
from firebase_admin import credentials, storage
from zipfile import ZipFile
import io
import os
import shutil
from google.cloud import storage as gcs

def initialize_firebase():
    try:
        app = firebase_admin.get_app()
    except ValueError:
        cred_path = cred_path_entry.get()
        bucket_name = bucket_name_entry.get()

        if os.path.isfile('serviceAccountKey.json'):
            with open('last_cred_path.txt', 'w') as f:
                f.write(os.path.dirname(os.path.abspath(__file__))+'\serviceAccountKey.json')
        else:
            print("Fixa en serviceAccountKey.json fil!")

        with open('last_bucket_path.txt', 'w') as f:
            f.write(bucket_name_entry.get())

        with open('last_folder_path.txt', 'w') as f:
            f.write(folder_path_entry.get())

        if not cred_path or not bucket_name:
            return

        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'storageBucket': bucket_name
        })

def upload_file():
    initialize_firebase()
    bucket = storage.bucket()

    folder_path = folder_path_entry.get()
    if not folder_path:
        return

    if os.path.isfile('metaData.txt'):
        user = os.read(os.path.dirname(os.path.abspath(__file__))+'\metaData.txt')
            
    else:
        print("Fixa en metaData.txt fil!")

    # Skapa metadata
    metadata = {"user": "a"}

    if not fileOrNotVar.get():
        zip_file_name = os.path.basename(folder_path) + '.zip'

        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    zip_file.write(file_path, os.path.relpath(file_path, folder_path))

        # Upload the zip file to Firebase Storage
        blob = bucket.blob(zip_file_name)
        blob.metadata = metadata
        blob.upload_from_string(zip_buffer.getvalue(), content_type='application/zip')
    else:
        file_name = os.path.basename(folder_path)

        # Upload the file to Firebase Storage
        blob = bucket.blob(file_name)
        blob.metadata = metadata
        blob.upload_from_filename(file_name)

    with open('last_folder_path.txt', 'w') as f:
        f.write(folder_path)

def download_file():
    initialize_firebase()
    bucket = storage.bucket()

    folder_path = folder_path_entry.get()
    if not folder_path:
        return

    if not fileOrNotVar.get():
        zip_file_name = os.path.basename(folder_path) + '.zip'

        # Download the zip file from Firebase Storage
        blob = bucket.blob(zip_file_name)
        zip_buffer = io.BytesIO()
        blob.download_to_file(zip_buffer)

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Unzip the file to the specified folder
        with ZipFile(zip_buffer, 'r') as zip_file:
            zip_file.extractall(folder_path)
    else:
        zip_file_name = os.path.basename(folder_path)

        # Download the zip file from Firebase Storage
        blob = bucket.blob(zip_file_name)
        content = blob.download_as_bytes()

        # Skapa en fil från bytes
        file = io.BytesIO(content)

        # Skapa en ny fil med samma namn och lägg till rätt filändelse
        filename = folder_path.split("/")[-1]
        new_file = open(filename, "wb")

        # Skriv innehållet i den ursprungliga filen till den nya filen
        new_file.write(file.read())

        # Stäng båda filerna
        file.close()
        new_file.close()

    with open('last_folder_path.txt', 'w') as f:
        f.write(folder_path)

def browse_cred():
    cred_path = filedialog.askopenfilename()
    cred_path_entry.delete(0, tk.END)
    cred_path_entry.insert(0, cred_path)

def browse_folder():
    if fileOrNotVar.get():
        folder_path = filedialog.askopenfilename()
    else:
        folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_path)

root = tk.Tk()
root.geometry('250x250')
root.title("Fil Uppladnings Projekt")

tk.Label(root, text="Service account key: (json)").pack()
fileOrNotVar = tk.IntVar()

cred_frame = tk.Frame(root)
cred_frame.pack(fill=tk.X)

cred_path_entry = tk.Entry(cred_frame)
cred_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

browse_cred_button = tk.Button(cred_frame, text="Browse", command=browse_cred)
browse_cred_button.pack(side=tk.RIGHT)

tk.Label(root, text="Storage bucket: (web url)").pack()

bucket_name_entry = tk.Entry(root)
bucket_name_entry.pack(fill=tk.X)

tk.Label(root, text="Folder path: (folder/file)").pack()

folder_frame = tk.Frame(root)
folder_frame.pack(fill=tk.X)

folder_path_entry = tk.Entry(folder_frame)
folder_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

browse_folder_button = tk.Button(folder_frame, text="Browse", command=browse_folder)
browse_folder_button.pack(side=tk.RIGHT)

checkbutton = tk.Checkbutton(root, text="Tryck i ifall det är en fil!", variable=fileOrNotVar, onvalue=True, offvalue=False)
checkbutton.pack()

upload_button = tk.Button(root, text="Upload", command=upload_file)
upload_button.pack(fill=tk.X)

download_button = tk.Button(root, text="Download", command=download_file)
download_button.pack(fill=tk.X)



if os.path.exists('last_cred_path.txt'):
    with open('last_cred_path.txt', 'r') as f:
        last_cred_path = f.read().strip()
        cred_path_entry.insert(0, last_cred_path)

if os.path.exists('last_bucket_path.txt'):
    with open('last_bucket_path.txt', 'r') as f:
        last_bucket_path = f.read().strip()
        bucket_name_entry.insert(0, last_bucket_path)

if os.path.exists('last_folder_path.txt'):
    with open('last_folder_path.txt', 'r') as f:
        last_file_path = f.read().strip()
        folder_path_entry.insert(0, last_file_path)

root.mainloop()