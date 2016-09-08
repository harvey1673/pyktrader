import platform
from base import *

datayes_token = 'xxxxx'

dbconfig = {'user': 'xxxxx', 
          'password':'xxxxx', 
          'host':'localhost',
          'database': 'xxxxx',
          }
		  
EMAIL_HOTMAIL = {'host': 'smtp.live.com',
                 'user': 'xxxxxx@hotmail.com',
                 'passwd': 'xxxxx'}

				
def get_prod_folder():
    folder = ''
    system = platform.system()
    if system == 'Linux':
        folder = '/home/xxx/'
    elif system == 'Windows':
        folder = 'C:\\xxx\\'
    return folder
