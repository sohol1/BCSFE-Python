from typing import Any, Optional
from bcsfe.core import game_version, io


class Login:
    def __init__(self, count: int):
        self.count = count

    @staticmethod
    def read(stream: io.data.Data) -> "Login":
        count = stream.read_int()
        return Login(count)

    def write(self, stream: io.data.Data):
        stream.write_int(self.count)

    def serialize(self) -> dict[str, int]:
        return {"count": self.count}

    @staticmethod
    def deserialize(data: dict[str, int]) -> "Login":
        return Login(data["count"])

    def __repr__(self):
        return f"Login({self.count})"

    def __str__(self):
        return f"Login({self.count})"


class Logins:
    def __init__(self, logins: list[Login]):
        self.logins = logins

    @staticmethod
    def read(stream: io.data.Data) -> "Logins":
        total = stream.read_int()
        logins: list[Login] = []
        for _ in range(total):
            logins.append(Login.read(stream))
        return Logins(logins)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.logins))
        for login in self.logins:
            login.write(stream)

    def serialize(self) -> dict[str, list[dict[str, int]]]:
        return {"logins": [login.serialize() for login in self.logins]}

    @staticmethod
    def deserialize(data: dict[str, list[dict[str, int]]]) -> "Logins":
        return Logins([Login.deserialize(login) for login in data["logins"]])

    def __repr__(self):
        return f"Logins({self.logins})"

    def __str__(self):
        return f"Logins({self.logins})"


class LoginSets:
    def __init__(self, logins: list[Logins]):
        self.logins = logins

    @staticmethod
    def read(stream: io.data.Data) -> "LoginSets":
        total = stream.read_int()
        logins: list[Logins] = []
        for _ in range(total):
            logins.append(Logins.read(stream))
        return LoginSets(logins)

    def write(self, stream: io.data.Data):
        stream.write_int(len(self.logins))
        for login in self.logins:
            login.write(stream)

    def serialize(self) -> dict[str, list[dict[str, list[dict[str, int]]]]]:
        return {"logins": [login.serialize() for login in self.logins]}

    @staticmethod
    def deserialize(
        data: dict[str, list[dict[str, list[dict[str, int]]]]]
    ) -> "LoginSets":
        return LoginSets([Logins.deserialize(login) for login in data["logins"]])

    def __repr__(self):
        return f"LoginSets({self.logins})"

    def __str__(self):
        return f"LoginSets({self.logins})"


class LoginBonus:
    def __init__(
        self,
        old_logins: Optional[LoginSets] = None,
        logins: Optional[dict[int, Login]] = None,
    ):
        self.old_logins = old_logins
        self.logins = logins

    @staticmethod
    def read(stream: io.data.Data, gv: game_version.GameVersion) -> "LoginBonus":
        if gv < 80000:
            logins_old = LoginSets.read(stream)
            return LoginBonus(logins_old)
        else:
            total = stream.read_int()
            logins: dict[int, Login] = {}
            for _ in range(total):
                id = stream.read_int()
                logins[id] = Login.read(stream)
            return LoginBonus(logins=logins)

    def write(self, stream: io.data.Data, gv: game_version.GameVersion):
        if gv < 80000 and self.old_logins is not None:
            self.old_logins.write(stream)
        elif gv >= 80000 and self.logins is not None:
            stream.write_int(len(self.logins))
            for id, login in self.logins.items():
                stream.write_int(id)
                login.write(stream)

    def serialize(
        self,
    ) -> dict[str, Any]:
        if self.old_logins is not None:
            return {"old_logins": self.old_logins.serialize()}
        elif self.logins is not None:
            return {
                "logins": {id: login.serialize() for id, login in self.logins.items()}
            }
        else:
            return {}

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "LoginBonus":
        if "old_logins" in data:
            return LoginBonus(old_logins=LoginSets.deserialize(data["old_logins"]))
        elif "logins" in data:
            return LoginBonus(
                logins={
                    int(id): Login.deserialize(login)
                    for id, login in data["logins"].items()
                }
            )
        else:
            return LoginBonus()

    def __repr__(self):
        return f"LoginBonus({self.old_logins}, {self.logins})"

    def __str__(self):
        return f"LoginBonus({self.old_logins}, {self.logins})"
