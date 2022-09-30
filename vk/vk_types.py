from typing import NamedTuple


class UploadFotoResp(NamedTuple):
    server: str
    photo: str
    hash: str


class SaveWallPhotoResp(NamedTuple):
    media_id: str
    owner_id: str
