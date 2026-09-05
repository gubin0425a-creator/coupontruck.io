Set WshShell = CreateObject("WScript.Shell")
strPath = Replace(WScript.ScriptFullName, WScript.ScriptName, "")
WshShell.Run "python """ & strPath & "server.py""", 0, False
