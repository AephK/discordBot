#!/usr/bin/python3
import os, logging, random, math, sys, platform, urllib.request, ffmpeg, subprocess
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
sys.stdout = open('bot.log', "w")
sys.stderr = open("botErr.log", "w")

#clear up exisiting logs
#os.system("rm bot.log")
#os.system("rm botErr.log")
subprocess.Popen("rm botErr.log", shell=True).wait()

scriptDir = os.path.dirname('__file__')
tokenFile = open(scriptDir + 'token', 'r')
token = tokenFile.read()

if platform.system() == 'Linux':
    cwd = os.getcwd() + '/'
    #ffmpegLoc = "/usr/bin/ffmpeg"
    ffmpegLoc = '/usr/lib/jellyfin-ffmpeg/ffmpeg'
    ffprobe = "/usr/bin/ffprobe"
    youtubedl = "/home/aephk/.local/bin/yt-dlp"
    deleteTemp = 'rm temp.*'

elif platform.system():
    cwd = os.getcwd() + '\\'
    ffmpegLoc = "C:\\youtubedl\\ffmpeg.exe"
    ffprobe = "C:\\youtubedl\\ffprobe.exe"
    youtubedl = "C:\\youtubedl\\yt-dlp.exe"
    deleteTemp = 'del temp.*'

else:
    print("Unable to determine OS version")
    exit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        "Me bot!"
    )

async def v(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #os.system(deleteTemp)
    subprocess.Popen(deleteTemp, shell=True).wait()
    chat_id1=update.effective_chat.id
    message_id=update.message.message_id
    url = context.args[0]

    capt = '<a href="' + url + '">Sent by: ' + update.message.from_user.first_name + '</a>'
    print(url)
    update.message.reply_video
    await (
    context.bot.deleteMessage(chat_id1, message_id)
    )

    ydl_opts = {'cookiefile' : '/home/aephk/cookies.txt',
#               'format_sort' : ['res:720', '+br'],
                'format_sort' : ['res:1280', '+br'],
                'ffmpeg_location' : ffmpegLoc,
                'merge_output_format' : 'mp4',
                'outtmpl': cwd + 'temp.mp4'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    originalSize = int(ffmpeg.probe(cwd + "temp.mp4")["format"]["size"])

    if (originalSize > 2621000):
        try:
            print("renaming mp4 to temp")
            os.rename(cwd + "temp.mp4", cwd + "temp.temp")

            #Get video length and calculate max video bitrate in order to come in under 50MB (25MB?)
            sourceLength = ffmpeg.probe(cwd + "temp.temp")["format"]["duration"]
            print("SourceLength: " + sourceLength)
            finalMaxBitrate = ((25/int(float((sourceLength))))*8)
            audioBitrate=64
            videoBitrate = finalMaxBitrate-(audioBitrate/1000)
            videoBitrate = math.floor(videoBitrate)
            if (videoBitrate > 2):
                videoBitrate = 2
            command = ffmpegLoc + " -i " + cwd + 'temp.temp -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -c:v h264_qsv -b:v ' + str(videoBitrate) + "M -c:a copy -b:a " + str(audioBitrate) + "k -maxrate " + str(finalMaxBitrate) + "M -bufsize 1M " + cwd + 'temp.mp4'

            #os.system(command)
            subprocess.Popen(command, shell=True).wait()

        except:
            print("renaming temp to mp4")
            if os.path.isfile(cwd + "temp.temp"):
                os.rename(cwd + "temp.temp", cwd + "temp.mp4")

    file = open(cwd + 'temp.mp4', 'rb')
    files = {
        'video' : file
        }
    await (
        context.bot.send_video(chat_id=chat_id1, video=file, parse_mode='html', caption=capt, disable_notification=True)
    )
    file.close()

    #os.system(deleteTemp)
    subprocess.Popen(deleteTemp, shell=True).wait()

async def roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id1=update.effective_chat.id
    message_id=update.message.message_id

    await (
    context.bot.deleteMessage(chat_id1, message_id)
    )

    name = update.message.from_user.first_name
    result = 0
    diceCount = 0
    diceType = 0

    if context.args:
        if 'd' in context.args[0]:
            roll = context.args[0]
            diceCount = roll.split('d')[0]
            diceType = roll.split('d')[1]

    else:
        diceCount = 1
        diceType = 20

    if str(diceCount).isdigit() and str(diceType).isdigit():
        diceCount = int(math.floor(float(diceCount)))
        diceType = int(math.floor(float(diceType)))

        if diceCount != 0 and diceType != 1 and diceType != 0:

            for i in range(diceCount):
                result += random.randint(1, diceType)

            message = name + " rolled " + str(diceCount) + "d" + str(diceType) + " and got: " + str(result)

        else:
            message = name + " failed the constipation check."

    else:
        message = name + " failed the constipation check."

    await(
        context.bot.send_message(chat_id=update.effective_chat.id, disable_notification=True, text=message)
    )


def main() -> None:


    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('roll', roll))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('v', v))

    application.run_polling()

if __name__ == "__main__":
    main()
