import pathlib

# Function to convert float seconds to SRT time format
def seconds_to_srt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def gen_srt_file(subtitle_data: dict, output_path: pathlib.Path):
    # Prepare content for the SRT file
    srt_content = []
    for index, item in enumerate(subtitle_data, start=1):
        start_time = seconds_to_srt_time(item['start'])
        end_time = seconds_to_srt_time(item['end'])
        srt_content.append(f"{index}")
        srt_content.append(f"{start_time} --> {end_time}")
        srt_content.append(item['text'])
        srt_content.append("")  # Blank line to separate entries

    # Join the content with new lines to follow SRT format
    srt_file_content = "\n".join(srt_content)

    # Save to .srt file
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(srt_file_content)
