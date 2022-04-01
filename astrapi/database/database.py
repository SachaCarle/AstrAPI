#import library
import gspread, os
#Service client credential from oauth2client
from oauth2client.service_account import ServiceAccountCredentials

current_folder = os.path.dirname(os.path.realpath(__file__))
authfile = 'database_manager.json'
if True:
    authfile = 'production.json'
database_manager = os.path.join(current_folder, authfile)

#Create scope
scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
#create some credential using that scope and content of startup_funding.json
creds = ServiceAccountCredentials.from_json_keyfile_name(database_manager, scope)
#create gspread authorize using that credential
client = gspread.authorize(creds)

database_name = 'database'

def getSpreadSheetDatabase():
    return client.open(database_name)

database_schema = {
    'planet_sign_txts': ['planet', 'sign', 'txt'],
    'house_sign_txts': ['house', 'sign', 'txt'],
    'rising_sign_txts': ['sign', 'txt'],
    'midheaven_sign_txts': ['sign', 'txt'],
    'planet_house_txts': ['planet', 'house', 'txt'],
    'ruler_house_txts': ['ruler', 'house', 'txt'],
    'various_txts': ['key', 'txt'],
}
print ('Core database loaded');