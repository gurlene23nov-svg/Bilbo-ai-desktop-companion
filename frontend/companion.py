import json
import subprocess
import tkinter as tk
from pathlib import Path

from PIL import Image, ImageTk


# ============================================================
# PATHS
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

CHAT_FILE = PROJECT_DIR / "frontend" / "chat_window.py"
PYTHON_EXE = PROJECT_DIR / "venv" / "Scripts" / "python.exe"

STATE_FILE = PROJECT_DIR / "data" / "pet_state.json"

ASSET_DIR = PROJECT_DIR / "frontend" / "assets"

MOOD_SHEET = ASSET_DIR / "bilbo_moods.png.png"

HAPPY_IMAGE = ASSET_DIR / "bilbo_happy.png"


# ============================================================
# SETTINGS
# ============================================================

TRANSPARENT = "#ff00ff"

IMAGE_SCALE = 0.75

ALPHA_CUTOFF = 16

POLL_MS = 500

ROAM_MS = 60


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(image):

    image = image.convert("RGBA")

    # Remove almost-transparent pixels.
    alpha = image.getchannel("A").point(
        lambda value: 0 if value < ALPHA_CUTOFF else value
    )

    image.putalpha(alpha)

    # Scale image.
    new_size = (
        round(image.width * IMAGE_SCALE),
        round(image.height * IMAGE_SCALE)
    )

    image = image.resize(
        new_size,
        Image.Resampling.LANCZOS
    )

    # Clean transparency again.
    alpha = image.getchannel("A").point(
        lambda value: 0 if value < ALPHA_CUTOFF else value
    )

    image.putalpha(alpha)

    return image


# ============================================================
# CONVERT PIL IMAGE TO TKINTER IMAGE
# ============================================================

def to_tk_image(image):

    return ImageTk.PhotoImage(image)


# ============================================================
# LOAD INDIVIDUAL IMAGE
# ============================================================

def load_image_file(path):

    image = Image.open(path)

    image = prepare_image(image)

    return to_tk_image(image)


# ============================================================
# LOAD MOOD SHEET
# ============================================================

def load_mood_sheet():

    images = {}

    if not MOOD_SHEET.exists():

        print("ERROR: Mood sheet not found:")
        print(MOOD_SHEET)

        return images


    print("Loading Bilbo mood sheet...")


    # Open the sheet.
    sheet = Image.open(
        MOOD_SHEET
    ).convert("RGBA")


    width, height = sheet.size

    print(
        f"Mood sheet size: {width} x {height}"
    )


    # --------------------------------------------------------
    # THE GENERATED SHEET:
    #
    # TOP:
    # HAPPY | SAD | STRESSED | TIRED
    #
    # BOTTOM:
    # EXCITED | ANGRY | NORMAL
    # --------------------------------------------------------

    top_width = width // 4

    bottom_width = width // 3

    half_height = height // 2


    # ========================================================
    # TOP ROW
    # ========================================================

    top_moods = [
        ("happy", 0),
        ("sad", 1),
        ("stressed", 2),
        ("tired", 3),
    ]


    for mood, index in top_moods:

        left = index * top_width

        right = (index + 1) * top_width


        crop = sheet.crop(
            (
                left,
                0,
                right,
                half_height
            )
        )


        crop = prepare_image(crop)


        # IMPORTANT:
        # Tkinter requires ImageTk.PhotoImage.
        images[mood] = to_tk_image(crop)


    # ========================================================
    # BOTTOM ROW
    # ========================================================

    bottom_moods = [
        ("excited", 0),
        ("angry", 1),
        ("normal", 2),
    ]


    for mood, index in bottom_moods:

        left = index * bottom_width

        right = (index + 1) * bottom_width


        crop = sheet.crop(
            (
                left,
                half_height,
                right,
                height
            )
        )


        crop = prepare_image(crop)


        # IMPORTANT:
        # Convert PIL image to Tkinter image.
        images[mood] = to_tk_image(crop)


    print("")
    print("Bilbo moods loaded:")

    for mood in images:

        print(
            f"  ✓ {mood}"
        )


    return images


