from gradio_client import Client, handle_file

client = Client("https://llava-onevision.lmms-lab.com/")
result = client.predict(
    video_input={
        "video": handle_file(
            "https://github.com/gradio-app/gradio/raw/main/demo/video_component/files/world.mp4"
        )
    },
    messages={"text": "", "files": []},
    image_process_mode="Default",
    api_name="/add_text",
)
print(result)
