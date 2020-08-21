Instructions to build an executable from python code:

Setup:
  pip install pyinstaller

To create executable:
	cd to directory and then type:
	pyinstaller --onefile pythonScriptName.py
	pyinstaller --noconsole --icon=icon.ico --onefile pythonScriptName.py
