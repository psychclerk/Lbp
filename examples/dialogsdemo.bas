' Liberty BASIC GUI & Dialogs Demo
' Showcases all available GUI elements and multi-window capability

WindowWidth = 600
WindowHeight = 700

MENU #demo, "&File", "&Exit", [quit]
MENU #demo, "&Windows", "Open Subwindow", [openSub], "---", "Show Info", [showInfo]

TABCONTROL #demo.tabs, 5, 5, 580, 600

PRINT #demo.tabs, "addtab Basic Controls"

STATICTEXT #demo.lbl1, "This is a StaticText", 20, 40, 200, 20
TEXTBOX #demo.txt, "Default Text", 20, 70, 200, 25
BUTTON #demo.btn, "Click Me", [btnClick], UL, 230, 68, 100, 30

CHECKBOX #demo.chk, "Enable Option", [chkClick], UL, 20, 110, 150, 20
PRINT #demo.chk, "set"

GROUPBOX #demo.grp, "Radio Options", 20, 140, 200, 100
RADIOBUTTON #demo.r1, "Option A", [rClick], UL, 30, 165, 100, 20
RADIOBUTTON #demo.r2, "Option B", [rClick], UL, 30, 195, 100, 20
PRINT #demo.r1, "set"

COMBOBOX #demo.cb, "Apple,Banana,Cherry,Date", [cbClick], UL, 20, 250, 200, 25
PRINT #demo.cb, "set Banana"

LISTBOX #demo.lb, "", 20, 290, 200, 100
PRINT #demo.lb, "additem Item 1"
PRINT #demo.lb, "additem Item 2"
PRINT #demo.lb, "additem Item 3"

PRINT #demo.tabs, "append #demo.lbl1"
PRINT #demo.tabs, "append #demo.txt"
PRINT #demo.tabs, "append #demo.btn"
PRINT #demo.tabs, "append #demo.chk"
PRINT #demo.tabs, "append #demo.grp"
PRINT #demo.tabs, "append #demo.r1"
PRINT #demo.tabs, "append #demo.r2"
PRINT #demo.tabs, "append #demo.cb"
PRINT #demo.tabs, "append #demo.lb"

PRINT #demo.tabs, "addtab Advanced"

TEXTEDITOR #demo.edit, "This is a TextEditor.\nYou can type multiple lines here.", 20, 40, 540, 150

LISTVIEW #demo.lv, "", 20, 200, 540, 150
PRINT #demo.lv, "setcolumns Name,Role,Status"
PRINT #demo.lv, "additem Alice,Developer,Active"
PRINT #demo.lv, "additem Bob,Designer,Away"
PRINT #demo.lv, "columnwidths 150,150,100"
PRINT #demo.lv, "showgrid"

DATEPICKER #demo.dp, 20, 360, 200, 25

PSTRINGGRID #demo.grid, "", 20, 400, 540, 150
PRINT #demo.grid, "setcolumns Column A,Column B"
PRINT #demo.grid, "additem Row 1 A,Row 1 B"
PRINT #demo.grid, "additem Row 2 A,Row 2 B"

PRINT #demo.tabs, "append #demo.edit"
PRINT #demo.tabs, "append #demo.lv"
PRINT #demo.tabs, "append #demo.dp"
PRINT #demo.tabs, "append #demo.grid"

STATICTEXT #demo.status, "Ready", 5, 610, 580, 20

OPEN "GUI Elements Demo" FOR window AS #demo

WAIT

SUB btnClick
    val$ = #demo.txt
    NOTICE "You entered: " + val$
    PRINT #demo.status, "set Button clicked."
END SUB

SUB chkClick
    PRINT #demo.status, "set Checkbox toggled."
END SUB

SUB rClick
    PRINT #demo.status, "set Radiobutton changed."
END SUB

SUB cbClick
    sel$ = #demo.cb
    PRINT #demo.status, "set Selected: " + sel$
END SUB

SUB openSub
    STATICTEXT #sub.lbl, "This is a sub-window!", 20, 20, 200, 20
    BUTTON #sub.close, "Close", [closeSub], UL, 20, 60, 100, 30
    OPEN "Subwindow" FOR window AS #sub
END SUB

SUB closeSub
    CLOSE #sub
END SUB

SUB showInfo
    NOTICE "Dialogs Demo v1.0" + CHR$(10) + "Showcasing the Transpiler capabilities."
END SUB

SUB quit
    CONFIRM "Exit demo?"; ok
    IF ok THEN
        CLOSE #demo
    END IF
END SUB
