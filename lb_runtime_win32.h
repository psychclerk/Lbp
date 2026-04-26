/* 
 * Liberty BASIC Win32 Runtime Header for C99
 * Designed for Pelles C and native Win32 API.
 */

#ifndef LB_RUNTIME_WIN32_H
#define LB_RUNTIME_WIN32_H

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <commctrl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static inline char* lb_strdup(const char* s) {
    size_t len = strlen(s) + 1;
    char* res = (char*)malloc(len);
    if (res) memcpy(res, s, len);
    return res;
}

// Link with common controls
#pragma comment(lib, "comctl32.lib")

// Global state
static HINSTANCE g_hInstance;
static int g_nCmdShow;
static int WindowWidth = 800;
static int WindowHeight = 600;
static int UpperLeftX = 100;
static int UpperLeftY = 100;
static int DisplayWidth = 1024;
static int DisplayHeight = 768;
static int MouseX = 0;
static int MouseY = 0;
static void (*g_menu_handlers[256])();
static int g_menu_count = 0;
static HFONT g_hFont = NULL;

// Handle Mapping
typedef struct {
    char name[64];
    HWND hwnd;
} HandleEntry;

static HandleEntry g_handle_map[256];
static int g_handle_count = 0;

static inline void lb_register_handle(const char* name, void* handle) {
    if (!IsWindow((HWND)handle)) return;
    // Check if handle already exists, update it if so
    for (int i = 0; i < g_handle_count; i++) {
        if (strcmp(g_handle_map[i].name, name) == 0) {
            g_handle_map[i].hwnd = (HWND)handle;
            return;
        }
    }
    // Otherwise add new entry
    if (g_handle_count < 256) {
        strncpy(g_handle_map[g_handle_count].name, name, 63);
        g_handle_map[g_handle_count].name[63] = 0;
        g_handle_map[g_handle_count].hwnd = (HWND)handle;
        g_handle_count++;
    }
}

static inline HWND lb_find_handle(const char* name) {
    for (int i = 0; i < g_handle_count; i++) {
        if (strcmp(g_handle_map[i].name, name) == 0) {
            return g_handle_map[i].hwnd;
        }
    }
    return NULL;
}

// Tab Control Info
typedef struct {
    HWND pages[32];
    int count;
} LB_TabInfo;

// Escape decoding
static inline const char* lb_decode_escapes(const char* s) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    
    int j = 0;
    for (int i = 0; s[i] && j < 65535; i++) {
        if (s[i] == '\\' && s[i+1]) {
            i++;
            if (s[i] == 'n') {
                buf[j++] = '\r';
                if (j < 65535) buf[j++] = '\n';
            } else if (s[i] == 'r') {
                buf[j++] = '\r';
            } else if (s[i] == 't') {
                buf[j++] = '\t';
            } else if (s[i] == '\\') {
                buf[j++] = '\\';
            } else {
                buf[j++] = s[i];
            }
        } else if (s[i] == '\n') {
            // Convert literal \n to \r\n if not preceded by \r
            if (j > 0 && buf[j-1] != '\r') {
                buf[j++] = '\r';
            }
            if (j < 65535) buf[j++] = '\n';
        } else {
            buf[j++] = s[i];
        }
    }
    buf[j] = 0;
    return buf;
}

// Forward declarations
static inline void lb_execute_db(void* db, const char* sql);

// Utility functions
static inline const char* lb_add_strings(const char* s1, const char* s2) {
    static char buffers[16][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 16;
    buf[0] = 0;
    if (s1) {
        strncpy(buf, s1, 65535);
        buf[65535] = 0;
    }
    if (s2) {
        size_t len = strlen(buf);
        if (len < 65535) {
            strncat(buf, s2, 65535 - len);
        }
    }
    return buf;
}

static inline const char* lb_str(double n) {
    static char buffers[8][64];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    sprintf(buf, "%g", n);
    return buf;
}

static inline char* lb_left(const char* s, int n) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    if (n < 0) n = 0;
    if (n > 65535) n = 65535;
    strncpy(buf, s, n);
    buf[n] = 0;
    return buf;
}

