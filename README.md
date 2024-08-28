Install the requirements by going to cmd navigate to the files that you installed (\DiscordMusicPlayerYT)
then run the command in the terminal:
                                    pip install -r requirements.txt

this should install all the dependencys you need but they may be errors in the pytube library Check the 
YoutubeRequester.py it may help to fix the problem

go the Main.py file and add your Token inside of it:


```python
from DiscordBot import DiscordPlayer

Token = "xxxx-xxxx-xxxx-xxxx" # add your bot token
x = DiscordPlayer(Token)
x.Run()
```

now run the Main.py file make sure that you have the discord bot setup and with the right prmissions
