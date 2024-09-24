import io

def save_buffer_to_file(buffer: io.BytesIO, output_filename: str):
    """
    Save the content of a BytesIO buffer to a video file.

    :param buffer: BytesIO buffer containing video data.
    :param output_filename: The name of the file to save.
    """
    with open(f"videos/{output_filename}", 'wb') as f:
        f.write(buffer.getbuffer())
    print(f"Video saved to {output_filename}")

def read_template(template_name):
    with open(f"frontend/templates/{template_name}.html", 'r') as f:
        return f.read()