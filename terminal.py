# -*- coding: utf-8 -*-
"""
Created on Sun Feb  5 17:06:42 2023

@author: eirik
"""


#%% Config
# Config
import runpy

# Name & Version
version_name = "Terminal"
version_number = "1.0.0"
color_open = "\x1b["
color_close = "\x1b[0m"
color_green = "0;32;40m"
color_orange = "0;33;40m"
color_red = "0;31;40m"
color_blue = "0;34;40m"
color_white = "0;37;40m"
color_special_command = "3;37;40m"



#%% Welcome Screen 
print("\n"+"Booting "+version_name+" v "+version_number+"...")


print(
"""
======================================================================================================="""+color_open+color_green+"""

88888888888                             d8b                   888 
    888                                 Y8P                   888 
    888                                                       888 
    888   .d88b.  888d888 88888b.d88b.  888 88888b.   8888b.  888 
    888  d8P  Y8b 888P"   888 "888 "88b 888 888 "88b     "88b 888 
    888  88888888 888     888  888  888 888 888  888 .d888888 888 
    888  Y8b.     888     888  888  888 888 888  888 888  888 888 
    888   "Y8888  888     888  888  888 888 888  888 "Y888888 888 
                                                                  
"""+color_close+"======================================================================================================="+"\n")

 
 #%% Launcher

menu_item_1 = input("""What program would you like to launch?
1. Project Eidos
2. Project BDR \n""")
      
if menu_item_1 == 1:
    print("\n Launching Project Eidos")
    # exec(open("Production Code/Project Eidos.py").read())
    # subprocess.call("./Production Code/Project Eidos.py")
    runpy.run_path(path_name='Production Code/Project Eidos.py')

    
elif menu_item_1 == 2:
    print("\n Launching Project BDR")
    exec(open("Production Code/Project BDR.py").read())


