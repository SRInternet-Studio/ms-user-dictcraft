import os, sys, ctypes, json
import darkdetect
import pandas as pd
from datetime import datetime
from lib.user_dict import UserDict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO if getattr(sys, 'frozen', False) else logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

default_config = {
    "enable_high_dpi_awareness": False,
    "new_file_name": "new.dat",
    "window_size": "800x600",
    "dark_mode": "auto"
}

def load_config():
    global default_config
    config_path = 'config.json'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            default_config = config
        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
    else:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        logger.info("已创建默认配置文件: config.json")

def enable_high_dpi_awareness():
    if sys.platform == 'win32':
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # 回退方案：兼容 Windows 7/8 的旧版 DPI Aware API
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

load_config()
if default_config.get("enable_high_dpi_awareness", False): enable_high_dpi_awareness()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk

class UserDictGUI:
    def __init__(self, root: tk.Tk):
        global default_config
        
        self.root = root
        self.root.title("MS User DictCraft")
        self.root.resizable(True, True)
        
        if sys.platform == 'win32' and default_config.get("enable_high_dpi_awareness", False):
            try: ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.windll.user32.GetParent(self.root.winfo_id()), 
                    2, ctypes.byref(ctypes.c_int(1)), 4
                )
            except: pass
        
        self.bg_color = "#f5f5f5"
        self.btn_color = "#4a90e2"
        self.text_color = "#333333"
        self.frame_color = "#ffffff"
        
        self.title_font = ("Helvetica", 16, "bold")
        self.label_font = ("Helvetica", 10)
        self.btn_font = ("Helvetica", 10, "bold")
        
        self.root.configure(bg=self.bg_color)
        
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
      
        self.style = ttk.Style()
        
        self.font_path = os.path.join(os.path.dirname(__file__), 'sources', 'HarmonyOS_Sans_SC_Regular.ttf')
        try:
            import tkinter.font as tkfont
            from tkinter import font
            font.families()  # 刷新字体列表
            self.custom_font = tkfont.Font(family="HarmonyOS Sans SC", size=10)
            self.title_font = tkfont.Font(family="HarmonyOS Sans SC", size=16, weight="bold")
            self.label_font = tkfont.Font(family="HarmonyOS Sans SC", size=10)
            self.btn_font = tkfont.Font(family="HarmonyOS Sans SC", size=10, weight="bold")
            self.style.configure(".", font=(self.custom_font.cget("family"), self.custom_font.cget("size")))
            self.style.configure("TLabel", font=(self.label_font.cget("family"), self.label_font.cget("size")))
            self.style.configure("TButton", font=(self.btn_font.cget("family"), self.btn_font.cget("size")))
            self.style.configure("TEntry", font=(self.custom_font.cget("family"), self.custom_font.cget("size")))
        except Exception as e:
            logger.error(f"加载字体失败: {e}")
            self.custom_font = None
            self.title_font = None
            self.label_font = None
            self.btn_font = None
        
        self.style.configure("Accent.TButton", background=self.btn_color, foreground="black")
        self.style.map("Accent.TButton", background=[("active", "#357abd")])
        
        self.style.configure("TLabelframe", font=(self.label_font.cget("family"), self.label_font.cget("size")) if self.label_font else None)
        self.style.configure("TLabelframe.Label", font=(self.label_font.cget("family"), self.label_font.cget("size")) if self.label_font else None)
        
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        self.generate_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.generate_tab, text="生成词典")
        
        self.editor_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_tab, text="词条编辑")
        
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text="批量生成")
        
        self.about_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.about_tab, text="关于")
        
        self.init_generate_tab()
        self.init_editor_tab()
        self.init_batch_tab()
        self.init_about_tab()
    
    def create_scrollable_frame(self, parent):
        touch_state = {"y": 0, "is_dragging": False}
        canvas = tk.Canvas(parent, bg=self.bg_color, highlightthickness=0)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollable_frame = ttk.Frame(canvas, padding="20")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        def on_configure(event: tk.Event):
            req_height = scrollable_frame.winfo_reqheight()
            if event.height > req_height:
                canvas.itemconfig(canvas_frame_id, width=event.width, height=event.height)
            else:
                canvas.itemconfig(canvas_frame_id, width=event.width)
            
        def _on_mousewheel(event: tk.Event):
            if str(canvas) not in str(event.widget): return
            if isinstance(event.widget, (tk.Text, ttk.Treeview, ttk.Scrollbar, tk.Scrollbar)): return
            logger.info(f"滚动事件: {event.delta}")

            if sys.platform == "darwin":  # macOS
                canvas.yview_scroll(int(-1 * event.delta), "units")
            else:  # Windows
                logger.info(f"Windows 滚轮事件: {event.delta}")
                # canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                if event.delta > 0:
                    canvas.yview_scroll(-1, "units") # 向上滚
                elif event.delta < 0:
                    canvas.yview_scroll(1, "units")  # 向下滚
                    
        def _on_touch_press(event: tk.Event):
            if str(canvas) not in str(event.widget): return
            try:
                if isinstance(event.widget, (tk.Text, ttk.Treeview, ttk.Scrollbar, tk.Scrollbar, ttk.Entry, tk.Entry, ttk.Combobox, ttk.Button, tk.Button)):
                    touch_state["is_dragging"] = False
                    return
            except Exception:
                pass

            touch_state["is_dragging"] = True
            touch_state["y"] = event.y_root
                
        def _on_linux_scroll_up(event: tk.Event):
            if str(canvas) not in str(event.widget): return 
            if not isinstance(event.widget, (tk.Text, ttk.Treeview, ttk.Scrollbar, tk.Scrollbar)):
                logger.info(f"Linux 滚轮事件: {event.delta}")
                canvas.yview_scroll(-1, "units")
                
        def _on_linux_scroll_down(event: tk.Event): 
            if str(canvas) not in str(event.widget): return 
            if not isinstance(event.widget, (tk.Text, ttk.Treeview, ttk.Scrollbar, tk.Scrollbar)):
                logger.info(f"Linux 滚轮事件: {event.delta}")
                canvas.yview_scroll(1, "units")
                
        def _on_touch_drag(event: tk.Event):
            if not touch_state["is_dragging"] or str(canvas) not in str(event.widget): return

            delta_y = touch_state["y"] - event.y_root
            if delta_y == 0:
                return

            bbox = canvas.bbox("all")
            if not bbox:
                return
                
            total_height = bbox[3] - bbox[1]
            if total_height <= 0:
                return

            fraction_delta = delta_y / total_height
            current_fraction = canvas.yview()[0]
            canvas.yview_moveto(current_fraction + fraction_delta)
            touch_state["y"] = event.y_root
        
        canvas_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)
        canvas.bind("<Configure>", on_configure)
        self.root.bind_all("<MouseWheel>", _on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", _on_linux_scroll_up, add="+")
        self.root.bind_all("<Button-5>", _on_linux_scroll_down, add="+")
        self.root.bind_all("<ButtonPress-1>", _on_touch_press, add="+")
        self.root.bind_all("<B1-Motion>", _on_touch_drag, add="+")
        
        canvas.configure(background=self.bg_color, highlightthickness=0)
        return scrollable_frame
        
    def init_generate_tab(self):
        global default_config
        scrollable_frame = self.create_scrollable_frame(self.generate_tab)
        
        self.title_label = ttk.Label(scrollable_frame, text="MS User DictCraft", font=self.title_font)
        self.title_label.pack(pady=(0, 20))
        
        self.input_frame = ttk.LabelFrame(scrollable_frame, text="输入设置", padding="10")
        self.input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.input_label = ttk.Label(self.input_frame, text="现有DAT文件（可选）:", font=self.label_font)
        self.input_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(self.input_frame, textvariable=self.input_var, width=40)
        self.input_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.input_btn = ttk.Button(self.input_frame, text="浏览", command=self.browse_input)
        self.input_btn.grid(row=0, column=2, pady=5)
        self.input_frame.columnconfigure(1, weight=1)
        
        self.output_frame = ttk.LabelFrame(scrollable_frame, text="输出设置", padding="10")
        self.output_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.output_label = ttk.Label(self.output_frame, text="输出DAT文件:", font=self.label_font)
        self.output_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.output_var = tk.StringVar(value=default_config.get("new_file_name", "new.dat"))
        self.output_entry = ttk.Entry(self.output_frame, textvariable=self.output_var, width=40)
        self.output_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.output_btn = ttk.Button(self.output_frame, text="浏览", command=self.browse_output)
        self.output_btn.grid(row=0, column=2, pady=5)
        self.output_frame.columnconfigure(1, weight=1)
        
        self.generate_btn = ttk.Button(scrollable_frame, text="生成词典", command=self.generate_dict, style="Accent.TButton")
        self.generate_btn.pack(fill=tk.X, padx=150, pady=20, ipady=3)
        
        self.status_frame = ttk.LabelFrame(scrollable_frame, text="状态信息", padding="10")
        self.status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text_font = self.custom_font if self.custom_font else ("Helvetica", 10)
        self.status_text = tk.Text(self.status_frame, height=10, wrap=tk.WORD, font=text_font)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
    def init_editor_tab(self):
        scrollable_frame = self.create_scrollable_frame(self.editor_tab)
        
        toolbar = ttk.Frame(scrollable_frame)
        toolbar.pack(fill=tk.X, pady=5)
        
        self.add_item_btn = ttk.Button(toolbar, text="添加", command=self.add_item)
        self.add_item_btn.pack(side=tk.LEFT, padx=5)
        
        self.edit_item_btn = ttk.Button(toolbar, text="编辑", command=self.edit_item)
        self.edit_item_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_item_btn = ttk.Button(toolbar, text="删除", command=self.delete_item)
        self.delete_item_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_items_btn = ttk.Button(toolbar, text="保存", command=self.save_items, style="Accent.TButton")
        self.save_items_btn.pack(side=tk.RIGHT, padx=5)
        
        tree_frame = ttk.Frame(scrollable_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.items_tree = ttk.Treeview(tree_frame, columns=("符号", "中文名", "英文名", "拼音", "位置", "描述"), show="headings")
        
        self.items_tree.heading("符号", text="符号")
        self.items_tree.heading("中文名", text="中文名")
        self.items_tree.heading("英文名", text="英文名")
        self.items_tree.heading("拼音", text="拼音")
        self.items_tree.heading("位置", text="位置")
        self.items_tree.heading("描述", text="描述")
        
        self.items_tree.column("符号", width=80)
        self.items_tree.column("中文名", width=100)
        self.items_tree.column("英文名", width=150)
        self.items_tree.column("拼音", width=100)
        self.items_tree.column("位置", width=80)
        self.items_tree.column("描述", width=250)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加双击事件绑定
        self.items_tree.bind('<Double-1>', lambda event: self.edit_item())
        
        self.load_items()
        
    def load_items(self):
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        try:
            df = pd.read_csv('dict.csv')
            logger.info(f"加载数据成功，共 {len(df)} 条记录")
            
            for i, row in df.iterrows():
                position = row.get('位置', 1)
                self.items_tree.insert("", tk.END, values=(row['符号'], row['中文名'], row['英文名'], row['拼音'], position, row['描述']))
                logger.debug(f"加载条目: {row['符号']} - {row['拼音']} - 位置: {position}")
                
        except FileNotFoundError:
            logger.info("dict.csv 文件不存在，将创建新文件")
            df = pd.DataFrame(columns=['符号', '中文名', '英文名', '拼音', '位置', '描述'])
            df.to_csv('dict.csv', index=False, encoding='utf-8-sig')
        except pd.errors.EmptyDataError:
            logger.info("dict.csv 文件为空，将创建新文件")
            df = pd.DataFrame(columns=['符号', '中文名', '英文名', '拼音', '位置', '描述'])
            df.to_csv('dict.csv', index=False, encoding='utf-8-sig')
        except Exception as e:
            logger.error(f"加载数据时出错: {str(e)}")
            messagebox.showerror("错误", f"加载数据时出错: {str(e)}")
    
    def add_item(self):
        self.show_edit_dialog("添加词条", self.items_tree)
    
    def delete_item(self):
        selected_item = self.items_tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请选择要删除的项")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的项吗？"):
            self.items_tree.delete(selected_item)
    
    def edit_item(self, event=None):
        # 如果没有事件参数，使用当前选中的项
        if event is None:
            selected_item = self.items_tree.selection()
        else:
            # 从事件中获取双击的项
            selected_item = self.items_tree.identify_row(event.y)
            if selected_item:
                self.items_tree.selection_set(selected_item)
            else:
                selected_item = []
        
        if not selected_item:
            messagebox.showwarning("警告", "请选择要编辑的项")
            return
        
        self.show_edit_dialog("编辑词条", self.items_tree)
    
    def show_edit_dialog(self, title, tree):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        
        dialog_width = 500
        dialog_height = 350
        screen_w = dialog.winfo_screenwidth()
        screen_h = dialog.winfo_screenheight()
        center_x = int((screen_w - dialog_width) / 2)
        center_y = int((screen_h - dialog_height) / 2)
        dialog.geometry(f"{dialog_width}x{dialog_height}+{center_x}+{center_y}")
        dialog.resizable(True, True)
        
        dialog.update_idletasks() 
        apply_theme_to_titlebar(dialog)
        
        frame = ttk.Frame(dialog, padding="20 20 20 5")
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        labels = ["符号", "中文名", "英文名", "拼音", "位置", "描述"]
        entries = []
        
        for i, label_text in enumerate(labels):
            label_font = self.label_font if self.label_font else ("Helvetica", 10)
            label = ttk.Label(frame, text=label_text + ":", font=label_font)
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            entry_font = self.custom_font if self.custom_font else ("Helvetica", 10)
            entry = ttk.Entry(frame, width=40, font=entry_font)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=5, padx=5)
            entries.append(entry)
        
        frame.columnconfigure(1, weight=1)
        
        selected_item = tree.selection()
        if selected_item:
            values = tree.item(selected_item, "values")
            for i, entry in enumerate(entries):
                if i < len(values):
                    entry.insert(0, values[i])
        
        def save():
            values = [entry.get() for entry in entries]
            if not all(values):
                messagebox.showwarning("警告", "请填写所有字段")
                return
            
            try:
                position = int(values[4])
                if position <= 0:
                    messagebox.showwarning("警告", "位置必须是正整数")
                    return
            except ValueError:
                messagebox.showwarning("警告", "位置必须是数字")
                return
            
            if selected_item:
                tree.item(selected_item, values=values)
            else:
                tree.insert("", tk.END, values=values)
            
            dialog.destroy()
        
        btn_frame = ttk.Frame(dialog, padding="20 0 20 20")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        save_btn = ttk.Button(btn_frame, text="保存", command=save, style="Accent.TButton")
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        cancel_btn = ttk.Button(btn_frame, text="取消", command=dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 10))
        
        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)
    
    def save_items(self):
        try:
            data = []
            for item in self.items_tree.get_children():
                values = self.items_tree.item(item, "values")
                data.append({
                    "符号": values[0],
                    "中文名": values[1],
                    "英文名": values[2],
                    "拼音": values[3],
                    "位置": values[4],
                    "描述": values[5]
                })
            
            pinyin_positions = {}
            for item in data:
                pinyin = item['拼音']
                position = item['位置']
                if pinyin in pinyin_positions:
                    if position in pinyin_positions[pinyin]:
                        messagebox.showwarning("警告", f"拼音 '{pinyin}' 存在重复的位置 {position}")
                        return
                    pinyin_positions[pinyin].add(position)
                else:
                    pinyin_positions[pinyin] = {position}
            
            df = pd.DataFrame(data)
            df.to_csv('dict.csv', index=False, encoding='utf-8-sig')
            logger.info(f"保存数据成功，共 {len(data)} 条记录")
            
            messagebox.showinfo("成功", "数据保存成功！")
            
        except Exception as e:
            logger.error(f"保存数据时出错: {str(e)}")
            messagebox.showerror("错误", f"保存数据时出错: {str(e)}")
    
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="选择DAT文件",
            filetypes=[("DAT文件", "*.dat"), ("所有文件", "*.*")]
        )
        if filename:
            self.input_var.set(filename)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="保存DAT文件",
            defaultextension=".dat",
            filetypes=[("DAT文件", "*.dat"), ("所有文件", "*.*")]
        )
        if filename:
            self.output_var.set(filename)
    
    def log(self, message):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def init_batch_tab(self):
        scrollable_frame = self.create_scrollable_frame(self.batch_tab)
        
        self.batch_title = ttk.Label(scrollable_frame, text="词条批量生成器", font=self.title_font)
        self.batch_title.pack(pady=(0, 20))
        
        self.batch_input_frame = ttk.LabelFrame(scrollable_frame, text="输入设置", padding="10")
        self.batch_input_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.txt_label = ttk.Label(self.batch_input_frame, text="TXT文件:", font=self.label_font)
        self.txt_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.txt_var = tk.StringVar()
        self.txt_entry = ttk.Entry(self.batch_input_frame, textvariable=self.txt_var, width=40)
        self.txt_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.txt_btn = ttk.Button(self.batch_input_frame, text="浏览", command=self.browse_txt)
        self.txt_btn.grid(row=0, column=2, pady=5)
        self.batch_input_frame.columnconfigure(1, weight=1)
        
        self.pinyin_frame = ttk.LabelFrame(scrollable_frame, text="拼音生成方式", padding="10")
        self.pinyin_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.pinyin_method = tk.StringVar(value="1")
        
        self.method1 = ttk.Radiobutton(self.pinyin_frame, text="首字母组成 (你好→nh, Alice Kingsley→ak)", variable=self.pinyin_method, value="1")
        self.method1.pack(anchor=tk.W, pady=5)
        
        self.method2 = ttk.Radiobutton(self.pinyin_frame, text="首字全拼 (你好→ni, Alice Kingsley→alice)", variable=self.pinyin_method, value="2")
        self.method2.pack(anchor=tk.W, pady=5)
        
        self.method3 = ttk.Radiobutton(self.pinyin_frame, text="全部全拼 (你好→nihao, Alice Kingsley→alicekingsley)", variable=self.pinyin_method, value="3")
        self.method3.pack(anchor=tk.W, pady=5)
        
        self.batch_settings_frame = ttk.LabelFrame(scrollable_frame, text="批量设置", padding="10")
        self.batch_settings_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.batch_cn_label = ttk.Label(self.batch_settings_frame, text="中文名:", font=self.label_font)
        self.batch_cn_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.batch_cn_var = tk.StringVar()
        self.batch_cn_entry = ttk.Entry(self.batch_settings_frame, textvariable=self.batch_cn_var, width=40)
        self.batch_cn_entry.grid(row=0, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.batch_en_label = ttk.Label(self.batch_settings_frame, text="英文名:", font=self.label_font)
        self.batch_en_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.batch_en_var = tk.StringVar()
        self.batch_en_entry = ttk.Entry(self.batch_settings_frame, textvariable=self.batch_en_var, width=40)
        self.batch_en_entry.grid(row=1, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.batch_pos_label = ttk.Label(self.batch_settings_frame, text="位置:", font=self.label_font)
        self.batch_pos_label.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.batch_pos_var = tk.StringVar(value="1")
        self.batch_pos_entry = ttk.Entry(self.batch_settings_frame, textvariable=self.batch_pos_var, width=40)
        self.batch_pos_entry.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.batch_desc_label = ttk.Label(self.batch_settings_frame, text="描述:", font=self.label_font)
        self.batch_desc_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        
        self.batch_desc_var = tk.StringVar()
        self.batch_desc_entry = ttk.Entry(self.batch_settings_frame, textvariable=self.batch_desc_var, width=40)
        self.batch_desc_entry.grid(row=3, column=1, sticky=tk.EW, pady=5, padx=5)
        
        self.batch_settings_frame.columnconfigure(1, weight=1)
        
        self.batch_generate_btn = ttk.Button(scrollable_frame, text="批量生成", command=self.batch_generate, style="Accent.TButton")
        self.batch_generate_btn.pack(fill=tk.X, padx=150, pady=20, ipady=3)
        
        self.batch_status_frame = ttk.LabelFrame(scrollable_frame, text="状态信息", padding="10")
        self.batch_status_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        text_font = self.custom_font if self.custom_font else ("Helvetica", 10)
        self.batch_status_text = tk.Text(self.batch_status_frame, height=10, wrap=tk.WORD, font=text_font)
        self.batch_status_text.pack(fill=tk.BOTH, expand=True)
        self.batch_status_text.config(state=tk.DISABLED)
    
    def browse_txt(self):
        filename = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.txt_var.set(filename)
    
    def batch_log(self, message):
        self.batch_status_text.config(state=tk.NORMAL)
        self.batch_status_text.insert(tk.END, message + "\n")
        self.batch_status_text.see(tk.END)
        self.batch_status_text.config(state=tk.DISABLED)
        self.root.update()
    
    def is_chinese(self, char):
        return '\u4e00' <= char <= '\u9fff'
    
    def is_english(self, char):
        return ('a' <= char <= 'z') or ('A' <= char <= 'Z')
    
    def generate_pinyin(self, text, method):
        import re
        
        filtered_text = ''.join([c for c in text if self.is_chinese(c) or self.is_english(c) or c == ' '])
        
        if not filtered_text:
            return ''
        
        if method == "1":
            if any(self.is_chinese(c) for c in filtered_text):
                chinese_chars = [c for c in filtered_text if self.is_chinese(c)]
                try:
                    from pypinyin import lazy_pinyin
                    pinyin_list = lazy_pinyin(chinese_chars)
                    return ''.join([p[0].lower() for p in pinyin_list])
                except ImportError:
                    return ''.join([c[0].lower() for c in chinese_chars])
            else:
                words = filtered_text.split()
                return ''.join([word[0].lower() for word in words if word])
        
        elif method == "2":
            if any(self.is_chinese(c) for c in filtered_text):
                first_char = next((c for c in filtered_text if self.is_chinese(c)), '')
                if first_char:
                    try:
                        from pypinyin import lazy_pinyin
                        return lazy_pinyin(first_char)[0].lower()
                    except ImportError:
                        return first_char[0].lower()
                return ''
            else:
                words = filtered_text.split()
                return words[0].lower() if words else ''
        
        elif method == "3":
            if any(self.is_chinese(c) for c in filtered_text):
                chinese_chars = [c for c in filtered_text if self.is_chinese(c)]
                try:
                    from pypinyin import lazy_pinyin
                    return ''.join(lazy_pinyin(chinese_chars)).lower()
                except ImportError:
                    return ''.join([c.lower() for c in chinese_chars])
            else:
                words = filtered_text.split()
                return ''.join(words).lower()
    
    def batch_generate(self):
        try:
            self.batch_log("开始批量生成...")
            
            # 获取TXT文件路径
            txt_file = self.txt_var.get()
            if not txt_file:
                messagebox.showwarning("警告", "请选择TXT文件")
                return
            
            # 读取TXT文件
            self.batch_log(f"读取TXT文件: {txt_file}")
            with open(txt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 过滤空行和只有空格的行
            entries = [line.strip() for line in lines if line.strip()]
            self.batch_log(f"共读取 {len(entries)} 个词条")
            
            # 检测非中文或英文的字符
            invalid_chars = set()
            for entry in entries:
                for char in entry:
                    if not (self.is_chinese(char) or self.is_english(char) or char == ' '):
                        invalid_chars.add(char)
            
            if invalid_chars:
                messagebox.showwarning("警告", f"检测到非中文或英文的字符: {''.join(invalid_chars)}")
                return
            
            # 获取批量设置
            cn_name = self.batch_cn_var.get()
            en_name = self.batch_en_var.get()
            try:
                position = int(self.batch_pos_var.get())
                if position <= 0:
                    messagebox.showwarning("警告", "位置必须是正整数")
                    return
            except ValueError:
                messagebox.showwarning("警告", "位置必须是数字")
                return
            description = self.batch_desc_var.get()
            
            # 获取拼音生成方式
            method = self.pinyin_method.get()
            
            # 生成词条
            self.batch_log("生成词条...")
            data = []
            pinyin_positions = {}
            
            for entry in entries:
                # 生成拼音
                pinyin = self.generate_pinyin(entry, method)
                if not pinyin:
                    self.batch_log(f"跳过空拼音的词条: {entry}")
                    continue
                
                # 处理重复拼音的情况
                current_position = position
                while pinyin in pinyin_positions and current_position in pinyin_positions[pinyin]:
                    current_position += 1
                
                # 记录位置
                if pinyin not in pinyin_positions:
                    pinyin_positions[pinyin] = set()
                pinyin_positions[pinyin].add(current_position)
                
                # 添加到数据
                data.append({
                    "符号": entry,
                    "中文名": cn_name,
                    "英文名": en_name,
                    "拼音": pinyin,
                    "位置": current_position,
                    "描述": description
                })
                
                self.batch_log(f"生成词条: {entry} → {pinyin} (位置: {current_position})")
            
            # 保存到CSV文件
            if data:
                self.batch_log("保存到CSV文件...")
                df = pd.DataFrame(data)
                
                # 读取现有数据
                try:
                    existing_df = pd.read_csv('dict.csv')
                    df = pd.concat([existing_df, df], ignore_index=True)
                except (FileNotFoundError, pd.errors.EmptyDataError):
                    pass
                
                df.to_csv('dict.csv', index=False, encoding='utf-8-sig')
                self.batch_log(f"保存成功，共 {len(data)} 个词条")
                
                # 重新加载数据到编辑器
                self.load_items()
                
                # 提醒用户重复拼音的处理
                messagebox.showinfo("成功", f"批量生成完成！\n共生成 {len(data)} 个词条\n注意：如果有相同拼音，位置已自动顺延")
            else:
                self.batch_log("没有生成任何词条")
                messagebox.showinfo("提示", "没有生成任何词条")
            
        except Exception as e:
            self.batch_log(f"错误: {str(e)}")
            logger.error(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"批量生成时出错: {str(e)}")
    
    def generate_dict(self):
        try:
            self.log("开始生成词典...")
            logger.info("开始生成词典...")
            
            # 读取CSV文件
            self.log("读取数据文件...")
            logger.info("读取数据文件...")
            df = pd.read_csv('dict.csv')
            logger.info(f"读取到 {len(df)} 条记录")
            
            # 处理输入文件
            input_file = self.input_var.get()
            if input_file:
                self.log(f"加载现有词典文件: {input_file}")
                logger.info(f"加载现有词典文件: {input_file}")
                input_user_dict = UserDict.from_dat_file(input_file)
            else:
                self.log("未指定输入文件，创建新词典")
                logger.info("未指定输入文件，创建新词典")
                input_user_dict = None
            
            output_file = self.output_var.get()
            logger.info(f"输出文件: {output_file}")
            
            # 创建新词典
            user_dict = UserDict()
            user_dict.utctimestamp = int(datetime.now().timestamp())
            logger.debug(f"创建新词典，时间戳: {user_dict.utctimestamp}")
            
            # 添加现有词条
            if input_user_dict:
                self.log(f"添加现有词条...")
                logger.info(f"添加现有词条，共 {len(input_user_dict.items)} 条")
                for item in input_user_dict.items:
                    if item['pinyin'].startswith('i'): 
                        continue  # 跳过特殊字符
                    user_dict.add_item(item['pinyin'], item['phrase'], item['i_candidate'])
            
            # 添加所有词条
            self.log("添加词条...")
            logger.info("添加词条...")
            for i, row in df.iterrows():
                symbol = row['符号']
                pinyin = row['拼音'].strip().lower()
                position = int(row.get('位置', 1))
                logger.debug(f"添加词条: {symbol} - {pinyin} - 位置: {position}")
                user_dict.add_item(pinyin, symbol, position)
            
            # 保存到文件
            self.log(f"保存到文件: {output_file}")
            logger.info(f"保存到文件: {output_file}")
            user_dict.to_dat_file(output_file)
            
            self.log(f"词典生成完成！共添加 {len(user_dict.items)} 个词条")
            logger.info(f"词典生成完成！共添加 {len(user_dict.items)} 个词条")
            messagebox.showinfo("成功", f"词典生成完成！\n共添加 {len(user_dict.items)} 个词条\n保存到: {output_file}")
            
        except Exception as e:
            self.log(f"错误: {str(e)}")
            logger.error(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("错误", f"生成词典时出错: {str(e)}")
            
    def init_about_tab(self):
        # 创建滚动视图
        scrollable_frame = self.create_scrollable_frame(self.about_tab)
        
        # 创建内容框架
        content_frame = ttk.Frame(scrollable_frame, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 图标
        icon_path = os.path.join(os.path.dirname(__file__), 'sources', 'app.png')
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                icon_label = ttk.Label(content_frame, image=icon)
                icon_label.image = icon  # 保持引用
                icon_label.pack(pady=20)
            except Exception as e:
                logger.error(f"加载图标失败: {e}")
        
        # 产品名称
        product_name = ttk.Label(content_frame, text="MS User DictCraft", font=self.title_font)
        product_name.pack(pady=10)
        
        # 产品描述
        description = ttk.Label(content_frame, text="智造词库，高效输入。", font=self.label_font)
        description.pack(pady=5)
        
        ttk.Label(content_frame, text="", font=self.label_font).pack(pady=5) # 空一行
        
        # 产品版本
        version = ttk.Label(content_frame, text="版本: v26.1.1", font=self.label_font)
        version.pack(pady=5)
        
        # 适用于 Windows10/11
        system = ttk.Label(content_frame, text="适用于: Windows 10/11", font=self.label_font)
        system.pack(pady=5)
        
        ttk.Label(content_frame, text="", font=self.label_font).pack(pady=5) # 空一行
        
        # 开源协议
        license = ttk.Label(content_frame, text="开源协议: MIT", font=self.label_font)
        license.pack(pady=5)
        
        # 开源仓库
        repo_frame = ttk.Frame(content_frame)
        repo_frame.pack(pady=5)
        repo_label = ttk.Label(repo_frame, text="开源仓库: ", font=self.label_font)
        repo_label.pack(side=tk.LEFT, padx=(0, 5))
        repo_link = ttk.Label(repo_frame, text="SRInternet-Studio/MS-User-DictCraft", font=self.label_font, foreground="#007acc", cursor="hand2")
        repo_link.pack(side=tk.LEFT)
        repo_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/SRInternet-Studio/ms-user-dictcraft"))
        
        # 基于项目
        based_frame = ttk.Frame(content_frame)
        based_frame.pack(pady=5)
        based_label = ttk.Label(based_frame, text="本项目基于" , font=self.label_font)
        based_label.pack(side=tk.LEFT, padx=(0, 5))
        based_link = ttk.Label(based_frame, text="MS User Dictionary Toolkit", font=self.label_font, foreground="#007acc", cursor="hand2")
        based_link.pack(side=tk.LEFT)
        based_link.bind("<Button-1>", lambda e: self.open_url("https://github.com/Louisredstone/ms-user-dict-toolkit"))
        based_label_2 = ttk.Label(based_frame, text=" 二次创作" , font=self.label_font)
        based_label_2.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Label(content_frame, text="", font=self.label_font).pack(pady=5) # 空一行
        
        # 官网
        website_frame = ttk.Frame(content_frame)
        website_frame.pack(pady=5)
        website_label = ttk.Label(website_frame, text="官网: ", font=self.label_font)
        website_label.pack(side=tk.LEFT, padx=(0, 5))
        website_link = ttk.Label(website_frame, text="www.sr-studio.cn", font=self.label_font, foreground="#007acc", cursor="hand2")
        website_link.pack(side=tk.LEFT)
        website_link.bind("<Button-1>", lambda e: self.open_url("https://www.sr-studio.cn"))
        
        # 联系邮箱
        email = ttk.Label(content_frame, text="联系邮箱: srinternet@qq.com", font=self.label_font)
        email.pack(pady=5)
        
    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)
            
def apply_theme_to_titlebar(root):
    if sys.platform != "win32": return
    
    import pywinstyles
    version = sys.getwindowsversion()
    if version.major == 10 and version.build >= 22000:
        # Set the title bar color to the background color on Windows 11 for better appearance
        pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
    elif version.major == 10:
        pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

        # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
        root.wm_attributes("-alpha", 0.99)
        root.wm_attributes("-alpha", 1)

if __name__ == "__main__":
    root = tk.Tk()
    
    # 应用窗口大小设置
    root.geometry(default_config.get("window_size", "800x600"))
    
    icon_path = os.path.join(os.path.dirname(__file__), 'sources', 'app.png')
    if os.path.exists(icon_path):
        try:
            root.iconphoto(True, tk.PhotoImage(file=icon_path))
        except Exception as e:
            logger.error(f"设置图标失败: {e}")
    
    # 应用主题设置
    match default_config.get("dark_mode", "auto"):
        case "dark":
            sv_ttk.set_theme("dark")
        case "light":
            sv_ttk.set_theme("light")
        case _:
            sv_ttk.set_theme(darkdetect.theme())
    
    app = UserDictGUI(root)
    apply_theme_to_titlebar(root)
    root.mainloop()