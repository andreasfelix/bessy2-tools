import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import os, json
from name_conversion import epics2short, short2epics, quad_list_epics
from tk_utils import grid_configure, ScrollSpinbox

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
        self.master.minsize(width=800, height=600)
        self.master.tk_setPalette(background='white', activeBackground='#639ee4', activeForeground='white')
        self.master.protocol("WM_DELETE_WINDOW", self.master.quit)
        grid_configure(self.master, 4, 1, weight_row=[0, 0, 1, 0])
        self.create_top_frame()
        self.create_multiknob_frame()
        self.create_tree_view()
        self.create_bottom_frame()
        self.master.deiconify()

        if DEBUG:
            self.update_dict_from_file(self.new_quad_values, self.new_quad_values_path, "example_values/V3_max_center.json", True)
            self.update_dict_from_file(self.ref_quad_values, self.ref_quad_values_path, "example_values/BII_2017-08-04_23-42_LOCOFitByPS_noID_ActualUserMode.json", True)
            self.update_dict_from_file(self.ref_PS_values, self.ref_PS_values_path, "example_values/BII_2017-08-04_23-42_LOCOFitByPS_noID_ActualUserMode.values", False)
            self.update_dict_from_file(self.second_new_quad_values, self.second_new_quad_values_path, "example_values/V3_min_center.json", True)

    def create_top_frame(self):
        self.top_frame = tk.Frame(self.master)
        grid_configure(self.top_frame, 3, 2, weight_col=[1, 6])
        self.top_frame.grid(row=0, sticky="wens")

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
        self.tree_view = ttk.Treeview(self.master)
        self.tree_view.grid(row=2, sticky="wens")
        headings = ["Magnet", "New PS values", "Ref PS values", "Current PS values", "Factor", "New k values", "Ref k values"]
        self.tree_view["columns"] = headings
        self.tree_view["show"] = "headings"
        for heading in headings:
            self.tree_view.heading(heading, text=heading)

    def update_tree_view(self): # correct new k valuet
        self.tree_view.delete(*self.tree_view.get_children())
        if self.new_PS_values:
            for i, magnet in enumerate(self.new_PS_values.keys()):
                values = (magnet, self.new_PS_values[magnet], self.ref_PS_values[magnet], caget(magnet + ':set'),
                          self.new_PS_values[magnet] / self.ref_PS_values[magnet], self.new_quad_values[magnet], self.ref_quad_values[magnet])
                values = tuple(round(x, 3) if isinstance(x, float) else x for x in values)
                self.tree_view.insert('', i, magnet, values=values)
        else:
            print("Could not update Tree view")

    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.master)
        self.bottom_frame.grid(row=3, sticky="wens")

        self.button_set_new_PS_values = tk.Button(self.bottom_frame, text="Set new PS values", command=self.set_new_PS_values, bg="#DC143C", fg="white")
        self.button_save_all_PS_values = tk.Button(self.bottom_frame, text="Save All PS values", command=self.save_all_PS_values, bg="#DC143C", fg="white")
        self.button_set_saved_PS_values = tk.Button(self.bottom_frame, text="Set saved PS values", command=self.set_saved_PS_values, bg="#DC143C", fg="white")
        self.button_compute_new_PS_values = tk.Button(self.bottom_frame, text="Compute new PS values", command=lambda: self.compute_new_PS_values(self.new_quad_values))
        self.button_print_new_PS_values = tk.Button(self.bottom_frame, text="Update view", command=self.update_tree_view)
        self.toggle_multiknob = tk.IntVar()
        self.toggle_multiknob.set(0)
        self.checkbutton_toggle_multiknob = tk.Checkbutton(self.bottom_frame, text="Toggle Multiknob", variable=self.toggle_multiknob, command=self.toggle_multiknob_frame)

        self.button_compute_new_PS_values.pack(side="left")
        self.button_print_new_PS_values.pack(side="left")
        self.checkbutton_toggle_multiknob.pack(side="left")
        self.button_set_new_PS_values.pack(side="right")
        self.button_set_saved_PS_values.pack(side="right")
        self.button_save_all_PS_values.pack(side="right")

    def create_multiknob_frame(self):
        self.second_new_quad_values = {}
        self.multiknob_new_quad_values = {}
        self.second_new_quad_values_path = tk.StringVar()
        self.multiknob = tk.DoubleVar()
        self.multiknob.set(0)

        self.multiknob_frame = tk.Frame(self.master)
        grid_configure(self.multiknob_frame, 1, 3, weight_col=[2, 1, 50])
        self.button_second_new_quad_values = tk.Button(self.multiknob_frame, text="Second lattice file",
                                                       command=lambda: self.open_json_from_file(self.second_new_quad_values, self.second_new_quad_values_path, "New quad values", lattice_file=True))
        self.label_second_new_quad_values = tk.Label(self.multiknob_frame, textvariable=self.second_new_quad_values_path)
        self.spinbox_multiknob = ScrollSpinbox(self.multiknob_frame, textvariable=self.multiknob, width=5, from_=0, to=1, increment=0.01, command=lambda: self.compute_multiknob_new_quad_values() or self.compute_new_PS_values(self.multiknob_new_quad_values) or self.update_tree_view())

        for i, x in enumerate([self.button_second_new_quad_values, self.spinbox_multiknob, self.label_second_new_quad_values]):
            x.grid(row=0, column=i, sticky="wens")

    def toggle_multiknob_frame(self):
        if self.toggle_multiknob.get():
            self.multiknob_frame.grid(row=1, sticky="wens")
        else:
            self.multiknob_frame.grid_forget()

    def open_json_from_file(self, dictionary, string_var, message, lattice_file=False):
        path = tk.filedialog.askopenfilename(initialdir=os.getcwd() + "/example_values", title=message)
        if path:
            self.update_dict_from_file(dictionary, string_var, path, lattice_file)

    def update_dict_from_file(self, dictionary, string_var, path, lattice_file):
        with open(path) as file:
            dictionary.clear()
            json_dict = json.load(file)
            if lattice_file:
                json_dict = json_dict["elements"]
                json_dict = {short2epics[short]: attributes["k1"] for short, attributes in json_dict.items() if attributes["type"] == "Quad" and short !="QIT6"}
            dictionary.update(json_dict)
            string_var.set(path)

    def compute_new_PS_values(self, quad_values):
        if set(quad_values.keys()).issubset(set(self.ref_PS_values.keys())):
            self.new_PS_values.clear()
            for key in quad_values:
                if quad_values[key] != self.ref_quad_values[key]:
                    print(quad_values[key], self.ref_quad_values[key])
                    self.new_PS_values[key] = quad_values[key] * self.ref_PS_values[key] / self.ref_quad_values[key]
            print(self.new_PS_values)
        else:
            print("Different Magnets!", set(quad_values.keys()) - set(self.ref_PS_values.keys()))

    def compute_multiknob_new_quad_values(self):
        if self.new_quad_values.keys() == self.second_new_quad_values.keys():
            self.multiknob_new_quad_values.clear()
            self.multiknob_new_quad_values.update(self.new_quad_values)
            for key in self.new_quad_values:
                if self.new_quad_values[key] != self.second_new_quad_values[key]:
                    self.multiknob_new_quad_values[key] = (1 - self.multiknob.get()) * self.new_quad_values[key] + self.multiknob.get() * self.second_new_quad_values[key]
            print(self.multiknob_new_quad_values)
        else:
            print("Multiknob lattices do not have the same Magnet!")


    def set_new_PS_values(self):  # TODO: implement with Paul
        for magnet,value in self.new_PS_values.items():
            caput(magnet + ':set', value)


    def save_all_PS_values(self):  # TODO: implement with Paul
        self.saved_PS_values = {}
        for magnet in quad_list_epics:
            self.saved_PS_values[magnet] = caget(magnet + ':set')

    def set_saved_PS_values(self):
        for magnet,value in self.saved_PS_values.items():
            caput(magnet + ':set', value)



if __name__ == '__main__':
    GUI().master.mainloop()
