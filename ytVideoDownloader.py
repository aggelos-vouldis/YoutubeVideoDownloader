from tkinter import ttk, filedialog, messagebox
import tkinter as tk
from ttkthemes import ThemedTk
import asyncio
import threading
from pytube import YouTube, exceptions, Playlist
import os
from os.path import exists
import json


def get_download_folder():
    with open("settings.json", 'r') as input_file:
        data = json.load(input_file)
    if data["download_folder"] == '':
        VIDEOS_DOWNLOADS_DIR = fr'C:/Users/{os.getlogin()}/Downloads/Youtube Downloader/videos'
        MUSIC_DOWNLOADS_DIR = fr'C:/Users/{os.getlogin()}/Downloads/Youtube Downloader/music'
    else:
        VIDEOS_DOWNLOADS_DIR = fr'{data["download_folder"]}/videos'
        MUSIC_DOWNLOADS_DIR = fr'{data["download_folder"]}/music'
    return VIDEOS_DOWNLOADS_DIR, MUSIC_DOWNLOADS_DIR


class TakenURLException(Exception):
    "Raise when a URL is already taken"
    pass


class Treeview:
    def __init__(self, master, widths, columns):
        if (len(widths) != len(columns)):
            print("different")
        self.treeview = ttk.Treeview(master, selectmode="extended")
        self.treeview['columns'] = columns
        self.treeview['show'] = 'headings'

        # Format Columns
        self.treeview.column("#0", width=1)
        for idx, column in enumerate(columns):
            self.treeview.column(column, anchor=tk.CENTER, width=widths[idx])

        # Create Headings
        self.treeview.heading("#0", text="", anchor=tk.CENTER)

        for idx, column in enumerate(columns):
            self.treeview.heading(column, text=column, anchor=tk.CENTER)

        self.treeview.pack(pady=12, padx=10, expand=tk.YES, fill="both")

    def insert(self, parent, index, iid, text, values):
        self.treeview.insert(parent=parent, index=index,
                             iid=iid, text=text, values=values)
        return

    def get_focus(self):
        return self.treeview.focus()

    def get_item(self, focused):
        return self.treeview.item(focused)

    def set_item(self, focused, values):
        self.treeview.item(focused, values=values)


class Window:
    def __init__(self, master, async_loop):
        self.all_videos = []
        self.master = master
        self.main_iid = 0
        # Create a Settings Menu
        my_menu = tk.Menu(master)
        master.config(menu=my_menu)
        self.settings_menu = tk.Menu(my_menu, tearoff=0)
        my_menu.add_cascade(label="Settings", menu=self.settings_menu)

        # Sub Menu
        self.settings_menu.add_command(
            label="Change Download Folder", command=change_download_folder)
        self.settings_menu.add_command(
            label="Open Download Folder", command=open_download_folder)

        # Define Style
        self.style = ttk.Style(master)
        self.style.theme_use("adapta")

        # Define Frame for Search Entry and Search Button
        search_frame = tk.Frame(
            master=master, borderwidth=5)
        search_frame.pack(pady=12, padx=10, expand=True, fill="both")

        # Define and place URL Entry and search button
        self.url_entry = tk.Entry(master=search_frame)
        self.url_entry.pack(pady=12, padx=10, side=tk.LEFT,
                            fill="both", expand=True)

        self.retrieve_info_button = tk.Button(master=search_frame, text='Get video Info',
                                              command=lambda: do_start_tasks(async_loop, "info"))
        self.retrieve_info_button.pack(pady=12, padx=10, side=tk.RIGHT)

        # Define the video information Frame
        self.video_frame = tk.Frame(master=master)
        self.video_frame.pack(pady=12, padx=10, expand=True, fill="both")

        # Define video information Treeview and download Progress Bar
        self.treeview = Treeview(
            self.video_frame, [200, 100, 5, 5, 5, 5], ("Title", "Author", "File_Size", "Resolution", "Views", "Downloaded?"))

        self.persentage_progress_bar = ttk.Progressbar(
            master=self.video_frame, mode="determinate", orient="horizontal")
        self.persentage_progress_bar["value"] = 0
        self.persentage_progress_bar.pack(
            pady=12, padx=10, fill="both", expand=True)

        # Define download Frame
        download_frame = tk.Frame(
            master=master, borderwidth=5)
        download_frame.pack(pady=12, padx=10, expand=True, fill="both")
        # Define and place download Button
        self.download_button = tk.Button(master=download_frame, text='Download Video',
                                         command=lambda: do_start_tasks(async_loop, "download"),  state=tk.DISABLED)
        self.download_button.pack(pady=12, padx=10, side=tk.LEFT)

        # Define and Place mp3 toggle Checkbox
        self.mp3_toggle_var = tk.IntVar()
        mp3_toggle = tk.Checkbutton(
            master=download_frame, text="Download only MP3", variable=self.mp3_toggle_var, onvalue=1, offvalue=0)
        mp3_toggle.pack(pady=12, padx=10, side=tk.RIGHT)

        # Define and place download all Button
        self.download_all_button = tk.Button(
            master=master, text="download all videos!", state=tk.DISABLED, command=lambda: do_start_tasks(async_loop, "download_all"))
        self.download_all_button.pack(
            pady=12, padx=10)

        # Define and Place the error label
        self.error_label = tk.Label(master=master,
                                    text='', fg="red")
        self.error_label.pack(pady=12, padx=10, side=tk.BOTTOM)

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


