pragma journal_mode = WAL;
pragma synchronous = normal;
pragma user_version = 3;

CREATE TABLE IF NOT EXISTS model (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    category TEXT NOT NULL,
    nsfw INTEGER NOT NULL,
    creator_name TEXT NOT NULL,
    creator_image TEXT NOT NULL,
    image TEXT NOT NULL,
    image_blur_hash TEXT NOT NULL,
    description TEXT NOT NULL,
    updated_at INTEGER NOT NULL,
    download_cnt INTEGER NOT NULL,
    favorite_cnt INTEGER NOT NULL,
    thumbs_up_cnt INTEGER NOT NULL,
    thumbs_down_cnt INTEGER NOT NULL,
    comment_cnt INTEGER NOT NULL,
    rating_cnt INTEGER NOT NULL,
    rating_score REAL NOT NULL,
    tipped_amt_cnt INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS model_version (
    id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    trained_words TEXT NOT NULL,
    base_model TEXT NOT NULL,
    download_cnt INTEGER NOT NULL,
    rating_cnt INTEGER NOT NULL,
    rating_score REAL NOT NULL,
    thumbs_up_cnt INTEGER NOT NULL,
    thumbs_down_cnt INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model (id)
);

CREATE TABLE IF NOT EXISTS model_file (
    id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    model_version_id INTEGER NOT NULL,
    is_primary BOOLEAN NOT NULL,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    size INTEGER NOT NULL,
    safe BOOLEAN NOT NULL,
    format TEXT NOT NULL,
    datatype TEXT NOT NULL,
    pruned BOOLEAN NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model (id),
    FOREIGN KEY (model_version_id) REFERENCES model_version (id)
);

CREATE TABLE IF NOT EXISTS model_image (
    id INTEGER PRIMARY KEY,
    model_id INTEGER NOT NULL,
    model_version_id INTEGER NOT NULL,
    url TEXT NOT NULL,
    generation_data TEXT NOT NULL,
    blur_hash TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    FOREIGN KEY (model_id) REFERENCES model (id),
    FOREIGN KEY (model_version_id) REFERENCES model_version (id)
);

CREATE TABLE IF NOT EXISTS metadata (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    UNIQUE (key)
);

CREATE TABLE IF NOT EXISTS download_history (
    id INTEGER PRIMARY KEY,
    download_count INTEGER NOT NULL,
    FOREIGN KEY (model_version_id) REFERENCES model_version (id)
);