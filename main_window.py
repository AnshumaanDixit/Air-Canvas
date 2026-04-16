import tkinter as tk
import subprocess
global air_controller
def run_air_controller():
    air_controller = subprocess.Popen(["python","aircontroller.py"])
    return air_controller
main = tk.Tk()
main.title("Air Controller")
main.geometry("800x400")
tk.Button(main,text="Air Controller",command=run_air_controller,state=tk.NORMAL,width=10,height=5).pack()
main.mainloop()