# -*- coding: utf-8 -*-
import os
import subprocess

desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
target = r"c:\Users\user\Documents\antigravity\nifty-pythagoras\START_SHORTS_STUDIO.bat"
working_dir = r"c:\Users\user\Documents\antigravity\nifty-pythagoras"
icon = r"c:\Users\user\Documents\antigravity\nifty-pythagoras\shorts_studio\assets\app_icon.ico"
shortcut_path = os.path.join(desktop, "WonkaShorts Studio.lnk")

vbs_script = f"""Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target}"
oLink.WorkingDirectory = "{working_dir}"
oLink.IconLocation = "{icon},0"
oLink.Description = "WonkaShorts Studio - 원카AI 신비한 건축사전 숏폼 30일치 풀 자동화"
oLink.Save
"""

vbs_path = os.path.join(working_dir, "temp_shortcut.vbs")
with open(vbs_path, "w", encoding="cp949") as f:
    f.write(vbs_script)

res = subprocess.run(["cscript", "//nologo", vbs_path], capture_output=True, text=True)
if os.path.exists(vbs_path):
    os.remove(vbs_path)

print("VBS Output:", res.stdout, res.stderr)
print("Shortcut Path:", shortcut_path)
print("Shortcut Exists:", os.path.exists(shortcut_path))
