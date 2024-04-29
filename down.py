import tkinter as tk
from tkinter import messagebox, ttk, filedialog

import pytube
from PIL import Image, ImageTk
import requests
import threading
from io import BytesIO
import os

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Video Downloader")
        self.geometry("1200x800")
        self.center_window()
        self.config(bg="#f0f0f0")  # Light gray background

        # Set background image
        background_image = Image.open("Music.jpg")
        background_photo = ImageTk.PhotoImage(background_image)
        self.background_label = tk.Label(self, image=background_photo)
        self.background_label.image = background_photo
        self.background_label.place(relwidth=1, relheight=1)

        # Frames for quality selection, download buttons, and audio only option
        self.setup_frames()

        # URL input, Paste button, and OK button
        self.setup_url_input()

        # Display video thumbnail and title
        self.setup_video_display()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        window_width = 1200
        window_height = 800

        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        self.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

    def setup_url_input(self):
        input_label = tk.Label(self, text="Enter the YouTube video URL:", bg="#f0f0f0", fg="#333333", font=("Quicksand", 14))
        input_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.video_url_var = tk.StringVar()
        video_url_entry = tk.Entry(self, textvariable=self.video_url_var, font=("Segoe UI", 14), bg="#ffffff")  # White background
        video_url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Paste button
        paste_btn = tk.Button(self, text="Paste", bg="#3498db", fg="#ffffff", font=("Segoe UI", 11, "bold"), command=self.on_paste)  # Blue button
        paste_btn.grid(row=0, column=2, padx=10, pady=10)

        ok_btn = tk.Button(self, text="OK", bg="#2ecc71", fg="#ffffff", font=("Segoe UI", 14, "bold"), command=self.on_ok)  # Green button
        ok_btn.grid(row=0, column=3, padx=10, pady=10)

    def setup_frames(self):
        self.top_frame = tk.Frame(self, bg="#f0f0f0")  # Light gray background
        self.top_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.bottom_frame = tk.Frame(self, bg="#f0f0f0")  # Light gray background
        self.bottom_frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.bottom_frame, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)
        self.progress_bar.grid(row=0, column=1, padx=10, pady=10)

        # Quality selection dropdown
        self.selected_quality = tk.StringVar()
        self.selected_quality.set("Select Quality")
        self.quality_menu = ttk.Combobox(self.top_frame, textvariable=self.selected_quality, font=("Quicksand", 12), state="readonly")
        self.quality_menu.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Download buttons
        self.download_btn = tk.Button(self.bottom_frame, text="Download Video", bg="#3498db", fg="#322C2B", font=("Tilt Neon", 12, "bold"), relief=tk.RAISED, state=tk.DISABLED, command=self.on_download)
        self.download_btn.grid(row=0, column=0, padx=10, pady=10)

        self.download_audio_btn = tk.Button(self.bottom_frame, text="Download Audio", bg="#75A47F", fg="#322C2B", font=("Quicksand", 12, "bold"), relief=tk.RAISED, state=tk.DISABLED, command=self.on_download_audio)
        self.download_audio_btn.grid(row=0, column=2, padx=10, pady=10)

    def setup_video_display(self):
        self.video_title_var = tk.StringVar()
        video_title_label = tk.Label(self, textvariable=self.video_title_var, bg="#3498db", fg="#ffffff", font=("Quicksand", 16, "bold"))  # Blue background
        video_title_label.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.video_thumbnail_var = tk.StringVar()
        video_thumbnail_label = tk.Label(self, image=None, bg="#f0f0f0")  # Light gray background
        video_thumbnail_label.grid(row=4, column=0, columnspan=4, padx=10, pady=10)
        self.video_thumbnail_label = video_thumbnail_label


    def on_ok(self):
        try:
            url = self.video_url_var.get()
            if url == "":
                raise ValueError("URL cannot be empty.")
            else:
                self.fetch_video_data(url)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_paste(self):
        try:
            self.video_url_var.set(self.clipboard_get())
        except tk.TclError:
            messagebox.showerror("Error", "Nothing to paste")

    def fetch_video_data(self, url):
        try:
            self.yt = pytube.YouTube(url)
            self.populate_quality_options()
            self.update_video_display()
            self.download_btn.config(state=tk.NORMAL)
            self.download_audio_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def populate_quality_options(self):
        self.quality_menu['values'] = [stream.resolution for stream in self.yt.streams.filter(progressive=True, file_extension='mp4')]

    def update_video_display(self):
        self.video_title_var.set(self.yt.title)
        self.update_video_thumbnail(self.yt.thumbnail_url)

    def update_video_thumbnail(self, url):
        try:
            thumbnail_data = requests.get(url).content
            thumbnail_image = Image.open(BytesIO(thumbnail_data))
            thumbnail_photo = ImageTk.PhotoImage(thumbnail_image)
            self.video_thumbnail_label.config(image=thumbnail_photo)
            self.video_thumbnail_label.image = thumbnail_photo
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_download(self):
        if self.selected_quality.get() == "Select Quality":
            messagebox.showerror("Error", "Please select a quality option.")
        else:
            selected_stream = self.yt.streams.get_by_resolution(self.selected_quality.get())
            file_path = filedialog.askdirectory()
            if file_path == "":
                messagebox.showerror("Error", "Download path cannot be empty.")
            else:
                self.download_btn.config(state=tk.DISABLED)
                self.download_audio_btn.config(state=tk.DISABLED)
                self.progress_bar.grid(row=0, column=1, padx=10, pady=5)
                threading.Thread(target=self.download_video, args=(selected_stream, file_path)).start()

    def on_download_audio(self):
        file_path = filedialog.askdirectory()
        if file_path == "":
            messagebox.showerror("Error", "Download path cannot be empty.")
        else:
            self.download_btn.config(state=tk.DISABLED)
            self.download_audio_btn.config(state=tk.DISABLED)
            self.progress_bar.grid(row=0, column=1, padx=10, pady=5)
            threading.Thread(target=self.download_audio, args=(file_path,)).start()

    def download_video(self, selected_stream, file_path):
        try:
            # Start the download and monitor the progress
            downloaded_file_path = selected_stream.download(file_path, filename="temp_video")

            # Reset progress bar
            self.progress_var.set(0)

            # Update progress bar while downloading
            file_size = os.path.getsize(downloaded_file_path)
            bytes_written = 0
            while bytes_written < file_size:
                bytes_written += 1024  # Increment by 1KB
                progress = (bytes_written / file_size) * 100
                self.progress_var.set(progress)

            # Rename the file to the correct name
            os.rename(downloaded_file_path,
                      os.path.join(file_path, selected_stream.default_filename))

            messagebox.showinfo("Success", "Video downloaded successfully.")
            self.download_btn.config(state=tk.NORMAL)
            self.download_audio_btn.config(state=tk.NORMAL)
            self.progress_bar.grid_forget()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def download_audio(self, file_path):
        try:
            audio_stream = self.yt.streams.get_audio_only()
            audio_file_path = os.path.join(file_path, f"{self.yt.title}.mp3")
            audio_stream.download(output_path=file_path, filename=f"{self.yt.title}.mp3")

            messagebox.showinfo("Success", "Audio downloaded successfully.")
            self.download_btn.config(state=tk.NORMAL)
            self.download_audio_btn.config(state=tk.NORMAL)
            self.progress_bar.grid_forget()
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
