from database import client

shs = client.openall()
for sh in shs:
    print ("Database " + sh.title + " ==> " + sh.id)