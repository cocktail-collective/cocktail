"""
This module contains the data classes for the database.
These are used to extract data from the Civitai API and insert it into the database.
NamedTuple is favored as its easy to decompose into columns for batch insertion.
"""
import logging

import datetime
import json
import enum
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


def items_from_model_version(data: dict):
    version = ModelVersion.from_json(data)
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
        version, version_files, version_images = items_from_model_version(version_data)
        versions.append(version)
        files.extend(version_files)
        images.extend(version_images)

    if len(versions) == 0:
        logger.warning(f"Model {model.name} has no versions, discarding.")
        return [], [], [], []
    else:
        return model, versions, files, images


def deserialise_page(page: typing.List[dict]):
    models = []
    versions = []
    files = []
    images = []
    for model_data in page:
        model, model_versions, model_files, model_images = items_from_model_json(
            model_data
        )
        models.append(model)
        versions.extend(model_versions)
        files.extend(model_files)
        images.extend(model_images)

    return Page(models, versions, files, images)


class Model(typing.NamedTuple):
    id: int
    name: str
    type: str
    category: str
    nsfw: bool
    creator_name: str
    creator_image: str
    image: str
    description: str
    updated_at: int

    @classmethod
    def from_json(cls, data: dict):
        image_data = util.get_image(data)

        timestamps = list(iter_model_timestamps(data))
        if timestamps:
            timestamp = max(timestamps)
        else:
            timestamp = datetime.datetime.now().timestamp()

        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            category=util.select_category(data["tags"]),
            nsfw=util.detect_nsfw(data, image_data),
            creator_name=data["creator"]["username"],
            creator_image=data["creator"]["image"] or "",
            image=image_data.get("url", ""),
            description=data["description"] or "",
            updated_at=timestamp,
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
            description=record.value("description"),
            updated_at=record.value("updated_at"),
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

    @classmethod
    def from_json(cls, model_id, model_version_id, data: dict):
        metadata = {
            "prompt": data.get("prompt", ""),
            "negativePrompt": data.get("negativePrompt", ""),
        }

        return cls(
            id=data["id"],
            model_id=model_id,
            model_version_id=model_version_id,
            url=data["url"],
            generation_data=json.dumps(metadata),
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            model_id=record.value("model_id"),
            model_version_id=record.value("model_version_id"),
            url=record.value("url"),
            generation_data=json.loads(record.value("generation_data")),
        )


class ModelVersion(typing.NamedTuple):
    id: int
    model_id: int
    name: str
    description: str

    @classmethod
    def from_json(cls, data: dict):
        return cls(
            id=data["id"],
            model_id=data["modelId"],
            name=data["name"],
            description=data["description"] or "",
        )

    @classmethod
    def from_record(cls, record: QtSql.QSqlRecord):
        return cls(
            id=record.value("id"),
            model_id=record.value("model_id"),
            name=record.value("name"),
            description=record.value("description"),
        )


class Page(typing.NamedTuple):
    models: typing.List[Model]
    versions: typing.List[ModelVersion]
    files: typing.List[ModelFile]
    images: typing.List[ModelImage]


def parse_timestamp(date_str: str):
    date_str = date_str.replace("Z", "+00:00")
    return int(datetime.datetime.fromisoformat(date_str).timestamp())


def iter_model_timestamps(model_data):
    for version in model_data["modelVersions"]:
        updated_at_str = (
            version.get("updatedAt", version["createdAt"]) or version["createdAt"]
        )
        yield parse_timestamp(updated_at_str)


if __name__ == "__main__":
    with open("/home/rob/dev/browser/model_data.json") as file:
        data = json.load(file)
