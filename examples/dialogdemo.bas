' Liberty BASIC Dialog Demo
' Comprehensive showcase of all GUI elements and multi-window management

WindowWidth = 650
WindowHeight = 750

' --- Menus ---
MENU #demo, "&File", "&Exit", [quit]
MENU #demo, "&Windows", "Open Subwindow", [openSub], "---", "Show Info", [showInfo]
MENU #demo, "&Options", "Checkbox On", [chkOn], "Checkbox Off", [chkOff]

' --- Tab Control ---
TABCONTROL #demo.tabs, 5, 5, 630, 650

' --- Tab 1: Basic Controls ---
PRINT #demo.tabs, "addtab Basic Controls"

STATICTEXT #demo.lbl1, "Liberty BASIC GUI elements:", 20, 20, 250, 20
TEXTBOX #demo.txt, "Hello World!", 20, 50, 200, 25
BUTTON #demo.btn, "Notice Me", [btnNotice], UL, 230, 48, 100, 30

CHECKBOX #demo.chk, "Enable experimental features", [chkClick], UL, 20, 90, 250, 20
GROUPBOX #demo.grp, "Select Mode", 20, 120, 200, 100
RADIOBUTTON #demo.r1, "Standard Mode", [rClick], UL, 30, 145, 150, 20
RADIOBUTTON #demo.r2, "Advanced Mode", [rClick], UL, 30, 175, 150, 20
PRINT #demo.r1, "set"

COMBOBOX #demo.cb, "Red,Green,Blue,Yellow", [cbClick], UL, 20, 230, 200, 25
PRINT #demo.cb, "set Blue"

LISTBOX #demo.lb, "", 20, 270, 200, 100
PRINT #demo.lb, "additem Selection 1"
PRINT #demo.lb, "additem Selection 2"
PRINT #demo.lb, "additem Selection 3"

PRINT #demo.tabs, "append #demo.lbl1"
PRINT #demo.tabs, "append #demo.txt"
PRINT #demo.tabs, "append #demo.btn"
PRINT #demo.tabs, "append #demo.chk"
PRINT #demo.tabs, "append #demo.grp"
PRINT #demo.tabs, "append #demo.r1"
PRINT #demo.tabs, "append #demo.r2"
PRINT #demo.tabs, "append #demo.cb"
PRINT #demo.tabs, "append #demo.lb"

' --- Tab 2: Advanced Controls ---
PRINT #demo.tabs, "addtab Advanced"

STATICTEXT #demo.lbl2, "Multi-line Text Editor:", 20, 20, 200, 20
TEXTEDITOR #demo.edit, "Line 1\nLine 2\nLine 3", 20, 40, 580, 120

STATICTEXT #demo.lbl3, "ListView with Columns:", 20, 170, 200, 20
LISTVIEW #demo.lv, "", 20, 190, 580, 150
PRINT #demo.lv, "setcolumns ID,Description,Status"
PRINT #demo.lv, "additem 1,First task,Done"
PRINT #demo.lv, "additem 2,Second task,Pending"
PRINT #demo.lv, "columnwidths 50,400,100"
PRINT #demo.lv, "showgrid"

STATICTEXT #demo.lbl4, "Date Picker:", 20, 350, 100, 20
DATEPICKER #demo.dp, 120, 350, 150, 25

STATICTEXT #demo.lbl5, "Data Grid (PSTRINGGRID):", 20, 390, 200, 20
PSTRINGGRID #demo.grid, "", 20, 410, 580, 150
PRINT #demo.grid, "setcolumns Col 1,Col 2,Col 3"
PRINT #demo.grid, "additem A1,B1,C1"
PRINT #demo.grid, "additem A2,B2,C2"
PRINT #demo.grid, "showgrid"

PRINT #demo.tabs, "append #demo.lbl2"
PRINT #demo.tabs, "append #demo.edit"
PRINT #demo.tabs, "append #demo.lbl3"
PRINT #demo.tabs, "append #demo.lv"
PRINT #demo.tabs, "append #demo.lbl4"
PRINT #demo.tabs, "append #demo.dp"
PRINT #demo.tabs, "append #demo.lbl5"
PRINT #demo.tabs, "append #demo.grid"

' --- Status Bar ---
STATICTEXT #demo.status, "Application Ready.", 5, 660, 630, 20

' --- Open Main Window ---
OPEN "GUI & Dialogs Demo" FOR window AS #demo

WAIT

' --- Subroutines ---

SUB btnNotice
    msg$ = #demo.txt
    NOTICE "The message is: " + msg$
    PRINT #demo.status, "set Notice displayed."
END SUB

SUB chkClick
    PRINT #demo.status, "set Checkbox state changed."
END SUB

SUB rClick
    PRINT #demo.status, "set Radio mode changed."
END SUB

SUB cbClick
    c$ = #demo.cb
    PRINT #demo.status, "set Color selected: " + c$
END SUB

SUB openSub
    STATICTEXT #sub.msg, "This is a secondary window.", 20, 20, 250, 20
    BUTTON #sub.cls, "Close Me", [closeSub], UL, 20, 60, 100, 30
    OPEN "Subwindow" FOR window AS #sub
    PRINT #demo.status, "set Subwindow opened."
END SUB

SUB closeSub
    CLOSE #sub
    PRINT #demo.status, "set Subwindow closed."
END SUB

SUB showInfo
    NOTICE "Dialog Demo v1.1" + CHR$(10) + "Liberty BASIC 4 Transpiler Showcase"
END SUB

SUB chkOn
    PRINT #demo.chk, "set"
END SUB

SUB chkOff
    PRINT #demo.chk, "reset"
END SUB

SUB quit
    CONFIRM "Really quit the demo?"; ok
    IF ok THEN
        CLOSE #demo
    END IF
END SUB
