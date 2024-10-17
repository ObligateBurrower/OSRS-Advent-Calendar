import datetime
import json
import os
from PIL import Image, ImageTk
import tkinter as tk


class AdventCalendar(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Advent Calendar")
        self.geometry("635x801")  # Set this to half of the original image size for simplicity

        # Load the main calendar image
        image_path = os.path.join(os.getcwd(), "Christmas_Advent_Calendar.png")
        self.calendar_img = Image.open(image_path)
        original_width, original_height = self.calendar_img.size
        new_width = original_width // 3
        new_height = original_height // 3
        self.calendar_img = self.calendar_img.resize((new_width, new_height), Image.LANCZOS)
        self.calendar_photo = ImageTk.PhotoImage(self.calendar_img)

        self.canvas = tk.Canvas(self, width=new_width, height=new_height)
        self.canvas.pack()
        self.calendar_on_canvas = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.calendar_photo)

        # Load and resize Chathead images
        self.chatheads = self.load_chathead_images(new_width, new_height)

        # Load clickable areas from JSON file
        self.areas = self.load_areas("original_area.json", new_width, original_width, new_height, original_height)

        # State handling
        self.state_file = "advent_calendar_state.json"
        self.clicked_days = self.load_state()

        # Overlay clicked chatheads
        for day in self.clicked_days:
            self.overlay_chathead(day)

        # Bind the mouse click event
        self.canvas.bind("<Button-1>", self.on_click)

    def load_chathead_images(self, width, height):
        chatheads = {}
        for i in range(1, 26):
            path = os.path.join(os.getcwd(), "chatheads", f"Chathead_{i}.png")
            img = Image.open(path)
            img = img.resize((width, height), Image.LANCZOS)
            chatheads[i] = ImageTk.PhotoImage(img)
        return chatheads

    def load_areas(self, json_file, new_width, original_width, new_height, original_height):
        # Load the areas from a JSON file and adjust them based on the scaling factors
        with open(json_file, 'r') as file:
            original_areas = json.load(file)

        scale_x = new_width / original_width
        scale_y = new_height / original_height
        return {int(day): [int(coord[0] * scale_x), int(coord[1] * scale_y), int(coord[2] * scale_x),
                           int(coord[3] * scale_y)]
                for day, coord in original_areas.items()}

    def load_state(self):
        try:
            with open(self.state_file, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_state(self):
        with open(self.state_file, 'w') as file:
            json.dump(self.clicked_days, file)

    def on_click(self, event):
        today = datetime.date.today().day  # Get the current day of the month
        for day, coords in self.areas.items():
            if coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                if day > today:
                    self.show_no_peeking_message()  # Show warning if the day is in the future
                elif day not in self.clicked_days:
                    self.clicked_days.append(day)
                    self.save_state()
                    self.overlay_chathead(day)
                    self.show_image_for_day(day)
                break

    def show_no_peeking_message(self):
        # Create a popup window with a warning message
        popup = tk.Toplevel(self)
        popup.title("No Peeking!")

        # Load and display an image
        image_path = "image.png"  # Replace with the path to your image
        img = Image.open(image_path)
        img = img.resize((124, 124), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(popup, image=photo)
        img_label.image = photo  # Keep a reference
        img_label.pack(pady=10)

        # Display the message
        message = tk.Label(popup, text="Santa says no peeking early!", font=("Helvetica", 14))
        message.pack(pady=20)

        # Add a button to close the popup
        button = tk.Button(popup, text="Okay", command=popup.destroy)
        button.pack(pady=10)

    def overlay_chathead(self, day):
        chathead_img = self.chatheads[day]
        self.canvas.create_image(0, 0, anchor=tk.NW, image=chathead_img)
        self.canvas.chathead_photo = chathead_img  # Keep a reference to prevent garbage collection

    def show_image_for_day(self, day):
        image_path = os.path.join(os.getcwd(), "daily_images", f"Day {day} Event Card.png")
        img = Image.open(image_path)
        img = img.resize((810, 540), Image.LANCZOS)  # Adjusted for new window size
        img = ImageTk.PhotoImage(img)

        top = tk.Toplevel(self)
        top.title(f"Day {day}")
        top.geometry("820x550")  # Adjusted for new window size
        panel = tk.Label(top, image=img)
        panel.photo = img
        panel.pack()


if __name__ == "__main__":
    app = AdventCalendar()
    app.mainloop()
