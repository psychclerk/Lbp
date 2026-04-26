' Contact Manager Example
OPEN "contacts.db" FOR sqlite AS #db
#db "CREATE TABLE IF NOT EXISTS contacts (name TEXT, phone TEXT)"

OPEN "Contact Manager" FOR window AS #main
STATICTEXT #main.lbl1, "Name:", 10, 10, 100, 20
TEXTBOX #main.name, "", 120, 10, 200, 20
STATICTEXT #main.lbl2, "Phone:", 10, 40, 100, 20
TEXTBOX #main.phone, "", 120, 40, 200, 20
BUTTON #main.add, "Add Contact", [addContact], UL, 10, 80, 100, 30
PSTRINGGRID #main.grid, "", 10, 120, 380, 200

' Initial load
#main.grid "fill #db 'SELECT * FROM contacts'"

SUB addContact
    n$ = #main.name
    p$ = #main.phone
    if n$ <> "" then
        sql$ = "INSERT INTO contacts VALUES ('" + n$ + "', '" + p$ + "')"
        #db sql$
        #main.grid "fill #db 'SELECT * FROM contacts'"
        NOTICE "Contact Added"
    else
        NOTICE "Please enter a name"
    end if
END SUB

WAIT
