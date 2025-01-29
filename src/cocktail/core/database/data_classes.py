"""
This module contains the data classes for the database.
These are used to extract data from the Civitai API and insert it into the database.
NamedTuple is favored as its easy to decompose into columns for batch insertion.
"""
import logging

import datetime
import json
import enum
import time
import typing
from PySide6 import QtSql
from cocktail.core.database import util

logger = logging.getLogger(__name__)


class Period(enum.Enum):
    Day = "Day"
    Week = "Week"
    Month = "Month"
    Year = "Year"
    AllTime = "AllTime"


def items_from_model_version(model_id: int, data: dict):
    version = ModelVersion.from_json(model_id, data)

    files = [
        ModelFile.from_json(version.model_id, version.id, file)
        for file in data["files"]
    ]
    files = [file for file in files if file.safe]
    images = [
        ModelImage.from_json(version.model_id, version.id, image)
        for image in data["images"]
    ]

    return version, files, images


def items_from_model_json(data: dict):
    model = Model.from_json(data)
    versions = []
    files = []
    images = []

    for version_data in data["modelVersions"]:
        version, version_files, version_images = items_from_model_version(model.id, version_data)
        versions.append(version)
        files.extend(version_files)
        images.extend(version_images)

    if len(versions) == 0:
        logger.warning(f"Model {model.name} has no versions, discarding.")
        return None, None, None, None
    else:
        return model, versions, files, images


def deserialise_items(page: typing.List[dict]):
    models = []
    versions = []
    files = []
    images = []
    for model_data in page:
        model, model_versions, model_files, model_images = items_from_model_json(
            model_data
        )

        if model is None:
            continue

        models.append(model)
        versions.extend(model_versions)
        files.extend(model_files)
        images.extend(model_images)

    return Page(models, versions, images, files)


class Model(typing.NamedTuple):
    id: int
    name: str
    type: str
    category: str
    nsfw: bool
    creator_name: str
    creator_image: str
    image: str
    image_blur_hash: str
    description: str
    updated_at: int
    download_cnt: int
    favorite_cnt: int
    thumbs_up_cnt: int
    thumbs_down_cnt: int
    comment_cnt: int
    rating_cnt: int
    rating_score: float
    tipped_amt_cnt: int

    @classmethod
    def from_json(cls, data: dict):
        image_data = util.get_image(data)

        timestamps = list(iter_model_timestamps(data))
        if timestamps:
            timestamp = max(timestamps)
        else:
            timestamp = datetime.datetime.now().timestamp()

        if "creator" in data:
            creator_name = data["creator"]["username"]
            creator_image = data["creator"]["image"] or ""
        else:
            creator_name = ""
            creator_image = ""

        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            category=util.select_category(data["tags"]),
            nsfw=util.detect_nsfw(data, image_data),
            creator_name=creator_name,
            creator_image=creator_image,
            image=image_data.get("url", ""),
            image_blur_hash=image_data.get("hash", "") or "",
            description=data["description"] or "",
            updated_at=timestamp,
            download_cnt=data["stats"]["downloadCount"],
            favorite_cnt=data["stats"]["favoriteCount"],
            thumbs_up_cnt=data["stats"]["thumbsUpCount"],
            thumbs_down_cnt=data["stats"]["thumbsDownCount"],
            comment_cnt=data["stats"]["commentCount"],
            rating_cnt=data["stats"]["ratingCount"],
            rating_score=data["stats"]["rating"],
            tipped_amt_cnt=data["stats"]["tippedAmountCount"]
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            name=record.value("name"),
            type=record.value("type"),
            category=record.value("category"),
            nsfw=record.value("nsfw"),
            creator_name=record.value("creator_name"),
            creator_image=record.value("creator_image"),
            image=record.value("image"),
            image_blur_hash=record.value("image_blur_hash"),
            description=record.value("description"),
            updated_at=record.value("updated_at"),
            download_cnt=record.value("download_cnt"),
            favorite_cnt=record.value("favorite_cnt"),
            thumbs_up_cnt=record.value("thumbs_up_cnt"),
            thumbs_down_cnt=record.value("thumbs_down_cnt"),
            comment_cnt=record.value("comment_cnt"),
            rating_cnt=record.value("rating_cnt"),
            rating_score=record.value("rating_score"),
            tipped_amt_cnt=record.value("tipped_amt_cnt")
        )


