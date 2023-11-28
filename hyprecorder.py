import subprocess
import signal
import os
import time
import datetime
import tkinter as tk
from tkinter import messagebox

class ScreenRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.recording_process = None
        self.start_time = None
        self.elapsed_var = tk.StringVar()
        self.elapsed_var.set("00:00:00")

        self.create_menu()
        self.create_elapsed_label()
        self.create_open_output_button()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        recording_menu = tk.Menu(menu_bar, tearoff=0)
        recording_menu.add_command(label="Start Recording", command=self.start_recording)
        recording_menu.add_command(label="Stop Recording", command=self.stop_recording)
        menu_bar.add_cascade(label="hypRecorder", menu=recording_menu)

    def create_elapsed_label(self):
        elapsed_label = tk.Label(self.root, textvariable=self.elapsed_var, font=("Arial", 18))
        elapsed_label.pack(pady=20)

    def create_open_output_button(self):
        open_output_button = tk.Button(self.root, text="Output Directory", command=self.open_output_directory)
        open_output_button.pack(pady=10)

    def open_output_directory(self):
        output_dir = "output"
        self.create_directory(output_dir)

        if self.is_wayland_display_server():
            subprocess.Popen(["xdg-open", output_dir])
        else:
            subprocess.Popen(["xdg-open", output_dir], env=dict(os.environ, DISPLAY=":0"))

    def is_wayland_display_server(self):
        display_server = os.environ.get("XDG_SESSION_TYPE", "")
        return display_server.lower() == "wayland"

    def start_recording(self):
        if self.recording_process is not None:
            messagebox.showwarning("Recording", "Recording is already in progress.")
            return

        output_dir = "output"
        self.create_directory(output_dir)

        # Generate a unique filename based on the date and time
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = os.path.join(output_dir, f"output_{filename}.mp4")

        self.recording_process = subprocess.Popen([
            "wf-recorder", "--audio", "pulse", "--muxer", "mp4",
            "--muxer-raw-fps", "60", "--file", output_path
        ])

        self.start_time = time.time()
        self.update_elapsed_time()

    def stop_recording(self):
        if self.recording_process is None:
            messagebox.showwarning("Recording", "Recording is not in progress.")
            return

        self.recording_process.send_signal(signal.SIGINT)
        self.recording_process.wait()

        self.recording_process = None
        self.start_time = None

        messagebox.showinfo("Recording", "Recording stopped.")

    def create_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def update_elapsed_time(self):
        if self.start_time is not None:
            elapsed = int(time.time() - self.start_time)
            elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            self.elapsed_var.set(elapsed_str)

        self.root.after(1000, self.update_elapsed_time)

def main():
    root = tk.Tk()
    root.title("hypRecorder")

    app = ScreenRecorderGUI(root)

    root.mainloop()

if __name__ == '__main__':
    main()
