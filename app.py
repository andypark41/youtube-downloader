from flask import Flask, render_template_string, request, send_file, after_this_request
import yt_dlp as youtube_dl
import os
from threading import Timer

app = Flask(__name__)

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'force_generic_extractor': True,
    'encoding': 'utf-8',
}

def download_media(url: str, media_type: str):
    ytdl_options = ytdl_format_options.copy()
    
    if media_type == 'audio':
        ytdl_options['format'] = 'bestaudio/best'
        ytdl_options['outtmpl'] = '%(title)s.mp3'
    elif media_type == 'video':
        ytdl_options['format'] = 'bestvideo+bestaudio'
        ytdl_options['outtmpl'] = '%(title)s.mp4'
    
    ytdl = youtube_dl.YoutubeDL(ytdl_options)
    
    try:
        info_dict = ytdl.extract_info(url, download=True)
        file_name = ytdl.prepare_filename(info_dict)
        return file_name
    except Exception as e:
        print(f"Error downloading {media_type}: {e}")
        return None

def delete_file_after_delay(file_path: str, delay: int):
    Timer(delay, lambda: os.remove(file_path) if os.path.isfile(file_path) else None).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        media_type = request.form.get('media_type')
        
        if 'youtube.com/watch?' in url or 'youtu.be/' in url:
            file_name = download_media(url, media_type)
            
            if file_name:
                @after_this_request
                def remove_file(response):
                    delete_file_after_delay(file_name, 1)
                    return response

                return send_file(file_name, as_attachment=True)
            else:
                return "Error in downloading the file."
        else:
            return "Invalid YouTube URL."
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube Downloader</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                margin-bottom: 20px;
            }
            input, select, button {
                padding: 10px;
                margin-top: 10px;
                margin-bottom: 10px;
                width: 100%;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-sizing: border-box;
            }
            button {
                background-color: #28a745;
                color: #fff;
                cursor: pointer;
            }
            button:hover {
                background-color: #218838;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YouTube Downloader</h1>
            <form method="POST">
                <label for="url">YouTube URL:</label><br>
                <input type="text" id="url" name="url" required><br><br>
                <label for="media_type">Download as:</label><br>
                <select id="media_type" name="media_type" required>
                    <option value="audio">Audio (MP3)</option>
                    <option value="video">Video (MP4)</option>
                </select><br><br>
                <button type="submit">Download</button>
            </form>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(debug=True)
