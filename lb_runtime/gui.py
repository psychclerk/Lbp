import csv
import logging
import sys

def _int(val):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0

def unquote(s):
    if not isinstance(s, str): return s
    s = s.strip()
    if len(s) >= 2:
        if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
            return s[1:-1]
    return s

def _decode_escapes(s):
    if not isinstance(s, str): return s
    # Use a placeholder for escaped backslashes to avoid double-processing
    s = s.replace('\\\\', '\x00')
    s = s.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    s = s.replace('\\"', '"').replace("\\'", "'")
    return s.replace('\x00', '\\')

# Mock tkinter if not available (e.g., in a sandbox)
try:
    import tkinter as tk
    from tkinter import messagebox, simpledialog, ttk, font as tkfont
    TK_AVAILABLE = True
except ImportError:
    TK_AVAILABLE = False
    class tk:
        class Tk:
            def __init__(self): pass
            def withdraw(self): pass
            def quit(self): pass
            def destroy(self): pass
            def mainloop(self): pass
            def Menu(self, *args, **kwargs): return self
            def add_cascade(self, **kwargs): pass
            def add_command(self, **kwargs): pass
            def config(self, **kwargs): pass
        class Toplevel:
            def __init__(self, master=None): pass
            def title(self, t): pass
            def geometry(self, g): pass
            def protocol(self, p, c): pass
            def destroy(self): pass
            def update_idletasks(self): pass
            def config(self, **kwargs): pass
        class Menu:
            def __init__(self, *args, **kwargs): pass
            def add_cascade(self, **kwargs): pass
            def add_command(self, **kwargs): pass
            def add_separator(self, **kwargs): pass
        class Frame:
            def __init__(self, master=None): pass
            def place(self, **kwargs): pass
        class Button:
            def __init__(self, master=None, **kwargs): pass
            def place(self, **kwargs): pass
            def config(self, **kwargs): pass
        class Entry:
            def __init__(self, master=None, **kwargs): self.v = ""
            def place(self, **kwargs): pass
            def insert(self, idx, val): self.v = val
            def delete(self, start, end): self.v = ""
            def get(self): return self.v
            def config(self, **kwargs): pass
            def focus_set(self): pass
        class Text:
            def __init__(self, master=None, **kwargs): pass
            def insert(self, idx, val): pass
            def delete(self, start, end): pass
            def get(self, start, end): return ""
            def pack(self, **kwargs): pass
            def config(self, **kwargs): pass
            def yview(self, *args): pass
        class Label:
            def __init__(self, master=None, **kwargs): pass
            def place(self, **kwargs): pass
            def config(self, **kwargs): pass
        class Listbox:
            def __init__(self, master=None, **kwargs): pass
            def insert(self, idx, val): pass
            def delete(self, start, end): pass
            def pack(self, **kwargs): pass
            def config(self, **kwargs): pass
            def curselection(self): return []
            def get(self, idx): return ""
            def yview(self, *args): pass
            def bind(self, seq, callback): pass
            def selection_clear(self, start, end): pass
            def selection_set(self, idx): pass
            def see(self, idx): pass
        class Scrollbar:
            def __init__(self, master=None, **kwargs): pass
            def pack(self, **kwargs): pass
            def config(self, **kwargs): pass
            def set(self, *args): pass
        class Checkbutton:
            def __init__(self, master=None, **kwargs): pass
            def place(self, **kwargs): pass
            def config(self, **kwargs): pass
        class Radiobutton:
            def __init__(self, master=None, **kwargs): pass
            def place(self, **kwargs): pass
            def config(self, **kwargs): pass
        class LabelFrame:
            def __init__(self, master=None, **kwargs): pass
            def place(self, **kwargs): pass
        class IntVar:
            def __init__(self): self.v = 0
            def set(self, v): self.v = v
            def get(self): return self.v
        class StringVar:
            def __init__(self): self.v = ""
            def set(self, v): self.v = v
            def get(self): return self.v
        END = "end"
        RIGHT = "right"
        LEFT = "left"
        Y = "y"
        X = "x"
        BOTH = "both"
        HORIZONTAL = "horizontal"
        BOTTOM = "bottom"

    class messagebox:
        @staticmethod
        def showinfo(t, m): print(f"NOTICE: {m}")
        @staticmethod
        def askyesno(t, m): return True

    class simpledialog:
        @staticmethod
        def askstring(t, m): return "mock_input"

    class ttk:
        class Combobox:
            def __init__(self, master=None, **kwargs): self.values = []
            def place(self, **kwargs): pass
            def set(self, v): pass
            def get(self): return ""
            def __setitem__(self, k, v): pass
            def bind(self, seq, callback): pass
            def config(self, **kwargs): pass
        class Treeview:
            def __init__(self, master=None, **kwargs): self.cols = []
            def pack(self, **kwargs): pass
            def heading(self, c, text): pass
            def column(self, c, width): pass
            def insert(self, p, idx, values=None): pass
            def delete(self, *args): pass
            def get_children(self): return []
            def __setitem__(self, k, v):
                if k == "columns": self.cols = v
            def __getitem__(self, k):
                if k == "columns": return self.cols
                return None
            def yview(self, *args): pass
            def xview(self, *args): pass
            def bind(self, seq, callback): pass
            def selection(self): return []
            def item(self, item): return {"values": []}
            def config(self, **kwargs): pass
        class Notebook:
            def __init__(self, master=None, **kwargs): pass
            def add(self, child, **kwargs): pass
            def place(self, **kwargs): pass
            def index(self, idx): return 0
            def select(self, tab_id): pass

