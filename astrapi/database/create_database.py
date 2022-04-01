from database import client, database_name, database_schema



created = False
database = None

shs = client.openall()
for sh in shs:
    print ("Speadsheet " + sh.title + " ==> " + sh.id)
    if sh.title == database_name:
        created = True
        if not database is None:
            raise Exception("Multiple " + database_name + " spreadsheet.")
        else:
            database = sh

if not created:
    print ("Creating " + database_name)
    database = client.create(database_name)
    database.share('carle.sacha@gmail.com', perm_type='user', role='writer')

error = False
for k,v in database_schema.items():
    try:
        ws = database.add_worksheet(title=k, rows="144", cols="10")
        print ("\tTable " + k + " created")
        for i in v:
            idx = v.index(i)
            ws.update_cell(1, 1 + idx, i)
    except Exception as e:
        print (e)
        error = True

if not error:
    database.del_worksheet(database.sheet1)