def open_download_folder():
    os.startfile(f'F:\Downloads\Youtube Downloads')


def change_download_folder():
    filename = filedialog.askdirectory()
    if filename == '':
        return
    new_destination_folder = {"download_folder": filename}
    with open("settings.json", 'w') as output_file:
        json.dump(new_destination_folder, output_file)
    messagebox.showinfo("Download Folder Changed",
                        "Your Download folder is successfully updated!")


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
    mainWindow.retrieve_info_button.configure(state=tk.DISABLED)
    playlist = Playlist(url)
    for url in playlist.video_urls:
        get_info(url)
    mainWindow.retrieve_info_button.configure(state=tk.NORMAL)


def get_info(url):
    try:
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()

        mainWindow.all_videos.append(Video(yt, video, url, video.title, f'{round(video.filesize * 0.000001, 2)}',
                                           video.resolution, yt.author, "{:,}\n".format(yt.views), mainWindow.get_main_iid()))
        values = []
        values = mainWindow.all_videos[-1].get_video_info() + ("NO",)
        values = tuple(values)
        mainWindow.treeview.insert(
            parent='', index='end', iid=mainWindow.get_main_iid(), text="", values=values)
        mainWindow.set_main_iid(mainWindow.get_main_iid()+1)
        mainWindow.download_button.configure(state=tk.NORMAL)
        mainWindow.download_all_button.configure(state=tk.NORMAL)

    # Handle ALL the exceptions
    except TakenURLException:
        mainWindow.error_label.configure(
            text="This video is already on the list!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except exceptions.VideoPrivate:
        mainWindow.error_label.configure(
            text="This video is private!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except exceptions.VideoRegionBlocked:
        mainWindow.error_label.configure(
            text="This video is unavaliable in your Region!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except exceptions.VideoUnavailable:
        mainWindow.error_label.configure(
            text="This video is unavaliable!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except exceptions.RegexMatchError:
        mainWindow.error_label.configure(
            text="Please insert a valid Youtube URL!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except exceptions.PytubeError:
        mainWindow.error_label.configure(
            text="There seems to be a problem, please try again later!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except Exception as error:
        mainWindow.error_label.configure(
            text="Fatal Error. Please try again later!")
        print(error)
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
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
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
    except TakenURLException:
        mainWindow.error_label.configure(
            text="This video is already on the list!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        return
    except Exception as error:
        mainWindow.error_label.configure(
            text="There seems to be a problem, please try again later!")
        mainWindow.retrieve_info_button.configure(state=tk.NORMAL)
        print(error)
        return


def on_progress(stream, chunk, bytes_remaining):
    # Function for persentage_progress_bar changes
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100

    mainWindow.persentage_progress_bar["value"] = (
        round(percentage_of_completion))


def download(item):
    VIDEOS_DOWNLOADS_DIR, MUSIC_DOWNLOADS_DIR = get_download_folder()
    if mainWindow.mp3_toggle_var.get() == 0:

        mainWindow.all_videos[int(item)
                              ].yt.register_on_progress_callback(on_progress)
        mainWindow.persentage_progress_bar["value"] = 0
        mainWindow.all_videos[int(item)].yt_video.download(
            VIDEOS_DOWNLOADS_DIR)

        # change downloaded variable to 'YES'
        values = mainWindow.treeview.get_item(item)["values"]
        values[5] = 'YES'
        mainWindow.treeview.set_item(item, values)
        return

    mp3_video = mainWindow.all_videos[int(
        item)].yt.streams.filter(only_audio=True).first()
    mainWindow.all_videos[int(item)
                          ].yt.register_on_progress_callback(on_progress)
    mainWindow.persentage_progress_bar["value"] = 0

    out_file = mp3_video.download(output_path=MUSIC_DOWNLOADS_DIR)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    # change downloaded variable to 'YES'
    values = mainWindow.treeview.get_item(item)["values"]
    values[5] = 'YES'
    mainWindow.treeview.set_item(item, values)


async def do_download_all():
    mainWindow.download_button.configure(state=tk.DISABLED)
    mainWindow.retrieve_info_button.configure(state=tk.DISABLED)
    mainWindow.download_all_button.configure(state=tk.DISABLED)

    for idx, video in enumerate(mainWindow.all_videos):
        chunk_size = 1024
        download(idx)
    mainWindow.retrieve_info_button.configure(state=tk.NORMAL)


async def do_download():
    chunk_size = 1024
    focused_item = mainWindow.treeview.get_focus()
    download(focused_item)


def main(async_loop):
    root = ThemedTk()
    root.title("Youtube Saver")
    root.geometry("1020x650")
    # Define the icon
    try:
        root.iconphoto(False, tk.PhotoImage(file='icon.png'))
    except:
        pass
    global mainWindow
    mainWindow = Window(root, async_loop)

    root.mainloop()


if __name__ == '__main__':
    if exists('settings.json'):
        async_loop = asyncio.get_event_loop()
        main(async_loop)
    else:
        # first time install
        with open("settings.json", 'w') as output_file:
            json.dump({"download_folder": ""}, output_file)
        async_loop = asyncio.get_event_loop()
        main(async_loop)
