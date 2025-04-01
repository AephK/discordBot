#general packages
import os, logging, random, math, sys, platform, urllib.request, subprocess
#media handling packages
import yt_dlp, ffmpeg

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
sys.stdout = open("discordBot.log", "w")
sys.stderr = open("discordBotErr.log","w")

scriptDir = os.path.dirname('__file__')
tokenFile = open(scriptDir + 'discordToken', 'r')
token = tokenFile.read()


if platform.system() == 'Linux':
    cwd = os.getcwd() + '/'
    cookieFile = '/home/aephk/cookies.txt'
    ffmpegLoc = '/usr/lib/jellyfin-ffmpeg/ffmpeg'
    #ffprobe = '/usr/lib/jellyfin-ffmpeg/ffmpeg'
    #youtubedl = "/home/aephk/.local/bin/yt-dlp"
    deleteTemp = 'rm temp.*'

elif platform.system():
    cwd = os.getcwd() + '\\'
    cookieFile = 'C:\\Temp\\discordBotTest\\cookies.txt'
    ffmpegLoc = "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
    #ffprobe = "C:\\Temp\\ffmpeg\\bin\\ffprobe.exe"
    #youtubedl = "C:\\youtubedl\\yt-dlp.exe"
    deleteTemp = 'del temp.*'

print(cwd)

import discord
from discord.ext import commands
import random

description = '''intrvBot!

User ?v [url] to send an inline video.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

@bot.command()
async def v(ctx, url: str):
    await ctx.message.delete()
    subprocess.Popen(deleteTemp, shell=True).wait()
    ydl_opts = {'format_sort' : ['res:1280', '+br'],
                'cookiefile' : cookieFile,
                'ffmpeg_location' : ffmpegLoc,
                'merge_output_format' : 'mp4',
                'outtmpl': cwd + 'temp.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    originalSize = int(ffmpeg.probe(cwd + "temp.mp4")["format"]["size"])

    if (originalSize > 10000000):
        try:
            print("renaming mp4 to temp")
            os.rename(cwd + "temp.mp4", cwd + "temp.temp")

            #Get video length and calculate max video bitrate in order to come in under 50MB (25MB?)
            sourceLength = ffmpeg.probe(cwd + "temp.temp")["format"]["duration"]
            print("SourceLength: " + sourceLength)
            finalMaxBitrate = ((10/int(float((sourceLength))))*8)
            audioBitrate=64
            videoBitrate = finalMaxBitrate-(audioBitrate/1000)
            videoBitrate = math.floor(videoBitrate)
            if (videoBitrate > 2):
                videoBitrate = 2

            output_file = f"{cwd}temp.mp4"
            ffmpeg.input(f"{cwd}temp.temp").filter('pad', width='ceil(iw/2)*2', height='ceil(ih/2)*2').output(output_file,
                vcodec='h264_qsv',
                vb=f"{videoBitrate}M",
                acodec='copy',
                ab=f"{audioBitrate}k",
                maxrate=f"{finalMaxBitrate}M",
                bufsize="1M",
                map='0:a') \
            .run()

        except:
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

    file = open(cwd + 'temp.mp4', 'rb')
    caption='Sent by: ' + str(ctx.author.display_name)
    await ctx.send(caption, file=discord.File(cwd + "temp.mp4"), silent=True)


bot.run(token)