from lb_runtime import builtins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lb_gui")

_handles = None

def set_handles(h):
    global _handles
    _handles = h

def get_handle(name):
    if _handles and hasattr(_handles, name):
        return getattr(_handles, name)
    return None

class WindowManager:
    """Manages the lifecycle of the application and its windows."""
    _root = None
    _windows = []
    _running = False

    @classmethod
    def get_container(cls):
        if cls._root is None:
            cls._root = tk.Tk()
            cls._root.withdraw()
        return cls._root

    @classmethod
    def add_window(cls, window):
        cls._windows.append(window)

    @classmethod
    def remove_window(cls, window):
        if window in cls._windows:
            cls._windows.remove(window)
        if not cls._windows and cls._root:
            cls._root.quit()
            cls._root.destroy()
            cls._root = None
            cls._running = False

    @classmethod
    def run(cls):
        if cls._running:
            return
        try:
            if not TK_AVAILABLE:
                logger.info("Tkinter not available, skipping event loop.")
                return
            root = cls.get_container()
            if cls._windows:
                cls._running = True
                root.mainloop()
        except KeyboardInterrupt:
            cls.shutdown()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            cls.shutdown()
        finally:
            cls._running = False

    @classmethod
    def shutdown(cls):
        if cls._root:
            try:
                cls._root.quit()
                cls._root.destroy()
            except:
                pass
            cls._root = None
        cls._windows = []

def run_event_loop():
    WindowManager.run()

def notice(msg):
    messagebox.showinfo("Notice", _decode_escapes(msg))

def confirm(msg):
    res = messagebox.askyesno("Confirm", _decode_escapes(msg))
    return 1 if res else 0

def prompt(msg):
    res = simpledialog.askstring("Prompt", _decode_escapes(msg))
    return res if res is not None else ""

class LBWindow:
    """Production-grade Liberty BASIC window implementation."""
    def __init__(self):
        self.root = None
        self.controls = []
        self.title_str = ""
        self.menus = []

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)

    def __str__(self):
        return f"Window({self.title_str})"

    def open(self, title, width=None, height=None):
        if self.root:
            return
        self.title_str = title
        self.root = tk.Toplevel(WindowManager.get_container())
        self.root.title(title)
        
        # Use values from builtins if available
        try:
            w = _int(width if width is not None else getattr(builtins, 'WindowWidth', 800))
            h = _int(height if height is not None else getattr(builtins, 'WindowHeight', 600))
            x = _int(getattr(builtins, 'UpperLeftX', 100))
            y = _int(getattr(builtins, 'UpperLeftY', 100))
        except (ValueError, TypeError):
            w, h, x, y = 800, 600, 100, 100
        
        self.root.geometry(f"{w}x{h}{x:+d}{y:+d}")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        WindowManager.add_window(self)
        
        # Initialize Menus
        if self.menus:
            self.menubar = tk.Menu(self.root)
            self.root.config(menu=self.menubar)
            for m_title, m_items in self.menus:
                menu = tk.Menu(self.menubar, tearoff=0)
                clean_title = m_title.replace('&', '')
                self.menubar.add_cascade(label=clean_title, menu=menu)
                for label, handler in m_items:
                    if label in ("", "---"):
                        menu.add_separator()
                    else:
                        clean_label = label.replace('&', '')
                        menu.add_command(label=clean_label, command=handler)

        # Initialize all registered controls
        for ctrl in self.controls:
            try:
                ctrl.create_widget()
            except Exception as e:
                logger.error(f"Failed to create control {ctrl}: {e}")

    def add_menu(self, title, items):
        self.menus.append((title, items))

    def close(self):
        if self.root:
            self.root.destroy()
            self.root = None
            WindowManager.remove_window(self)

    def command(self, cmd):
        if not isinstance(cmd, str): return
        raw_cmd = cmd.strip()
        cmd_lower = raw_cmd.lower()
        if cmd_lower.startswith("title "):
            if self.root:
                self.root.title(_decode_escapes(unquote(raw_cmd[6:].strip())))
        elif cmd_lower.startswith("resize "):
            try:
                parts = cmd_lower[7:].split()
                if len(parts) >= 2 and self.root:
                    w = _int(parts[0])
                    h = _int(parts[1])
                    self.root.geometry(f"{w}x{h}")
            except:
                pass
        elif cmd_lower == "flush":
            if self.root: self.root.update_idletasks()

