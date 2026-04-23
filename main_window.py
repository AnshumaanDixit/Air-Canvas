import tkinter as tk
import subprocess
global air_controller
def run_air_controller():
    air_controller = subprocess.Popen(["python","aircontroller.py"])
    return air_controller
def run_air_draw():
    air_draw = subprocess.Popen(["python","airdraw.py"])
    return air_draw
main = tk.Tk()
main.title("Air Controller")
main.geometry("800x400")
button = tk.Button(main,text="Air Controller",command=run_air_controller,state=tk.NORMAL,width=25,height=5,relief=tk.RAISED,bd=10,cursor="hand2").grid(row=0,column=0)
button2 = tk.Button(main,text="Air Draw",command=run_air_draw,state=tk.NORMAL,width=25,height=5,relief=tk.RAISED,bd=10,cursor="hand2").grid(row=0,column=1)
main.mainloop()