import os
import subprocess
from tkinter import filedialog

DEFAULT_PATH = os.path.dirname(__file__)

print("The Forge Installer Window should have opened!")
print("1) Select 'Install Server'")
print("2) Click the 3 dots next to the path")
print("3) Navigate to the Path where the file should install")
print("4) Hit 'Ok' and the server files should install.")

filename = filedialog.askopenfilename(
    title="Select Forge Installer",
    initialdir=f"{DEFAULT_PATH}/"
)
target_dir = filedialog.askdirectory(
    title="Select Install Location",
    initialdir=f"{DEFAULT_PATH}/"
    
)
installer = f"java -jar \"{filename}\" --installServer --target {target_dir}"
executable = f"java -Xmx{8 * 1024}m -jar \"{filename}\" nogui"

with subprocess.Popen(installer, stdin=subprocess.PIPE) as process:
    input("Hit 'enter' in the terminal when finished\n")
    # while True:
    #     try:
    #         # Write command to the input stream
    #         process.stdin.write(str.encode(input("Command: ")))
    #         process.stdin.flush()
    #     except OSError:
    #         print("Error Writing to Server. Is it inactive?")
