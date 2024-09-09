from InstallYoutubeVideosMT import YTVideosInstaller
from urllib.parse import urlparse, parse_qs
from YoutubeRequester import YoutubeAPI
from discord.ext import commands
from discord import app_commands
import discord.ext.commands
from typing import Union
import discord.ext
import threading
import discord
import json
import sys
import os






class DiscordPlayer():

    def __init__(self, Token) -> None:
        self.Token = Token
        self.intents = discord.Intents.all()
        self.intents.message_content = True
        self.intents.voice_states = True  # Enable voice state intent
        self.Bot = commands.Bot(command_prefix='/', intents=self.intents)
        self.VideoInstaller = YTVideosInstaller()
        self.DiscordServersData = {
                #Structure-> DiscordServer : {"Queue" : [Queue:list], "SongPlaying": None, "CurentlyPlaying": False}
        }



        #Mapping the events to the functions
        @self.Bot.event
        async def on_ready():
            print(f'Logged in as {self.Bot.user}!')
            await self.Bot.tree.sync()
            

        @self.Bot.tree.command(name='play', description='Play a song through youtube url')
        async def play(interaction: discord.Interaction, url: str):
            await self.OnPlay(interaction, url)

        @self.Bot.tree.command(name='playlist', description='play a playlist through its youtube url')
        async def playlist(interaction: discord.Interaction, url: str):
            await self.On_PlayList(interaction, url)

        @self.Bot.tree.command(name='skip',description="skips the curretly playing song")
        async def skip(interaction: discord.Interaction):
            await self.On_Skip(interaction)


        @self.Bot.tree.command(name='disconnect')
        async def disconnect(interaction: discord.Interaction):
            await self.OnDisconnect(interaction)

        @self.Bot.tree.command(name="restart", description="This will restart the whole bot script")
        async def restart(interaction: discord.Interaction):
            await self.On_Restart(interaction)


       




    async def OnPlay(self, interaction: discord.Interaction, url: str):
        url = self.extract_youtube_video_id(url)


        user = interaction.user
        if user.voice is None:
            await interaction.response.send_message("You're not in a voice channel!")
            return

        DiscordServer = user.guild
        channel = user.voice.channel

        #If there is a song that is already playing the just add the next song the the queue if the song is not in the server install it while playing the other song using asyc
        if DiscordServer in self.DiscordServersData and self.DiscordServersData[DiscordServer]["CurentlyPlaying"] == True:
            self.DiscordServersData[DiscordServer]["Queue"].append(url)
            try:
                with open("InstalledVideos.json", 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                data = {}

            if not (url in data and os.path.exists(f"VideosOutput/{data[url]}")):
                await interaction.response.send_message(f'The Song is not in the server and will be graped Online')
                await self.InstallSong(url, "VideosOutput")
                await interaction.followup.send("The song is installed and added to the queue and will be played after the current song")
            else:
                await interaction.response.send_message(f'The Song is already in the server and is added to the queue to play after the current song')
            return


        #if there is no infromation about the server intiate the infromation
        if DiscordServer not in self.DiscordServersData:
            self.DiscordServersData[DiscordServer] = {"Queue" : [], 
                                                      "SongPlaying": None, 
                                                      "CurentlyPlaying": False}


        # If the bot is not already connected, connect it to the channel
        if interaction.guild.voice_client is None:
            await channel.connect()
            await interaction.response.send_message(f'Joined {channel}')
        else:
            await interaction.response.send_message(f'Preparing The Bot')
            await interaction.guild.voice_client.move_to(channel)

        #if everything goes well then we can start playing the music
        await self.PlaySong(interaction, url)


    async def On_PlayList(self, interaction: discord.Interaction, url: str):
        print(url)
        await interaction.response.send_message("The PlayList is getting imported")
        PlayListHerfs = YoutubeAPI().PlaylistHerfsRequest(url)

        
        
        if PlayListHerfs != []:
            user = interaction.user
            if user.voice is None:
                await interaction.followup.send("You're not in a voice channel!")
                return

            DiscordServer = user.guild
            channel = user.voice.channel

            #if there is no infromation about the server intiate the infromation
            if DiscordServer not in self.DiscordServersData:
                self.DiscordServersData[DiscordServer] = {
                                                            "Queue" : PlayListHerfs[1:],
                                                            "SongPlaying": None, 
                                                            "CurentlyPlaying": False
                                                            }
            else:
                self.DiscordServersData[DiscordServer]["Queue"] = PlayListHerfs[1:]


            # If the bot is not already connected, connect it to the channel
            if interaction.guild.voice_client is None:
                await channel.connect()
                await interaction.followup.send(f'Joined {channel}')
            else:
                await interaction.followup.send(f'Preparing The Bot')
                await interaction.guild.voice_client.move_to(channel)
            
            await self.PlaySong(interaction, PlayListHerfs[0])
            if len(PlayListHerfs) != 1: # we check if there is another song so in orginal queue (remember that is not the Queue we just saved) 
                                        #so we can just check if it has more than one if it has less than one then it will get flaged from before 
                await self.install_Song_On_Thread_if_not_avalibale(interaction, PlayListHerfs[1])
            




    #this function is need because some music videos require more than 10 second and will block the main thread this way it is run on a async which will not 
    #raise the error of main thread being blocked i know know if this methode may cuz problem in the future due to loop backs in the async methods refare to
    #the discord documnation or use your own async mthode through import async to write the methode from scratch or use the threading library with the .join 
    #may work
    async def InstallSong(self, url:str, OutputFolder:str):
        SongName = self.VideoInstaller.download_video(url, "VideosOutput") #the download function has its own error handling refare to the files that is being used
        return SongName

    async def PlaySong(self, interaction:discord.Interaction, url:str):
        try:
            with open("InstalledVideos.json", 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}

        DiscordServer = interaction.user.guild

        #Play the song if the song is not installed install it
        if url in data and os.path.exists(f"VideosOutput/{data[url]}"):
            SongName = data[url]
            audio_source = discord.FFmpegPCMAudio(source=f"VideosOutput/{data[url]}")
            self.DiscordServersData[DiscordServer]["CurentlyPlaying"] = True
        else:
            await interaction.followup.send(f'The Song is getting Installed on the server...')
            SongName = self.VideoInstaller.download_video(url, "VideosOutput")
            await interaction.followup.send(f'The Song Installed')
            audio_source = discord.FFmpegPCMAudio(source=f"VideosOutput/{SongName}")
            self.DiscordServersData[DiscordServer]["CurentlyPlaying"] = True
            
        
        interaction.guild.voice_client.play(audio_source, after=lambda e:  self.Bot.loop.create_task(self.song_finished(interaction, e)))
        await interaction.followup.send(f'Started playing "{url}" -> {SongName}')



    async def song_finished(self, interaction: discord.Interaction, error:Union[str, None]):
        if error:
            print(f"An error occurred: {error}")
        else:
            Queue = self.DiscordServersData[interaction.user.guild]["Queue"]
            PlayingStutas = self.DiscordServersData[interaction.user.guild]["CurentlyPlaying"]
            if Queue != [] and PlayingStutas:
                url = Queue[0]
                Queue.pop(0)
                await self.PlaySong(interaction, url)
                
                if Queue != []:
                    await self.install_Song_On_Thread_if_not_avalibale(interaction, Queue[0])

            else:
                self.DiscordServersData[interaction.user.guild]["CurentlyPlaying"] = False
                await self.OnDisconnect(interaction) #simulate the disconnect so it does not stay in the server after the song ends


    async def install_Song_On_Thread_if_not_avalibale(self, interaction: discord.Interaction, url:str)->None: #this function will be used to install the video in prepration after the first music stops playing
                try:
                    with open("InstalledVideos.json", 'r') as file:
                        data = json.load(file)
                except FileNotFoundError:
                    data = {}
                #check if the video is not installed or not in the folder
                if not(url in data and os.path.exists(f"VideosOutput/{data[url]}")):
                    threading.Thread(target=self.VideoInstaller.download_video, args=(url, "VideosOutput",)).start() # start the thread to install it 


    async def On_Skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message(f'Song is skiped')
        else:
            await interaction.response.send_message(f'Nothing is playing')


    async def OnDisconnect(self, interaction: discord.ext.commands):
        if interaction.guild.voice_client is not None:
            if interaction.user.guild in self.DiscordServersData:
                self.DiscordServersData[interaction.user.guild]["CurentlyPlaying"] = False
            await interaction.guild.voice_client.disconnect()
        # If the interaction has already been responded to, use followup this elementates the issue with event has only one response
        if interaction.response.is_done():
            await interaction.followup.send(f'Disconnected')
        else:
            await interaction.response.send_message(f'Disconnected')




    async def On_Restart(self, interaction: discord.ext.commands):
        await interaction.response.send_message(f'The bot is restarting')
        os.execv(sys.executable, ['python'] + sys.argv)




    def Run(self):
        self.Bot.run(self.Token)



    #private functions
    def extract_youtube_video_id(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            video_id = query_params.get('v', [''])[0]
            return f"watch?v={video_id}"
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return ''