import contextlib
import os
import typing
import youtube_dl
from .ytdlinfo import YtdlInfo
from .errors import NotFoundError, MultipleFilesError, MissingInfoError, AlreadyDownloadedError


class YtdlFile:
    """Information about a youtube-dl downloaded file."""

    _default_ytdl_args = {
        "quiet": True,  # Do not print messages to stdout.
        "noplaylist": True,  # Download single video instead of a playlist if in doubt.
        "no_warnings": True,  # Do not print out anything for warnings.
        "outtmpl": "%(title)s-%(id)s.%(ext)s"  # Use the default outtmpl.
    }

    def __init__(self,
                 url: str,
                 info: YtdlInfo = None,
                 filename: str = None):
        self.url: str = url
        self.info: YtdlInfo = info
        self.filename: str = filename

    def has_info(self) -> bool:
        return self.info is not None

    def is_downloaded(self) -> bool:
        return self.filename is not None and os.path.exists(self.filename)

    @contextlib.contextmanager
    def open(self):
        if not self.is_downloaded():
            raise FileNotFoundError("The file hasn't been downloaded yet.")
        with open(self.filename, "r") as file:
            yield file

    def update_info(self, **ytdl_args) -> None:
        infos = YtdlInfo.retrieve_for_url(self.url, **ytdl_args)
        if len(infos) == 0:
            raise NotFoundError()
        elif len(infos) > 1:
            raise MultipleFilesError()
        self.info = infos[0]

    def download_file(self, **ytdl_args) -> None:
        if not self.has_info():
            raise MissingInfoError()
        if self.is_downloaded():
            raise AlreadyDownloadedError()
        with youtube_dl.YoutubeDL({**self._default_ytdl_args, **ytdl_args}) as ytdl:
            ytdl.download([self.info.webpage_url])
            self.filename = ytdl.prepare_filename(self.info.__dict__)

    def delete_file(self):
        """Delete the file located at ``self.filename``."""
        if not self.is_downloaded():
            raise FileNotFoundError("The file hasn't been downloaded yet.")
        os.remove(self.filename)
        self.filename = None

    @classmethod
    def download_from_url(cls, url: str, **ytdl_args) -> typing.List["YtdlFile"]:
        infos = YtdlInfo.retrieve_for_url(url, **ytdl_args)
        files = []
        for info in infos:
            file = YtdlFile(url=info.webpage_url, info=info)
            file.download_file(**ytdl_args)
            files.append(file)
        return files
