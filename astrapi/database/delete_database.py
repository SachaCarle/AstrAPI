from database import client

shs = client.openall()
for sh in shs:
    print ("Delete " + sh.title + " ==> " + sh.id)
    client.del_spreadsheet(sh.id)