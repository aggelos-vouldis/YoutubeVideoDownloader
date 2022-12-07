from pytube import YouTube


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
        return f'\n\nyt: {self.yt} \nyt_video: {self.yt_video}\nURL: {self.url}\nTitle: {self.title}\nFile Size: {self.file_size}\nHighest Resolution: {self.highest_res}\nAuthor: {self.author}\nViews: {self.views}'


def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100

    print(round(percentage_of_completion))


def download():
    chunk_size = 1024
    v1.yt.register_on_progress_callback(on_progress)

    print(f"Downloading \"{v1.title}\"..")
    v1.yt_video.download('D:\\Videos')


def get_video_info(url):
    yt = YouTube(url)
    video = yt.streams.get_highest_resolution()

    return {"yt": yt, "yt_video": video, "URL": url, "Title": video.title, "File Size": {round(video.filesize * 0.000001, 2)}, "Res": video.resolution, "Author": yt.author, "Views": "{:,}\n".format(yt.views)}


download_video = True

while download_video == True:
    url = input("Give me the URl to download\n")
    information = get_video_info(url)
    v1 = Video(information["yt"], information["yt_video"], information["URL"], information["Title"], information["File Size"],
               information["Res"], information["Author"], information["Views"])

    print(v1.__str__())

    want_to_download = input("Do you want to download the video? (y/n):")

    if want_to_download == 'y':
        download()
        another_download = input(
            "Do you want to download another video? (y/n):")
        if another_download == 'n':
            download_video = False
    else:
        download_video = False
