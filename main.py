import ctypes
import os
import sys
import threading
import time
import tkinter
from tkinter.filedialog import askdirectory, askopenfilenames

import customtkinter
import cv2 as cv
import numpy as np
from CTkMessagebox import CTkMessagebox


class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.running: bool = False
        self.currentdir: str = ""
        self.savedir: str = ""
        self.selected_files: list = []
        self.available_extensions: tuple = (".jpg", ".png", ".tiff", ".webp", ".bmp")
        self.font_config: dict = {"subtitle": ("", 0, "bold")}
        self.ipadx_config: dict = {"normal": 0}
        self.ipady_config: dict = {"normal": 0}
        self.padx_config: dict = {"normal": (10, 10), "checkbutton": (20, 10)}
        self.pady_config: dict = {
            "normal": (2, 2),
            "subtitle": (4, 0),
            "label": (0, 0),
            "entry": (0, 4),
            "combobox": (0, 2),
            "radiobutton": (4, 1),
            "progressbar": (0, 4),
        }

        self.tkstr_filecount = tkinter.StringVar(value="No file is selected")
        self.tkstr_namepreview = tkinter.StringVar(value="No file is selected")
        self.tkstr_savedir = tkinter.StringVar(
            value="(After any file is selected, the directory in which the file resides is set as default.)"
        )
        self.tkbool_horizontal = tkinter.BooleanVar()
        self.tkbool_vertical = tkinter.BooleanVar()
        self.tkbool_invert_color = tkinter.BooleanVar()
        self.tkbool_grayscale = tkinter.BooleanVar()
        self.tkbool_whiteboard = tkinter.BooleanVar()
        self.tkint_degree = tkinter.IntVar()

        customtkinter.set_appearance_mode("system")
        customtkinter.set_default_color_theme("blue")

        self.title("Py Image Editor 1.0")
        self.geometry("+10+10")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        row = 0

        self.inner = customtkinter.CTkFrame(master=self)
        self.inner.grid(
            column=0,
            row=row,
            ipadx=3,
            ipady=3,
            padx=(3, 3),
            pady=(3, 3),
        )
        row += 1

        self.inner.grid_columnconfigure(0, minsize=250)
        self.inner.grid_columnconfigure(1, minsize=250)

        self.title_files = customtkinter.CTkLabel(
            master=self.inner, text="Files", font=self.font_config["subtitle"]
        )
        self.title_files.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["subtitle"],
        )
        row += 1

        self.lable_files = customtkinter.CTkLabel(master=self.inner, text="Files:")
        self.lable_files.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.button_open = customtkinter.CTkButton(
            master=self.inner, text="Open", width=10
        )
        self.button_open.grid(
            column=0,
            row=row,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        self.button_open.bind("<Button-1>", self.launch_file_opener)
        self.label_status = customtkinter.CTkLabel(
            master=self.inner, textvariable=self.tkstr_filecount
        )
        self.label_status.grid(
            column=1,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.title_editor = customtkinter.CTkLabel(
            master=self.inner, text="Editor", font=self.font_config["subtitle"]
        )
        self.title_editor.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["subtitle"],
        )
        row += 1

        self.label_w = customtkinter.CTkLabel(master=self.inner, text="Width (px):")
        self.label_w.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.entry_w = customtkinter.CTkEntry(master=self.inner, width=10)
        self.entry_w.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["entry"],
        )
        row += 1

        self.label_h = customtkinter.CTkLabel(master=self.inner, text="Height (px):")
        self.label_h.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.entry_h = customtkinter.CTkEntry(master=self.inner, width=10)
        self.entry_h.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["entry"],
        )
        row += 1

        self.checkbutton_vartical = customtkinter.CTkCheckBox(
            master=self.inner, text="Flip vertical", variable=self.tkbool_vertical
        )
        self.checkbutton_vartical.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["checkbutton"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.checkbutton_horizontal = customtkinter.CTkCheckBox(
            master=self.inner, text="Flip horizontal", variable=self.tkbool_horizontal
        )
        self.checkbutton_horizontal.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["checkbutton"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.radiobuttons = customtkinter.CTkFrame(master=self.inner)
        self.radiobuttons.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.W,
            ipadx=1,
            ipady=2,
            padx=(10, 10),
            pady=(2, 4),
        )
        row += 1

        self.radiobutton_0 = customtkinter.CTkRadioButton(
            self.radiobuttons,
            text="Rotate right 0°",
            variable=self.tkint_degree,
            value=0,
        )
        self.radiobutton_0.grid(
            column=0,
            row=0,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["radiobutton"],
        )

        self.radiobutton_90 = customtkinter.CTkRadioButton(
            self.radiobuttons,
            text="Rotate right 90°",
            variable=self.tkint_degree,
            value=90,
        )
        self.radiobutton_90.grid(
            column=1,
            row=0,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["radiobutton"],
        )

        self.radiobutton_180 = customtkinter.CTkRadioButton(
            self.radiobuttons,
            text="Rotate right 180°",
            variable=self.tkint_degree,
            value=180,
        )
        self.radiobutton_180.grid(
            column=0,
            row=1,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["radiobutton"],
        )

        self.radiobutton_270 = customtkinter.CTkRadioButton(
            self.radiobuttons,
            text="Rotate right 270°",
            variable=self.tkint_degree,
            value=270,
        )
        self.radiobutton_270.grid(
            column=1,
            row=1,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["radiobutton"],
        )

        self.label_filter = customtkinter.CTkLabel(
            master=self.inner, text="Filters", font=self.font_config["subtitle"]
        )
        self.label_filter.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["subtitle"],
        )
        row += 1

        self.checkbutton_grayscale = customtkinter.CTkCheckBox(
            master=self.inner, text="Grayscale", variable=self.tkbool_grayscale
        )
        self.checkbutton_grayscale.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["checkbutton"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.checkbutton_invert_color = customtkinter.CTkCheckBox(
            master=self.inner,
            text="Invert Colors",
            variable=self.tkbool_invert_color,
        )
        self.checkbutton_invert_color.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["checkbutton"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.checkbutton_whiteboard = customtkinter.CTkCheckBox(
            master=self.inner, text="Whiteboard", variable=self.tkbool_whiteboard
        )
        self.checkbutton_whiteboard.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["checkbutton"],
            pady=self.pady_config["normal"],
        )
        row += 1

        self.label_output_properties = customtkinter.CTkLabel(
            master=self.inner,
            text="Output Properties",
            font=self.font_config["subtitle"],
        )
        self.label_output_properties.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["subtitle"],
        )
        row += 1

        self.label_format = customtkinter.CTkLabel(master=self.inner, text="Format:")
        self.label_format.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.combobox_extension = customtkinter.CTkComboBox(
            master=self.inner,
            justify="center",
            state="readonly",
            values=self.available_extensions,
            width=10,
        )
        self.combobox_extension.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["combobox"],
        )
        self.combobox_extension.set(".jpg")
        row += 1

        self.label_name = customtkinter.CTkLabel(master=self.inner, text="Name:")
        self.label_name.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.label_namepreview = customtkinter.CTkLabel(
            master=self.inner, textvariable=self.tkstr_namepreview
        )
        self.label_namepreview.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=2,
        )
        row += 1

        self.entry_optional_name = customtkinter.CTkEntry(master=self.inner, width=10)
        self.entry_optional_name.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["entry"],
        )
        self.entry_optional_name.insert(0, "_modified")
        row += 1

        self.button_clearname = customtkinter.CTkButton(
            master=self.inner, text="Restore default", width=10
        )
        self.button_clearname.grid(
            column=1,
            row=row,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        self.button_clearname.bind("<Button-1>", self.reset_optional_name)
        row += 1

        self.label_save = customtkinter.CTkLabel(master=self.inner, text="Save to:")
        self.label_save.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.label_savedir = customtkinter.CTkLabel(
            master=self.inner, textvariable=self.tkstr_savedir
        )
        self.label_savedir.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=2,
        )
        row += 1

        self.button_browse = customtkinter.CTkButton(
            master=self.inner, text="Browse", width=10
        )
        self.button_browse.grid(
            column=0,
            row=row,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        self.button_browse.bind("<Button-1>", self.ask_savedir)
        self.button_set_currentdir_as_savedir = customtkinter.CTkButton(
            master=self.inner, text="Restore default"
        )
        self.button_set_currentdir_as_savedir.grid(
            column=1,
            row=row,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        self.button_set_currentdir_as_savedir.bind(
            "<Button-1>", self.set_currentdir_as_savedir
        )
        row += 1

        self.title_status = customtkinter.CTkLabel(
            master=self.inner, text="Status", font=self.font_config["subtitle"]
        )
        self.title_status.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["subtitle"],
        )
        row += 1

        self.label_progress = customtkinter.CTkLabel(
            master=self.inner, text="Progress:"
        )
        self.label_progress.grid(
            column=0,
            row=row,
            sticky=tkinter.W,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["label"],
        )
        row += 1

        self.progressbar = customtkinter.CTkProgressBar(
            master=self.inner,
            orientation="horizontal",
            mode="determinate",
        )
        self.progressbar.grid(
            column=0,
            row=row,
            columnspan=2,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["progressbar"],
        )
        self.progressbar.set(0)
        row += 1

        self.button_ok = customtkinter.CTkButton(
            master=self.inner, text="Start", width=10
        )
        self.button_ok.grid(
            column=1,
            row=row,
            sticky=tkinter.NSEW,
            ipadx=self.ipadx_config["normal"],
            ipady=self.ipady_config["normal"],
            padx=self.padx_config["normal"],
            pady=self.pady_config["normal"],
        )
        self.button_ok.bind("<Return>", self.launch_image_processor)
        self.button_ok.bind("<Button-1>", self.launch_image_processor)

        self.bind("<Return>", self.launch_image_processor)
        self.bind("<Escape>", self.close_window_)

        self.running = True

        self.updater = threading.Thread(target=self.update)
        self.updater.daemon = True
        self.updater.start()

    # Support path including Japanese letters
    def imread_(self, filename, flags=cv.IMREAD_COLOR, dtype=np.uint8):
        try:
            n = np.fromfile(filename, dtype)
            img = cv.imdecode(n, flags)
            return img
        except Exception as e:
            print(e)
            return None

    def imwrite_(self, filename, img, params=None):
        try:
            ext = os.path.splitext(filename)[1]
            result, n = cv.imencode(ext, img, params)

            if result:
                with open(filename, mode="w+b") as f:
                    n.tofile(f)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def showinfo(self, title="Info", message=""):
        CTkMessagebox(title=title, message=message)

    def showerror(self, title="Error", message=""):
        CTkMessagebox(title="Error", message=message, icon="cancel")

    def shorten_string_length(self, str, max) -> str:
        if len(str) >= max:
            return "{}...{}".format(
                str[0 : (max // 2 - 1)], str[-(max // 2) : len(str)]
            )
        else:
            return str

    def launch_file_opener(self, event):
        file_opener = threading.Thread(target=self.openflies)
        file_opener.start()

    def launch_image_processor(self, event):
        image_prosessor = threading.Thread(target=self.process_image)
        image_prosessor.start()

    def openflies(self):
        self.selected_files = list(askopenfilenames())
        if not self.selected_files:
            sys.exit()
        else:
            pass

        self.currentdir = os.path.dirname(self.selected_files[0])
        self.savedir = self.currentdir

        if len(self.selected_files) == 1:
            self.tkstr_filecount.set("1 file selected")
        else:
            self.tkstr_filecount.set(
                "{} files selected".format(len(self.selected_files))
            )

    def process_image(self):
        if len(self.selected_files) == 0:
            self.showinfo("Info", "No file selected.")
            sys.exit()

        do_flip_horizontal: bool = self.tkbool_horizontal.get()
        do_flip_vertical: bool = self.tkbool_vertical.get()
        do_rotate_degree: int = self.tkint_degree.get()
        do_grayscale: bool = self.tkbool_grayscale.get()
        do_invert_color: bool = self.tkbool_invert_color.get()
        do_whiteboard: bool = self.tkbool_whiteboard.get()
        optional_name: str = self.entry_optional_name.get()
        extension: str = self.combobox_extension.get()

        if self.entry_w.get():
            try:
                iw = int(self.entry_w.get())
                if iw < 0:
                    do_flip_horizontal = True
                    iw = abs(iw)
                else:
                    pass
            except:
                self.showerror("Error", "Invalid width input")
                self.entry_w.delete(0, tkinter.END)
                self.entry_h.delete(0, tkinter.END)
                sys.exit()
        else:
            iw = None

        if self.entry_h.get():
            try:
                ih = int(self.entry_h.get())
                if ih < 0:
                    do_flip_vertical = True
                    ih = abs(ih)
                else:
                    pass
            except:
                self.showerror("Error", "Invalid height input")
                self.entry_w.delete(0, tkinter.END)
                self.entry_h.delete(0, tkinter.END)
                sys.exit()
        else:
            ih = None

        ignore_count = 0
        step = 1 / len(self.selected_files)
        value = step
        self.progressbar.set(0)
        self.progressbar.start()

        for src in self.selected_files:
            img = self.imread_(src)
            if img is None:
                ignore_count += 1
                self.progressbar.set(value)
                value += step
                self.update_idletasks()
                continue
            else:
                pass

            h, w, _ = img.shape

            if iw and ih:
                img = cv.resize(img, dsize=(iw, ih))
            elif iw and not ih:
                img = cv.resize(img, dsize=(iw, round(iw / w * h)))
            elif not iw and ih:
                img = cv.resize(img, dsize=(round(ih / h * w), ih))
            else:
                pass

            if do_flip_horizontal == True:
                img = cv.flip(img, 1)
            else:
                pass

            if do_flip_vertical == True:
                img = cv.flip(img, 0)
            else:
                pass

            if do_rotate_degree == 0:
                pass
            elif do_rotate_degree == 90:
                img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
            elif do_rotate_degree == 180:
                img = cv.rotate(img, cv.ROTATE_180)
            elif do_rotate_degree == 270:
                img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
            else:
                pass

            if do_grayscale:
                img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
            else:
                pass

            if do_invert_color:
                img = cv.bitwise_not(img)
            else:
                pass

            if do_whiteboard:
                img = self.whiteboard(img)
            else:
                pass

            self.imwrite_(
                "{}/{}{}{}".format(
                    self.savedir,
                    os.path.splitext(os.path.basename(src))[0],
                    optional_name,
                    extension,
                ),
                img,
            )

            self.progressbar.set(value)
            value += step
            self.update_idletasks()

        self.progressbar.stop()

        if len(self.selected_files) - ignore_count == 0:
            msg1 = "No file processed successfully"
        elif len(self.selected_files) - ignore_count == 1:
            msg1 = "1 file processed successfully"
        else:
            msg1 = "{} files processed successfully".format(
                len(self.selected_files) - ignore_count
            )
        if ignore_count == 0:
            msg2 = "No file ignored"
        elif ignore_count == 1:
            msg2 = "1 file ignored"
        else:
            msg2 = "{} files ignored".format(ignore_count)

        self.showinfo("Operation completed", "{}\n{}".format(msg1, msg2))
        self.progressbar.set(0)

    def ask_savedir(self, event):
        self.savedir = askdirectory()

    def set_currentdir_as_savedir(self, event):
        if self.currentdir:
            self.savedir = self.currentdir
        else:
            pass

    def reset_optional_name(self, event):
        self.entry_optional_name.delete(0, tkinter.END)
        self.entry_optional_name.insert(0, "_modified")

    def update(self):
        while self.running:
            self.tkstr_namepreview.set(
                self.shorten_string_length(
                    str=(
                        "sample{}{}".format(
                            self.entry_optional_name.get(),
                            self.combobox_extension.get(),
                        )
                    ),
                    max=50,
                )
            )
            if self.savedir:
                self.tkstr_savedir.set(
                    self.shorten_string_length(str=self.savedir, max=50)
                )
            time.sleep(1 / 60)

    def close_window(self):
        self.running = False
        self.quit()
        self.destroy()

    def close_window_(self, event):
        self.running = False
        self.quit()
        self.destroy()

    """



    The source code below here is referenced or quoted from the following URL, but how can I show it on GitHub?
    https://github.com/santhalakshminarayana/whiteboard-image-enhance/blob/main/whiteboard_image_enhance.py



    """

    def normalize_kernel(self, kernel, k_width, k_height, scaling_factor=1.0):
        """Zero-summing normalize kernel"""

        K_EPS = 1.0e-12
        # positive and negative sum of kernel values
        pos_range, neg_range = 0, 0
        for i in range(k_width * k_height):
            if abs(kernel[i]) < K_EPS:
                kernel[i] = 0.0
            if kernel[i] < 0:
                neg_range += kernel[i]
            else:
                pos_range += kernel[i]

        # scaling factor for positive and negative range
        pos_scale, neg_scale = pos_range, -neg_range
        if abs(pos_range) >= K_EPS:
            pos_scale = pos_range
        else:
            pos_sacle = 1.0
        if abs(neg_range) >= K_EPS:
            neg_scale = 1.0
        else:
            neg_scale = -neg_range

        pos_scale = scaling_factor / pos_scale
        neg_scale = scaling_factor / neg_scale

        # scale kernel values for zero-summing kernel
        for i in range(k_width * k_height):
            if not np.nan == kernel[i]:
                kernel[i] *= pos_scale if kernel[i] >= 0 else neg_scale

        return kernel

    def dog(self, img, k_size, sigma_1, sigma_2):
        """Difference of Gaussian by subtracting kernel 1 and kernel 2"""

        k_width = k_height = k_size
        x = y = (k_width - 1) // 2
        kernel = np.zeros(k_width * k_height)

        # first gaussian kernal
        if sigma_1 > 0:
            co_1 = 1 / (2 * sigma_1 * sigma_1)
            co_2 = 1 / (2 * np.pi * sigma_1 * sigma_1)
            i = 0
            for v in range(-y, y + 1):
                for u in range(-x, x + 1):
                    kernel[i] = np.exp(-(u * u + v * v) * co_1) * co_2
                    i += 1
        # unity kernel
        else:
            kernel[x + y * k_width] = 1.0

        # subtract second gaussian from kernel
        if sigma_2 > 0:
            co_1 = 1 / (2 * sigma_2 * sigma_2)
            co_2 = 1 / (2 * np.pi * sigma_2 * sigma_2)
            i = 0
            for v in range(-y, y + 1):
                for u in range(-x, x + 1):
                    kernel[i] -= np.exp(-(u * u + v * v) * co_1) * co_2
                    i += 1
        # unity kernel
        else:
            kernel[x + y * k_width] -= 1.0

        # zero-normalize scling kernel with scaling factor 1.0
        norm_kernel = self.normalize_kernel(
            kernel, k_width, k_height, scaling_factor=1.0
        )

        # apply filter with norm_kernel
        return cv.filter2D(img, -1, norm_kernel.reshape(k_width, k_height))

    def negate(self, img):
        """Negative of image"""

        return cv.bitwise_not(img)

    def get_black_white_indices(self, hist, tot_count, black_count, white_count):
        """Blacking and Whiting out indices same as color balance"""

        black_ind = 0
        white_ind = 255
        co = 0
        for i in range(len(hist)):
            co += hist[i]
            if co > black_count:
                black_ind = i
                break

        co = 0
        for i in range(len(hist) - 1, -1, -1):
            co += hist[i]
            if co > (tot_count - white_count):
                white_ind = i
                break

        return [black_ind, white_ind]

    def contrast_stretch(self, img, black_point, white_point):
        """Contrast stretch image with black and white cap"""

        tot_count = img.shape[0] * img.shape[1]
        black_count = tot_count * black_point / 100
        white_count = tot_count * white_point / 100
        ch_hists = []
        # calculate histogram for each channel
        for ch in cv.split(img):
            ch_hists.append(
                cv.calcHist([ch], [0], None, [256], (0, 256)).flatten().tolist()
            )

        # get black and white percentage indices
        black_white_indices = []
        for hist in ch_hists:
            black_white_indices.append(
                self.get_black_white_indices(hist, tot_count, black_count, white_count)
            )

        stretch_map = np.zeros((3, 256), dtype="uint8")

        # stretch histogram
        for curr_ch in range(len(black_white_indices)):
            black_ind, white_ind = black_white_indices[curr_ch]
            for i in range(stretch_map.shape[1]):
                if i < black_ind:
                    stretch_map[curr_ch][i] = 0
                else:
                    if i > white_ind:
                        stretch_map[curr_ch][i] = 255
                    else:
                        if (white_ind - black_ind) > 0:
                            stretch_map[curr_ch][i] = (
                                round((i - black_ind) / (white_ind - black_ind)) * 255
                            )
                        else:
                            stretch_map[curr_ch][i] = 0

        # stretch image
        ch_stretch = []
        for i, ch in enumerate(cv.split(img)):
            ch_stretch.append(cv.LUT(ch, stretch_map[i]))

        return cv.merge(ch_stretch)

    def fast_gaussian_blur(self, img, ksize, sigma):
        """Gussian blur using linear separable property of Gaussian distribution"""

        kernel_1d = cv.getGaussianKernel(ksize, sigma)
        return cv.sepFilter2D(img, -1, kernel_1d, kernel_1d)

    def gamma(self, img, gamma_value):
        """Gamma correction of image"""

        i_gamma = 1 / gamma_value
        lut = np.array(
            [((i / 255) ** i_gamma) * 255 for i in np.arange(0, 256)], dtype="uint8"
        )
        return cv.LUT(img, lut)

    def color_balance(self, img, low_per, high_per):
        """Contrast stretch image by histogram equilization with black and white cap"""

        tot_pix = img.shape[1] * img.shape[0]
        # no.of pixels to black-out and white-out
        low_count = tot_pix * low_per / 100
        high_count = tot_pix * (100 - high_per) / 100

        cs_img = []
        # for each channel, apply contrast-stretch
        for ch in cv.split(img):
            # cummulative histogram sum of channel
            cum_hist_sum = np.cumsum(cv.calcHist([ch], [0], None, [256], (0, 256)))

            # find indices for blacking and whiting out pixels
            li, hi = np.searchsorted(cum_hist_sum, (low_count, high_count))
            if li == hi:
                cs_img.append(ch)
                continue
            # lut with min-max normalization for [0-255] bins
            lut = np.array(
                [
                    0
                    if i < li
                    else (255 if i > hi else round((i - li) / (hi - li) * 255))
                    for i in np.arange(0, 256)
                ],
                dtype="uint8",
            )
            # constrast-stretch channel
            cs_ch = cv.LUT(ch, lut)
            cs_img.append(cs_ch)

        return cv.merge(cs_img)

    def whiteboard(self, img):
        """Enhance Whiteboard image"""

        # parameters for enhancing functions
        dog_k_size, dog_sigma_1, dog_sigma_2 = 15, 100, 0
        cs_black_per, cs_white_per = 2, 99.5
        gauss_k_size, gauss_sigma = 3, 1
        gamma_value = 1.1
        cb_black_per, cb_white_per = 2, 1

        # Difference of Gaussian (DoG)
        dog_img = self.dog(img, dog_k_size, dog_sigma_1, dog_sigma_2)
        # Negative of image
        negative_img = self.negate(dog_img)
        # Contrast Stretch (CS)
        contrast_stretch_img = self.contrast_stretch(
            negative_img, cs_black_per, cs_white_per
        )
        # Gaussian Blur
        blur_img = self.fast_gaussian_blur(
            contrast_stretch_img, gauss_k_size, gauss_sigma
        )
        # Gamma Correction
        gamma_img = self.gamma(blur_img, gamma_value)
        # Color Balance (CB) (also Contrast Stretch)
        color_balanced_img = self.color_balance(gamma_img, cb_black_per, cb_white_per)

        return color_balanced_img


if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)
    except:
        pass

    app = App()
    app.mainloop()
