from tkinter import ttk
import tkinter as tk
from ttkthemes import ThemedTk
import asyncio
import threading
from pytube import YouTube, exceptions

main_iid = 0


def changer(theme):
    mainWindow.style.theme_use(theme)
    mainWindow.error_label.config(text=f'Theme: {theme}')
    pass


class Window:
    def __init__(self, master):
        self.master = master

        # Define Style
        self.style = ttk.Style(master)
        self.style.theme_use("scidblue")

        # ------------------------------------------------
        # TODO: REMOVE THIS
        all_themes = master.get_themes()
        my_menu = tk.Menu(master)
        master.config(menu=my_menu)
        self.theme_menu = tk.Menu(my_menu)
        my_menu.add_cascade(label="Themes", menu=self.theme_menu)

        # Sub Menu
        for theme in all_themes:
            self.theme_menu.add_command(
                label=theme, command=lambda theme=theme: changer(theme))

        # ------------------------------------------------

        # Define and place Tab View
        self.tabview = ttk.Notebook(master)

        self.video_download_tab = tk.Frame(self.tabview)
        self.playlist_download_tab = tk.Frame(self.tabview)

        self.tabview.add(self.video_download_tab, text="Video Download")
        self.tabview.add(self.playlist_download_tab, text="Playlist Download")

        self.tabview.pack(expand=1, fill="both")

        # Define and place URL Entry
        self.url_entry = tk.Entry(master=self.video_download_tab, width=500)
        self.url_entry.pack(pady=12, padx=10)

        # Define and place Buttons for info and download
        self.retrieve_info_button = tk.Button(master=self.video_download_tab, text='Get video Info',
                                              command=lambda: do_start_tasks(async_loop, "info"))
        self.retrieve_info_button.pack(pady=12, padx=10)

        self.download_button = tk.Button(master=self.video_download_tab, text='Download Video',
                                         command=lambda: do_start_tasks(async_loop, "download"),  state=tk.DISABLED)
        self.download_button.pack(pady=12, padx=10)

        # Define the video information Frame
        self.video_frame = tk.Frame(master=self.video_download_tab, width=900)
        self.video_frame.pack(pady=12, padx=10, expand=True, fill="both")

        # Define video information Label and download Progress Bar
        #self.info_label = tk.Label(master=self.video_frame, text='')
        #self.info_label.pack(pady=12, padx=10, side="left")
        self.treeview = ttk.Treeview(self.video_frame)
        self.treeview['columns'] = (
            "Title", "Author", "File_Size", "Resolution", "Views")
        # Format Columns
        self.treeview.column("#0", width=0)
        self.treeview.column("Title", anchor=tk.CENTER, width=50)
        self.treeview.column("Author", anchor=tk.CENTER, width=50)
        self.treeview.column("File_Size", anchor=tk.CENTER, width=50)
        self.treeview.column("Resolution", anchor=tk.CENTER, width=50)
        self.treeview.column("Views", anchor=tk.CENTER, width=50)

        # Create Headings
        self.treeview.heading("#0", text="", anchor=tk.CENTER)
        self.treeview.heading("Title", text="Title", anchor=tk.CENTER)
        self.treeview.heading("Author", text="Author", anchor=tk.CENTER)
        self.treeview.heading("File_Size", text="Size", anchor=tk.CENTER)
        self.treeview.heading(
            "Resolution", text="Resolution", anchor=tk.CENTER)
        self.treeview.heading("Views", text="Views", anchor=tk.CENTER)

        self.treeview.pack(pady=20)

        self.persentage_progress_bar = ttk.Progressbar(
            master=self.video_frame, mode="determinate", orient="horizontal")
        self.persentage_progress_bar["value"] = 0

        self.error_label = tk.Label(master=self.video_download_tab,
                                    text='', fg="red")
        self.error_label.pack(pady=12, padx=10)

    def get_attr(self):
        return self


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

    def get_video_info(self):
        return (self.title, self.author, self.file_size, self.highest_res, self.views)

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
        mainWindow.error_label.configure(text='')
        url = mainWindow.url_entry.get()
        yt = YouTube(url)
        # mainWindow.info_label.configure(text="...")
        video = yt.streams.get_highest_resolution()

        global v1
        v1 = Video(yt, video, url, video.title, f'{round(video.filesize * 0.000001, 2)}',
                   video.resolution, yt.author, "{:,}\n".format(yt.views))
        mainWindow.treeview.insert(
            parent='', index='end', iid=main_iid, text="", values=v1.get_video_info())
        main_iid += 1
        # mainWindow.info_label.configure(text=v1.__str__())
        mainWindow.download_button.configure(state=tk.NORMAL)
    except exceptions.VideoPrivate:
        mainWindow.error_label.configure(
            text="This video is private!")
        return
    except exceptions.VideoUnavailable:
        mainWindow.error_label.configure(
            text="This video is unavaliable!")
        return
    except exceptions.RegexMatchError:
        mainWindow.error_label.configure(
            text="Please insert a valid Youtube URL!")
        return
    except exceptions.PytubeError:
        mainWindow.error_label.configure(
            text="There seems to be a problem, please try again later!")
        return
    except Exception as error:
        mainWindow.error_label.configure(
            text="There seems to be a problem, please try again later!2")
        print(error)
        return


def on_progress(stream, chunk, bytes_remaining):
    # Function for persentage_progress_bar changes
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100

    print(round(percentage_of_completion))
    mainWindow.persentage_progress_bar["value"] = (
        round(percentage_of_completion))


async def do_download():
    mainWindow.persentage_progress_bar.pack(pady=12, padx=10, side="right")
    chunk_size = 1024
    v1.yt.register_on_progress_callback(on_progress)
    mainWindow.persentage_progress_bar["value"] = 0
    print(f"Downloading \"{v1.title}\"..")
    v1.yt_video.download('downloads')
    mainWindow.download_button.configure(state=tk.DISABLED)


def main(async_loop):
    root = ThemedTk()
    root.title("Youtube Video Downloader")
    root.geometry("1020x540")

    global mainWindow
    mainWindow = Window(root)

    root.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)
