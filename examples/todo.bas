' Production-Grade TODO Professional Example
' Demonstrates: Menus, TabControl, SQLite, Multi-Window, Search, and Grid interaction

' Set up window size and position
WindowWidth = 800
WindowHeight = 600
UpperLeftX = 100
UpperLeftY = 100

' --- Main Window UI ---
MENU #main, "&File", "&Exit", [quit]
MENU #main, "&Help", "&About", [showAbout]

TABCONTROL #main.tabs, 10, 10, 780, 500

STATICTEXT #main.lblSearch, "Search Tasks:", 20, 50, 100, 20
TEXTBOX #main.search, "", 120, 50, 200, 25
BUTTON #main.btnSearch, "Search", [loadTasks], UL, 330, 48, 80, 30

PSTRINGGRID #main.grid, "", 20, 90, 740, 300

STATICTEXT #main.lblTask, "New Task:", 20, 410, 80, 20
TEXTBOX #main.taskName, "", 100, 410, 300, 25
BUTTON #main.btnAdd, "Add Task", [addTask], UL, 410, 408, 100, 30
BUTTON #main.btnDel, "Delete Selected", [deleteTask], UL, 520, 408, 150, 30

STATICTEXT #main.status, "Ready.", 10, 540, 500, 20

' --- Initialize Database ---
OPEN "todo.db" FOR sqlite AS #db
PRINT #db, "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT)"
PRINT #db, "CREATE TABLE IF NOT EXISTS comments (task_id INTEGER, comment TEXT)"

' Open Main Window
OPEN "TODO Professional v1.0" FOR window AS #main

' Setup Tabs and Grid
PRINT #main.tabs, "addtab Tasks"
PRINT #main.tabs, "append #main.lblSearch"
PRINT #main.tabs, "append #main.search"
PRINT #main.tabs, "append #main.btnSearch"
PRINT #main.tabs, "append #main.grid"
PRINT #main.tabs, "append #main.lblTask"
PRINT #main.tabs, "append #main.taskName"
PRINT #main.tabs, "append #main.btnAdd"
PRINT #main.tabs, "append #main.btnDel"

PRINT #main.tabs, "addtab Archive"
STATICTEXT #main.archivelbl, "Archived Tasks (History)", 20, 50, 200, 20
LISTVIEW #main.archivelist, "", 20, 80, 740, 350
PRINT #main.tabs, "append #main.archivelbl"
PRINT #main.tabs, "append #main.archivelist"
PRINT #main.archivelist, "setcolumns ID,Task,CompletedDate"
PRINT #main.archivelist, "columnwidths 50,400,150"
PRINT #main.archivelist, "showgrid"
PRINT #main.archivelist, "additem 101,Fix UI issues,2023-10-01"
PRINT #main.archivelist, "additem 102,Implement SQLite,2023-10-05"

PRINT #main.grid, "doubleclick [openComments]"

' Initial Load
loadTasks

' Instruction for double-click
NOTICE "Tip: Double-click a task in the grid to view comments."

WAIT

SUB loadTasks
    s$ = #main.search
    sql$ = "SELECT id, title, status FROM tasks"
    IF s$ <> "" THEN
        sql$ = sql$ + " WHERE title LIKE '%" + s$ + "%'"
    END IF
    PRINT #main.grid, "fill #db '" + sql$ + "'"
END SUB

SUB addTask
    t$ = #main.taskName
    IF t$ = "" THEN
        NOTICE "Please enter a task name."
    ELSE
        sql$ = "INSERT INTO tasks (title, status) VALUES ('" + t$ + "', 'Pending')"
        PRINT #db, sql$
        PRINT #main.taskName, "set "
        loadTasks
        PRINT #main.status, "set Task added."
    END IF
END SUB

SUB deleteTask
    id$ = ""
    PROMPT "Enter Task ID to delete:"; id$
    IF id$ <> "" THEN
        sql$ = "DELETE FROM tasks WHERE id = " + id$
        PRINT #db, sql$
        loadTasks
        PRINT #main.status, "set Task deleted."
    END IF
END SUB

SUB showAbout
    NOTICE "TODO Professional v1.0" + CHR$(10) + "Built with Liberty BASIC Transpiler"
END SUB

SUB quit
    ok = 0
    CONFIRM "Are you sure you want to exit?"; ok
    IF ok THEN
        CLOSE #db
        CLOSE #main
    END IF
END SUB

SUB openComments
    ' Multi-window management
    id$ = ""
    PROMPT "View comments for Task ID:"; id$
    IF id$ = "" THEN EXIT SUB
    
    STATICTEXT #comments.lbl, "Comments for Task #" + id$, 10, 10, 200, 20
    LISTBOX #comments.list, "", 10, 40, 280, 200
    TEXTBOX #comments.newComm, "", 10, 250, 200, 25
    BUTTON #comments.btnAdd, "Add", [addComment], UL, 215, 248, 70, 30
    
    OPEN "Task Comments" FOR window AS #comments
    
    PRINT #comments.list, "additem Sample comment for task " + id$
END SUB

SUB addComment
    NOTICE "Comment added (Simulation)"
    CLOSE #comments
END SUB
