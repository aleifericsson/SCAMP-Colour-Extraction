import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np

# ===== SETTINGS =====
frame_rate = 10
delay = int(1000 / frame_rate)
index = 0
playing = True

# ==========  FUNCTIONS  ==========
def update_delay(value):
    global delay
    fps = max(1, int(float(value)))   # prevent division by zero
    delay = int(1000 / fps)

def update_frame():
    global index
    if playing:
        label.config(image=frames[index])
        label.image = frames[index]
        index = (index + 1) % len(frames)
        frame_label.config(text=f"{index+1} / {len(frames)}")

    root.after(delay, update_frame)

def toggle_play():
    global playing
    playing = not playing
    play_button.config(text="⏸" if playing else "▶")

def step_left():
    global index
    index = (index - 1) % len(frames)
    label.config(image=frames[index])
    label.image = frames[index]
    frame_label.config(text=f"{index+1} / {len(frames)}")

def step_right():
    global index
    index = (index + 1) % len(frames)
    label.config(image=frames[index])
    label.image = frames[index]
    frame_label.config(text=f"{index+1} / {len(frames)}")

def apply_matrix():
    global frames
    matrix = []
    for r in range(3):
        row = []
        for c in range(3):
            value = float(matrix_entries[r][c].get())
            row.append(value)
        matrix.append(row)

    matrix = np.array(matrix, dtype=np.float32)
    lightness = float(lightness_entry.get())
    saturation = float(saturation_entry.get())

    new_frames = []

    for file in frame_files:
        path = os.path.join(save_dir, file)
        img = Image.open(path).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        # --- matrix transform ---
        transformed = arr @ matrix.T

        # --- lightness multiplier ---
        transformed *= lightness

        # --- saturation adjustment ---
        gray = transformed.mean(axis=2, keepdims=True)
        transformed = gray + (transformed - gray) * saturation
        transformed = np.clip(transformed, 0, 255).astype(np.uint8)
        new_img = Image.fromarray(transformed)
        new_frames.append(ImageTk.PhotoImage(new_img))

    frames = new_frames
    print("Matrix + lightness + saturation applied to all frames.")

