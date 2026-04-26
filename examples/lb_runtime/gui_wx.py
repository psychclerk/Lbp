import csv
import logging
import sys
from lb_runtime import builtins

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lb_gui_wx")

try:
    import wx
    import wx.adv
    import wx.dataview
    WX_AVAILABLE = True
except ImportError:
    WX_AVAILABLE = False
    class wx:
        ID_ANY = -1
        ID_OK = 1
        YES = 2
        NO = 3
        OK = 4
        ICON_INFORMATION = 5
        ICON_QUESTION = 6
        TE_MULTILINE = 7
        LC_REPORT = 8
        NOT_FOUND = -1
        EVT_BUTTON = None
        EVT_MENU = None
        EVT_CLOSE = None
        EVT_LISTBOX = None
        EVT_COMBOBOX = None
        EVT_CHECKBOX = None
        EVT_RADIOBUTTON = None
        EVT_LIST_ITEM_ACTIVATED = None
        class App:
            def __init__(self, *args, **kwargs): pass
            def MainLoop(self): pass
            def ExitMainLoop(self): pass
        class Frame:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def Show(self, *args, **kwargs): pass
            def Destroy(self): pass
            def SetTitle(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
            def SetMenuBar(self, *args, **kwargs): pass
        class Panel:
            def __init__(self, *args, **kwargs): pass
        class MenuBar:
            def __init__(self): pass
            def Append(self, *args, **kwargs): pass
        class Menu:
            def __init__(self): pass
            def AppendSeparator(self): pass
            def Append(self, *args, **kwargs): pass
        class Button:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def Enable(self, *args, **kwargs): pass
            def Hide(self): pass
            def Show(self): pass
            def SetFocus(self): pass
            def SetBackgroundColour(self, *args, **kwargs): pass
            def SetForegroundColour(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class TextCtrl:
            def __init__(self, *args, **kwargs): pass
            def GetValue(self): return ""
            def SetValue(self, *args, **kwargs): pass
            def SelectAll(self): pass
            def Clear(self): pass
            def Enable(self, *args, **kwargs): pass
            def Hide(self): pass
            def Show(self): pass
            def SetFocus(self): pass
            def SetBackgroundColour(self, *args, **kwargs): pass
            def SetForegroundColour(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class StaticText:
            def __init__(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class ListBox:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def Clear(self): pass
            def Append(self, *args, **kwargs): pass
            def SetSelection(self, *args, **kwargs): pass
            def GetSelection(self): return -1
            def GetString(self, *args, **kwargs): return ""
            def SetSize(self, *args, **kwargs): pass
        class ComboBox:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def Clear(self): pass
            def Append(self, *args, **kwargs): pass
            def SetValue(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class CheckBox:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def SetValue(self, *args, **kwargs): pass
            def GetValue(self): return False
            def SetSize(self, *args, **kwargs): pass
        class RadioButton:
            def __init__(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class StaticBox:
            def __init__(self, *args, **kwargs): pass
            def SetSize(self, *args, **kwargs): pass
        class ListCtrl:
            def __init__(self, *args, **kwargs): pass
            def DeleteAllColumns(self): pass
            def InsertColumn(self, *args, **kwargs): pass
            def DeleteAllItems(self): pass
            def InsertItem(self, *args, **kwargs): return 0
            def SetItem(self, *args, **kwargs): pass
            def GetItemCount(self): return 0
            def GetColumnCount(self): return 0
            def SetColumnWidth(self, *args, **kwargs): pass
            def Bind(self, *args, **kwargs): pass
            def GetFirstSelected(self): return -1
            def GetItemText(self, *args, **kwargs): return ""
            def SetSize(self, *args, **kwargs): pass
        class Notebook:
            def __init__(self, *args, **kwargs): pass
            def AddPage(self, *args, **kwargs): pass
            def SetSelection(self, *args, **kwargs): pass
            def GetSelection(self): return 0
            def GetPageCount(self): return 0
            def SetSize(self, *args, **kwargs): pass
        class DateTime:
            def __init__(self): pass
            def ParseDate(self, *args, **kwargs): return False
            def ParseISODate(self, *args, **kwargs): return False
            def FormatISODate(self): return ""
            def IsValid(self): return False
        class TextEntryDialog:
            def __init__(self, *args, **kwargs): pass
            def ShowModal(self): return 0
            def GetValue(self): return ""
            def Destroy(self): pass
        @staticmethod
        def MessageBox(str, caption, style): return 0
    class wxadv:
        class DatePickerCtrl:
            def __init__(self, *args, **kwargs): pass
            def SetValue(self, *args, **kwargs): pass
            def GetValue(self): return None
            def SetSize(self, *args, **kwargs): pass
    class wxdataview:
        pass

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

_handles = None

def set_handles(h):
    global _handles
    _handles = h

def get_handle(name):
    if _handles and hasattr(_handles, name):
        return getattr(_handles, name)
    return None

class WindowManager:
    _app = None
    _windows = []
    _running = False

    @classmethod
    def get_app(cls):
        if cls._app is None:
            cls._app = wx.App(False)
        return cls._app

    @classmethod
    def add_window(cls, window):
        cls._windows.append(window)

    @classmethod
    def remove_window(cls, window):
        if window in cls._windows:
            cls._windows.remove(window)
        if not cls._windows and cls._app:
            cls._app.ExitMainLoop()
            cls._app = None
            cls._running = False

    @classmethod
    def run(cls):
        if cls._running:
            return
        if not WX_AVAILABLE:
            logger.info("wxPython not available, skipping event loop.")
            return
        app = cls.get_app()
        if cls._windows:
            cls._running = True
            app.MainLoop()
        cls._running = False

def run_event_loop():
    WindowManager.run()

def notice(msg):
    if not WX_AVAILABLE:
        print(f"NOTICE: {msg}")
        return
    WindowManager.get_app()
    wx.MessageBox(_decode_escapes(str(msg)), "Notice", wx.OK | wx.ICON_INFORMATION)

def confirm(msg):
    if not WX_AVAILABLE:
        print(f"CONFIRM: {msg}")
        return 1
    WindowManager.get_app()
    res = wx.MessageBox(_decode_escapes(str(msg)), "Confirm", wx.YES_NO | wx.ICON_QUESTION)
    return 1 if res == wx.YES else 0

def prompt(msg):
    if not WX_AVAILABLE:
        print(f"PROMPT: {msg}")
        return ""
    WindowManager.get_app()
    dlg = wx.TextEntryDialog(None, _decode_escapes(str(msg)), "Prompt")
    if dlg.ShowModal() == wx.ID_OK:
        res = dlg.GetValue()
    else:
        res = ""
    dlg.Destroy()
    return res

class LBWindow:
    def __init__(self):
        self.root = None
        self.panel = None
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
        WindowManager.get_app()
        
        try:
            w = _int(width if width is not None else getattr(builtins, 'WindowWidth', 800))
            h = _int(height if height is not None else getattr(builtins, 'WindowHeight', 600))
            x = _int(getattr(builtins, 'UpperLeftX', 100))
            y = _int(getattr(builtins, 'UpperLeftY', 100))
        except (ValueError, TypeError):
            w, h, x, y = 800, 600, 100, 100

        self.root = wx.Frame(None, title=title, size=(w, h), pos=(x, y))
        self.panel = wx.Panel(self.root)
        
        self.root.Bind(wx.EVT_CLOSE, self.on_close)
        WindowManager.add_window(self)

        # Initialize Menus
        if self.menus:
            menubar = wx.MenuBar()
            for m_title, m_items in self.menus:
                menu = wx.Menu()
                clean_title = m_title.replace('&', '')
                for label, handler in m_items:
                    if label in ("", "---"):
                        menu.AppendSeparator()
                    else:
                        clean_label = label.replace('&', '')
                        item = menu.Append(wx.ID_ANY, clean_label)
                        if handler:
                            self.root.Bind(wx.EVT_MENU, lambda e, h=handler: h(), item)
                menubar.Append(menu, clean_title)
            self.root.SetMenuBar(menubar)

        # Initialize all registered controls
        for ctrl in self.controls:
            try:
                ctrl.create_widget()
            except Exception as e:
                logger.error(f"Failed to create control {ctrl}: {e}")
        
        if WX_AVAILABLE:
            self.panel.Layout()
            self.panel.Refresh()

        self.root.Show()

    def on_close(self, event):
        self.close()

    def add_menu(self, title, items):
        self.menus.append((title, items))

    def close(self):
        if self.root:
            self.root.Destroy()
            self.root = None
            WindowManager.remove_window(self)

    def command(self, cmd):
        if not isinstance(cmd, str): return
        raw_cmd = cmd.strip()
        cmd_lower = raw_cmd.lower()
        if cmd_lower.startswith("title "):
            if self.root: self.root.SetTitle(_decode_escapes(unquote(raw_cmd[6:].strip())))
        elif cmd_lower.startswith("resize "):
            try:
                parts = cmd_lower[7:].split()
                if len(parts) >= 2 and self.root:
                    w = _int(parts[0])
                    h = _int(parts[1])
                    self.root.SetSize((w, h))
            except:
                pass

class LBControl:
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
        if parent:
            if hasattr(parent, 'controls'):
                parent.controls.append(self)
            if hasattr(parent, 'root') and parent.root:
                self.create_widget()

    def create_widget(self):
        if self.widget: return True
        return False

    def _after_create(self):
        for cmd in self.pending_commands:
            self.command(cmd)
        self.pending_commands = []
        if self.widget and WX_AVAILABLE:
            self.widget.Refresh()
            self.widget.Update()

    def get_container(self):
        if self.container:
            return self.container
        p = self.parent
        while p and not hasattr(p, 'panel'):
            p = p.parent
        return p.panel if p else None

    def reparent(self, new_container):
        """Re-parents the control to a new container by recreating it."""
        # Store current state
        state = self._get_widget_state()
        
        if self.widget:
            self.widget.Destroy()
            self.widget = None
            
        self.container = new_container
        self.create_widget()
        
        # Restore state
        self._set_widget_state(state)

    def _get_widget_state(self):
        state = {'value': str(self)}
        if self.widget:
            if isinstance(self.widget, wx.ListBox):
                state['items'] = [self.widget.GetString(i) for i in range(self.widget.GetCount())]
                state['selection'] = self.widget.GetSelection()
            elif isinstance(self.widget, wx.ComboBox):
                state['items'] = [self.widget.GetString(i) for i in range(self.widget.GetCount())]
            elif isinstance(self.widget, wx.ListCtrl):
                state['col_count'] = self.widget.GetColumnCount()
                state['columns'] = []
                for j in range(state['col_count']):
                    col = self.widget.GetColumn(j)
                    state['columns'].append((col.GetText(), col.GetWidth()))
                items = []
                for i in range(self.widget.GetItemCount()):
                    row = []
                    for j in range(state['col_count']):
                        row.append(self.widget.GetItemText(i, j))
                    items.append(row)
                state['items'] = items
        return state

    def _set_widget_state(self, state):
        if not self.widget: return
        
        if 'columns' in state and isinstance(self.widget, wx.ListCtrl):
            self.widget.DeleteAllColumns()
            for i, (text, width) in enumerate(state['columns']):
                self.widget.InsertColumn(i, text, width=width)

        if 'items' in state:
            if isinstance(self.widget, wx.ListBox):
                self.widget.Clear()
                for item in state['items']:
                    self.widget.Append(item)
                if 'selection' in state and state['selection'] != wx.NOT_FOUND:
                    self.widget.SetSelection(state['selection'])
            elif isinstance(self.widget, wx.ComboBox):
                self.widget.Clear()
                for item in state['items']:
                    self.widget.Append(item)
            elif isinstance(self.widget, wx.ListCtrl):
                self.widget.DeleteAllItems()
                for item in state['items']:
                    index = self.widget.InsertItem(self.widget.GetItemCount(), str(item[0]))
                    for i, val in enumerate(item[1:]):
                        self.widget.SetItem(index, i + 1, str(val))
        
        if state.get('value') and state['value'] != self.caption:
            self.command(f"set {state['value']}")

    def place(self):
        if self.widget:
            self.widget.SetSize(_int(self.x), _int(self.y), _int(self.w), _int(self.h))

    def command(self, cmd):
        if not isinstance(cmd, str): return
        raw_cmd = cmd.strip()
        cmd_lower = raw_cmd.lower()
        if not self.widget:
            self.pending_commands.append(raw_cmd)
            return
        try:
            if cmd_lower == "enable":
                self.widget.Enable(True)
            elif cmd_lower == "disable":
                self.widget.Enable(False)
            elif cmd_lower == "hide":
                self.widget.Hide()
            elif cmd_lower == "show":
                self.widget.Show()
            elif cmd_lower == "setfocus":
                self.widget.SetFocus()
            elif cmd_lower.startswith("backcolor "):
                self.widget.SetBackgroundColour(raw_cmd[10:].strip())
            elif cmd_lower.startswith("color "):
                self.widget.SetForegroundColour(raw_cmd[6:].strip())
        except Exception as e:
            logger.warning(f"Failed to execute command '{raw_cmd}' on {self.__class__.__name__}: {e}")

    def __eq__(self, other):
        return str(self) == str(other)

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)

    def __str__(self):
        if self.widget:
            try:
                if isinstance(self.widget, wx.ListBox):
                    sel = self.widget.GetSelection()
                    return str(self.widget.GetString(sel)) if sel != wx.NOT_FOUND else ""
                if isinstance(self.widget, wx.ListCtrl):
                    sel = self.widget.GetFirstSelected()
                    if sel != -1:
                        return self.widget.GetItemText(sel)
                    return ""
                if hasattr(self.widget, 'GetValue'):
                    return str(self.widget.GetValue())
            except:
                pass
        return str(self.caption) if self.caption else ""

class LBButton(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.Button(self.get_container(), label=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        if self.handler:
            self.widget.Bind(wx.EVT_BUTTON, lambda e: self.handler())
        self._after_create()

class LBTextbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.TextCtrl(self.get_container(), value=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        self._after_create()
    
    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return
        if cmd_lower.startswith("set "):
            self.widget.SetValue(_decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower == "selectall":
            self.widget.SelectAll()
        else:
            super().command(cmd)

class LBTexteditor(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.TextCtrl(self.get_container(), value=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)), style=wx.TE_MULTILINE)
        self._after_create()

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return
        if cmd_lower.startswith("set "):
            self.widget.SetValue(_decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower == "clear":
            self.widget.Clear()
        else:
            super().command(cmd)

class LBStatictext(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.StaticText(self.get_container(), label=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        self._after_create()

class LBListbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.ListBox(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        if self.handler:
            self.widget.Bind(wx.EVT_LISTBOX, lambda e: self.handler())
        self._after_create()
    
    def fill_from_db(self, db_handle, sql):
        db = get_handle(db_handle) if isinstance(db_handle, str) else db_handle
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                self.widget.Clear()
                for r in results:
                    val = " ".join(str(v) for v in r.values())
                    self.widget.Append(val)
                if WX_AVAILABLE:
                    self.widget.Refresh()
                    self.widget.Update()

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return
        if cmd_lower.startswith("additem "):
            self.widget.Append(_decode_escapes(unquote(cmd_strip[8:].strip())))
            if WX_AVAILABLE:
                self.widget.Refresh()
                self.widget.Update()
        elif cmd_lower.startswith("fill "):
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        elif cmd_lower == "clear":
            self.widget.Clear()
        elif cmd_lower.startswith("selectindex "):
            try:
                idx = _int(cmd_lower[12:])
                self.widget.SetSelection(idx)
            except: pass
        else:
            super().command(cmd)

class LBCombobox(LBControl):
    def create_widget(self):
        if self.widget: return
        choices = self.caption.split(',') if self.caption else []
        self.widget = wx.ComboBox(self.get_container(), value="", pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)), choices=choices)
        if self.handler:
            self.widget.Bind(wx.EVT_COMBOBOX, lambda e: self.handler())
        self._after_create()
    
    def fill_from_db(self, db_handle, sql):
        db = get_handle(db_handle) if isinstance(db_handle, str) else db_handle
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                self.widget.Clear()
                for r in results:
                    val = " ".join(str(v) for v in r.values())
                    self.widget.Append(val)
                if WX_AVAILABLE:
                    self.widget.Refresh()
                    self.widget.Update()

    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return
        if cmd_lower.startswith("set "):
            self.widget.SetValue(_decode_escapes(unquote(cmd_strip[4:].strip())))
        elif cmd_lower.startswith("reload "):
            self.widget.Clear()
            for c in cmd_strip[7:].split(','):
                self.widget.Append(_decode_escapes(unquote(c.strip())))
            if WX_AVAILABLE:
                self.widget.Refresh()
                self.widget.Update()
        elif cmd_lower.startswith("fill "):
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        else:
            super().command(cmd)

class LBCheckbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.CheckBox(self.get_container(), label=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        if self.handler:
            self.widget.Bind(wx.EVT_CHECKBOX, lambda e: self.handler())
        self._after_create()
    
    def command(self, cmd):
        if not isinstance(cmd, str): return
        cmd_strip = cmd.strip()
        cmd_lower = cmd_strip.lower()
        if not self.widget:
            self.pending_commands.append(cmd_strip)
            return
        if cmd_lower == "set":
            self.widget.SetValue(True)
        elif cmd_lower == "reset":
            self.widget.SetValue(False)
        else:
            super().command(cmd)
    
    def __str__(self):
        if self.widget:
            return "1" if self.widget.GetValue() else "0"
        return "0"

class LBRadiobutton(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.RadioButton(self.get_container(), label=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        if self.handler:
            self.widget.Bind(wx.EVT_RADIOBUTTON, lambda e: self.handler())
        self._after_create()

    def __str__(self):
        if self.widget:
            return "1" if self.widget.GetValue() else "0"
        return "0"

class LBGroupbox(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.StaticBox(self.get_container(), label=self.caption, pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        self._after_create()

class LBListview(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.ListCtrl(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)), style=wx.LC_REPORT)
        self._after_create()
    
    def set_columns(self, columns):
        if isinstance(columns, str):
            columns = columns.split(',')
        self.widget.DeleteAllColumns()
        for i, col in enumerate(columns):
            self.widget.InsertColumn(i, col, width=100)
        if WX_AVAILABLE:
            self.widget.Refresh()
            self.widget.Update()

    def add_row(self, values):
        index = self.widget.InsertItem(self.widget.GetItemCount(), str(values[0]))
        for i, val in enumerate(values[1:]):
            self.widget.SetItem(index, i + 1, str(val))

    def fill_from_db(self, db_handle, sql):
        db = get_handle(db_handle) if isinstance(db_handle, str) else db_handle
        if db and hasattr(db, 'query'):
            results = db.query(sql)
            if results:
                self.widget.DeleteAllItems()
                if self.widget.GetColumnCount() == 0:
                    headers = list(results[0].keys())
                    self.set_columns(headers)
                for r in results:
                    self.add_row(list(r.values()))
                if WX_AVAILABLE:
                    self.widget.Refresh()
                    self.widget.Update()

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
            for i, w in enumerate(widths):
                if i < self.widget.GetColumnCount():
                    self.widget.SetColumnWidth(i, _int(w))
        elif cmd_lower == "showgrid":
            pass # wx.LC_REPORT always shows columns
        elif cmd_lower.startswith("additem "):
            values = [_decode_escapes(unquote(v.strip())) for v in cmd_strip[8:].split(',')]
            self.add_row(values)
            if WX_AVAILABLE:
                self.widget.Refresh()
                self.widget.Update()
        elif cmd_lower == "clear":
            self.widget.DeleteAllItems()
        elif cmd_lower.startswith("doubleclick "):
            handler_name = cmd_strip[12:].strip().replace("[", "").replace("]", "").lower()
            import __main__
            handler = getattr(__main__, handler_name, None)
            if not handler and _handles:
                handler = getattr(_handles, handler_name, None)
            if handler:
                self.widget.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda e: handler())
        else:
            super().command(cmd)

class LBDatepicker(LBControl):
    def create_widget(self):
        if self.widget: return
        try:
            self.widget = wx.adv.DatePickerCtrl(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        except:
            logger.warning("wx.adv.DatePickerCtrl not available, falling back to TextCtrl")
            self.widget = wx.TextCtrl(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
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
            if hasattr(self.widget, 'SetValue') and isinstance(self.widget, wx.adv.DatePickerCtrl):
                dt = wx.DateTime()
                if dt.ParseDate(val) or dt.ParseISODate(val):
                    self.widget.SetValue(dt)
            elif hasattr(self.widget, 'SetValue'):
                self.widget.SetValue(val)
        else:
            super().command(cmd)
    
    def __str__(self):
        if self.widget:
            if isinstance(self.widget, wx.adv.DatePickerCtrl):
                dt = self.widget.GetValue()
                return dt.FormatISODate() if dt.IsValid() else ""
            return self.widget.GetValue()
        return ""

class LBStringGrid(LBControl):
    def create_widget(self):
        if self.widget: return
        self.widget = wx.ListCtrl(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)), style=wx.LC_REPORT)
        self._after_create()

    def set_grid_data(self, data, headers=None):
        if not self.widget: return
        self.widget.DeleteAllItems()
        if headers:
            self.widget.DeleteAllColumns()
            for i, h in enumerate(headers):
                self.widget.InsertColumn(i, h, width=100)
        for row in data:
            index = self.widget.InsertItem(self.widget.GetItemCount(), str(row[0]))
            for i, val in enumerate(row[1:]):
                self.widget.SetItem(index, i + 1, str(val))
        if WX_AVAILABLE:
            self.widget.Refresh()
            self.widget.Update()

    def fill_from_db(self, db_handle, sql):
        db = get_handle(db_handle) if isinstance(db_handle, str) else db_handle
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
            parts = cmd_strip.split(None, 2)
            if len(parts) >= 3:
                db_handle_name = parts[1][1:] if parts[1].startswith('#') else parts[1]
                sql = unquote(parts[2].strip())
                self.fill_from_db(db_handle_name, sql)
        elif cmd_lower.startswith("setcolumns "):
            columns = cmd_strip[11:].split(',')
            self.widget.DeleteAllColumns()
            for i, h in enumerate(columns):
                self.widget.InsertColumn(i, h, width=100)
            if WX_AVAILABLE:
                self.widget.Refresh()
                self.widget.Update()
        elif cmd_lower.startswith("columnwidths "):
            widths = cmd_strip[13:].split(',')
            for i, w in enumerate(widths):
                if i < self.widget.GetColumnCount():
                    self.widget.SetColumnWidth(i, _int(w))
        elif cmd_lower == "clear":
            self.widget.DeleteAllItems()
        elif cmd_lower.startswith("additem "):
            values = [_decode_escapes(unquote(v.strip())) for v in cmd_strip[8:].split(',')]
            self.add_row(values)
            if WX_AVAILABLE:
                self.widget.Refresh()
                self.widget.Update()
        elif cmd_lower.startswith("doubleclick "):
            handler_name = cmd_strip[12:].strip().replace("[", "").replace("]", "").lower()
            import __main__
            handler = getattr(__main__, handler_name, None)
            if not handler and _handles:
                handler = getattr(_handles, handler_name, None)
            if handler:
                self.widget.Bind(wx.EVT_LIST_ITEM_ACTIVATED, lambda e: handler())
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
        self.widget = wx.Panel(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        self.widget.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.widget.Bind(wx.EVT_PAINT, self.on_paint)
        self.buffer = wx.Bitmap(_int(self.w), _int(self.h))
        self.clear_buffer()
        self._after_create()
        self.curr_color = wx.BLACK
        self.curr_pos = (0, 0)

    def clear_buffer(self):
        dc = wx.MemoryDC(self.buffer)
        dc.SetBackground(wx.Brush(wx.WHITE))
        dc.Clear()
        del dc

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self.widget)
        dc.DrawBitmap(self.buffer, 0, 0)

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
            self.widget.Bind(wx.EVT_LEFT_DOWN, lambda e: self._handle_click(e, handler_name))
            return
        
        dc = wx.MemoryDC(self.buffer)
        dc.SetPen(wx.Pen(self.curr_color))
        dc.SetBrush(wx.Brush(self.curr_color, wx.BRUSHSTYLE_TRANSPARENT))

        if parts[0] == "line" and len(parts) >= 5:
            dc.DrawLine(_int(parts[1]), _int(parts[2]), _int(parts[3]), _int(parts[4]))
        elif parts[0] == "box" and len(parts) >= 5:
            dc.DrawRectangle(_int(parts[1]), _int(parts[2]), _int(parts[3]) - _int(parts[1]), _int(parts[4]) - _int(parts[2]))
        elif parts[0] == "fill" and len(parts) >= 5:
            dc.SetBrush(wx.Brush(self.curr_color))
            dc.DrawRectangle(_int(parts[1]), _int(parts[2]), _int(parts[3]) - _int(parts[1]), _int(parts[4]) - _int(parts[2]))
        elif parts[0] == "circle" and len(parts) >= 4:
            dc.DrawCircle(_int(parts[1]), _int(parts[2]), _int(parts[3]))
        elif parts[0] == "color" and len(parts) >= 2:
            self.curr_color = parts[1]
        elif cmd_lower == "clear":
            self.clear_buffer()
        
        del dc
        self.widget.Refresh()
        self.widget.Update()
        super().command(cmd)

    def _handle_click(self, event, handler_name):
        # Set MouseX, MouseY in LB builtins
        setattr(builtins, 'MouseX', event.GetX())
        setattr(builtins, 'MouseY', event.GetY())
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
        self.tab_panels = []
        self.pending_tabs = []
        self.pending_appends = []

    def create_widget(self):
        if self.widget: return
        self.widget = wx.Notebook(self.get_container(), pos=(_int(self.x), _int(self.y)), size=(_int(self.w), _int(self.h)))
        for label in self.pending_tabs:
            self._do_add_tab(label)
        self.pending_tabs = []
        for tab_idx, ctrl_handle in self.pending_appends:
            self._do_append(tab_idx, ctrl_handle)
        self.pending_appends = []
        self._after_create()

    def _do_add_tab(self, label):
        panel = wx.Panel(self.widget)
        self.widget.AddPage(panel, label)
        self.tab_panels.append(panel)
        self.widget.SetSelection(self.widget.GetPageCount() - 1)

    def _do_append(self, tab_idx, ctrl_handle_name):
        ctrl = get_handle(ctrl_handle_name)
        if ctrl:
            try:
                target_panel = self.tab_panels[tab_idx]
                ctrl.reparent(target_panel)
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
                current_tab_idx = self.widget.GetSelection()
                self._do_append(current_tab_idx, ctrl_handle_name)
            else:
                tab_idx = len(self.pending_tabs) - 1
                if tab_idx >= 0:
                    self.pending_appends.append((tab_idx, ctrl_handle_name))
        elif cmd_lower.startswith("selectindex "):
            try:
                idx = _int(cmd_lower[12:])
                if self.widget:
                    self.widget.SetSelection(idx)
            except: pass
        else:
            super().command(cmd)
