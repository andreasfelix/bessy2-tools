import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os, json
from name_conversion import epics2short, short2epics

try:
    from epics import caget, caput
except:
    import random
    caget = caput = lambda *args: print("Epics is not installed") or random.uniform(-3, 3)

DEBUG = True


class GUI:
    def __init__(self):
        self.master = tk.Tk()
        self.master.withdraw()
        self.master.title("Quadrupole values")
        # self.master.geometry("1280x600")
        self.master.tk_setPalette(background='white', activeBackground='#639ee4', activeForeground='white')
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        self.create_top_frame()
        self.create_tree_view()
        self.create_bottom_frame()
        self.master.deiconify()

        if DEBUG:
            self.update_dict_from_file(self.new_quad_values, self.new_quad_values_path, "example_values/Q5T2off_turn_off.json", True)
            self.update_dict_from_file(self.ref_quad_values, self.ref_quad_values_path, "example_values/BII_2017-08-04_23-42_LOCOFitByPS_noID_ActualUserMode.json", True)
            self.update_dict_from_file(self.ref_PS_values, self.ref_PS_values_path, "example_values/BII_2017-08-04_23-42_LOCOFitByPS_noID_ActualUserMode.values", False)


    def create_top_frame(self):
        self.top_frame = tk.Frame(self.master)
        grid_configure(self.top_frame, 3, 2, weight_col=[1, 6])
        self.top_frame.pack(fill=tk.X)

        self.new_quad_values = {}
        self.new_PS_values = {}
        self.ref_quad_values = {}
        self.ref_PS_values = {}
        self.present_PS_values = {}

        self.new_quad_values_path = tk.StringVar()
        self.button_new_quad_values = tk.Button(self.top_frame, text="New lattice file",
                                                command=lambda: self.open_json_from_file(self.new_quad_values, self.new_quad_values_path, "New quad values", lattice_file=True))
        self.label_new_quad_values = tk.Label(self.top_frame, textvariable=self.new_quad_values_path)

        self.ref_quad_values_path = tk.StringVar()
        self.button_ref_quad_values = tk.Button(self.top_frame, text="Ref lattice file",
                                                command=lambda: self.open_json_from_file(self.ref_quad_values, self.ref_quad_values_path, "Ref quad values", lattice_file=True))
        self.label_ref_quad_values = tk.Label(self.top_frame, textvariable=self.ref_quad_values_path)

        self.ref_PS_values_path = tk.StringVar()
        self.button_ref_PS_values = tk.Button(self.top_frame, text="Ref PS values",
                                              command=lambda: self.open_json_from_file(self.ref_PS_values, self.ref_PS_values_path, "Ref PS values"))
        self.label_ref_PS_values = tk.Label(self.top_frame, textvariable=self.ref_PS_values_path)

        for i, (button, label) in enumerate(zip([self.button_new_quad_values, self.button_ref_quad_values, self.button_ref_PS_values],
                                                [self.label_new_quad_values, self.label_ref_quad_values, self.label_ref_PS_values])):
            button.grid(row=i, column=0, sticky="wens")
            label.grid(row=i, column=1, sticky="wens")

    def create_tree_view(self):
        self.tree_view = ttk.Treeview(self.master, height=30)
        self.tree_view.pack(fill=tk.BOTH, expand=1)
        headings = ["Magnet", "New PS values", "Ref PS values", "Current PS values", "Factor", "New k values", "Ref k values"]
        self.tree_view["columns"] = headings
        self.tree_view["show"] = "headings"
        for heading in headings:
            self.tree_view.heading(heading, text=heading)

    def update_tree_view(self):
        self.tree_view.delete(*self.tree_view.get_children())
        if self.new_PS_values:
            for i, magnet in enumerate(self.new_PS_values.keys()):
                values = (magnet, self.new_PS_values[magnet], self.ref_PS_values[magnet], caget(magnet + ':rdbk'),
                          self.new_PS_values[magnet] / self.ref_PS_values[magnet], self.new_quad_values[magnet], self.ref_quad_values[magnet])
                values = tuple(round(x,3) if isinstance(x, float) else x for x in values)
                self.tree_view.insert('', i, magnet, values=values)

    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.pack(fill=tk.X)

        self.button_set_new_PS_values = tk.Button(self.bottom_frame, text="Set new PS values", command=self.set_new_PS_values, bg="#DC143C", fg="white")
        self.button_set_ref_PS_values = tk.Button(self.bottom_frame, text="Set ref PS values", command=self.set_ref_PS_values, bg="#DC143C", fg="white")
        self.button_compute_new_PS_values = tk.Button(self.bottom_frame, text="Compute new PS values", command=self.compute_new_PS_values)
        self.button_print_new_PS_values = tk.Button(self.bottom_frame, text="Update view", command=self.update_tree_view)

        self.button_compute_new_PS_values.pack(side="left")
        self.button_print_new_PS_values.pack(side="left")
        self.button_set_new_PS_values.pack(side="right")
        self.button_set_ref_PS_values.pack(side="right")

    def open_json_from_file(self, dictionary, string_var, message, lattice_file=False):
        path = tk.filedialog.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__)), title=message)
        if path:
            self.update_dict_from_file(dictionary, string_var, path, lattice_file)

    def update_dict_from_file(self, dictionary, string_var, path, lattice_file):
        with open(path) as file:
            dictionary.clear()
            json_dict = json.load(file)
            if lattice_file:
                json_dict = json_dict["elements"]
                json_dict = {short2epics[short]: attributes["k1"] for short, attributes in json_dict.items() if attributes["type"] == "Quad"}
            dictionary.update(json_dict)
            string_var.set(path)

    def compute_new_PS_values(self):
        if self.new_quad_values.keys() == self.ref_quad_values.keys():
            for key in self.new_quad_values.keys():
                if self.new_quad_values[key] != self.ref_quad_values[key]:
                    self.new_PS_values[key] = self.new_quad_values[key] * self.ref_PS_values[key] / self.ref_quad_values[key]
            print(self.new_PS_values)
        else:
            print("Different Magnets!")

    def set_new_PS_values(self):  # TODO: implement with Paul
        pass

    def set_ref_PS_values(self):  # TODO: implement with Paul
        pass

def grid_configure(widget, N, M, weight_row=None, weight_col=None):
    for i in range(N):
        widget.grid_rowconfigure(i, weight=1 if weight_row is None else weight_row[i])
    for j in range(M):
        widget.grid_columnconfigure(j, weight=1 if weight_col is None else weight_col[j])

if __name__ == '__main__':
    GUI().master.mainloop()
