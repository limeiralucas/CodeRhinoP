from distutils.core import setup
import py2exe

Mydata_files = [('icon.ico')]

setup(
    data_files = Mydata_files,
    options = {
        "py2exe":{
            "dll_excludes": ["MSVCP90.dll"]
        }
    }, 
    windows=[{"script": 'server.py', "icon_resources": [(0, "icon.ico")]}]
)