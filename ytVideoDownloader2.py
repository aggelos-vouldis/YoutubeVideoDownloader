from tkinter import ttk
import tkinter as tk
from ttkthemes import ThemedTk
import asyncio
import threading
from pytube import YouTube, exceptions, Playlist


def changer(theme):
    mainWindow.style.theme_use(theme)
    mainWindow.error_label.config(text=f'Theme: {theme}')
    pass


class TakenURLException(Exception):
    "Raise when a URL is already taken"
    pass


class Window:
    def __init__(self, master, async_loop):
        self.all_videos = []
        self.master = master
        self.main_iid = 0

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

        # Define and place URL Entry
        self.url_entry = tk.Entry(master=master, width=500)
        self.url_entry.pack(pady=12, padx=10)

        # Define and place Buttons for info and download
        self.retrieve_info_button = tk.Button(master=master, text='Get video Info',
                                              command=lambda: do_start_tasks(async_loop, "info"))
        self.retrieve_info_button.pack(
            pady=12, padx=10, side="top", anchor="w")

        self.download_button = tk.Button(master=master, text='Download Video',
                                         command=lambda: do_start_tasks(async_loop, "download"),  state=tk.DISABLED)
        self.download_button.pack(pady=12, padx=10, side="top", anchor="e")

        # Define the video information Frame
        self.video_frame = tk.Frame(master=master, width=900)
        self.video_frame.pack(pady=12, padx=10, expand=True, fill="both")

        # Define video information Label and download Progress Bar
        self.treeview = ttk.Treeview(
            self.video_frame, selectmode="extended")
        self.treeview['columns'] = (
            "Title", "Author", "File_Size", "Resolution", "Views")
        self.treeview['show'] = 'headings'
        # Format Columns
        self.treeview.column("#0", width=1)
        self.treeview.column("Title", anchor=tk.CENTER, width=200)
        self.treeview.column("Author", anchor=tk.CENTER, width=100)
        self.treeview.column("File_Size", anchor=tk.CENTER, width=5)
        self.treeview.column("Resolution", anchor=tk.CENTER, width=5)
        self.treeview.column("Views", anchor=tk.CENTER, width=5)

        # Create Headings
        self.treeview.heading("#0", text="", anchor=tk.CENTER)
        self.treeview.heading("Title", text="Title", anchor=tk.CENTER)
        self.treeview.heading("Author", text="Author", anchor=tk.CENTER)
        self.treeview.heading("File_Size", text="Size", anchor=tk.CENTER)
        self.treeview.heading(
            "Resolution", text="Resolution", anchor=tk.CENTER)
        self.treeview.heading("Views", text="Views", anchor=tk.CENTER)

        self.treeview.pack(pady=12, padx=10, expand=tk.YES, fill="both")

        self.persentage_progress_bar = ttk.Progressbar(
            master=self.video_frame, mode="determinate", orient="horizontal")
        self.persentage_progress_bar["value"] = 0

        self.download_all_button = tk.Button(
            master=master, text="download all videos!", state=tk.DISABLED, command=do_start_tasks(async_loop, "download_all"))
        self.download_all_button.pack(pady=12, padx=10)

        self.error_label = tk.Label(master=master,
                                    text='', fg="red")
        self.error_label.pack(pady=12, padx=10)

    def get_attr(self):
        return self

    def set_main_iid(self, new_iid):
        self.main_iid = new_iid

    def get_main_iid(self):
        return self.main_iid


class Video:

    def __init__(self, yt, yt_video, url, title, file_size, highest_res, author, views, id):
        self.url = url
        self.yt = yt
        self.yt_video = yt_video
        self.title = title
        self.file_size = file_size
        self.highest_res = highest_res
        self.author = author
        self.views = views
        self.id = id

    def __str__(self):
        return f'{self.title} by {self.author}\n{self.file_size} MB, {self.highest_res}\n{self.views}views'

    def get_video_id(self):
        return self.id

    def get_video_info(self):
        return (self.title, self.author, f'{self.file_size} MB', self.highest_res, self.views)

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
        if "playlist" in mainWindow.url_entry.get():
            async_loop.run_until_complete(do_get_playlist_info())
        else:
            async_loop.run_until_complete(do_get_video_info())
    elif _from_ == "download":
        async_loop.run_until_complete(do_download())
    elif _from_ == "download_all":
        async_loop.run_until_complete(do_download_all())


def do_start_tasks(async_loop, _from_):
    """ Button-Event-Handler starting the asyncio part. """
    threading.Thread(target=_asyncio_thread, args=(async_loop, _from_)).start()


async def do_get_playlist_info():
    url = mainWindow.url_entry.get()
    playlist = Playlist(url)
    for url in playlist.video_urls:
        get_info(url)


def get_info(url):
    try:
        yt = YouTube(url)
        # mainWindow.info_label.configure(text="...")
        video = yt.streams.get_highest_resolution()

        mainWindow.all_videos.append(Video(yt, video, url, video.title, f'{round(video.filesize * 0.000001, 2)}',
                                           video.resolution, yt.author, "{:,}\n".format(yt.views), mainWindow.get_main_iid()))
        mainWindow.treeview.insert(
            parent='', index='end', iid=mainWindow.get_main_iid(), text="", values=mainWindow.all_videos[-1].get_video_info())
        mainWindow.set_main_iid(mainWindow.get_main_iid()+1)
        mainWindow.download_button.configure(state=tk.NORMAL)
    except TakenURLException:
        mainWindow.error_label.configure(
            text="This video is already on the list!")
        return
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


async def do_get_video_info():
    try:
        mainWindow.error_label.configure(text='')
        url = mainWindow.url_entry.get()
        for video in mainWindow.all_videos:
            if video.url == url:
                raise TakenURLException()
        mainWindow.retrieve_info_button.configure(state=tk.DISABLED)
        get_info(url)
    except TakenURLException:
        mainWindow.error_label.configure(
            text="This video is already on the list!")
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


async def do_download_all():
    for video in mainWindow.all_videos:
        mainWindow.download_button.configure(state=tk.DISABLED)
        mainWindow.retrieve_info_button.configure(state=tk.DISABLED)
        mainWindow.download_all_button.configure(state=tk.DISABLED)

        mainWindow.persentage_progress_bar.pack(pady=12, padx=10)
        chunk_size = 1024
        video.yt.register_on_progress_callback(on_progress)
        mainWindow.persentage_progress_bar["value"] = 0
        video.yt_video.download('downloads')


async def do_download():
    mainWindow.persentage_progress_bar.pack(pady=12, padx=10)
    chunk_size = 1024
    focused_item = mainWindow.treeview.focus()
    mainWindow.all_videos[int(focused_item)
                          ].yt.register_on_progress_callback(on_progress)
    mainWindow.persentage_progress_bar["value"] = 0
    mainWindow.all_videos[int(focused_item)].yt_video.download('downloads')


def main(async_loop):
    root = ThemedTk()
    root.title("Youtube Video Downloader")
    root.geometry("1020x540")

    global mainWindow
    mainWindow = Window(root, async_loop)

    root.mainloop()


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)