static inline char* lb_mid(const char* s, int start, int len) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    int s_len = (int)strlen(s);
    if (start > s_len || start < 1) {
        buf[0] = 0;
        return buf;
    }
    if (len < 0) len = s_len - start + 1;
    if (start + len - 1 > s_len) len = s_len - start + 1;
    if (len > 65535) len = 65535;
    strncpy(buf, s + start - 1, len);
    buf[len] = 0;
    return buf;
}

static inline char* lb_right(const char* s, int n) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    int len = (int)strlen(s);
    if (n > len) n = len;
    if (n < 0) n = 0;
    if (n > 65535) n = 65535;
    strncpy(buf, s + len - n, n);
    buf[n] = 0;
    return buf;
}

static inline char* lb_upper(const char* s) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    strncpy(buf, s, 65535);
    buf[65535] = 0;
    for (char* p = buf; *p; ++p) *p = (char)toupper(*p);
    return buf;
}

static inline char* lb_lower(const char* s) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    strncpy(buf, s, 65535);
    buf[65535] = 0;
    for (char* p = buf; *p; ++p) *p = (char)tolower(*p);
    return buf;
}

static inline double lb_instr(const char* s, const char* t) {
    if (!s || !t) return 0;
    const char* p = strstr(s, t);
    return p ? (double)(p - s + 1) : 0;
}

static inline const char* lb_chr(double n) {
    static char buffers[8][2];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    buf[0] = (char)n;
    buf[1] = 0;
    return buf;
}

static inline const char* lb_get_text(HWND hwnd) {
    static char buffers[8][65536];
    static int next = 0;
    char* buf = buffers[next];
    next = (next + 1) % 8;
    GetWindowText(hwnd, buf, 65535);
    return buf;
}

// Window Procedure
static LRESULT CALLBACK lb_WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    switch(msg) {
        case WM_MOUSEMOVE:
            MouseX = (int)(short)LOWORD(lParam);
            MouseY = (int)(short)HIWORD(lParam);
            break;
        case WM_SIZE:
            WindowWidth = (int)(short)LOWORD(lParam);
            WindowHeight = (int)(short)HIWORD(lParam);
            break;
        case WM_NOTIFY:
            if (((LPNMHDR)lParam)->code == TCN_SELCHANGE) {
                HWND hTab = ((LPNMHDR)lParam)->hwndFrom;
                LB_TabInfo* info = (LB_TabInfo*)GetWindowLongPtr(hTab, GWLP_USERDATA);
                if (info) {
                    int sel = SendMessage(hTab, TCM_GETCURSEL, 0, 0);
                    for (int i = 0; i < info->count; i++) {
                        ShowWindow(info->pages[i], i == sel ? SW_SHOW : SW_HIDE);
                    }
                }
            }
            break;
        case WM_COMMAND:
            if (lParam != 0) { // Control
                HWND hCtrl = (HWND)lParam;
                int notify = HIWORD(wParam);
                char classname[64];
                GetClassName(hCtrl, classname, sizeof(classname));
                
                if (strcmp(classname, WC_TABCONTROL) == 0) {
                    // Tab controls use WM_NOTIFY, handled above
                } else {
                    void (*handler)() = (void (*)())GetWindowLongPtr(hCtrl, GWLP_USERDATA);
                    if (handler) {
                        if (strcmp(classname, "BUTTON") == 0) {
                            if (notify == BN_CLICKED) handler();
                        } else if (strcmp(classname, "LISTBOX") == 0) {
                            if (notify == LBN_SELCHANGE) handler();
                        } else if (strcmp(classname, "COMBOBOX") == 0) {
                            if (notify == CBN_SELCHANGE) handler();
                        } else {
                            handler();
                        }
                    }
                }
            } else { // Menu
                int id = LOWORD(wParam);
                if (id >= 2000 && id < 2000 + g_menu_count) {
                    void (*handler)() = g_menu_handlers[id - 2000];
                    if (handler) handler();
                }
            }
            break;
        case WM_DESTROY:
            if (g_hFont) DeleteObject(g_hFont);
            PostQuitMessage(0);
            return 0;
    }
    return DefWindowProc(hwnd, msg, wParam, lParam);
}

