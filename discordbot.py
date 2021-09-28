import discord, enum
import dltwitchclips as dltwitch

class Commands(enum.Enum):
    Download = "!download"

    def usage(self):
        if self.value == Commands.Download.value:
            return "Usage: !download [-u] { -subreddit LivestreamFail -limit 5 | -single https://www.twitch.tv/hasanabi/clip/PerfectPlacidCrabsPanicVis }"
        return "Usage not defined"

class Options(enum.Enum):
    SubredditClips = "-subreddit"
    SingleClip = "-single"
    Limit = "-limit" 
    Upload = "-u"

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.startswith(Commands.Download.value):
            if Options.SubredditClips.value in message.content and Options.Limit.value in message.content:
                split = message.content.split()
                if len(split) >= 5:
                    await message.channel.send("Fetching subreddit posts...")
                    sr_index = split.index(Options.SubredditClips.value)
                    lim_index = split.index(Options.Limit.value)
                    videos = dltwitch.get_urls(split[sr_index + 1], int(split[lim_index + 1]))
                    await message.channel.send("Downloading clips...")
                    dltwitch.download_videos(videos)
                    await message.channel.send("Downloaded videos: " + str(len(videos)))
                    if Options.Upload.value in message.content:
                        await message.channel.send("Uploading to YouTube...")
                        dltwitch.upload_videos(videos)
                        await message.channel.send("Upload to YouTube successful.")
                else:
                    await message.channel.send(Commands.Download.usage())
            elif Options.SingleClip.value in message.content:
                if "https://www.twitch.tv/" in message.content:
                    split = message.content.split()
                    print(split)
                else:
                    await message.channel.send(Commands.Download.usage())
            else:
                await message.channel.send(Commands.Download.usage())


#print(dltwitch.get_urls("LivestreamFail"))

client = MyClient()
client.run('discord token here')

