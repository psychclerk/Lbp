' Contact Manager Pro v1.1
' Demonstrates Tabs, Listview, SQLite, and Datepicker
' Improved with multi-line notices and better layout comments.

WindowWidth = 600
WindowHeight = 500

' --- Main Window Controls ---
' The TabControl will host our main interface sections
TABCONTROL #main.tabs, 10, 10, 580, 440

' --- Tab 1: Contact List ---
' This tab shows all contacts in a searchable grid
PRINT #main.tabs, "addtab Contact List"
STATICTEXT #main.st1, "Search:", 20, 50, 60, 25
TEXTBOX #main.search, "", 80, 50, 200, 25
BUTTON #main.btnSearch, "Search", [searchContacts], UL, 290, 50, 80, 25
LISTVIEW #main.list, "", 20, 90, 540, 300

' Append controls to the first tab
PRINT #main.tabs, "append #main.st1"
PRINT #main.tabs, "append #main.search"
PRINT #main.tabs, "append #main.btnSearch"
PRINT #main.tabs, "append #main.list"

' Buttons for global actions
BUTTON #main.btnNew, "New Contact", [newContact], UL, 20, 400, 120, 30
BUTTON #main.btnDelete, "Delete Selected", [deleteContact], UL, 150, 400, 150, 30
PRINT #main.tabs, "append #main.btnNew"
PRINT #main.tabs, "append #main.btnDelete"

' --- Tab 2: Details ---
' This tab is used for adding or editing contact details
PRINT #main.tabs, "addtab Contact Details"
STATICTEXT #main.st2, "Name:", 20, 50, 100, 25
TEXTBOX #main.name, "", 120, 50, 300, 25

STATICTEXT #main.st3, "Phone:", 20, 90, 100, 25
TEXTBOX #main.phone, "", 120, 90, 300, 25

STATICTEXT #main.st4, "Email:", 20, 130, 100, 25
TEXTBOX #main.email, "", 120, 130, 300, 25

STATICTEXT #main.st5, "DOB:", 20, 170, 100, 25
DATEPICKER #main.dob, "", 120, 170, 200, 25

BUTTON #main.btnSave, "Save Contact", [saveContact], UL, 120, 220, 120, 30
BUTTON #main.btnCancel, "Cancel", [showList], UL, 250, 220, 120, 30

' Hidden ID field to track which record we're editing
TEXTBOX #main.contactId, "", -100, -100, 50, 25

' Append controls to the second tab
PRINT #main.tabs, "append #main.st2"
PRINT #main.tabs, "append #main.name"
PRINT #main.tabs, "append #main.st3"
PRINT #main.tabs, "append #main.phone"
PRINT #main.tabs, "append #main.st4"
PRINT #main.tabs, "append #main.email"
PRINT #main.tabs, "append #main.st5"
PRINT #main.tabs, "append #main.dob"
PRINT #main.tabs, "append #main.btnSave"
PRINT #main.tabs, "append #main.btnCancel"
PRINT #main.tabs, "append #main.contactId"

' --- Menu Setup ---
MENU #main, "&File", "E&xit", [quit]
MENU #main, "&Help", "&About", [about]

' --- Initialize Database ---
' Open SQLite database and ensure the table exists
OPEN "contacts.db" FOR sqlite AS #db
PRINT #db, "CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT, dob TEXT)"

' --- Open the Main Window ---
OPEN "Contact Manager Pro" FOR window AS #main

' Configure Listview columns and behavior
PRINT #main.list, "setcolumns ID,Name,Phone,Email,DOB"
PRINT #main.list, "columnwidths 30,150,100,150,100"
PRINT #main.list, "showgrid"
PRINT #main.list, "doubleclick [editContact]"

' Initial load of contacts from database
loadContacts

WAIT

' --- Subroutines ---

SUB searchContacts
    searchTerm$ = #main.search
    ' Basic SQL injection protection would be better, but keeping it simple for example
    sql$ = "SELECT * FROM contacts WHERE name LIKE '%" + searchTerm$ + "%' OR email LIKE '%" + searchTerm$ + "%'"
    FILL #main.list #db sql$
END SUB

SUB loadContacts
    FILL #main.list #db "SELECT * FROM contacts"
END SUB

SUB showList
    PRINT #main.tabs, "selectindex 0"
END SUB

SUB newContact
    ' Clear fields for a new entry
    PRINT #main.contactId, "set "
    PRINT #main.name, "set "
    PRINT #main.phone, "set "
    PRINT #main.email, "set "
    PRINT #main.dob, "set "
    PRINT #main.tabs, "selectindex 1"
END SUB

SUB editContact
    ' Get ID of selected contact from Listview
    id$ = #main.list
    IF id$ = "" THEN EXIT SUB
    
    PRINT #main.contactId, "set " + id$
    NOTICE "Editing contact ID: " + id$ + "\nYou can now modify the details."
    PRINT #main.tabs, "selectindex 1"
END SUB

SUB saveContact
    id$ = #main.contactId
    name$ = #main.name
    phone$ = #main.phone
    email$ = #main.email
    dob$ = #main.dob
    
    IF name$ = "" THEN
        NOTICE "Error: Name is required!\nPlease enter a name before saving."
        EXIT SUB
    END IF
    
    IF id$ = "" THEN
        ' New record
        sql$ = "INSERT INTO contacts (name, phone, email, dob) VALUES ('" + name$ + "', '" + phone$ + "', '" + email$ + "', '" + dob$ + "')"
    ELSE
        ' Existing record
        sql$ = "UPDATE contacts SET name='" + name$ + "', phone='" + phone$ + "', email='" + email$ + "', dob='" + dob$ + "' WHERE id=" + id$
    END IF
    
    PRINT #db, sql$
    loadContacts
    PRINT #main.tabs, "selectindex 0"
END SUB

SUB deleteContact
    id$ = #main.list
    IF id$ = "" THEN
        NOTICE "Selection Required\nPlease select a contact to delete from the list."
        EXIT SUB
    END IF
    
    ok = 0
    CONFIRM "Are you sure you want to delete this contact?\nThis action cannot be undone."; ok
    IF ok = 0 THEN EXIT SUB
    
    sql$ = "DELETE FROM contacts WHERE id = " + id$
    PRINT #db, sql$
    loadContacts
END SUB

SUB about
    NOTICE "Contact Manager Pro v1.1\n\nCross-platform Liberty BASIC\nNow supporting literal \n escapes!"
END SUB

SUB quit
    CLOSE #db
    CLOSE #main
END SUB
