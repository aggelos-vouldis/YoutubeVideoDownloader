from pytube import YouTube, exceptions, Playlist
from enum import Enum


class ExceptionCode(Enum):
    PRIVATE_VIDEO = 0x0100
    REGION_BLOCKED = 0x0101
    VIDEO_UNAVAILABLE = 0x0102
    PY_TUBE_ERROR = 0x0103
    WRONG_URL = 0x0104
    MAJOR_ERROR = 0x0202


def get_error_message(code: ExceptionCode):
    if code == ExceptionCode.PRIVATE_VIDEO:
        return "This video is private"
    elif code == ExceptionCode.REGION_BLOCKED:
        return "This video is not available in your country"
    elif code == ExceptionCode.VIDEO_UNAVAILABLE:
        return "This video is not available"
    elif code == ExceptionCode.PY_TUBE_ERROR:
        return "There is a problem with services"
    elif code == ExceptionCode.WRONG_URL:
        return "The url you entered is wrong"
    elif code == ExceptionCode.MAJOR_ERROR:
        return "Serious problem with services"


class CustomVideoException(Exception):
    def __init__(self, code: ExceptionCode) -> None:
        super().__init__(f"Error code: {code.value}, {get_error_message(code)}")


class Video:
    def __init__(self, url) -> None:

        try:
            self.yt = YouTube(url)
        except exceptions.VideoPrivate:
            raise CustomVideoException(ExceptionCode.PRIVATE_VIDEO)
        except exceptions.VideoRegionBlocked:
            raise CustomVideoException(ExceptionCode.REGION_BLOCKED)
        except exceptions.VideoUnavailable:
            raise CustomVideoException(ExceptionCode.VIDEO_UNAVAILABLE)
        except exceptions.PytubeError:
            raise CustomVideoException(ExceptionCode.PY_TUBE_ERROR)
        except Exception:
            raise CustomVideoException(ExceptionCode.MAJOR_ERROR)

        video_streams = self.yt.streams.filter(file_extension='mp4')
        audio_streams = self.yt.streams.filter(only_audio=True)
        self.video_resolutions = list()
        self.audio_resolutions = list()

        self.title = self.yt.title
        self.author = self.yt.author
        self.views = self.yt.views

        for stream in video_streams:
            self.video_resolutions.append({"_type": stream.mime_type, "res": stream.resolution})
        for stream in audio_streams:
            self.audio_resolutions.append({"_type": stream.mime_type, "abr": stream.abr})

    def _download(self, selected_res: str, on_progress_callback):
        # return self.yt.streams.get_by_resolution(selected_res)
        self.yt.register_on_progress_callback(on_progress_callback)
        self.yt.streams.get_by_resolution(selected_res).download()

    def on_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100

        print(round(percentage_of_completion))

    def __str__(self) -> str:
        return f'VIDEO:\nTitle: {self.title}, Author: {self.author}, Views: {self.views}\nVideo Resolutions: ' \
               f'{self.video_resolutions}\nAudio Resolutions: {self.audio_resolutions}'


class _Playlist:
    def __init__(self) -> None:
        self.videos = list()

    def read_playlist(self, url: str):
        temp_playlist = Playlist(url)
        for video_url in temp_playlist.video_urls:
            self.videos.append({"code": video_url.split("=")[1], "video": Video(video_url)})

    def add_video(self, url: str):
        if "youtube.com" not in url:
            raise CustomVideoException(ExceptionCode.WRONG_URL)
        if "watch?v=" not in url:
            raise CustomVideoException(ExceptionCode.WRONG_URL)
        self.videos.append({"code": url.split("=")[1], "video": Video(url)})

    async def add_video_async(self, url:str) -> None:
        if "youtube.com" not in url:
            raise CustomVideoException(ExceptionCode.WRONG_URL)
        if "watch?v=" not in url:
            raise CustomVideoException(ExceptionCode.WRONG_URL)
        await self.videos.append({"code": url.split("=")[1], "video": Video(url)})

    def print_video_urls(self):
        for v in self.videos:
            print(v["video"])


if __name__ == "__main__":
    video_list = _Playlist()
    video_list.add_video(url="https://www.youtube.com/watch?v=GceNsojnMf0")
    # video_list.read_playlist(url="https://www.youtube.com/playlist?list=PLk0xntvQ2OlK5Ep-R-qnszWDrP_nzgGEW")
    for video in video_list.videos:
        print(video["video"])
    # video_list.print_video_urls()
