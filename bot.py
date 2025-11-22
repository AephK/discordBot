#general packages
import os, logging, random, math, sys, platform, urllib.request, subprocess
#media handling packages
import yt_dlp, ffmpeg
#platform api packages
import discord
from discord.ext import commands

videoMaxSize = 10000 #max size in KB
overhead = 0.80

if platform.system() == 'Linux':
    cwd = os.getcwd() + '/'
    cookieFile = '/home/aephk/cookies.txt'
    deleteTemp = 'rm temp.*'

elif platform.system():
    cwd = os.getcwd() + '\\'
    cookieFile = 'C:\\Temp\\discordBotTest\\cookies.txt'
    deleteTemp = 'del temp.*'

else:
    print("Unable to determine OS version")
    exit()

scriptDir = cwd
tokenFile = open(scriptDir + 'discordToken', 'r')
token = tokenFile.read()

#####logging config
stdout_path = os.path.join(scriptDir, 'bot.log')
stderr_path = os.path.join(scriptDir, 'botErr.log')

try:
    os.remove(stdout_path)
except FileNotFoundError:
    pass

try:
    os.remove(stderr_path)
except FileNotFoundError:
    pass

sys.stdout = open(stdout_path, "w")
sys.stderr = open(stderr_path, "w")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
#####

print(cwd)

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
                'merge_output_format' : 'mp4',
                'outtmpl': cwd + 'temp.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    originalSize = int(ffmpeg.probe(cwd + "temp.mp4")["format"]["size"])

    if (originalSize > videoMaxSize):
        try:
            print("File too big. Resizing...")
            print("Renaming mp4 to temp")
            os.rename(cwd + "temp.mp4", cwd + "temp.temp")

            #Get video length and calculate max video bitrate in order to come in under 50MB (25MB?)
            sourceLength = ffmpeg.probe(cwd + "temp.temp")["format"]["duration"]
            #account for overhead, reduce max size
            finalMaxSize = (videoMaxSize * overhead)
            finalMaxBitrate = (((finalMaxSize)/float((sourceLength)))*8)

            audioBitrate=64
            videoBitrate = math.floor(finalMaxBitrate-(audioBitrate))
            if (videoBitrate > 2000):
                videoBitrate = 2000
            print("videoBitrate: " + str(videoBitrate))

            in_path = os.path.join(cwd, 'temp.temp')
            out_path = os.path.join(cwd, 'temp.mp4')

            stream = (
                ffmpeg
                .input(in_path)
                .filter('pad', 'ceil(iw/2)*2', 'ceil(ih/2)*2')  # make width/height even
                .output(
                    out_path,
                    vcodec='h264_qsv',
                    acodec='aac',
                    **{
                        'b:v': f'{videoBitrate}k',
                        'b:a': f'{audioBitrate}k',
                        'maxrate': f'{math.floor(finalMaxBitrate)}k',
                        'bufsize': '3M',
                    }
                )
            )
            stream.run(overwrite_output=True)

        except Exception as e:
            print(f"Error: {e}", flush=True)
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

    file = open(cwd + 'temp.mp4', 'rb')
    caption='Sent by: ' + str(ctx.author.display_name)
    await ctx.send(caption, file=discord.File(cwd + "temp.mp4"), silent=True)

bot.run(token)
