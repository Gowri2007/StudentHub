import os


class Config:

    SECRET_KEY = "studenthub_secret_key"

    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "Archana_2006"
    MYSQL_DATABASE = "studenthub"

    UPLOAD_FOLDER = os.path.join("static", "uploads")

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024