// Runtime Initialization
static inline void lb_init(HINSTANCE hInst, int nCmdShow) {
    g_hInstance = hInst;
    g_nCmdShow = nCmdShow;
    
    DisplayWidth = GetSystemMetrics(SM_CXSCREEN);
    DisplayHeight = GetSystemMetrics(SM_CYSCREEN);
    
    // Suppress unused variable warnings
    (void)WindowWidth; (void)WindowHeight;
    (void)UpperLeftX; (void)UpperLeftY;
    (void)DisplayWidth; (void)DisplayHeight;
    (void)MouseX; (void)MouseY;
    
    g_hFont = CreateFont(-12, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE, ANSI_CHARSET,
        OUT_DEFAULT_PRECIS, CLIP_DEFAULT_PRECIS, DEFAULT_QUALITY,
        DEFAULT_PITCH | FF_SWISS, "Arial");
    
    InitCommonControls();
    
    WNDCLASSEX wc;
    wc.cbSize = sizeof(WNDCLASSEX);
    wc.style = CS_HREDRAW | CS_VREDRAW;
    wc.lpfnWndProc = lb_WndProc;
    wc.cbClsExtra = 0;
    wc.cbWndExtra = 0;
    wc.hInstance = g_hInstance;
    wc.hIcon = LoadIcon(NULL, IDI_APPLICATION);
    wc.hCursor = LoadCursor(NULL, IDC_ARROW);
    wc.hbrBackground = (HBRUSH)(COLOR_BTNFACE + 1);
    wc.lpszMenuName = NULL;
    wc.lpszClassName = "LBWindowClass";
    wc.hIconSm = LoadIcon(NULL, IDI_APPLICATION);
    
    RegisterClassEx(&wc);
}

static inline HWND lb_open_window(const char* title) {
    HWND hwnd = CreateWindowEx(
        WS_EX_CONTROLPARENT,
        "LBWindowClass",
        lb_decode_escapes(title),
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 800, 600,
        NULL, NULL, g_hInstance, NULL
    );
    
    ShowWindow(hwnd, g_nCmdShow);
    UpdateWindow(hwnd);
    return hwnd;
}

static inline HWND lb_create_control(const char* type, HWND parent, const char* caption, int x, int y, int w, int h, void (*handler)()) {
    const char* win_class = "STATIC";
    DWORD style = WS_CHILD | WS_VISIBLE;
    
    if (strcmp(type, "BUTTON") == 0) {
        win_class = "BUTTON";
        style |= BS_PUSHBUTTON;
    } else if (strcmp(type, "TEXTBOX") == 0) {
        win_class = "EDIT";
        style |= ES_AUTOHSCROLL | WS_BORDER;
    } else if (strcmp(type, "TEXTEDITOR") == 0) {
        win_class = "EDIT";
        style |= ES_MULTILINE | ES_AUTOVSCROLL | WS_VSCROLL | WS_BORDER;
    } else if (strcmp(type, "LISTBOX") == 0) {
        win_class = "LISTBOX";
        style |= LBS_NOTIFY | WS_VSCROLL | WS_BORDER;
    } else if (strcmp(type, "COMBOBOX") == 0) {
        win_class = "COMBOBOX";
        style |= CBS_DROPDOWN | WS_VSCROLL;
    } else if (strcmp(type, "STATICTEXT") == 0) {
        win_class = "STATIC";
    } else if (strcmp(type, "CHECKBOX") == 0) {
        win_class = "BUTTON";
        style |= BS_AUTOCHECKBOX;
    } else if (strcmp(type, "RADIOBUTTON") == 0) {
        win_class = "BUTTON";
        style |= BS_AUTORADIOBUTTON;
    } else if (strcmp(type, "GROUPBOX") == 0) {
        win_class = "BUTTON";
        style |= BS_GROUPBOX;
    } else if (strcmp(type, "LISTVIEW") == 0 || strcmp(type, "PSTRINGGRID") == 0) {
        win_class = WC_LISTVIEW;
        style |= LVS_REPORT | WS_BORDER;
    } else if (strcmp(type, "DATEPICKER") == 0) {
        win_class = DATETIMEPICK_CLASS;
    } else if (strcmp(type, "GRAPHICBOX") == 0) {
        win_class = "STATIC";
        style |= SS_OWNERDRAW;
    }
    
    HWND hwnd = CreateWindow(
        win_class,
        lb_decode_escapes(caption),
        style,
        x, y, w, h,
        parent,
        NULL,
        g_hInstance,
        NULL
    );
    if (hwnd && handler) {
        SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)handler);
    }
    if (hwnd && g_hFont) {
        SendMessage(hwnd, WM_SETFONT, (WPARAM)g_hFont, TRUE);
    }
    return hwnd;
}

