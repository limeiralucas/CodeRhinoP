from distutils.core import setup
import py2exe

Mydata_files = [('icon.ico'), ('exit.ico'), ('imageformats', ['C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qgif4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qico4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qjpeg4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qmng4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qsvg4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qtga4.dll', 'C:\Python27\Lib\site-packages\PyQt4\plugins\imageformats\qtiff4.dll'])]

setup(
    data_files = Mydata_files,
    options = {
        "py2exe":{
            "dll_excludes": ["MSVCP90.dll"]
        }
    }, 
    windows=[{"script": 'server.py', "icon_resources": [(0, "icon.ico")]}]
)