class LBControl:
    """Base class for all Liberty BASIC GUI controls."""
    def __init__(self, parent=None, caption="", handler=None, x=0, y=0, w=100, h=30):
        self.parent = parent
        self.caption = _decode_escapes(unquote(caption))
        self.handler = handler
        self.widget = None
        self.container = None
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.pending_commands = []
        self.frame = None
        if parent:
            if hasattr(parent, 'controls'):
                parent.controls.append(self)
            if hasattr(parent, 'root') and parent.root:
                self.create_widget()

    def create_widget(self):
        """Must be implemented by subclasses."""
        if self.widget: return True
        return False

    def _after_create(self):
        """Replay pending commands after widget creation."""
        for cmd in self.pending_commands:
            self.command(cmd)
        self.pending_commands = []

    def get_container(self):
        if self.container:
            return self.container
        p = self.parent
        while p and not hasattr(p, 'root'):
            p = p.parent
        return p.root if p else None

    def reparent(self, new_container):
        """Re-parents the control to a new container by recreating it."""
        # Store current state
        state = self._get_widget_state()
        
        # Destroy existing widgets
        if hasattr(self, 'frame') and self.frame:
            try: self.frame.destroy()
            except: pass
            self.frame = None
        if self.widget:
            try: self.widget.destroy()
            except: pass
            self.widget = None
            
        self.container = new_container
        self.create_widget()
        
        # Restore state
        self._set_widget_state(state)

    def _get_widget_state(self):
        state = {'value': str(self)}
        if self.widget:
            if isinstance(self.widget, tk.Listbox):
                state['items'] = self.widget.get(0, tk.END)
                state['selection'] = self.widget.curselection()
            elif isinstance(self.widget, ttk.Combobox):
                state['items'] = self.widget['values']
            elif isinstance(self.widget, ttk.Treeview):
                state['columns'] = self.widget['columns']
                items = []
                for item_id in self.widget.get_children():
                    items.append(self.widget.item(item_id)['values'])
                state['items'] = items
        return state

    def _set_widget_state(self, state):
        if not self.widget: return

        if 'columns' in state and isinstance(self.widget, ttk.Treeview):
             self.widget['columns'] = state['columns']
             for col in state['columns']:
                 self.widget.heading(col, text=col)
                 self.widget.column(col, width=100)

        if 'items' in state:
            if isinstance(self.widget, tk.Listbox):
                self.widget.delete(0, tk.END)
                for item in state['items']:
                    self.widget.insert(tk.END, item)
                if 'selection' in state and state['selection']:
                    for idx in state['selection']:
                        self.widget.selection_set(idx)
            elif isinstance(self.widget, ttk.Combobox):
                self.widget['values'] = state['items']
            elif isinstance(self.widget, ttk.Treeview):
                # Clear existing
                for child in self.widget.get_children():
                    self.widget.delete(child)
                for item in state['items']:
                    self.widget.insert("", tk.END, values=item)

        if state.get('value') and state['value'] != self.caption:
            self.command(f"set {state['value']}")

    def place(self):
        target = getattr(self, 'frame', self.widget)
        if target:
            target.place(x=_int(self.x), y=_int(self.y), 
                         width=_int(self.w), height=_int(self.h))

    def command(self, cmd):
        """Universal command handler for all controls."""
        if not isinstance(cmd, str): return
        
        raw_cmd = cmd.strip()
        cmd_lower = raw_cmd.lower()

        if not self.widget and not hasattr(self, 'frame'):
            self.pending_commands.append(raw_cmd)
            return

        try:
            target = getattr(self, 'frame', self.widget)
            if cmd_lower == "enable":
                target.config(state="normal")
            elif cmd_lower == "disable":
                target.config(state="disabled")
            elif cmd_lower == "hide":
                target.place_forget()
            elif cmd_lower == "show":
                self.place()
            elif cmd_lower == "setfocus":
                self.widget.focus_set()
            elif cmd_lower.startswith("backcolor "):
                target.config(bg=raw_cmd[10:].strip())
            elif cmd_lower.startswith("color "):
                target.config(fg=raw_cmd[6:].strip())
            elif cmd_lower.startswith("font "):
                # Basic font parsing: font name size
                parts = raw_cmd[5:].split()
                if len(parts) >= 2:
                    target.config(font=(parts[0], _int(parts[1])))
        except Exception as e:
            logger.warning(f"Failed to execute command '{raw_cmd}' on {self.__class__.__name__}: {e}")

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)

    def __str__(self):
        """Default string representation (returns control value)."""
        if hasattr(self, 'var') and self.var:
            return str(self.var.get())
        
        if self.widget:
            try:
                if isinstance(self.widget, tk.Text):
                    return self.widget.get("1.0", tk.END).rstrip('\n')
                if isinstance(self.widget, tk.Listbox):
                    sel = self.widget.curselection()
                    return str(self.widget.get(sel[0])) if sel else ""
                if isinstance(self.widget, ttk.Treeview):
                    sel = self.widget.selection()
                    if sel:
                        vals = self.widget.item(sel[0])['values']
                        return str(vals[0]) if vals else ""
                    return ""
                if hasattr(self.widget, 'get'):
                    return str(self.widget.get())
            except:
                pass
        return str(self.caption) if self.caption else ""

