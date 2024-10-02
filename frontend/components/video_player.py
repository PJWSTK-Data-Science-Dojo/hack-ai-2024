import base64
import io
from jinja2 import Template
from utils import read_template
import streamlit.components.v1 as components
import streamlit as st

def video_player(video: io.BytesIO, subtitles: io.BytesIO = None, timestamps=None):
    subtitles_url = None
    if subtitles is not None:
        subtitles_url = f"data:text/srt;base64,{base64.b64encode(subtitles).decode()}"
    
    # template_str = read_template("video_player")
    # template = Template(template_str)
    # html_output = template.render(
    #     video_url=f"data:video/mp4;base64,{base64.b64encode(video).decode()}",
    #     subtitle_url=subtitles_url,
    #     timestamps=timestamps,
    # )

    # components.html(html_output, height=600)
    
    st.video(video, subtitles=subtitles_url)
