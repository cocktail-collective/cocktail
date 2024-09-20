import json
import os

# additional words that indicate nsfw content. Civitai's nsfw tag is not very reliable.
# I never thought I'd have to put these words in a repo but here we are.
NSFW_WORDS = [
    "blood",
    "gore",
    "nsfw",
    "sex",
    "nude",
    "naked",
    "areola",
    "breast",
    "nipple" "tits",
    "titjob",
    "fuck",
    "boob",
    "topless",
    "ass",
    "anal",
    "pussy",
    "cameltoe",
    "vagina",
    "hentai",
    "furry",
    "anthro",
    "underwear",
    "lingerie",
    "pantie",
    "tentacle",
    "fetish",
    "gag",
    "bondage",
    "penis",
    "cock",
    "bbc",
    "bj",
    "futa",
    "deepthroat",
    "blowjob",
    "cum",
    "bukkake",
    "porn",
    "waifu",
    "erotic",
    "fellatio",
    "prolapse",
    "peeing",
    "bimbo",
]

# creators who produce NSFW content and don't mark their models
NSFW_CREATORS = [
    "wisematronai",
    "tipzy",
    "hearmeneigh",
    "runkun07",
    "scorchingflames",
    "xsiri1",
    "wtfusion",
    "sworddaolee",
    "myk3sr621",
    "ai_art_factory",
    "new50",
    "nomosx",
    "watterystool",
    "mik357",
    "kankybou44",
    "janloy",
    "throwawayjm",
    "blueb",
    "eldisss",
    "sono36484is989",
    "ydoomenaud",
    "shivae",
    "hoshi119",
]

CATEGORIES = [
    "character",
    "style",
    "celebrity",
    "concept",
    "clothing",
    "base model",
    "poses",
    "background",
    "tool",
    "buildings",
    "vehicle",
    "objects",
    "animal",
    "action",
    "asset",
]

CATEGORY_ICONS = {
    "character": "fa5.user-circle",
    "style": "fa.paint-brush",
    "celebrity": "ei.adult",
    "concept": "mdi6.head-lightbulb",
    "clothing": "fa5s.tshirt",
    "base model": "mdi.cube-scan",
    "poses": "fa5s.running",
    "background": "fa5.image",
    "tool": "fa5s.toolbox",
    "buildings": "fa5s.building",
    "vehicle": "mdi.car-hatchback",
    "objects": "fa.coffee",
    "animal": "fa5s.dog",
    "action": "mdi6.run-fast",
    "asset": "mdi.cube-scan",
}

MODEL_TYPE_ICONS = {
    "All": "fa.asterisk",
    "Checkpoint": "mdi.file-check",
    "TextualInversion": "mdi6.file-cloud",
    "AestheticGradient": "mdi.gradient",
    "Hypernetwork": "ph.share-network-bold",
    "LORA": "mdi.file-plus",
    "Other": "fa5s.question",
    "LoCon": "mdi.file-plus",
    "ControlNet": "ph.person-simple",
    "Poses": "mdi6.run-fast",
    "Wildcards": "fa.asterisk",
    "Workflows": "mdi.teach",
    "VAE": "fa.arrows-h",
    "Upscaler": "mdi6.image-size-select-large",
    "MotionModule": "mdi6.run-fast",
}


def get_db_path():
    return os.path.expanduser("~/.cache/cocktail/cocktail.db")


def get_image(model_data):
    for version in model_data["modelVersions"]:
        for image in version["images"]:
            return image

    return {}


def select_category(tags):
    for category in CATEGORIES:
        if category in tags:
            return category

    return "other"


def is_file_safe(file_data: dict):
    return (
            file_data["pickleScanResult"] == "Success"
            and file_data["virusScanResult"] == "Success"
    )


def detect_nsfw(model_data: dict, image: dict):
    if "nsfwLevel" in model_data:
        return model_data["nsfwLevel"]
    else:
        try:
            if detect_nsfw(model_data, image):
                return 50
        except KeyError:
            return False


def detect_nsfw_legacy(model_data: dict, image: dict):
    creator = model_data["creator"]["username"]
    if creator.lower() in NSFW_CREATORS:
        return True

    image = image if image is not None else {}

    nsfw_prompt = False
    nsfw_name = False
    nsfw_tag = False

    meta = image.get("meta", {}) or {}
    prompt = meta.get("prompt", "").lower()
    model_name = model_data["name"].lower()

    for nsfw_word in NSFW_WORDS:
        for tag in model_data["tags"]:
            if nsfw_word in tag.lower():
                nsfw_tag = True
                break

    for nsfw_word in NSFW_WORDS:
        if nsfw_word in model_name.lower():
            nsfw_name = True
            break

    for nsfw_word in NSFW_WORDS:
        if nsfw_word in prompt.lower():
            nsfw_prompt = True
            break

    return nsfw_tag or nsfw_prompt or nsfw_name
