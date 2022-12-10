from tkinter import ttk
import customtkinter as ctk
import asyncio
import threading
from pytube import YouTube, exceptions


class Video:

    def __init__(self, yt, yt_video, url, title, file_size, highest_res, author, views):
        self.url = url
        self.yt = yt
        self.yt_video = yt_video
        self.title = title
        self.file_size = file_size
        self.highest_res = highest_res
        self.author = author
        self.views = views

    def __str__(self):
        return f'{self.title} by {self.author}\n{self.file_size} MB, {self.highest_res}\n{self.views}views'

    def get_yt_video(self):
        return self.yt, self.yt_video


def center(win, width, height):
    """
    centers a tkinter window
    :param win: the main window or Toplevel window to center
    """
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


def _asyncio_thread(async_loop, _from_):
    if _from_ == "info":
        async_loop.run_until_complete(do_get_video_info())
    elif _from_ == "download":
        async_loop.run_until_complete(do_download())


def do_start_tasks(async_loop, _from_):
    """ Button-Event-Handler starting the asyncio part. """
    threading.Thread(target=_asyncio_thread, args=(async_loop, _from_)).start()


async def do_get_video_info():
    try:
        error_label.configure(text='')
        url = url_entry.get()
        yt = YouTube(url)
        info_label.configure(text="...")
        video = yt.streams.get_highest_resolution()

        global v1
        v1 = Video(yt, video, url, video.title, f'{round(video.filesize * 0.000001, 2)}',
                   video.resolution, yt.author, "{:,}\n".format(yt.views))
        info_label.configure(text=v1.__str__())
        download_button.configure(state=ctk.NORMAL)
        print(v1.__str__())
    except exceptions.VideoPrivate:
        error_label.configure(
            text="This video is private!")
        return
    except exceptions.VideoUnavailable:
        error_label.configure(
            text="This video is unavaliable!")
        return
    except exceptions.RegexMatchError:
        error_label.configure(text="Please insert a valid Youtube URL!")
        return
    except exceptions.PytubeError:
        error_label.configure(
            text="There seems to be a problem, please try again later!")
        return
    except Exception as error:
        error_label.configure(
            text="There seems to be a problem, please try again later!")
        print(error)
        return


def on_progress(stream, chunk, bytes_remaining):
    # Function for persentage_progress_bar changes
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100

    print(round(percentage_of_completion))
    persentage_progress_bar.set(round(percentage_of_completion)/100)


async def do_download():
    persentage_progress_bar.pack(pady=12, padx=10, side="right")
    chunk_size = 1024
    v1.yt.register_on_progress_callback(on_progress)
    persentage_progress_bar.set(0)
    print(f"Downloading \"{v1.title}\"..")
    v1.yt_video.download('downloads')
    download_button.configure(state=ctk.DISABLED)


def main(async_loop):
    root = ctk.CTk()
    ctk.set_default_color_theme("green")
    root.geometry("1020x540")
    #center(root, 1020, 540)
    # ctk.deactivate_automatic_dpi_awareness()

    tabview = ctk.CTkTabview(root, border_width=3, width=1000, height=520)
    tabview.add("video download")
    tabview.add("playlist download")
    tabview.pack(pady=12, padx=10)

    global url_entry
    url_entry = ctk.CTkEntry(master=tabview.tab("video download"), width=500)
    url_entry.pack(pady=12, padx=10)

    retrieve_info_button = ctk.CTkButton(master=tabview.tab("video download"), text='Get video Info',
                                         command=lambda: do_start_tasks(async_loop, "info"))
    retrieve_info_button.pack(pady=12, padx=10)

    global download_button
    download_button = ctk.CTkButton(master=tabview.tab("video download"), text='Download Video',
                                    command=lambda: do_start_tasks(async_loop, "download"),  state=ctk.DISABLED)
    download_button.pack(pady=12, padx=10)

    video_frame = ctk.CTkFrame(master=tabview.tab(
        "video download"), corner_radius=10, width=900)
    video_frame.pack(pady=12, padx=10, expand=True, fill="both")

    global info_label
    info_label = ctk.CTkLabel(master=video_frame, text='')
    info_label.pack(pady=12, padx=10, side="left")

    global persentage_progress_bar
    persentage_progress_bar = ctk.CTkProgressBar(
        master=video_frame, mode="determinate", orientation="horizontal")
    persentage_progress_bar.set(0)

    global error_label
    error_label = ctk.CTkLabel(master=tabview.tab(
        "video download"), text='', text_color="red")
    error_label.pack(pady=12, padx=10)

    style = ttk.Style()
    style.theme_use("xpnative")
    style.configure("Treeview",
                    foreground="black",
                    rowheight=15,
                    )
    style.map('Treeview', background=[('selected', 'blue')])

    root.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)
