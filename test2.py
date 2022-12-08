from pytube import YouTube
import customtkinter as ctk
import asyncio


async def kati():
    for i in range(10000):
        percentage_label.configure(text=i)
    download_button.configure(state=ctk.NORMAL)
    search_video_button.configure(state=ctk.DISABLED)


def kati2():
    download_button.configure(state=ctk.DISABLED)
    search_video_button.configure(state=ctk.NORMAL)


ctk.set_appearance_mode("dark")

root = ctk.CTk()
root.geometry("1000x340")

input_box = ctk.CTkEntry(master=root)
input_box.pack(pady=12, padx=10)
search_video_button = ctk.CTkButton(
    master=root, text="Find Video", command=lambda: asyncio.run(kati()))
search_video_button.pack(pady=12, padx=10)

download_button = ctk.CTkButton(
    master=root, text="Press for Download", anchor="top", command=kati2, state=ctk.DISABLED)
download_button.pack(pady=12, padx=10)

percentage_label = ctk.CTkLabel(master=root, text="")
percentage_label.pack(pady=12, padx=10)

root.mainloop()