def load_matrix():
    path = filedialog.askopenfilename(
        title="Select Matrix File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )

    if not path:
        return

    with open(path, "r") as f:
        values = f.read().split()

    if len(values) != 9:
        print("Matrix file must contain exactly 9 numbers.")
        return

    k = 0
    for r in range(3):
        for c in range(3):
            matrix_entries[r][c].delete(0, tk.END)
            matrix_entries[r][c].insert(0, values[k])
            k += 1

def reset_matrix():
    global frames

    # reset matrix values
    for r in range(3):
        for c in range(3):
            matrix_entries[r][c].delete(0, tk.END)
            if r == c:
                matrix_entries[r][c].insert(0, "1")
            else:
                matrix_entries[r][c].insert(0, "0")

    # reset lightness / saturation
    lightness_entry.delete(0, tk.END)
    lightness_entry.insert(0, "1")

    saturation_entry.delete(0, tk.END)
    saturation_entry.insert(0, "1")

    # reload original frames
    new_frames = []

    for file in frame_files:
        path = os.path.join(save_dir, file)
        img = Image.open(path)
        new_frames.append(ImageTk.PhotoImage(img))

    frames = new_frames

    print("Matrix reset and original frames restored.")

def export_mp4():
    fps = frame_rate.get()
    if fps <= 0:
        return

    # read matrix from UI
    matrix = []
    for r in range(3):
        row = []
        for c in range(3):
            row.append(float(matrix_entries[r][c].get()))
        matrix.append(row)

    matrix = np.array(matrix, dtype=np.float32)

    lightness = float(lightness_entry.get())
    saturation = float(saturation_entry.get())

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_name = folder_name
    output_path = os.path.join(script_dir, f"{base_name}.mp4")

    counter = 1
    while os.path.exists(output_path):
        output_path = os.path.join(script_dir, f"{base_name} ({counter}).mp4")
        counter += 1

    first_path = os.path.join(save_dir, frame_files[0])
    first_frame = cv2.imread(first_path)
    height, width, _ = first_frame.shape

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for file in frame_files:
        frame_path = os.path.join(save_dir, file)
        frame = cv2.imread(frame_path)          # BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        arr = frame.astype(np.float32)

        # matrix transform
        transformed = arr @ matrix.T
        # lightness
        transformed *= lightness
        # saturation
        gray = transformed.mean(axis=2, keepdims=True)
        transformed = gray + (transformed - gray) * saturation
        transformed = np.clip(transformed, 0, 255).astype(np.uint8)
        transformed = cv2.cvtColor(transformed, cv2.COLOR_RGB2BGR)

        writer.write(transformed)

    writer.release()
    print(f"Exported to {output_path}")


# ======== MAIN LOOP =====
# Create root FIRST and only once
root = tk.Tk()
root.title("PNG Video Player")

# Ask for directory
save_dir = filedialog.askdirectory(title="Select Folder Containing Frames")
folder_name = os.path.basename(os.path.normpath(save_dir))

if not save_dir:
    raise SystemExit("No folder selected.")

# Get sorted frame list
frame_files = sorted(
    [f for f in os.listdir(save_dir) if f.endswith(".png")],
    key=lambda x: int(os.path.splitext(x)[0])
)

if not frame_files:
    raise SystemExit("No PNG files found.")

# Preload frames into memory
frames = []
for file in frame_files:
    path = os.path.join(save_dir, file)
    img = Image.open(path)
    frames.append(ImageTk.PhotoImage(img))

# Display label (DON"T ASK WHY IT"S A LABEL)
label = tk.Label(root)
label.pack()

#### PAUSE/PLAY/SEEK BUTTONS
controls = tk.Frame(root)
controls.pack()

left_button = tk.Button(controls, text="⏪︎", command=step_left)
left_button.pack(side="left", padx=5)

play_button = tk.Button(controls, text="⏸", command=toggle_play)
play_button.pack(side="left", padx=5)

right_button = tk.Button(controls, text="⏩︎", command=step_right)
right_button.pack(side="left", padx=5)

frame_label = tk.Label(controls, text="0 / 0")
frame_label.pack(side="left", padx=10)

### frame rate slider
frame_rate = tk.IntVar(value=10)
delay = int(1000 / frame_rate.get())

slider_frame = tk.Frame(root)
slider_frame.pack()

fps_label = tk.Label(slider_frame, text="FPS:")
fps_label.pack(side="left", padx=(0, 5))

slider = tk.Scale(slider_frame, from_=1, to=30, orient="horizontal", variable=frame_rate, command=update_delay)
slider.pack(side="left")

export_button = tk.Button(root, text="Export to MP4", command=export_mp4)
export_button.pack(pady=10)

# ===== MATRIX INPUT =====
matrix_frame = tk.Frame(root)
matrix_frame.pack(pady=10)

matrix_labels = [
    ["rr","rg","rb"],
    ["gr","gg","gb"],
    ["br","bg","bb"]
]

matrix_entries = []

for r in range(3):
    row_entries = []
    for c in range(3):
        cell = tk.Frame(matrix_frame)
        cell.grid(row=r, column=c, padx=5, pady=5)
        label2 = tk.Label(cell, text=matrix_labels[r][c])
        label2.pack()
        entry = tk.Entry(cell, width=5, justify="center")

        if r == c:
            entry.insert(0, "1")
        else:
            entry.insert(0, "0")
        entry.pack()
        entry.focus_force()
        row_entries.append(entry)
    matrix_entries.append(row_entries)

ls_frame = tk.Frame(root)
ls_frame.pack(pady=5)

tk.Label(ls_frame, text="Lightness").grid(row=0, column=0, padx=5)
lightness_entry = tk.Entry(ls_frame, width=6, justify="center")
lightness_entry.insert(0, "1")
lightness_entry.grid(row=0, column=1, padx=5)

tk.Label(ls_frame, text="Saturation").grid(row=0, column=2, padx=5)
saturation_entry = tk.Entry(ls_frame, width=6, justify="center")
saturation_entry.insert(0, "1")
saturation_entry.grid(row=0, column=3, padx=5)

button_row = tk.Frame(root)
button_row.pack(pady=10)

load_button = tk.Button(button_row, text="Load Matrix", command=load_matrix)
load_button.pack(side="left", padx=5)

apply_button = tk.Button(button_row, text="Apply Matrix", command=apply_matrix)
apply_button.pack(side="left", padx=5)

reset_button = tk.Button(button_row, text="Reset Matrix", command=reset_matrix)
reset_button.pack(side="left", padx=5)

# Start playback AFTER window is ready
root.after(0, update_frame)

root.mainloop()