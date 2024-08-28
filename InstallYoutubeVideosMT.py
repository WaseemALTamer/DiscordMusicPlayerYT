from typing import Union
from yt_dlp import YoutubeDL
from pytube import YouTube
import datetime
import json
import os




class YTVideosInstaller():
    def __init__(self) -> None:
        self.Queue = None
        self.VideoURLs = []
        self.DownloadedVideos = 0



    def write_key_to_json(self, file_path: str, key: str, value) -> None:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
        except:
            data = {}
        data[key] = value
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)


    def extract_array_from_json(self, json_file: str) -> Union[dict, None]:
        with open(json_file, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                print("The JSON file does not contain an array.")


    def write_to_file(self, line: str, filename:str) -> dict:
        with open(filename, 'a', encoding='utf-8') as file:
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{formatted_datetime}: {line}\n")


    def download_highest_quality_video(self, url:str , output_path:str) -> None:
        # Ensure output folder exists
        os.makedirs(output_path, exist_ok=True)

        # yt-dlp options to download the best format available (either video+audio combined or just video)

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',  # Specify mp4 format for both video and audio
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),  # Save with the video title as filename
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Convert the video to mp4 if necessary
            }],
            'quiet': False,
            'progress_hooks': []
        }
        
        # Download video
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"Video downloaded to {output_path}")




    def download_video(self, url:str, output_path:str, HighRes=False) -> str:
        if HighRes == True:
            output_path += "/1080p"
            self.download_highest_quality_video(url,output_path)
            return
        else:
            output_path += "/Audio"


        yt = YouTube(url)

        stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        if stream is None:
            stream = yt.streams.filter(progressive=True, file_extension="mp4").first()


        filename = stream.default_filename
        stream.download(output_path)
        return filename

    def download_video(self, url:str, output_path:str, HighRes=False, Record=True) -> str:
        yt = YouTube(url)
        try:
            stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
            filename = stream.default_filename
            stream.download(output_path)
            if Record:
                self.write_key_to_json("InstalledVideos.json", url, filename)
        except Exception as e:
            return e
        return filename




    #functions to be ran by a seperate threads 
    # Note! use the join method otherwise the theads will be only virtuallised and the installation process will be overall slower
    def ThreadProccess(self, OutputFolder ,HighRes=False):

        while True:
            if len(self.Queue) == 0:
                break

            temp = self.Queue[0]
            index = len(self.VideoURLs) - len(self.Queue)

            try:
                self.Queue.pop(0)
                File = self.download_video(temp, f"VideosOutputTest/{OutputFolder}", HighRes=HighRes, Record=False)            
                self.write_to_file(f"Download Complete : index --> {index} FileName --> {File} ","Logs/OutLog.txt")
            except Exception as e:
                print("An error occurred:", str(e))
                self.write_to_file(f"Couldn't install: {temp}         Error As----->{e}","Logs/ErrorLog.txt")
                self.write_to_file(self.DownloadedVideos,"Logs/UnComplete.txt")
                Errors += 1
            self.DownloadedVideos += 1
            print(f"Precentage Complete = {(int((self.DownloadedVideos/len(self.VideoURLs)) * 100))}%=============>{self.DownloadedVideos}/{len(self.VideoURLs)}")



