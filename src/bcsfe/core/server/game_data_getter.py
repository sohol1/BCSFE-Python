from typing import Any, Callable, Optional
from bcsfe.cli import color

from bcsfe import core


class GameDataGetter:
    def __init__(self, save_file: "core.SaveFile"):
        self.cc = save_file.cc
        self.url = core.config.get(core.ConfigKey.GAME_DATA_REPO)
        self.latest_version = self.get_latest_version()

    def get_latest_version(self) -> Optional[str]:
        versions = core.RequestHandler(self.url + "latest.txt").get().text.split("\n")
        length = len(versions)
        if self.cc == core.CountryCodeType.EN and length >= 1:
            return versions[0]
        if self.cc == core.CountryCodeType.JP and length >= 2:
            return versions[1]
        if self.cc == core.CountryCodeType.KR and length >= 3:
            return versions[2]
        if self.cc == core.CountryCodeType.TW and length >= 4:
            return versions[3]
        return None

    def get_file(self, pack_name: str, file_name: str) -> Optional["core.Data"]:
        if self.latest_version is None:
            return None
        url = self.url + f"{self.latest_version}/{pack_name}/{file_name}"
        response = core.RequestHandler(url).get()
        if response.status_code != 200:
            return None
        return core.Data(response.content)

    def get_file_path(self, pack_name: str, file_name: str) -> Optional["core.Path"]:
        if self.latest_version is None:
            return None
        path = (
            core.Path("game_data", is_relative=True)
            .add(self.latest_version)
            .add(pack_name)
        )
        path.generate_dirs()
        path = path.add(file_name)
        return path

    def save_file(self, pack_name: str, file_name: str) -> Optional["core.Data"]:
        data = self.get_file(pack_name, file_name)
        if data is None:
            return None

        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return None
        data.to_file(path)
        return data

    def is_downloaded(self, pack_name: str, file_name: str) -> bool:
        path = self.get_file_path(pack_name, file_name)
        if path is None:
            return False
        return path.exists()

    def download_from_path(
        self, path: str, retries: int = 2, display_text: bool = True
    ) -> Optional["core.Data"]:
        pack_name, file_name = path.split("/")
        return self.download(pack_name, file_name, retries, display_text)

    def download(
        self,
        pack_name: str,
        file_name: str,
        retries: int = 2,
        display_text: bool = True,
    ) -> Optional["core.Data"]:
        retries -= 1

        if self.is_downloaded(pack_name, file_name):
            path = self.get_file_path(pack_name, file_name)
            if path is None:
                return None
            return path.read()

        if retries == 0:
            return None

        if display_text:
            color.ColoredText.localize(
                "downloading",
                file_name=file_name,
                pack_name=pack_name,
                version=self.latest_version,
            )
        data = self.save_file(pack_name, file_name)
        if data is None:
            return self.download(pack_name, file_name, retries, display_text)
        return data

    def download_all(
        self, pack_name: str, file_names: list[str], display_text: bool = True
    ) -> list[Optional[tuple[str, "core.Data"]]]:
        callables: list[Callable[..., Any]] = []
        args: list[tuple[str, str, int, bool]] = []
        for file_name in file_names:
            callables.append(self.download)
            args.append((pack_name, file_name, 2, display_text))
        core.thread_run_many(callables, args)
        data_list: list[Optional[tuple[str, core.Data]]] = []
        for file_name in file_names:
            path = self.get_file_path(pack_name, file_name)
            if path is None:
                data_list.append(None)
            elif not path.exists():
                data_list.append(None)
            else:
                data_list.append((file_name, path.read()))
        return data_list
