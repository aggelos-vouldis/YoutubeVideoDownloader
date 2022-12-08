import customtkinter
import time


def start():
    progressbar.set(progressbar.get() + 0.1)
    print(progressbar.get())
    #current_value += 10
    # progressbar.set(current_value)


def stop():
    progressbar.set(100)
    progressbar.stop()


i = 0

win = customtkinter.CTk()
win.geometry("350x250")

button = customtkinter.CTkButton(
    master=win, text="start", command=start).pack(pady=12, padx=10)

button2 = customtkinter.CTkButton(
    master=win, text="stop", command=stop).pack(pady=12, padx=10)

progressbar = customtkinter.CTkProgressBar(
    master=win, width=160, height=20, border_width=2, mode="determinate", determinate_speed=1)
progressbar.set(0)
progressbar.pack(pady=12, padx=10)

win.mainloop()
# Valor del progressBar
