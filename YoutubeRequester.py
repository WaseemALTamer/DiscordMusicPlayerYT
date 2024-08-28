from urllib.parse import urlparse, parse_qs
from pytube import Playlist

#this file should be writen again and sohuld not be reliying on the pytube libray to grap the hefrs

class YoutubeAPI():
    #this request is using the pytube library to get the herfs the pytube libray had a problem and was not working due to youtube updataing there javascrip
    #if this accures again the pytybe library need to be fixed if the pytube library does not work for you it is most likely because of the invalid command
    #from the re library in my case i had to go to the cypher.py file in the library and change the function_patterns and add: 
    """function_patterns = [
    # https://github.com/ytdl-org/youtube-dl/issues/29326#issuecomment-865985377
    # https://github.com/yt-dlp/yt-dlp/commit/48416bc4a8f1d5ff07d5977659cb8ece7640dcd8
    # var Bpa = [iha];
    # ...
    # a.C && (b = a.get("n")) && (b = Bpa[0](b), a.set("n", b),
    # Bpa.length || iha("")) }};
    # In the above case, `iha` is the relevant function name
    r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&.*?\|\|\s*([a-z]+)',
    r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
    r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]"""
    #this fix my have already been fixed for later updates when they come out but as for now i am using pytube 24.1.2 which did not work until the fix has
    #has ben applied.



    def __init__(self) -> None:
        pass

    #this function is slow esspically if there is more than 50 videos in one play list check the pytube.Playlist to know why
    def PlaylistHerfsRequest(self, playlist_url: str) -> list:
        playlist = Playlist(playlist_url)
        video_urls = [video.watch_url for video in playlist.videos]
        Herfs = []
        for Video in video_urls:
            Herfs.append(self.extract_youtube_video_id(Video))
        return Herfs
    
    #private functions
    #this function is writen twice in the BotServer and here we should fix that and reuse the function but keep the structure of the code maintainable 
    def extract_youtube_video_id(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [''])[0]
            return f"watch?v={video_id}"
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return ''



#this only is excuted if the files it self is run not when you import it
if __name__ == "__main__":
    # Example usage
    x = YoutubeAPI()
    HerfsList = x.PlaylistHerfsRequest("https://www.youtube.com/watch?v=KvZ-EzOVB10&list=PL9FUXHTBubp-_e0wyNu1jfVVJ2QVAi5NW&index=5")
    print(HerfsList)