class ModelFile(typing.NamedTuple):
    id: int
    model_id: int
    model_version_id: int
    is_primary: bool
    name: str
    url: str
    size: int
    safe: bool
    format: str
    datatype: str
    pruned: bool

    @classmethod
    def from_json(cls, model_id, model_version_id, data: dict):
        metadata = data["metadata"]
        metadata.pop("trainingResults", None)

        datatype = metadata.get("fp", "") or ""
        pruned = (metadata.get("size", "") or "") != "full"
        format = metadata.get("format", "") or ""

        return cls(
            id=data["id"],
            model_id=model_id,
            model_version_id=model_version_id,
            is_primary=data.get("primary", False),
            name=data["name"],
            url=data["downloadUrl"],
            size=data["sizeKB"],
            format=format,
            pruned=pruned,
            datatype=datatype,
            safe=util.is_file_safe(data),
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            model_id=record.value("model_id"),
            model_version_id=record.value("model_version_id"),
            is_primary=record.value("is_primary"),
            name=record.value("name"),
            url=record.value("url"),
            size=record.value("size"),
            safe=record.value("safe"),
            format=record.value("format"),
            datatype=record.value("datatype"),
            pruned=record.value("pruned"),
        )


class ModelImage(typing.NamedTuple):
    id: int
    model_id: int
    model_version_id: int
    url: str
    generation_data: str
    blur_hash: str
    width: int
    height: int

    @classmethod
    def from_json(cls, model_id, model_version_id, data: dict):
        metadata = data.get("meta", {}) or {}

        generation_data = {
            "prompt": metadata.get("prompt", ""),
            "negativePrompt": metadata.get("negativePrompt", ""),
            "seed": metadata.get("seed", ""),
            "steps": metadata.get("steps", 20),
            "cfgScale": metadata.get("cfgScale", 7.0),
            "sampler": metadata.get("sampler", ""),
        }

        return cls(
            id=data["id"],
            model_id=model_id,
            model_version_id=model_version_id,
            url=data["url"],
            generation_data=generation_data,
            blur_hash=data.get("hash", "") or "",
            width=data["width"],
            height=data["height"],
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            model_id=record.value("model_id"),
            model_version_id=record.value("model_version_id"),
            url=record.value("url"),
            generation_data=json.loads(record.value("generation_data")),
            blur_hash=record.value("blur_hash"),
            width=record.value("width"),
            height=record.value("height"),
        )


class ModelVersion(typing.NamedTuple):
    id: int
    model_id: int
    name: str
    description: str
    trained_words: typing.List[str]
    base_model: str
    download_cnt: int
    rating_cnt: int
    rating_score: float
    thumbs_up_cnt: int
    thumbs_down_cnt: int

    @classmethod
    def from_json(cls, model_id: int, data: dict):
        return cls(
            id=data["id"],
            model_id=model_id,
            name=data["name"],
            description=data["description"] or "",
            trained_words=data["trainedWords"],
            base_model=data.get("baseModel", "Other"),
            download_cnt=data["stats"]["downloadCount"],
            rating_cnt=data["stats"]["ratingCount"],
            rating_score=data["stats"]["rating"],
            thumbs_up_cnt=data["stats"]["thumbsUpCount"],
            thumbs_down_cnt=data["stats"]["thumbsDownCount"],
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            model_id=record.value("model_id"),
            name=record.value("name"),
            description=record.value("description"),
            trained_words=json.loads(record.value("trained_words")),
            base_model=record.value("base_model"),
            download_cnt=record.value("download_cnt"),
            rating_cnt=record.value("rating_cnt"),
            rating_score=record.value("rating_score"),
            thumbs_up_cnt=record.value("thumbs_up_cnt"),
            thumbs_down_cnt=record.value("thumbs_down_cnt"),
        )


class Page(typing.NamedTuple):
    models: typing.List[Model]
    versions: typing.List[ModelVersion]
    images: typing.List[ModelImage]
    files: typing.List[ModelFile]


def parse_timestamp(date_str: str):
    date_str = date_str.replace("Z", "+00:00")
    return int(datetime.datetime.fromisoformat(date_str).timestamp())


def iter_model_timestamps(model_data):
    for version in model_data["modelVersions"]:
        updated_at = version.get("updatedAt")
        if updated_at:
            yield parse_timestamp(updated_at)
            continue

        published_at = version.get("publishedAt")
        if published_at:
            yield parse_timestamp(published_at)
            continue

        created_at = version.get("createdAt")
        if created_at:
            yield parse_timestamp(created_at)
            continue

        file_timestamps = [f.get("scannedAt") for f in version.get("files", [])]
        file_timestamps = [parse_timestamp(f) for f in file_timestamps if f]
        if file_timestamps:
            yield max(file_timestamps)
            continue

        yield int(datetime.datetime.now().timestamp())


if __name__ == "__main__":
    with open("/home/rob/dev/browser/model_data.json") as file:
        data = json.load(file)