# ============================================================
# BILBO PET
# ============================================================

class BilboPet:

    def __init__(self):

        # ----------------------------------------------------
        # WINDOW
        # ----------------------------------------------------

        self.root = tk.Tk()

        self.root.title("Bilbo")

        self.root.overrideredirect(True)

        self.root.attributes(
            "-topmost",
            True
        )

        self.root.configure(
            bg=TRANSPARENT
        )


        try:

            self.root.wm_attributes(
                "-transparentcolor",
                TRANSPARENT
            )

        except tk.TclError:

            pass


        # ----------------------------------------------------
        # CANVAS
        # ----------------------------------------------------

        self.canvas = tk.Canvas(
            self.root,
            bg=TRANSPARENT,
            highlightthickness=0,
            cursor="hand2"
        )

        self.canvas.pack()


        # ----------------------------------------------------
        # LOAD MOOD IMAGES
        # ----------------------------------------------------

        self.images = load_mood_sheet()


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if "happy" not in self.images:

            print(
                "Mood sheet could not be loaded."
            )

            print(
                "Trying bilbo_happy.png..."
            )


            if HAPPY_IMAGE.exists():

                self.images["happy"] = (
                    load_image_file(
                        HAPPY_IMAGE
                    )
                )

            else:

                print(
                    "ERROR: No Bilbo image found."
                )

                self.root.destroy()

                return


        # ----------------------------------------------------
        # ENSURE ALL MOODS EXIST
        # ----------------------------------------------------

        moods = [
            "sad",
            "stressed",
            "tired",
            "excited",
            "angry",
            "normal",
        ]


        for mood in moods:

            if mood not in self.images:

                print(
                    f"{mood} image missing."
                )

                # Use happy as fallback.
                self.images[mood] = (
                    self.images["happy"]
                )


        # ----------------------------------------------------
        # CURRENT MOOD
        # ----------------------------------------------------

        self.current_mood = "happy"


        # ----------------------------------------------------
        # CREATE IMAGE
        # ----------------------------------------------------

        self.pet_item = self.canvas.create_image(
            0,
            0,
            anchor="nw",
            image=self.images["happy"]
        )


        # ----------------------------------------------------
        # CLICK
        # ----------------------------------------------------

        self.canvas.tag_bind(
            self.pet_item,
            "<Button-1>",
            self.open_chat
        )

        self.canvas.bind(
            "<Button-1>",
            self.open_chat
        )


        # ----------------------------------------------------
        # DRAG
        # ----------------------------------------------------

        self.canvas.bind(
            "<ButtonPress-1>",
            self.start_drag
        )

        self.canvas.bind(
            "<B1-Motion>",
            self.drag
        )

        self.canvas.bind(
            "<ButtonRelease-1>",
            self.end_drag
        )


        # ----------------------------------------------------
        # POSITION
        # ----------------------------------------------------

        self.dragging = False

        self.drag_offset_x = 0

        self.drag_offset_y = 0

        self.x = 350

        self.y = 180


        # ----------------------------------------------------
        # MOVEMENT
        # ----------------------------------------------------

        self.dx = 1.5

        self.dy = 0.8


        # ----------------------------------------------------
        # SIZE
        # ----------------------------------------------------

        self.resize_to_image()


        self.root.geometry(
            f"{self.window_w}x{self.window_h}+"
            f"{int(self.x)}+{int(self.y)}"
        )


        # ----------------------------------------------------
        # ESCAPE
        # ----------------------------------------------------

        self.root.bind(
            "<Escape>",
            lambda event: self.root.destroy()
        )


        # ----------------------------------------------------
        # START LOOPS
        # ----------------------------------------------------

        self.poll_state()

        self.roam()


    # ========================================================
    # CHANGE MOOD
    # ========================================================

    def set_mood(self, mood):

        mood = str(
            mood
        ).lower().strip()


        valid_moods = {
            "happy",
            "sad",
            "stressed",
            "tired",
            "excited",
            "angry",
            "normal",
        }


        if mood not in valid_moods:

            mood = "normal"


        self.current_mood = mood


        image = self.images.get(
            mood,
            self.images["happy"]
        )


        self.canvas.itemconfigure(
            self.pet_item,
            image=image
        )


        self.resize_to_image()


        self.root.geometry(
            f"{self.window_w}x{self.window_h}+"
            f"{int(self.x)}+{int(self.y)}"
        )


        print(
            f"Bilbo mood changed to: {mood}"
        )


    # ========================================================
    # RESIZE
    # ========================================================

    def resize_to_image(self):

        image = self.images.get(
            self.current_mood,
            self.images["happy"]
        )


        self.window_w = image.width()

        self.window_h = image.height()


        self.canvas.configure(
            width=self.window_w,
            height=self.window_h
        )


        self.canvas.itemconfigure(
            self.pet_item,
            image=image
        )


    # ========================================================
    # READ MOOD
    # ========================================================

    def load_mood(self):

        try:

            if not STATE_FILE.exists():

                return "happy"


            with STATE_FILE.open(
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)


            mood = str(
                data.get(
                    "mood",
                    "happy"
                )
            ).lower()


            valid_moods = {
                "happy",
                "sad",
                "stressed",
                "tired",
                "excited",
                "angry",
                "normal",
            }


            if mood in valid_moods:

                return mood


            return "happy"


        except (
            OSError,
            json.JSONDecodeError
        ):

            return self.current_mood


    # ========================================================
    # POLL MOOD
    # ========================================================

    def poll_state(self):

        mood = self.load_mood()


        if mood != self.current_mood:

            self.set_mood(
                mood
            )


        self.root.after(
            POLL_MS,
            self.poll_state
        )


    # ========================================================
    # OPEN CHAT
    # ========================================================

    def open_chat(self, event=None):

        print(
            "Bilbo clicked!"
        )


        if not CHAT_FILE.exists():

            print(
                f"Chat file not found: {CHAT_FILE}"
            )

            return


        if not PYTHON_EXE.exists():

            print(
                f"Python environment not found: {PYTHON_EXE}"
            )

            return


        try:

            subprocess.Popen(
                [
                    str(PYTHON_EXE),
                    str(CHAT_FILE)
                ],
                cwd=str(PROJECT_DIR)
            )


            print(
                "Opening Bilbo chat..."
            )


        except Exception as error:

            print(
                f"Could not open chat: {error}"
            )


    # ========================================================
    # START DRAG
    # ========================================================

    def start_drag(self, event):

        self.dragging = True

        self.drag_offset_x = event.x

        self.drag_offset_y = event.y


    # ========================================================
    # DRAG
    # ========================================================

    def drag(self, event):

        if not self.dragging:

            return


        self.x = (
            self.root.winfo_pointerx()
            - self.drag_offset_x
        )


        self.y = (
            self.root.winfo_pointery()
            - self.drag_offset_y
        )


        self.root.geometry(
            f"{self.window_w}x{self.window_h}+"
            f"{int(self.x)}+{int(self.y)}"
        )


    # ========================================================
    # END DRAG
    # ========================================================

    def end_drag(self, event):

        self.dragging = False


    # ========================================================
    # ROAM
    # ========================================================

    def roam(self):

        if not self.dragging:

            screen_width = (
                self.root.winfo_screenwidth()
            )

            screen_height = (
                self.root.winfo_screenheight()
            )


            self.x += self.dx

            self.y += self.dy


            if (
                self.x <= 0
                or
                self.x + self.window_w
                >= screen_width
            ):

                self.dx *= -1


            if (
                self.y <= 0
                or
                self.y + self.window_h
                >= screen_height
            ):

                self.dy *= -1


            self.root.geometry(
                f"{self.window_w}x{self.window_h}+"
                f"{int(self.x)}+{int(self.y)}"
            )


        self.root.after(
            ROAM_MS,
            self.roam
        )


    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        self.root.mainloop()


# ============================================================
# START BILBO
# ============================================================

if __name__ == "__main__":

    BilboPet().run()