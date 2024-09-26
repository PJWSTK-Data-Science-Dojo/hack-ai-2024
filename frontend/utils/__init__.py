import io
from pathlib import Path


def save_buffer_to_file(buffer: io.BytesIO, file_name: str):
    """
    Save the content of a BytesIO buffer to a video file.

    :param buffer: BytesIO buffer containing video data.
    :param output_filename: The name of the file to save.
    """
    videos = Path("videos")
    if not videos.exists():
        videos.mkdir()

    with open(f"videos/{file_name}.mp4", "wb") as f:
        f.write(buffer.getbuffer())


def read_template(template_name):
    with open(f"frontend/templates/{template_name}.html", "r") as f:
        return f.read()
