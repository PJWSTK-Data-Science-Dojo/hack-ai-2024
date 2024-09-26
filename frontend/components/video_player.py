import base64
import io
from jinja2 import Template
from utils import read_template
import streamlit.components.v1 as components


def video_player(video: io.BytesIO, subtitle: io.BytesIO = None, timestamps=None):
    template_str = read_template("video_player")
    template = Template(template_str)
    html_output = template.render(
        video_url=f"data:video/mp4;base64,{base64.b64encode(video).decode()}",
        subtitle_url="data:text/vtt;base64,{srt_base64}",
        timestamps=timestamps,
    )

    components.html(html_output, height=600)