class LBButton(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = tk.Button(self.get_container(), text=self.caption, command=self.handler)
        self.place()
        self._after_create()

class LBTextbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = tk.Entry(self.get_container())
        self.widget.insert(0, self.caption)
        self.place()
        self._after_create()
    
    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("set "):
            self.widget.delete(0, tk.END)
            self.widget.insert(0, _decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower == "selectall":
            self.widget.selection_range(0, tk.END)
        else:
            super().command(cmd)

class LBTexteditor(LBControl):
    def create_widget(self):
        if self.frame: return
        self.frame = tk.Frame(self.get_container())
        self.scrollbar = tk.Scrollbar(self.frame)
        self.widget = tk.Text(self.frame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.widget.yview)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.widget.insert("1.0", self.caption)
        self.place()
        self._after_create()

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("set "):
            self.widget.delete("1.0", tk.END)
            self.widget.insert("1.0", _decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower == "clear":
            self.widget.delete("1.0", tk.END)
        else:
            super().command(cmd)

class LBStatictext(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = tk.Label(self.get_container(), text=self.caption, anchor="w", justify="left")
        self.place()
        self._after_create()

class LBListbox(LBControl):
    def create_widget(self):
        if self.frame: return
        self.frame = tk.Frame(self.get_container())
        self.scrollbar = tk.Scrollbar(self.frame)
        self.widget = tk.Listbox(self.frame, yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.widget.yview)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if self.handler:
            self.widget.bind('<<ListboxSelect>>', lambda e: self.handler())
            
        self.place()
        self._after_create()
    
    def fill_from_db(self, db_handle, sql):
        if isinstance(db_handle, str):
            db = get_handle(db_handle)
        else:
            db = db_handle
        
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                self.widget.delete(0, tk.END)
                for r in results:
                    # For Listbox, we just take the first value or a string rep
                    val = " ".join(str(v) for v in r.values())
                    self.widget.insert(tk.END, val)

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("additem "):
            self.widget.insert(tk.END, _decode_escapes(unquote(cmd_strip[8:].strip())))
        elif cmd_lower.startswith("fill "):
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        elif cmd_lower == "clear":
            self.widget.delete(0, tk.END)
        elif cmd_lower.startswith("selectindex "):
            try:
                idx = _int(cmd_lower[12:])
                self.widget.selection_clear(0, tk.END)
                self.widget.selection_set(idx)
                self.widget.see(idx)
            except:
                pass
        else:
            super().command(cmd)

class LBCombobox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = ttk.Combobox(self.get_container())
        if self.caption:
            self.widget['values'] = self.caption.split(',')
        if self.handler:
            self.widget.bind('<<ComboboxSelected>>', lambda e: self.handler())
        self.place()
        self._after_create()
    
    def fill_from_db(self, db_handle, sql):
        if isinstance(db_handle, str):
            db = get_handle(db_handle)
        else:
            db = db_handle
        
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                values = []
                for r in results:
                    values.append(" ".join(str(v) for v in r.values()))
                self.widget['values'] = values

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("set "):
            self.widget.set(_decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower.startswith("reload "):
            # Split and then unquote/decode each item
            items = [_decode_escapes(unquote(item.strip())) for item in cmd_strip[7:].split(',')]
            self.widget['values'] = items
        elif cmd_lower.startswith("fill "):
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        else:
            super().command(cmd)

class LBCheckbox(LBControl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.var = None

    def create_widget(self):
        if self.widget: return
        self.var = tk.IntVar()
        self.widget = tk.Checkbutton(self.get_container(), text=self.caption, variable=self.var, command=self.handler)
        self.place()
        self._after_create()
    
    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.var:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower == "set":
            self.var.set(1)
        elif cmd_lower == "reset":
            self.var.set(0)
        else:
            super().command(cmd)

class LBRadiobutton(LBControl):
    def create_widget(self):
        if self.widget: return
        root = self.get_container()
        if not hasattr(self.parent, '_radio_var'):
            self.parent._radio_var = tk.StringVar()
        self.widget = tk.Radiobutton(root, text=self.caption, variable=self.parent._radio_var, value=self.caption, command=self.handler)
        self.place()
        self._after_create()

    def __str__(self):
        if hasattr(self.parent, '_radio_var'):
            return "1" if self.parent._radio_var.get() == self.caption else "0"
        return "0"

class LBGroupbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = tk.LabelFrame(self.get_container(), text=self.caption)
        self.place()
        self._after_create()

class LBListview(LBControl):
    def create_widget(self):
        if self.frame: return
        self.frame = tk.Frame(self.get_container())
        self.scrollbar = tk.Scrollbar(self.frame)
        self.widget = ttk.Treeview(self.frame, yscrollcommand=self.scrollbar.set, show="headings")
        self.scrollbar.config(command=self.widget.yview)
        
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if self.handler:
            self.widget.bind('<<TreeviewSelect>>', lambda e: self.handler())
            
        self.place()
        self._after_create()
    
    def set_columns(self, columns):
        if isinstance(columns, str):
            columns = columns.split(',')
        self.widget["columns"] = columns
        for col in columns:
            self.widget.heading(col, text=col)
            self.widget.column(col, width=100)

    def add_row(self, values):
        self.widget.insert("", tk.END, values=values)

    def fill_from_db(self, db_handle, sql):
        if isinstance(db_handle, str):
            db = get_handle(db_handle)
        else:
            db = db_handle
        
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                # Clear existing rows
                for item in self.widget.get_children():
                    self.widget.delete(item)
                
                # Set columns based on first row if not already set
                if not self.widget["columns"]:
                    headers = list(results[0].keys())
                    self.set_columns(headers)
                
                for r in results:
                    self.add_row(list(r.values()))

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("fill "):
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        elif cmd_lower.startswith("setcolumns "):
            self.set_columns(cmd_strip[11:].strip())
        elif cmd_lower.startswith("columnwidths "):
            widths = cmd_strip[13:].split(',')
            if self.widget:
                cols = self.widget["columns"]
                for i, w in enumerate(widths):
                    if i < len(cols):
                        self.widget.column(cols[i], width=_int(w))
        elif cmd_lower == "showgrid":
            if self.widget:
                self.widget.config(show="headings")
        elif cmd_lower.startswith("additem "):
            # Split and then unquote/decode each item
            values = [_decode_escapes(unquote(v.strip())) for v in cmd_strip[8:].split(',')]
            self.add_row(values)
        elif cmd_lower == "clear":
            for item in self.widget.get_children():
                self.widget.delete(item)
        elif cmd_lower.startswith("doubleclick "):
            handler_name = cmd_strip[12:].strip().replace("[", "").replace("]", "").lower()
            if self.widget:
                import __main__
                handler = getattr(__main__, handler_name, None)
                if not handler and _handles:
                    handler = getattr(_handles, handler_name, None)
                if handler:
                    self.widget.bind("<Double-1>", lambda e: handler())
        else:
            super().command(cmd)

class LBDatepicker(LBControl):
    def create_widget(self):
        if self.widget: return
        try:
            from tkcalendar import DateEntry
            self.widget = DateEntry(self.get_container())
        except ImportError:
            logger.warning("tkcalendar not installed, falling back to Entry for Datepicker")
            self.widget = tk.Entry(self.get_container())
        self.place()
        self._after_create()

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("set "):
            val = _decode_escapes(unquote(cmd_strip[4:].strip()))
            try:
                # Try DateEntry set_date
                if hasattr(self.widget, 'set_date'):
                    self.widget.set_date(val)
                else:
                    # Fallback Entry
                    self.widget.delete(0, tk.END)
                    self.widget.insert(0, val)
            except:
                pass
        else:
            super().command(cmd)

class LBStringGrid(LBControl):
    def create_widget(self):
        if self.frame: return
        self.frame = tk.Frame(self.get_container())
        self.scrollbar_y = tk.Scrollbar(self.frame)
        self.scrollbar_x = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.widget = ttk.Treeview(self.frame, show="headings", 
                                   yscrollcommand=self.scrollbar_y.set,
                                   xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar_y.config(command=self.widget.yview)
        self.scrollbar_x.config(command=self.widget.xview)
        
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.place()
        self._after_create()

    def set_grid_data(self, data, headers=None):
        if not self.widget: return
        self.widget.delete(*self.widget.get_children())
        if headers:
            self.widget["columns"] = headers
            for h in headers:
                self.widget.heading(h, text=h)
                self.widget.column(h, width=100)
        for row in data:
            self.widget.insert("", tk.END, values=row)

    def fill_from_db(self, db_handle, sql):
        # Resolve db_handle if it's a name
        if isinstance(db_handle, str):
            db = get_handle(db_handle)
        else:
            db = db_handle
        
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                headers = list(results[0].keys())
                data = [list(r.values()) for r in results]
                self.set_grid_data(data, headers)

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        if cmd_lower.startswith("fill "):
            # Syntax: fill #db "SELECT..."
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        elif cmd_lower.startswith("setcolumns "):
            # Grid handles columns differently but we can reuse set_grid_data logic
            columns = cmd_strip[11:].split(',')
            self.widget["columns"] = columns
            for h in columns:
                self.widget.heading(h, text=h)
                self.widget.column(h, width=100)
        elif cmd_lower.startswith("columnwidths "):
            widths = cmd_strip[13:].split(',')
            if self.widget:
                cols = self.widget["columns"]
                for i, w in enumerate(widths):
                    if i < len(cols):
                        self.widget.column(cols[i], width=_int(w))
        elif cmd_lower == "showgrid":
            if self.widget:
                self.widget.config(show="headings")
        elif cmd_lower.startswith("additem "):
            values = [_decode_escapes(unquote(v.strip())) for v in cmd_strip[8:].split(',')]
            self.widget.insert("", tk.END, values=values)
        elif cmd_lower == "clear":
            if self.widget: self.widget.delete(*self.widget.get_children())
        elif cmd_lower.startswith("doubleclick "):
            handler_name = cmd_strip[12:].strip().replace("[", "").replace("]", "").lower()
            # Try to find the handler in the handles module or globals
            if self.widget:
                # We'll use a deferred approach or search globals
                import __main__
                handler = getattr(__main__, handler_name, None)
                if not handler and _handles:
                    handler = getattr(_handles, handler_name, None)
                
                if handler:
                    self.widget.bind("<Double-1>", lambda e: handler())
                else:
                    logger.warning(f"Handler {handler_name} not found for doubleclick")
        else:
            super().command(cmd)

    def import_csv(self, filename):
        try:
            with open(filename, newline='') as f:
                reader = csv.reader(f)
                data = list(reader)
                if data:
                    self.set_grid_data(data[1:], headers=data[0])
        except Exception as e:
            logger.error(f"Failed to import CSV {filename}: {e}")

class LBGraphicbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = tk.Canvas(self.get_container(), highlightthickness=0)
        self.place()
        self._after_create()
        self.curr_color = "black"
        self.curr_pos = (0, 0)
        self.pen_down = True

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return

        parts = cmd_lower.split()
        if not parts: return

        if cmd_lower.startswith("when leftbuttondown "):
            handler_name = cmd_strip[20:].strip().replace("[", "").replace("]", "").lower()
            self.widget.bind("<Button-1>", lambda e: self._handle_click(e, handler_name))
        elif parts[0] == "line" and len(parts) >= 5:
            self.widget.create_line(_int(parts[1]), _int(parts[2]), _int(parts[3]), _int(parts[4]), fill=self.curr_color)
        elif parts[0] == "box" and len(parts) >= 5:
            self.widget.create_rectangle(_int(parts[1]), _int(parts[2]), _int(parts[3]), _int(parts[4]), outline=self.curr_color)
        elif parts[0] == "fill" and len(parts) >= 5:
            self.widget.create_rectangle(_int(parts[1]), _int(parts[2]), _int(parts[3]), _int(parts[4]), fill=self.curr_color, outline=self.curr_color)
        elif parts[0] == "circle" and len(parts) >= 4:
            r = _int(parts[3])
            x, y = _int(parts[1]), _int(parts[2])
            self.widget.create_oval(x-r, y-r, x+r, y+r, outline=self.curr_color)
        elif parts[0] == "color" and len(parts) >= 2:
            self.curr_color = parts[1]
        elif cmd_lower == "clear":
            self.widget.delete("all")
        elif cmd_lower == "flush":
            self.widget.update_idletasks()
        else:
            super().command(cmd)

    def _handle_click(self, event, handler_name):
        # Set MouseX, MouseY in LB builtins
        setattr(builtins, 'MouseX', event.x)
        setattr(builtins, 'MouseY', event.y)
        # Call handler
        import __main__
        handler = getattr(__main__, handler_name, None)
        if not handler and _handles:
            handler = getattr(_handles, handler_name, None)
        if handler:
            handler()

class LBTabControl(LBControl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tab_frames = []
        self.pending_tabs = []
        self.pending_appends = [] # list of (tab_index, ctrl_handle)

    def create_widget(self):
        if self.widget: return
        self.widget = ttk.Notebook(self.get_container())
        for label in self.pending_tabs:
            self._do_add_tab(label)
        self.pending_tabs = []
        for tab_idx, ctrl_handle in self.pending_appends:
            self._do_append(tab_idx, ctrl_handle)
        self.pending_appends = []
        self.place()
        self._after_create()

    def _do_add_tab(self, label):
        frame = tk.Frame(self.widget)
        self.widget.add(frame, text=label)
        self.tab_frames.append(frame)
        # Select the newly added tab so subsequent 'append' commands target it
        self.widget.select(frame)

    def _do_append(self, tab_idx, ctrl_handle_name):
        ctrl = get_handle(ctrl_handle_name)
        if ctrl:
            try:
                target_frame = self.tab_frames[tab_idx]
                ctrl.reparent(target_frame)
            except Exception as e:
                logger.warning(f"Failed to append control to tab: {e}")
    
    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if cmd_lower.startswith("addtab "):
            label = _decode_escapes(unquote(cmd_strip[7:].strip()))
            if self.widget:
                self._do_add_tab(label)
            else:
                self.pending_tabs.append(label)
        elif cmd_lower.startswith("append "):
            ctrl_handle_name = cmd_strip[7:].strip()
            if ctrl_handle_name.startswith("#"):
                ctrl_handle_name = ctrl_handle_name[1:].replace('.', '_').lower()
            
            if self.widget:
                try:
                    current_tab_idx = self.widget.index("current")
                    self._do_append(current_tab_idx, ctrl_handle_name)
                except: pass
            else:
                # Use the last added tab as target for pending append
                tab_idx = len(self.pending_tabs) - 1
                if tab_idx >= 0:
                    self.pending_appends.append((tab_idx, ctrl_handle_name))
        elif cmd_lower.startswith("selectindex "):
            try:
                idx = _int(cmd_lower[12:])
                if self.widget:
                    self.widget.select(idx)
            except:
                pass
        else:
            super().command(cmd)