static inline void lb_notice(const char* msg) {
    MessageBox(NULL, lb_decode_escapes(msg), "Notice", MB_OK | MB_ICONINFORMATION);
}

static inline int lb_confirm(const char* msg) {
    return MessageBox(NULL, lb_decode_escapes(msg), "Confirm", MB_YESNO | MB_ICONQUESTION) == IDYES;
}

static inline void lb_prompt(const char* msg, char* buffer) {
    printf("%s: ", lb_decode_escapes(msg));
    fgets(buffer, 1024, stdin);
    buffer[strcspn(buffer, "\r\n")] = 0;
}

static inline void lb_command(void* handle, const char* cmd) {
    if (!handle) return;
    if (IsWindow((HWND)handle)) {
        HWND hwnd = (HWND)handle;
        char classname[64];
        GetClassName(hwnd, classname, sizeof(classname));
        
        if (strncmp(cmd, "set ", 4) == 0) {
            SetWindowText(hwnd, lb_decode_escapes(cmd + 4));
        } else if (strcmp(cmd, "clear") == 0) {
            if (strcmp(classname, "LISTBOX") == 0) SendMessage(hwnd, LB_RESETCONTENT, 0, 0);
            else SetWindowText(hwnd, "");
        } else if (strncmp(cmd, "addtab ", 7) == 0) {
            TCITEM tie;
            tie.mask = TCIF_TEXT;
            const char* tabname = lb_decode_escapes(cmd + 7);
            tie.pszText = (char*)tabname;
            int idx = SendMessage(hwnd, TCM_INSERTITEM, SendMessage(hwnd, TCM_GETITEMCOUNT, 0, 0), (LPARAM)&tie);
            if (idx == 0) SendMessage(hwnd, TCM_SETCURSEL, 0, 0);
            
            LB_TabInfo* info = (LB_TabInfo*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
            if (info && idx < 32) {
                RECT rc;
                GetClientRect(hwnd, &rc);
                SendMessage(hwnd, TCM_ADJUSTRECT, FALSE, (LPARAM)&rc);
                HWND hPage = CreateWindowEx(WS_EX_CONTROLPARENT, "STATIC", "", WS_CHILD | (idx == 0 ? WS_VISIBLE : 0) | WS_CLIPSIBLINGS, 
                    rc.left, rc.top, rc.right - rc.left, rc.bottom - rc.top, hwnd, NULL, g_hInstance, NULL);
                if (hPage && g_hFont) SendMessage(hPage, WM_SETFONT, (WPARAM)g_hFont, TRUE);
                info->pages[idx] = hPage;
                info->count++;
            }
        } else if (strncmp(cmd, "additem ", 8) == 0) {
            const char* item = lb_decode_escapes(cmd + 8);
            if (strcmp(classname, "LISTBOX") == 0)
                SendMessage(hwnd, LB_ADDSTRING, 0, (LPARAM)item);
            else if (strcmp(classname, "COMBOBOX") == 0)
                SendMessage(hwnd, CB_ADDSTRING, 0, (LPARAM)item);
        } else if (strncmp(cmd, "selectindex ", 12) == 0) {
            int idx = atoi(cmd + 12);
            if (strcmp(classname, "LISTBOX") == 0)
                SendMessage(hwnd, LB_SETCURSEL, idx, 0);
            else if (strcmp(classname, "COMBOBOX") == 0)
                SendMessage(hwnd, CB_SETCURSEL, idx, 0);
            else if (strcmp(classname, WC_TABCONTROL) == 0) {
                SendMessage(hwnd, TCM_SETCURSEL, idx, 0);
                LB_TabInfo* info = (LB_TabInfo*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
                if (info) {
                    for (int i = 0; i < info->count; i++) {
                        ShowWindow(info->pages[i], i == idx ? SW_SHOW : SW_HIDE);
                    }
                }
            }
        } else if (strncmp(cmd, "append ", 7) == 0) {
            HWND hCtrl = lb_find_handle(cmd + 7);
            if (hCtrl) {
                LB_TabInfo* info = (LB_TabInfo*)GetWindowLongPtr(hwnd, GWLP_USERDATA);
                if (info && info->count > 0) {
                    int sel = SendMessage(hwnd, TCM_GETCURSEL, 0, 0);
                    if (sel >= 0 && sel < info->count) {
                        RECT rc;
                        GetWindowRect(hCtrl, &rc);
                        MapWindowPoints(NULL, info->pages[sel], (LPPOINT)&rc, 2);
                        SetParent(hCtrl, info->pages[sel]);
                        SetWindowPos(hCtrl, NULL, rc.left, rc.top, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
                    }
                }
            }
        }
    } else {
        // Assume it's a database or file if not a window
        if (handle == (void*)0xDBDBDBDB) {
            lb_execute_db(handle, cmd);
        } else {
            fprintf((FILE*)handle, "%s\n", cmd);
            fflush((FILE*)handle);
        }
    }
}

// Database stubs
static inline void lb_execute_db(void* db, const char* sql) {
    (void)db;
    printf("SQL Execute: %s\n", sql);
}

static inline void* lb_open_sqlite(const char* path) { 
    printf("SQLite Open: %s\n", path);
    return (void*)0xDBDBDBDB;
}

static inline void lb_fill_from_db(HWND h, void* db, const char* sql) {
    (void)h; (void)db;
    printf("SQL Query to %p: %s\n", (void*)h, sql);
}

static inline void lb_close(void* handle) {
    if (IsWindow((HWND)handle))
        DestroyWindow((HWND)handle);
    else if (handle)
        fclose((FILE*)handle);
}

static inline void lb_wait() {
    MSG msg;
    while(GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }
}

// Menu helpers
static inline HMENU lb_create_menu(HWND hwnd, const char* title) {
    HMENU hMenu = GetMenu(hwnd);
    if (!hMenu) {
        hMenu = CreateMenu();
        SetMenu(hwnd, hMenu);
    }
    HMENU hSubMenu = CreatePopupMenu();
    AppendMenu(hMenu, MF_STRING | MF_POPUP, (UINT_PTR)hSubMenu, lb_decode_escapes(title));
    DrawMenuBar(hwnd);
    return hSubMenu;
}

static inline void lb_add_menu_item(HMENU hMenu, const char* caption, void (*handler)()) {
    if (g_menu_count < 256) {
        g_menu_handlers[g_menu_count] = handler;
        AppendMenu(hMenu, MF_STRING, 2000 + g_menu_count, lb_decode_escapes(caption));
        g_menu_count++;
    }
}

// Tab Control
static inline HWND lb_create_tabcontrol(HWND parent, int x, int y, int w, int h) {
    HWND hwnd = CreateWindow(
        WC_TABCONTROL, "",
        WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS,
        x, y, w, h,
        parent, NULL, g_hInstance, NULL
    );
    if (hwnd) {
        if (g_hFont) SendMessage(hwnd, WM_SETFONT, (WPARAM)g_hFont, TRUE);
        LB_TabInfo* info = (LB_TabInfo*)calloc(1, sizeof(LB_TabInfo));
        SetWindowLongPtr(hwnd, GWLP_USERDATA, (LONG_PTR)info);
    }
    return hwnd;
}

// File I/O
static inline FILE* lb_open_file(const char* path, const char* mode) {
    const char* m = "r";
    if (strcmp(mode, "input") == 0) m = "r";
    else if (strcmp(mode, "output") == 0) m = "w";
    else if (strcmp(mode, "append") == 0) m = "a";
    return fopen(path, m);
}

static inline void lb_line_input(FILE* f, char* buffer) {
    if (f) {
        if (fgets(buffer, 1024, f)) {
            buffer[strcspn(buffer, "\r\n")] = 0;
        } else {
            buffer[0] = 0;
        }
    }
}

static inline void lb_locate(int x, int y) {
    (void)x; (void)y;
}

#endif // LB_RUNTIME_WIN32_H
