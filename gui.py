# gui.py
# Separate GUI file; original logic remains untouched in neg2cineon.py
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from neg2cineon import process_negative_to_cineon


def main():
    root = tk.Tk()
    root.title("RAW to Cineon Converter GUI")
    root.geometry("600x400")

    # File selection frame
    frame_files = tk.Frame(root)
    frame_files.pack(fill=tk.BOTH, expand=True)
    listbox = tk.Listbox(frame_files, selectmode=tk.MULTIPLE)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(frame_files, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # Control panel
    ctrl = tk.Frame(root)
    ctrl.pack(fill=tk.X, pady=5)

    btn_add = tk.Button(ctrl, text="Add RAW", command=lambda: add_files(listbox))
    btn_add.pack(side=tk.LEFT, padx=5)
    btn_remove = tk.Button(ctrl, text="Remove", command=lambda: remove_selected(listbox))
    btn_remove.pack(side=tk.LEFT, padx=5)

    exposure_var = tk.DoubleVar(value=1.0)
    tk.Label(ctrl, text="Exposure").pack(side=tk.LEFT)
    tk.Scale(ctrl, variable=exposure_var, from_=0.1, to=5.0, resolution=0.1,
             orient=tk.HORIZONTAL).pack(side=tk.LEFT, padx=5)

    color_var = tk.StringVar(value="ProPhoto")
    tk.Label(ctrl, text="Color Space").pack(side=tk.LEFT)
    tk.OptionMenu(ctrl, color_var, *["raw","sRGB","Adobe","Wide","ProPhoto","XYZ","ACES","P3D65","Rec2020"]).pack(side=tk.LEFT, padx=5)

    wb_var = tk.BooleanVar()
    tk.Checkbutton(ctrl, text="Pick WB", variable=wb_var).pack(side=tk.LEFT, padx=5)

    btn_convert = tk.Button(ctrl, text="Convert", command=lambda: convert(listbox, exposure_var, color_var, wb_var))
    btn_convert.pack(side=tk.RIGHT, padx=5)

    # Log output
    log_frame = tk.Frame(root)
    log_frame.pack(fill=tk.BOTH, expand=True)
    log_text = tk.Text(log_frame, height=8)
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    log_scroll = tk.Scrollbar(log_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    log_text.config(yscrollcommand=log_scroll.set)

    def log(msg):
        log_text.insert(tk.END, msg + "\n")
        log_text.see(tk.END)

    def add_files(lb):
        files = filedialog.askopenfilenames(
            title="Select RAW files",
            filetypes=[("RAW", "*.CR2 *.NEF *.ARW *.RAF *.DNG")]
        )
        for f in files:
            if f not in lb.get(0, tk.END):
                lb.insert(tk.END, f)

    def remove_selected(lb):
        for i in reversed(lb.curselection()):
            lb.delete(i)

    def convert(lb, exp_var, col_var, wb_var):
        items = lb.get(0, tk.END)
        if not items:
            messagebox.showwarning("No files", "Please add RAW files first.")
            return
        paths = [Path(p) for p in items]
        exp = exp_var.get()
        cs = col_var.get()
        pick = wb_var.get()
        log(f"Processing {len(paths)} file(s): exposure={exp}, color_space={cs}, pick_wb={pick}")
        try:
            out = process_negative_to_cineon(paths, exposure=exp, color_space=cs, pick_white_balance=pick)
            log(f"Saved output: {out}")
            messagebox.showinfo("Success", f"Output saved to {out}")
        except Exception as e:
            log(f"Error: {e}")
            messagebox.showerror("Error", str(e))

    root.mainloop()


if __name__ == "__main__":
    main()
