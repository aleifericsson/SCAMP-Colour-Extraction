import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import csv
import cv2
import numpy as np

colorchecker_colors = [
    "#735244","#C29682","#627A9D","#576C43","#8580B1","#67BDAA",
    "#D67E2C","#505BA6","#C15A63","#5E3C6C","#9DBC40","#E0A32E",
    "#383D96","#469449","#AF363C","#E7C71F","#BB5695","#0885A1",
    "#F3F3F2","#C8C8C8","#A0A0A0","#7A7A79","#555555","#343434"
]


class ImageClickApp:
    def __init__(self, root):
        ##### DRAWING THE ROOT
        self.root = root
        self.root.title("Image Coordinate Viewer")
        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.pack(side="left", padx=10)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.pack(side="right", padx=10)

        self.canvas = tk.Canvas(self.left_frame, bg="gray")
        self.canvas.pack()
        
        self.selected_frame = tk.Frame(self.left_frame)
        self.selected_frame.pack(pady=2)
        self.selected_label = tk.Label(self.selected_frame, text="Selected: 1", font=("Arial", 11))
        self.selected_label.pack(side="left")
        self.selected_color_box = tk.Canvas(self.selected_frame, width=18, height=18)
        self.selected_color_box.pack(side="left", padx=5)
        self.selected_color_box.create_rectangle(
            0, 0, 18, 18,
            fill=colorchecker_colors[0],
            outline="black"
        )

        self.label = tk.Label(self.left_frame, text="x,y:", justify="left", font=("Arial", 7))
        self.label.pack(pady=5)
        self.open_btn = tk.Button(self.left_frame, text="Open Image", command=self.open_image)
        self.open_btn.pack(pady=5)
        self.export_btn = tk.Button(self.left_frame, text="Export CSV Format 1", command=self.export_csv)
        self.export_btn.pack(pady=5)
        self.export2_btn = tk.Button(self.left_frame, text="Export CSV Format 2", command=self.export_csv_format2)
        self.export2_btn.pack(pady=5)

        self.canvas.bind("<Button-1>", self.get_coordinates)

        ####### VARIABLES
        self.selected_color = 1
        self.image = None
        self.tk_image = None
        self.color_clicks = {i: [] for i in range(1, 25)}
        self.color_polygons = {i: None for i in range(1, 25)}

        ###### INIT FUNCTIONS
        self.build_color_grid()

    def build_color_grid(self):
        cols = 6

        for i, color in enumerate(colorchecker_colors):
            r = i // cols
            c = i % cols

            cell = tk.Frame(self.right_frame, relief="solid", borderwidth=1, padx=5, pady=5)
            cell.grid(row=r, column=c, padx=4, pady=4)

            id_label = tk.Label(cell, text=str(i + 1))
            id_label.pack()

            color_box = tk.Canvas(cell, width=35, height=25)
            color_box.pack(pady=2)
            color_box.create_rectangle(0, 0, 35, 25, fill=color, outline="black")

            btn = tk.Button(cell, text="Select", width=6, command=lambda idx=i+1: self.set_selected_color(idx))
            btn.pack()

    def set_selected_color(self, idx):
        self.selected_color = idx
        self.selected_label.config(text=f"Selected: {idx}")

        self.selected_color_box.delete("all")
        self.selected_color_box.create_rectangle(
            0, 0, 18, 18,
            fill=colorchecker_colors[idx-1],
            outline="black"
        )

        for cid, poly in self.color_polygons.items():
            if poly:
                color = "#93ff7d" if cid == self.selected_color else "white"
                self.canvas.itemconfig(poly, outline=color)

        self.update_label()

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not path:
            return

        self.image = Image.open(path)
        self.tk_image = ImageTk.PhotoImage(self.image)

        self.canvas.config(width=self.image.width, height=self.image.height)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.color_clicks = {i: [] for i in range(1, 25)}
        self.color_polygons = {i: None for i in range(1, 25)}
        self.update_label()

    def get_coordinates(self, event):
        if self.image is None:
            return

        x, y = event.x, event.y

        if 0 <= x < self.image.width and 0 <= y < self.image.height:
            clicks = self.color_clicks[self.selected_color]
            clicks.append((x, y))
            if len(clicks) > 4:
                clicks.pop(0)

            self.update_label()
            self.draw_polygon(self.selected_color)

    def draw_polygon(self, color_id):
        clicks = self.color_clicks[color_id]

        if self.color_polygons[color_id]:
            self.canvas.delete(self.color_polygons[color_id])
            self.color_polygons[color_id] = None

        if len(clicks) == 4:

            coords = []
            for x, y in clicks:
                coords.extend([x, y])

            outline_color = "#93ff7d" if color_id == self.selected_color else "white"

            poly = self.canvas.create_polygon(
                coords,
                outline=outline_color,
                fill="white",
                stipple="gray25",
                width=1
            )
            self.color_polygons[color_id] = poly
            
    def update_label(self):
        clicks = self.color_clicks[self.selected_color]

        if not clicks:
            text = "x,y: "
        else:
            entries = [f"{i}: ({x}, {y})" for i, (x, y) in enumerate(clicks, 1)]
            text = "x,y: " + ", ".join(entries)

        self.label.config(text=text)
    
    def export_csv(self):
        if self.image is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not path:
            return

        # convert PIL image → OpenCV BGR
        img = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
        rows = []

        for color_id in range(1, 25):
            target_hex = colorchecker_colors[color_id - 1]
            clicks = self.color_clicks[color_id]
            pixel_hex_values = []

            if len(clicks) == 4:

                pts = np.array(clicks, dtype=np.int32)
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [pts], 255)
                ys, xs = np.where(mask == 255)

                for x, y in zip(xs, ys):
                    b, g, r = img[y, x]
                    hex_val = "#{:02x}{:02x}{:02x}".format(r, g, b)
                    pixel_hex_values.append(hex_val)

            row = [color_id, target_hex] + pixel_hex_values
            rows.append(row)

        max_len = max(len(r) for r in rows)

        for r in rows:
            r.extend([""] * (max_len - len(r)))

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    
    def export_csv_format2(self):
        if self.image is None:
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )

        if not path:
            return

        img = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "target_hex", "pixel_hex"])

            for color_id in range(1, 25):

                target_hex = colorchecker_colors[color_id - 1]
                clicks = self.color_clicks[color_id]

                if len(clicks) != 4:
                    continue

                pts = np.array(clicks, dtype=np.int32)
                mask = np.zeros(img.shape[:2], dtype=np.uint8)
                cv2.fillPoly(mask, [pts], 255)
                ys, xs = np.where(mask == 255)

                if len(xs) == 0:
                    continue

                for x, y in zip(xs, ys):
                    b, g, r = img[y, x]
                    hex_val = "#{:02x}{:02x}{:02x}".format(r, g, b)
                    writer.writerow([color_id, target_hex, hex_val])


root = tk.Tk()
app = ImageClickApp(root)
root.mainloop()