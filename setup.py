
from cx_Freeze import setup, Executable

exe = [Executable("warmane_scanner.py", base = "Win32GUI")]
  
setup(name = "Macaw" , 
      version = "0.1" , 
      description = "Scrapes the warmane armory to gather meaningful data about a character." , 
      executables = exe,
      icon="icon_inspector.ico"
) 
