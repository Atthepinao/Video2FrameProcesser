import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import shutil
import threading
import time
import json
from PIL import Image, ImageTk, ImageDraw, ImageOps

# 获取资源文件的正确路径（支持打包后的环境）
def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和PyInstaller打包后的环境"""
    try:
        # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境下使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# 获取exe所在目录（用于输出文件）
def get_executable_dir():
    """获取exe文件所在的目录，兼容开发环境和打包后的环境"""
    if getattr(sys, 'frozen', False):
        # 打包后的环境：返回exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境：返回脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))

# --- Global Settings and Defaults ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "photoshop_exe": r"C:\Program Files\Adobe\Adobe Photoshop 2025\Photoshop.exe",
    "language": "zh",
    "frame_step": "3",
    "crop_w": "256",
    "crop_h": "256",
    "final_w": "128",
    "final_h": "128",
    "geometry": "1000x750",
    "clean_temp_files": False
}

# --- Language and Settings Loaders ---
def load_settings():
    """Loads settings, and if the file is missing or incomplete, complements it with default values."""
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            loaded_settings = json.load(f)
        
        # Key Fix: Ensure all default keys exist, add them if missing.
        for key, value in DEFAULT_SETTINGS.items():
            if key not in loaded_settings:
                loaded_settings[key] = value
        
        return loaded_settings
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f: json.dump(settings, f, indent=4)

def load_language(lang_code):
    lang_file = f"lang_{lang_code}.json"
    if not os.path.exists(lang_file): lang_file = "lang_en.json" # Fallback to English
    with open(lang_file, 'r', encoding='utf-8') as f: return json.load(f)

# --- Main Application ---
class App(tk.Tk):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.lang = load_language(self.settings.get("language", "zh"))
        
        self.title(self.lang.get("app_title", "Video Frame Processor"))
        self.geometry(self.settings.get("geometry", "1000x750"))

        self.video_queue = []
        self.mask_image = None
        self.is_updating_dimensions = False
        self.debounce_job = None
        self.stop_requested = threading.Event()
        
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_ui(self):
        # ... (Most of the UI code is identical to the previous version) ...
        for widget in self.winfo_children(): widget.destroy()
        self.create_menu()
        main_frame = ttk.Frame(self); main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1); main_frame.columnconfigure(1, weight=1); main_frame.rowconfigure(0, weight=1)
        
        left_frame = ttk.Frame(main_frame); left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_frame.rowconfigure(1, weight=1); left_frame.columnconfigure(0, weight=1)
        steps_frame = ttk.LabelFrame(left_frame, text=self.lang.get("process_steps_label")); steps_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        self.do_reduce_var = tk.BooleanVar(value=True); self.do_crop_var = tk.BooleanVar(value=True)
        self.do_photoshop_var = tk.BooleanVar(value=True); self.do_resize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(steps_frame, text=self.lang.get("step_reduce"), variable=self.do_reduce_var).pack(side="left", padx=5)
        ttk.Checkbutton(steps_frame, text=self.lang.get("step_crop"), variable=self.do_crop_var).pack(side="left", padx=5)
        ttk.Checkbutton(steps_frame, text=self.lang.get("step_photoshop"), variable=self.do_photoshop_var).pack(side="left", padx=5)
        ttk.Checkbutton(steps_frame, text=self.lang.get("step_resize"), variable=self.do_resize_var).pack(side="left", padx=5)
        tree_frame = ttk.Frame(left_frame); tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1); tree_frame.columnconfigure(0, weight=1)
        columns = ("out_folder", "prefix", "path", "crop_w", "crop_h", "offset_x", "offset_y")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("out_folder", text=self.lang.get("tree_col_out")); self.tree.heading("prefix", text=self.lang.get("tree_col_prefix")); self.tree.heading("path", text=self.lang.get("tree_col_video"))
        self.tree.heading("crop_w", text=self.lang.get("tree_col_w")); self.tree.heading("crop_h", text=self.lang.get("tree_col_h")); 
        self.tree.heading("offset_x", text=self.lang.get("tree_col_x")); self.tree.heading("offset_y", text=self.lang.get("tree_col_y"))
        self.tree.column("out_folder", width=100); self.tree.column("prefix", width=100); self.tree.column("path", width=150)
        self.tree.column("crop_w", width=40, anchor="center"); self.tree.column("crop_h", width=40, anchor="center")
        self.tree.column("offset_x", width=40, anchor="center"); self.tree.column("offset_y", width=40, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview); scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        right_frame = ttk.Frame(main_frame); right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1); right_frame.rowconfigure(1, weight=1)
        settings_frame = ttk.LabelFrame(right_frame, text=self.lang.get("frame_settings")); settings_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ff_frame = ttk.Frame(settings_frame); ff_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(ff_frame, text=self.lang.get("frame_step_label")).pack(side="left"); self.frame_step = tk.StringVar(value=self.settings.get("frame_step", "3"))
        ttk.Entry(ff_frame, textvariable=self.frame_step, width=5).pack(side="left", padx=5); ttk.Label(ff_frame, text=self.lang.get("frame_step_unit")).pack(side="left")

        out_frame = ttk.Frame(settings_frame); out_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(out_frame, text=self.lang.get("output_folder_label")).pack(side="left"); self.out_folder_var = tk.StringVar(value="")
        self.out_folder_entry = ttk.Entry(out_frame, textvariable=self.out_folder_var); self.out_folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.use_video_name_folder_var = tk.BooleanVar(value=True)
        self.use_video_name_folder_check = ttk.Checkbutton(out_frame, text=self.lang.get("use_video_name_checkbox"), variable=self.use_video_name_folder_var, command=self.toggle_out_folder_entry); self.use_video_name_folder_check.pack(side="left")

        p_frame = ttk.Frame(settings_frame); p_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(p_frame, text=self.lang.get("prefix_label")).pack(side="left"); self.prefix_var = tk.StringVar(value="frame")
        self.prefix_entry = ttk.Entry(p_frame, textvariable=self.prefix_var); self.prefix_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.use_video_name_prefix_var = tk.BooleanVar(value=False)
        self.use_video_name_prefix_check = ttk.Checkbutton(p_frame, text=self.lang.get("use_video_name_checkbox"), variable=self.use_video_name_prefix_var, command=self.toggle_prefix_entry); self.use_video_name_prefix_check.pack(side="left")

        c_frame = ttk.Frame(settings_frame); c_frame.pack(fill="x", padx=5, pady=2)
        self.crop_w = tk.StringVar(value=self.settings.get("crop_w", "256")); self.crop_h = tk.StringVar(value=self.settings.get("crop_h", "256")); self.offset_x = tk.StringVar(value="0"); self.offset_y = tk.StringVar(value="0")
        ttk.Label(c_frame, text=self.lang.get("crop_w_label")).pack(side="left"); ttk.Entry(c_frame, textvariable=self.crop_w, width=5).pack(side="left")
        ttk.Label(c_frame, text=self.lang.get("crop_h_label")).pack(side="left", padx=(10,0)); ttk.Entry(c_frame, textvariable=self.crop_h, width=5).pack(side="left")
        ttk.Label(c_frame, text=self.lang.get("offset_x_label")).pack(side="left", padx=(10,0)); ttk.Entry(c_frame, textvariable=self.offset_x, width=5).pack(side="left")
        ttk.Label(c_frame, text=self.lang.get("offset_y_label")).pack(side="left", padx=(10,0)); ttk.Entry(c_frame, textvariable=self.offset_y, width=5).pack(side="left")

        ar_frame = ttk.Frame(settings_frame); ar_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(ar_frame, text=self.lang.get("aspect_ratio_label")).pack(side="left"); self.aspect_ratio = tk.StringVar(value="1:1")
        ar_combo = ttk.Combobox(ar_frame, textvariable=self.aspect_ratio, values=[self.lang.get("aspect_ratio_free"), "1:1", "4:3", "16:9"], width=7)
        ar_combo.pack(side="left", padx=5); ar_combo.bind("<<ComboboxSelected>>", self.on_aspect_ratio_change)
        self.apply_button = ttk.Button(ar_frame, text=self.lang.get("apply_button"), command=self.apply_settings_to_selected); self.apply_button.pack(side="left", padx=10)

        resize_frame = ttk.Frame(settings_frame); resize_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(resize_frame, text=self.lang.get("output_res_label")).pack(side="left"); self.final_w = tk.StringVar(value=self.settings.get("final_w", "128")); self.final_h = tk.StringVar(value=self.settings.get("final_h", "128"))
        ttk.Label(resize_frame, text="W:").pack(side="left", padx=(10,0)); ttk.Entry(resize_frame, textvariable=self.final_w, width=5).pack(side="left")
        ttk.Label(resize_frame, text="H:").pack(side="left", padx=(10,0)); ttk.Entry(resize_frame, textvariable=self.final_h, width=5).pack(side="left")

        preview_controls_frame = ttk.Frame(settings_frame); preview_controls_frame.pack(fill="x", padx=5, pady=2)
        self.load_mask_button = ttk.Button(preview_controls_frame, text=self.lang.get("load_mask_button"), command=self.load_mask); self.load_mask_button.pack(side="left")
        self.preview_button = ttk.Button(preview_controls_frame, text=self.lang.get("preview_button"), command=self.generate_preview); self.preview_button.pack(side="right")

        self.preview_label = ttk.Label(right_frame, text=self.lang.get("preview_area_text"), anchor="center", background="gray"); self.preview_label.grid(row=1, column=0, sticky="nsew")

        button_frame = ttk.Frame(self); button_frame.pack(padx=10, pady=(0, 5), fill="x")
        self.add_button = ttk.Button(button_frame, text=self.lang.get("add_video_button"), command=self.add_videos); self.add_button.pack(side="left", padx=5)
        self.remove_button = ttk.Button(button_frame, text=self.lang.get("remove_video_button"), command=self.remove_selected); self.remove_button.pack(side="left", padx=5)
        
        self.process_control_frame = ttk.Frame(button_frame)
        self.process_control_frame.pack(side="right")
        self.start_button = ttk.Button(self.process_control_frame, text=self.lang.get("start_button"), command=self.start_processing_thread); self.start_button.pack(side="right", padx=5)
        self.stop_button = ttk.Button(self.process_control_frame, text=self.lang.get("stop_button"), command=self.request_stop);
        
        # 日志和进度区域
        log_frame = ttk.LabelFrame(self, text=self.lang.get("log_frame_title")); log_frame.pack(padx=10, pady=(0, 10), fill="both", expand=False)
        log_frame.rowconfigure(0, weight=1); log_frame.columnconfigure(0, weight=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(log_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        
        # 进度文本
        self.progress_label = ttk.Label(log_frame, text=self.lang.get("status_ready"), anchor="w")
        self.progress_label.grid(row=1, column=0, sticky="ew", padx=5, pady=(2, 0))
        
        # 日志文本框
        log_text_frame = ttk.Frame(log_frame); log_text_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        log_text_frame.rowconfigure(0, weight=1); log_text_frame.columnconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_text_frame, height=6, wrap="word", state="disabled", bg="#f0f0f0")
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient="vertical", command=self.log_text.yview)
        log_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.crop_w.trace_add("write", self.schedule_preview); self.crop_h.trace_add("write", self.schedule_preview)
        self.offset_x.trace_add("write", self.schedule_preview); self.offset_y.trace_add("write", self.schedule_preview)
        self.crop_w.trace_add("write", self.on_width_change); self.crop_h.trace_add("write", self.on_height_change)
        
        self.toggle_prefix_entry(); self.toggle_out_folder_entry()
    
    # --- METHOD DEFINITIONS ---
    
    def log(self, message):
        """在日志区域添加消息"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.update_idletasks()
    
    def update_progress(self, current, total, message=""):
        """更新进度条和进度文本"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        if message:
            self.progress_label.config(text=message)
        self.update_idletasks()

    def create_menu(self):
        menubar = tk.Menu(self); self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label=self.lang.get("menu_settings"), command=self.open_settings_window)
        file_menu.add_separator(); file_menu.add_command(label=self.lang.get("menu_exit"), command=self.on_closing)
        menubar.add_cascade(label=self.lang.get("menu_file"), menu=file_menu)

    def open_settings_window(self):
        settings_window = tk.Toplevel(self); settings_window.title(self.lang.get("settings_title")); settings_window.geometry("600x340")
        
        lang_frame = ttk.Frame(settings_window); lang_frame.pack(fill="x", padx=10, pady=5)
        ttk.Label(lang_frame, text=self.lang.get("lang_label")).pack(side="left")
        lang_var = tk.StringVar(value=self.settings.get("language", "zh"))
        lang_combo = ttk.Combobox(lang_frame, textvariable=lang_var, values=["zh", "en"], width=10)
        lang_combo.pack(side="left", padx=5)

        ps_frame = ttk.LabelFrame(settings_window, text=self.lang.get("ps_path_label")); ps_frame.pack(fill="x", padx=10, pady=5)
        ps_path_var = tk.StringVar(value=self.settings.get("photoshop_exe"))
        ttk.Entry(ps_frame, textvariable=ps_path_var).pack(side="left", fill="x", expand=True, padx=5)
        def browse_ps():
            path = filedialog.askopenfilename(title=self.lang.get("browse_ps_title"), filetypes=[(self.lang.get("file_type_executable"), "*.exe")])
            if path: ps_path_var.set(path)
        ttk.Button(ps_frame, text=self.lang.get("browse_button"), command=browse_ps).pack(side="left", padx=5)

        defaults_frame = ttk.LabelFrame(settings_window, text=self.lang.get("defaults_frame_title")); defaults_frame.pack(fill="x", padx=10, pady=5)
        fs_frame = ttk.Frame(defaults_frame); fs_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(fs_frame, text=self.lang.get("default_step_label")).pack(side="left", anchor="w")
        frame_step_var = tk.StringVar(value=self.settings.get("frame_step", "3")); ttk.Entry(fs_frame, textvariable=frame_step_var, width=10).pack(side="left", padx=10)
        
        crop_frame = ttk.Frame(defaults_frame); crop_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(crop_frame, text=self.lang.get("default_crop_label")).pack(side="left", anchor="w")
        crop_w_var = tk.StringVar(value=self.settings.get("crop_w", "256")); crop_h_var = tk.StringVar(value=self.settings.get("crop_h", "256"))
        ttk.Label(crop_frame, text="W:").pack(side="left", padx=(10, 0)); ttk.Entry(crop_frame, textvariable=crop_w_var, width=5).pack(side="left")
        ttk.Label(crop_frame, text="H:").pack(side="left", padx=(10, 0)); ttk.Entry(crop_frame, textvariable=crop_h_var, width=5).pack(side="left")
        
        res_frame = ttk.Frame(defaults_frame); res_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(res_frame, text=self.lang.get("default_res_label")).pack(side="left", anchor="w")
        final_w_var = tk.StringVar(value=self.settings.get("final_w", "128")); final_h_var = tk.StringVar(value=self.settings.get("final_h", "128"))
        ttk.Label(res_frame, text="W:").pack(side="left", padx=(10, 0)); ttk.Entry(res_frame, textvariable=final_w_var, width=5).pack(side="left")
        ttk.Label(res_frame, text="H:").pack(side="left", padx=(10, 0)); ttk.Entry(res_frame, textvariable=final_h_var, width=5).pack(side="left")
        
        # 清理临时文件选项
        clean_frame = ttk.Frame(settings_window); clean_frame.pack(fill="x", padx=10, pady=5)
        clean_temp_var = tk.BooleanVar(value=self.settings.get("clean_temp_files", False))
        ttk.Checkbutton(clean_frame, text=self.lang.get("clean_temp_files_label"), variable=clean_temp_var).pack(side="left")

        def save_and_close():
            current_lang = self.settings.get("language", "zh"); new_lang = lang_var.get()
            self.settings["photoshop_exe"] = ps_path_var.get()
            self.settings["frame_step"] = frame_step_var.get()
            self.settings["crop_w"] = crop_w_var.get()
            self.settings["crop_h"] = crop_h_var.get()
            self.settings["final_w"] = final_w_var.get()
            self.settings["final_h"] = final_h_var.get()
            self.settings["clean_temp_files"] = clean_temp_var.get()
            
            if current_lang != new_lang:
                self.settings["language"] = new_lang
                save_settings(self.settings)
                messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_language_changed"), parent=settings_window)
            else:
                save_settings(self.settings)
                messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_settings_saved"), parent=settings_window)
            settings_window.destroy()
            
        ttk.Button(settings_window, text=self.lang.get("save_close_button"), command=save_and_close).pack(pady=10)

    def on_closing(self):
        self.settings["geometry"] = self.geometry()
        save_settings(self.settings)
        self.destroy()

    # =================================================================
    # 新增: 重新加入被遗漏的 toggle_out_folder_entry 函数
    # =================================================================
    def toggle_out_folder_entry(self):
        if self.use_video_name_folder_var.get():
            self.out_folder_entry.config(state="disabled")
        else:
            self.out_folder_entry.config(state="normal")
            
    def toggle_prefix_entry(self):
        if self.use_video_name_prefix_var.get():
            self.prefix_entry.config(state="disabled")
        else:
            self.prefix_entry.config(state="normal")
    
    def schedule_preview(self, *args):
        if self.debounce_job:
            self.after_cancel(self.debounce_job)
        self.debounce_job = self.after(500, self.generate_preview)

    def add_videos(self):
        video_paths = filedialog.askopenfilenames(title=self.lang.get("add_video_button"), filetypes=[(self.lang.get("file_type_video"), "*.mp4 *.mov *.avi"), (self.lang.get("file_type_all"), "*.*")])
        # 从设置中获取默认裁剪大小
        default_crop_w = int(self.settings.get("crop_w", "256"))
        default_crop_h = int(self.settings.get("crop_h", "256"))
        for path in video_paths:
            base_name = os.path.splitext(os.path.basename(path))[0]
            video_data = {"out_folder": base_name, "prefix": "frame", "path": path, "crop_w": default_crop_w, "crop_h": default_crop_h, "offset_x": 0, "offset_y": 0}
            self.video_queue.append(video_data)
            self.tree.insert("", tk.END, values=(base_name, "frame", os.path.basename(path), default_crop_w, default_crop_h, 0, 0))

    def remove_selected(self):
        selected_items = self.tree.selection()
        indices_to_remove = [self.tree.index(item) for item in selected_items]
        indices_to_remove.sort(reverse=True)
        for index in indices_to_remove: del self.video_queue[index]
        for item in selected_items: self.tree.delete(item)

    def apply_settings_to_selected(self):
        selected_items = self.tree.selection()
        if not selected_items: messagebox.showwarning(self.lang.get("msg_warning"), self.lang.get("msg_select_video_first")); return
        try:
            w = int(self.crop_w.get()); h = int(self.crop_h.get()); ox = int(self.offset_x.get()); oy = int(self.offset_y.get())
        except ValueError: messagebox.showwarning(self.lang.get("msg_warning"), self.lang.get("msg_values_must_be_int")); return
            
        for item in selected_items:
            index = self.tree.index(item)
            if self.use_video_name_folder_var.get():
                video_path = self.video_queue[index]["path"]; out_folder = os.path.splitext(os.path.basename(video_path))[0]
            else:
                out_folder = self.out_folder_var.get(); 
                if not out_folder: out_folder = "custom_output"
            if self.use_video_name_prefix_var.get():
                video_path = self.video_queue[index]["path"]; prefix = os.path.splitext(os.path.basename(video_path))[0]
            else:
                prefix = self.prefix_var.get()
            self.video_queue[index].update({"out_folder": out_folder, "prefix": prefix, "crop_w": w, "crop_h": h, "offset_x": ox, "offset_y": oy})
            self.tree.item(item, values=(out_folder, prefix, os.path.basename(self.video_queue[index]["path"]), w, h, ox, oy))

    def on_aspect_ratio_change(self, event=None): self.on_width_change()
    def on_width_change(self, *args):
        if self.is_updating_dimensions: return
        self.is_updating_dimensions = True
        try:
            w = int(self.crop_w.get()); ratio = self.aspect_ratio.get()
            if ratio == "1:1": self.crop_h.set(str(w))
            elif ratio == "4:3": self.crop_h.set(str(int(w * 3 / 4)))
            elif ratio == "16:9": self.crop_h.set(str(int(w * 9 / 16)))
        except (ValueError, tk.TclError): pass
        finally: self.is_updating_dimensions = False

    def on_height_change(self, *args):
        if self.is_updating_dimensions: return
        self.is_updating_dimensions = True
        try:
            h = int(self.crop_h.get()); ratio = self.aspect_ratio.get()
            if ratio == "1:1": self.crop_w.set(str(h))
            elif ratio == "4:3": self.crop_w.set(str(int(h * 4 / 3)))
            elif ratio == "16:9": self.crop_w.set(str(int(h * 16 / 9)))
        except (ValueError, tk.TclError): pass
        finally: self.is_updating_dimensions = False

    def load_mask(self):
        mask_path = filedialog.askopenfilename(title=self.lang.get("load_mask_button"), filetypes=[(self.lang.get("file_type_png"), "*.png")])
        if not mask_path: return
        self.mask_image = Image.open(mask_path).convert("RGBA"); messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_mask_loaded"))

    def generate_preview(self):
        selected_items = self.tree.selection()
        if not selected_items:
            if self.debounce_job is None: messagebox.showwarning(self.lang.get("msg_warning"), self.lang.get("msg_select_video_first"))
            return
        index = self.tree.index(selected_items[0]); video_path = self.video_queue[index]["path"]
        try:
            crop_w = int(self.crop_w.get()); crop_h = int(self.crop_h.get()); offset_x = int(self.offset_x.get()); offset_y = int(self.offset_y.get())
        except ValueError:
            if self.debounce_job is not None: return
            messagebox.showwarning(self.lang.get("msg_warning"), self.lang.get("msg_values_must_be_int")); return
        
        # 使用exe所在目录存放预览文件
        preview_file = os.path.join(get_executable_dir(), "_preview.png")
        
        # 只在预览文件不存在或视频路径改变时才重新提取帧
        if not hasattr(self, '_last_preview_video') or self._last_preview_video != video_path or not os.path.exists(preview_file):
            try: 
                subprocess.run(['ffmpeg', '-i', video_path, '-vframes', '1', '-y', preview_file], check=True, **self.get_subprocess_args())
                self._last_preview_video = video_path
            except: return
        
        with Image.open(preview_file) as bg_img:
            bg_img = bg_img.convert("RGBA"); w, h = bg_img.size
            overlay_canvas = Image.new("RGBA", bg_img.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay_canvas)
            left = (w - crop_w) / 2 + offset_x; top = (h - crop_h) / 2 + offset_y; right = left + crop_w; bottom = top + crop_h
            if self.mask_image:
                mask_resized = self.mask_image.resize((crop_w, crop_h), Image.Resampling.LANCZOS)
                paste_x = int(left); paste_y = int(top)
                overlay_canvas.paste(mask_resized, (paste_x, paste_y), mask_resized)
            else:
                draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 128)); draw.rectangle([left, top, right, bottom], fill=(0, 0, 0, 0))
                draw.rectangle([left, top, right, bottom], outline="red", width=2)
            final_img = Image.alpha_composite(bg_img, overlay_canvas)
            final_img.thumbnail((self.preview_label.winfo_width(), self.preview_label.winfo_height()))
            self.preview_image = ImageTk.PhotoImage(final_img); self.preview_label.config(image=self.preview_image, text="")
        self.debounce_job = None
        
    def start_processing_thread(self):
        processing_thread = threading.Thread(target=self.process_queue, daemon=True); processing_thread.start()

    def process_queue(self):
        self.stop_requested.clear()
        self.toggle_buttons(enabled=False)
        if not self.video_queue: 
            messagebox.showinfo(self.lang.get("msg_info"), self.lang.get("msg_queue_empty"))
            self.toggle_buttons(enabled=True)
            return
        
        total_videos = len(self.video_queue)
        self.log(self.lang.get("log_start_processing").format(total=total_videos))
        
        try:
            for idx, video_data in enumerate(self.video_queue, 1):
                if self.stop_requested.is_set():
                    self.log(self.lang.get("msg_task_interrupted"))
                    messagebox.showwarning(self.lang.get("msg_warning"), self.lang.get("msg_task_interrupted"))
                    break
                
                self.log(f"\n{'='*50}")
                self.log(self.lang.get("log_processing_video").format(current=idx, total=total_videos, name=os.path.basename(video_data['path'])))
                self.log(f"{'='*50}")
                self.process_video(video_data)
            
            if not self.stop_requested.is_set():
                self.log("\n" + self.lang.get("log_all_complete"))
                self.update_progress(100, 100, self.lang.get("status_complete"))
                messagebox.showinfo(self.lang.get("msg_success"), self.lang.get("msg_all_done"))
        except Exception as e: 
            self.log(self.lang.get("log_error").format(error=str(e)))
            messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_process_error").format(e=e))
        finally: 
            self.toggle_buttons(enabled=True)
            if not self.stop_requested.is_set():
                self.update_progress(0, 100, self.lang.get("status_ready"))

    def toggle_buttons(self, enabled=True):
        state = "normal" if enabled else "disabled"
        if enabled:
            self.start_button.pack(side="right", padx=5); self.stop_button.pack_forget()
        else:
            self.start_button.pack_forget(); self.stop_button.config(text="停止", state="normal"); self.stop_button.pack(side="right", padx=5)
        for btn in [self.add_button, self.remove_button, self.preview_button, self.apply_button, self.load_mask_button, self.use_video_name_prefix_check, self.use_video_name_folder_check]: btn.config(state=state)

    def get_subprocess_args(self):
        """获取subprocess参数，在Windows下隐藏命令行窗口"""
        args = {"capture_output": True, "text": True, "encoding": "utf-8"}
        # 在Windows下隐藏命令行窗口
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            args["startupinfo"] = startupinfo
            args["creationflags"] = subprocess.CREATE_NO_WINDOW
        return args
    
    def create_jsx_for_run(self, template_path, run_path, input_dir, output_dir, prefix):
        try:
            with open(template_path, 'r', encoding='utf-8') as f: template_content = f.read()
            content = template_content.replace("PLACEHOLDER_PREFIX", prefix)
            content = content.replace("PLACEHOLDER_INPUT", input_dir.replace(os.sep, "/"))
            content = content.replace("PLACEHOLDER_OUTPUT", output_dir.replace(os.sep, "/"))
            with open(run_path, 'w', encoding='utf-8') as f: f.write(content)
        except FileNotFoundError: messagebox.showerror(self.lang.get("msg_error"), self.lang.get("msg_jsx_not_found")); raise

    def request_stop(self):
        self.log(self.lang.get("msg_user_stop"))
        self.stop_requested.set()
        self.stop_button.config(text=self.lang.get("status_processing") + "...", state="disabled")

    def process_video(self, video_data):
        video_path = video_data["path"]; offset_x = video_data["offset_x"]; offset_y = video_data["offset_y"]
        crop_w = video_data["crop_w"]; crop_h = video_data["crop_h"]; prefix = video_data["prefix"]; out_folder = video_data["out_folder"]
        target_w = int(self.final_w.get()); target_h = int(self.final_h.get()); frame_step = int(self.frame_step.get())
        
        self.log(self.lang.get("log_start_video").format(name=os.path.basename(video_path))); project_dir = get_executable_dir(); 
        main_output_dir = os.path.join(project_dir, "output"); os.makedirs(main_output_dir, exist_ok=True)
        video_specific_dir = os.path.join(main_output_dir, out_folder); 
        if os.path.exists(video_specific_dir): shutil.rmtree(video_specific_dir); os.makedirs(video_specific_dir)
        
        current_path = video_path
        
        if self.do_reduce_var.get():
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step1_reduce").format(step=frame_step))
            self.update_progress(1, 4, self.lang.get("progress_step1").format(step=frame_step))
            step1_dir = os.path.join(video_specific_dir, "1_reduced_frames"); os.makedirs(step1_dir)
            ffmpeg_filter = f"select='not(mod(n,{frame_step}))',setpts=N/FRAME_RATE/TB"
            subprocess.run(['ffmpeg', '-i', current_path, '-vf', ffmpeg_filter, '-vsync', 'vfr', f'{step1_dir}/frame_%04d.png'], check=True, **self.get_subprocess_args())
            current_path = step1_dir
        else:
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step1_all"))
            self.update_progress(1, 4, self.lang.get("progress_step1_all"))
            step1_dir = os.path.join(video_specific_dir, "1_all_frames"); os.makedirs(step1_dir)
            subprocess.run(['ffmpeg', '-i', current_path, f'{step1_dir}/frame_%04d.png'], check=True, **self.get_subprocess_args())
            current_path = step1_dir
        
        if self.do_crop_var.get():
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step2_crop"))
            self.update_progress(2, 4, self.lang.get("progress_step2"))
            step2_dir = os.path.join(video_specific_dir, "2_cropped_frames"); os.makedirs(step2_dir)
            files = [f for f in os.listdir(current_path) if f.endswith(".png")]
            for idx, filename in enumerate(files, 1):
                if self.stop_requested.is_set(): return
                input_file = os.path.join(current_path, filename); output_file = os.path.join(step2_dir, filename)
                # 使用 PIL 进行裁剪，支持超出边界时用透明像素填充
                with Image.open(input_file) as img:
                    img_w, img_h = img.size
                    # 计算裁剪框在原图中的位置
                    left = (img_w - crop_w) // 2 + offset_x
                    top = (img_h - crop_h) // 2 + offset_y
                    right = left + crop_w
                    bottom = top + crop_h
                    
                    # 创建一个透明背景的新图像
                    if img.mode == 'RGBA':
                        result = Image.new('RGBA', (crop_w, crop_h), (0, 0, 0, 0))
                    else:
                        result = Image.new('RGBA', (crop_w, crop_h), (0, 0, 0, 0))
                        img = img.convert('RGBA')
                    
                    # 计算原图在结果图中的粘贴位置
                    paste_left = max(0, -left)
                    paste_top = max(0, -top)
                    
                    # 计算从原图中裁剪的区域
                    crop_left = max(0, left)
                    crop_top = max(0, top)
                    crop_right = min(img_w, right)
                    crop_bottom = min(img_h, bottom)
                    
                    # 如果裁剪区域有效，则裁剪并粘贴
                    if crop_right > crop_left and crop_bottom > crop_top:
                        cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
                        result.paste(cropped, (paste_left, paste_top))
                    
                    result.save(output_file, 'PNG')
                
                if idx % 10 == 0:
                    self.update_progress(2, 4, self.lang.get("progress_step2_detail").format(current=idx, total=len(files)))
            current_path = step2_dir

        if self.do_photoshop_var.get():
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step3_ps"))
            self.update_progress(3, 4, self.lang.get("progress_step3"))
            step3_dir = os.path.join(video_specific_dir, "3_transparent_temp"); os.makedirs(step3_dir)
            jsx_template_path = resource_path('run_action_template.jsx'); jsx_run_path = os.path.join(project_dir, '_tmp_run_action.jsx')
            signal_file = os.path.join(project_dir, 'photoshop_done.tmp'); 
            if os.path.exists(signal_file): os.remove(signal_file)
            self.create_jsx_for_run(jsx_template_path, jsx_run_path, current_path, step3_dir, prefix)
            # 启动Photoshop时也隐藏窗口
            popen_args = {}
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                popen_args["startupinfo"] = startupinfo
                popen_args["creationflags"] = subprocess.CREATE_NO_WINDOW
            ps_process = subprocess.Popen([self.settings['photoshop_exe'], jsx_run_path], **popen_args)
            self.log(self.lang.get("log_step3_waiting"))
            wait_count = 0
            while not os.path.exists(signal_file):
                if self.stop_requested.is_set():
                    self.log(self.lang.get("log_step3_stop"))
                    ps_process.terminate()
                    break
                time.sleep(2)
                wait_count += 1
                if wait_count % 5 == 0:
                    self.update_progress(3, 4, self.lang.get("progress_step3_detail").format(seconds=wait_count*2))
                if ps_process.poll() is not None: raise RuntimeError(self.lang.get("msg_ps_terminated").format(video_name=out_folder))
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step3_done")); os.remove(signal_file)
            ps_process.terminate(); ps_process.wait(timeout=5); self.log(self.lang.get("log_step3_closed"))
            current_path = step3_dir

        if self.do_resize_var.get():
            if self.stop_requested.is_set(): return
            self.log(self.lang.get("log_step4_resize").format(w=target_w, h=target_h))
            self.update_progress(4, 4, self.lang.get("progress_step4"))
            step4_dir = os.path.join(video_specific_dir, "4_final_output"); os.makedirs(step4_dir)
            files = [f for f in os.listdir(current_path) if f.endswith(".png")]
            for idx, filename in enumerate(files, 1):
                if self.stop_requested.is_set(): return
                input_file = os.path.join(current_path, filename); output_file = os.path.join(step4_dir, filename)
                subprocess.run(['magick', input_file, '-resize', f'{target_w}x{target_h}', output_file], check=True, **self.get_subprocess_args())
                if idx % 10 == 0:
                    self.update_progress(4, 4, self.lang.get("progress_step4_detail").format(current=idx, total=len(files)))
            current_path = step4_dir

        self.log(self.lang.get("log_video_complete").format(name=os.path.basename(video_path), path=current_path))
        
        # 如果启用了清理临时文件选项
        if self.settings.get("clean_temp_files", False):
            self.log(self.lang.get("log_cleaning_temp"))
            
            # 将最终输出文件移动到视频文件夹根目录
            final_output_root = video_specific_dir
            if current_path != final_output_root:
                # 移动所有最终输出文件到根目录
                for filename in os.listdir(current_path):
                    if filename.endswith(".png"):
                        src = os.path.join(current_path, filename)
                        dst = os.path.join(final_output_root, filename)
                        shutil.move(src, dst)
                
                self.log(self.lang.get("log_moved_final").format(path=final_output_root))
            
            # 删除所有临时文件夹
            temp_dirs = [
                os.path.join(video_specific_dir, "1_reduced_frames"),
                os.path.join(video_specific_dir, "1_all_frames"),
                os.path.join(video_specific_dir, "2_cropped_frames"),
                os.path.join(video_specific_dir, "3_transparent_temp"),
                os.path.join(video_specific_dir, "4_final_output")
            ]
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
            
            self.log(self.lang.get("log_cleaned_temp"))

if __name__ == "__main__":
    app_settings = load_settings()
    app = App(app_settings)
    app.mainloop()