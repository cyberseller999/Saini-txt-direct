import os
import re
import sys
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, LOG_CHANNEL
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

AUTH_USER = os.environ.get('AUTH_USERS', '5680454765').split(',')
AUTH_USERS = [int(user_id) for user_id in AUTH_USER]
if int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
    
CHANNEL_OWNERS = {}
CHANNELS = os.environ.get('CHANNELS', '').split(',')
CHANNELS_LIST = [int(channel_id) for channel_id in CHANNELS if channel_id.isdigit()]

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")

api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
token_cp ='eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'
adda_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkcGthNTQ3MEBnbWFpbC5jb20iLCJhdWQiOiIxNzg2OTYwNSIsImlhdCI6MTc0NDk0NDQ2NCwiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiZHBrYSIsImVtYWlsIjoiZHBrYTU0NzBAZ21haWwuY29tIiwicGhvbmUiOiI3MzUyNDA0MTc2IiwidXNlcklkIjoiYWRkYS52MS41NzMyNmRmODVkZDkxZDRiNDkxN2FiZDExN2IwN2ZjOCIsImxvZ2luQXBpVmVyc2lvbiI6MX0.0QOuYFMkCEdVmwMVIPeETa6Kxr70zEslWOIAfC_ylhbku76nDcaBoNVvqN4HivWNwlyT0jkUKjWxZ8AbdorMLg"

photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png' #https://envs.sh/GV0.jpg
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png' #https://envs.sh/GVi.jpg
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'


# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot")]])
keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl"), InlineKeyboardButton(text="🛠️ Repo", url="https://github.com/cyberseller999/saini-txt-direct")],
])

# Image URLs for the random image feature
image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
    # Add more image URLs as needed
]

@bot.on_message(filters.command("addauth") & filters.private)
async def add_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("**This command only for bot Owner**")
    
    try:
        new_user_id = int(message.command[1])
        if new_user_id in AUTH_USERS:
            await message.reply_text("**User ID is already authorized.**")
        else:
            AUTH_USERS.append(new_user_id)
            # Update the environment variable (if needed)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"**User ID `{new_user_id}` added to authorized users.**")
    except (IndexError, ValueError):
        await message.reply_text("**Please provide a valid user ID.**")
        
@bot.on_message(filters.command("remauth") & filters.private)
async def remove_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("**This command only for bot Owner**")
    
    try:
        user_id_to_remove = int(message.command[1])
        if user_id_to_remove not in AUTH_USERS:
            await message.reply_text("**User ID is not in the authorized users list.**")
        else:
            AUTH_USERS.remove(user_id_to_remove)
            # Update the environment variable (if needed)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"**User ID `{user_id_to_remove}` removed from authorized users.**")
    except (IndexError, ValueError):
        await message.reply_text("**Please provide a valid user ID.**")

@bot.on_message(filters.command("users") & filters.private)
async def list_auth_users(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("**This command only for bot Owner**")
    
    user_list = '\n'.join(map(str, AUTH_USERS))
    await message.reply_text(f"<blockquote><b>Authorized Users:</b></blockquote>\n\n<blockquote>{user_list}</blockquote>")

@bot.on_message(filters.command("addchnl") & filters.private)
async def add_channel(client: Client, message: Message):
    if message.from_user.id not in AUTH_USERS:
        return await message.reply_text("**This command only for Authorised Users**")

    try:
        new_channel_id = int(message.command[1])
        
        # Validate that the channel ID starts with -100
        if not str(new_channel_id).startswith("-100"):
            return await message.reply_text("**Invalid channel ID. Channel IDs must start with -100.**")
        
        if new_channel_id in CHANNELS_LIST:
            await message.reply_text("**Channel ID is already added.**")
        else:
            CHANNELS_LIST.append(new_channel_id)
            CHANNEL_OWNERS[new_channel_id] = message.from_user.id  # Assign the user as the owner of the channel
            # Update the environment variable (if needed)
            os.environ['CHANNELS'] = ','.join(map(str, CHANNELS_LIST))
            await message.reply_text(f"**Channel ID `{new_channel_id}` added to the list and you are now the owner of this channel.**")
    except (IndexError, ValueError):
        await message.reply_text("**Please provide a valid channel ID.**")

@bot.on_message(filters.command("remchnl") & filters.private)
async def remove_channel(client: Client, message: Message):
    try:
        channel_id_to_remove = int(message.command[1])
        
        # Check if the channel exists in the list
        if channel_id_to_remove not in CHANNELS_LIST:
            return await message.reply_text("**Channel ID is not in the list.**")
        
        # Check if the user is the OWNER or the channel owner
        if message.from_user.id != OWNER and CHANNEL_OWNERS.get(channel_id_to_remove) != message.from_user.id:
            return await message.reply_text("**This channel is not added by you.**")

        # Remove the channel
        CHANNELS_LIST.remove(channel_id_to_remove)
        if channel_id_to_remove in CHANNEL_OWNERS:
            del CHANNEL_OWNERS[channel_id_to_remove]  # Remove from the ownership dictionary if present
        
        # Update the environment variable (if needed)
        os.environ['CHANNELS'] = ','.join(map(str, CHANNELS_LIST))
        await message.reply_text(f"**Channel ID `{channel_id_to_remove}` removed from the list.**")
    except (IndexError, ValueError):
        await message.reply_text("**Please provide a valid channel ID.**")

@bot.on_message(filters.command("channels") & filters.private)
async def list_channels(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("**This command only for bot Owner**")
    
    if not CHANNELS_LIST:
        await message.reply_text("**No channels have been added yet.**")
    else:
        channel_list = '\n'.join(map(str, CHANNELS_LIST))
        await message.reply_text(f"<blockquote><b>Authorized Channels:</b></blockquote>\n\n<blockquote><b>{channel_list}</b></blockquote>")
        
@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text("**Upload cookies file in .txt format.**")

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(m.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("**Invalid file type. Please upload a .txt file.**")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await m.reply_text(f"__**Failed Reason:**__\n<blockquote><b>{str(e)}</b></blockquote>")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    # Inform the user to send the text data and its desired file name
    editable = await message.reply_text(f"<blockquote><b>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</b></blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("**Send valid text data**")
        return

    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()  # Corrected here
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(f"**Send YouTube Playlist link for convert in .txt file**")

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'  # Specify the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(
                f"**__Failed Reason:__\n<blockquote>{str(e)}</blockquote>**"
            )
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<blockquote>{title}.txt</blockquote>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)


m_file_path= "main.py"
@bot.on_message(filters.command("getcookies") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(chat_id=m.chat.id, document=cookies_file_path, caption="Here is the `youtube_cookies.txt` file.")
    except Exception as e:
        await m.reply_text(f"**Failed Reason:\n<blockquote>{str(e)}</blockquote>**")     
@bot.on_message(filters.command("mfile") & filters.private)
async def getcookies_handler(client: Client, m: Message):
    try:
        await client.send_document(chat_id=m.chat.id, document=m_file_path, caption="Here is the `main.py` file.")
    except Exception as e:
        await m.reply_text(f"**Failed Reason:\n<blockquote>{str(e)}</blockquote>**")

@bot.on_message(filters.command(["ytm"]))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text("🔹**Send me the TXT file containing YouTube links.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await bot.send_document(OWNER, x)
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return

    await m.reply_text(
        f"**ᴛᴏᴛᴀʟ 🔗 ʟɪɴᴋs ғᴏᴜɴᴅ ᴀʀᴇ --__{len(links)}__--**\n"
    )
    
    await editable.edit("**🔹sᴇɴᴅ ғʀᴏᴍ ᴡʜᴇʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ**")
    try:
        input0: Message = await bot.listen(editable.chat.id, timeout=10)
        raw_text = input0.text
        await input0.delete(True)
    except asyncio.TimeoutError:
        raw_text = '1'
        
        await editable.delete()
        try:
            arg = int(raw_text)
        except:
            arg = 1

    await m.reply_text(
        f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n"
    )
    
    count = int(raw_text)
    try:
        for i in range(arg-1, len(links)):  # Iterate over each link

            Vxy = links[i][1].replace("www.youtube-nocookie.com/embed", "youtu.be")
            url = "https://" + Vxy

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "")
            name = f'{name1[:60]} {CREDIT}'

            if "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp -x --audio-format mp3 --cookies {cookies_file_path} "{url}" -o "{name}.mp3"'
                print(f"Running command: {cmd}")
                os.system(cmd)
                if os.path.exists(f'{name}.mp3'):
                   print(f"File {name}.mp3 exists, attempting to send...")
                   try:
                       await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp3', caption=f'**🎵 Title : **  {name}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By** : {CREDIT}')
                       os.remove(f'{name}.mp3')
                   except Exception as e:
                       print(f"Error sending document: {str(e)}")
                else:
                     print(f"File {name}.mp3 does not exist.")                
    except Exception as e:
        await m.reply_text(f"<b>Failed Reason:</b>\n<blockquote><b>{str(e)}</b></blockquote>")
    finally:
        await m.reply_text("🕊️Done Baby💞")


@bot.on_message(filters.command(["yt2m"]))
async def yt2m_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"🔹**Send me the YouTube link**")
    input: Message = await bot.listen(editable.chat.id)
    youtube_link = input.text.strip()
    await input.delete(True)

    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**\n\n🔗𝐔𝐑𝐋 »  {youtube_link}\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}🐦"
    await editable.edit(Show, disable_web_page_preview=True)
    await asyncio.sleep(10)

    try:
        Vxy = youtube_link.replace("www.youtube-nocookie.com/embed", "youtu.be")
        url = Vxy

        # Fetch the YouTube video title using oEmbed
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url)
        audio_title = response.json().get('title', 'YouTube Video')

        name = f'{audio_title[:60]} {CREDIT}'
        
        if "youtube.com" in url or "youtu.be" in url:
            cmd = f'yt-dlp -x --audio-format mp3 --cookies {cookies_file_path} "{url}" -o "{name}.mp3"'
            print(f"Running command: {cmd}")
            os.system(cmd)
            if os.path.exists(f'{name}.mp3'):
                print(f"File {name}.mp3 exists, attempting to send...")
                try:
                    await editable.delete()
                    await bot.send_document(chat_id=m.chat.id, document=f'{name}.mp3', caption=f'**🎵 Title : **  {name}.mp3\n\n🔗**Video link** : {url}\n\n🌟** Extracted By** : {CREDIT}')
                    os.remove(f'{name}.mp3')
                except Exception as e:
                    print(f"Error sending document: {str(e)}")
            else:
                print(f"File {name}.mp3 does not exist.")
    except Exception as e:
        await m.reply_text(f"**Failed Reason:**\n<blockquote>{str(e)}</blockquote>")



@bot.on_message(filters.command(["stop"]) )
async def restart_handler(_, m):
    if m.chat.id not in AUTH_USERS:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        await bot.send_message(
            m.chat.id, 
            f"<blockquote>__**Oopss! You are not a Premium member**__\n"
            f"__**PLEASE /upgrade YOUR PLAN**__\n"
            f"__**Send me your user id for authorization**__\n"
            f"__**Your User id** __- `{m.chat.id}`</blockquote>\n\n"
        )
    else:
        await m.reply_text("🚦**STOPPED**🚦", True)
        os.execl(sys.executable, sys.executable, *sys.argv)
        
@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    random_image_url = random.choice(image_urls)
    caption = (
        f"𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n"
        f"➠ 𝐈 𝐚𝐦 𝐚 𝐓𝐞𝐱𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n"
        f"➠ Can Extract Videos & PDFs From Your Text File and Upload to Telegram!\n\n"
        f"➠ For Guide Use Command /help 📖\n\n"
        f"➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 🦁"
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_image_url,
        caption=caption,
        reply_markup=keyboard
    )

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    
    text = (
        f"╭────────────────╮\n"
        f"│✨ **__Your Telegram Info__**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True,
        reply_markup=BUTTONSCONTACT
    )

@bot.on_message(filters.command(["help"]))
async def txt_handler(client: Client, m: Message):
    await bot.send_message(m.chat.id, text= (
        f"💥 𝐁𝐎𝐓𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒\n\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        f"📌 𝗠𝗮𝗶𝗻 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n\n"  
        f"➥ /start – Bot Status Check\n"
        f"➥ /drm – Extract from .txt (Auto)\n"
        f"➥ /y2t – YouTube → .txt Converter\n"  
        f"➥ /ytm – YT .txt → .mp3 downloader\n"  
        f"➥ /yt2m – YT link → .mp3 downloader\n"  
        f"➥ /t2t – Text → .txt Generator\n" 
        f"➥ /stop – Cancel Running Task\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰ \n" 
        f"⚙️ 𝗧𝗼𝗼𝗹𝘀 & 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀: \n\n" 
        f"➥ /cookies – Update YT Cookies\n" 
        f"➥ /id – Get Chat/User ID\n"  
        f"➥ /info – User Details\n"  
        f"➥ /logs – View Bot Activity\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"👤 𝐔𝐬𝐞𝐫 𝐀𝐮𝐭𝐡𝐞𝐧𝐭𝐢𝐜𝐚𝐭𝐢𝐨𝐧: **(OWNER)**\n\n" 
        f"➥ /addauth xxxx – Add User ID\n" 
        f"➥ /remauth xxxx – Remove User ID\n"  
        f"➥ /users – Total User List\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"📁 𝐂𝐡𝐚𝐧𝐧𝐞𝐥𝐬: **(Auth Users)**\n\n" 
        f"➥ /addchnl -100xxxx – Add\n" 
        f"➥ /remchnl -100xxxx – Remove\n"  
        f"➥ /channels – List - (OWNER)\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"💡 𝗡𝗼𝘁𝗲:\n\n"  
        f"• Send any link for auto-extraction\n"  
        f"• Supports batch processing\n\n"  
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
        )
    )                    
          
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):  # Correct parameter name
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs:\n<blockquote>{e}</blockquote>")

@bot.on_message(filters.command(["drm"]) )
async def txt_handler(bot: Client, m: Message):  
    if m.chat.id not in AUTH_USERS and m.chat.id not in CHANNELS_LIST:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        print(f"Channel ID not in CHANNELS_LIST", m.chat.id)
        await m.reply_text(f"<blockquote>__**Oopss! You are not a Premium member** __\n__**PLEASE /upgrade YOUR PLAN**__\n__**Send me your user id for authorization**__\n__**Your User id**__ - `{m.chat.id}`</blockquote>\n")
        return
    editable = await m.reply_text(f"**🔹Hi I am Poweful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.\n\n<blockquote><b>𝗡𝗼𝘁𝗲:\nAll input must be given in 20 sec</b></blockquote>**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await bot.send_document(OWNER, x)
    #await bot.send_document(LOG_CHANNEL, x)
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))  # Extract filename & extension
    path = f"./downloads/{m.chat.id}"
    pdf_count = 0
    img_count = 0
    zip_count = 0
    other_count = 0
    
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        
        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                links.append(i.split("://", 1))
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    other_count += 1
        os.remove(x)
    except:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        os.remove(x)
        return
    
    await editable.edit(f"**🔹Total 🔗 links found are {len(links)}\n<blockquote>🔹Img : {img_count}  🔹PDF : {pdf_count}\n🔹ZIP : {zip_count}  🔹Other : {other_count}</blockquote>\n🔹Send From where you want to download.**")
    try:
        input0: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text = input0.text
        await input0.delete(True)
    except asyncio.TimeoutError:
        raw_text = '1'
    
    if int(raw_text) > len(links) :
        await editable.edit(f"**🔹Enter number in range of Index**")
        processing_request = False  # Reset the processing flag
        await m.reply_text("**🔹Exiting Task......  **")
        return
    
    await editable.edit(f"**🔹Enter Batch Name or send /d for use default**")
    try:
        input1: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text0 = input1.text
        await input1.delete(True)
    except asyncio.TimeoutError:
        raw_text0 = '/d'
    
    if raw_text0 == '/d':
        b_name = file_name.replace('_', ' ')
    else:
        b_name = raw_text0


    await editable.edit(f"**╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋{CREDIT}🦋`]⚡⌋━━➣")
    try:
        input2: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text2 = input2.text
        await input2.delete(True)
    except asyncio.TimeoutError:
        raw_text2 = '480'
    quality = f"{raw_text2}p"
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"

    await editable.edit(f"**🔹Enter Your Name or send /d for use default**")
    try:
        input3: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text3 = input3.text
        await input3.delete(True)
    except asyncio.TimeoutError:
        raw_text3 = '/d'

    if raw_text3 == '/d':
        CR = f"{CREDIT}"
    else:
        CR = raw_text3

    await editable.edit("**🔹Enter __PW/CP/CW__ Working Token For 𝐌𝐏𝐃 𝐔𝐑𝐋 or send /d**")
    try:
        input4: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text4 = input4.text
        await input4.delete(True)
    except asyncio.TimeoutError:
        raw_text4 = '/d'

    if raw_text4 == '/d':
        cwtoken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
        cptoken = "cptoken"
        pwtoken = "pwtoken"
    else:
        cwtoken = raw_text4
        cptoken = raw_text4
        pwtoken = raw_text4
        
    await editable.edit(f"**🔹Send the Video Thumb URL or send /d for use default**")
    try:
        input6: Message = await bot.listen(editable.chat.id, timeout=20)
        raw_text6 = input6.text
        await input6.delete(True)
    except asyncio.TimeoutError:
        raw_text6 = '/d'

    if raw_text6.startswith("http://") or raw_text6.startswith("https://"):
        # If a URL is provided, download thumbnail from the URL
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = raw_text6
    await editable.delete()

    try:
        if raw_text == "1":
            batch_message = await m.reply_text(f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>")
            await bot.pin_chat_message(m.chat.id, batch_message.id)
            message_id = batch_message.id
            pinning_message_id = message_id + 1
            await bot.delete_messages(m.chat.id, pinning_message_id)
    except Exception as e:
        None
    
    failed_count = 0
    count =int(raw_text)    
    arg = int(raw_text)
    try:
        for i in range(arg-1, len(links)):
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = f"https://key-one-gamma.vercel.app/api?url={url}&token={raw_text4}"
                #url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = f"https://scammer-keys.vercel.app/api?url={url}&token={raw_text4}"
                #url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                params = {"url": f"{url}"}
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  
           
            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{raw_text4}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                params = {"url": f"{url}"}
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url   = response.json()['url']

            if "edge.api.brightcove.com" in url:
                bcov = f'bcov_auth={cwtoken}'
                url = url.split("bcov_auth")[0]+bcov
                
            elif "childId" in url and "parentId" in url:
                url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"

            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
             
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🎞️ Title :** `{name1}`\n**├── Extention :**  {CR} .mkv\n**├── Resolution :** [{res}]\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'
                cc1 = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {CR} .pdf\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'
                cczip = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {CR} .zip\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'
                ccimg = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🖼️ Title :** `{name1}`\n**├── Extention :**  {CR} .jpg\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'
                ccm = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🎵 Title :** `{name1}`\n**├── Extention :**  {CR} .mp3\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'
                cchtml = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🌐 Title :** `{name1}`\n**├── Extention :**  {CR} .html\n\n<blockquote><b>📚 Course :</b> {b_name}</blockquote>\n\n**🌟 Extracted By :** {CR}'

                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
  
                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                                    count += 1
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue  # Retry the next attempt if an exception occurs

                        # Delete all failure messages if the PDF is successfully downloaded
                        for msg in failure_msgs:
                            await msg.delete()
                            
                        if not success:
                            # Send the final failure message if all retries fail
                            await m.reply_text(f"Failed to download PDF after {max_retries} attempts.\n⚠️**Downloading Failed**⚠️\n**Name** =>> {str(count).zfill(3)} {name1}\n**Url** =>> {link0}", disable_web_page_preview)
                            
            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            continue        

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.d, photo=f'{name}.{ext}', caption=ccimg)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=ccm)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue    
                    
                elif 'encrypted.m' in url:    
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%</blockquote>\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote><b>⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Eɴᴄʀʏᴘᴛᴇᴅ Sᴛᴀʀᴛᴇᴅ...⏳</b></blockquote>\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » {name}</blockquote>\n┃\n" \
                           f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                           f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                           f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)  
                    count += 1  
                    await asyncio.sleep(1)  
                    continue  

                elif 'drmcdni' in url or 'drm/wv' in url:
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%</blockquote>\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote><b>⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Eɴᴄʀʏᴘᴛᴇᴅ Sᴛᴀʀᴛᴇᴅ...⏳</b></blockquote>\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » {name}</blockquote>\n┃\n" \
                           f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                           f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                           f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
                    continue
     
                else:
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%</blockquote>\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote><b>⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Eɴᴄʀʏᴘᴛᴇᴅ Sᴛᴀʀᴛᴇᴅ...⏳</b></blockquote>\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » {name}</blockquote>\n┃\n" \
                           f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                           f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                           f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)
                
            except Exception as e:
                await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n[Url](url) =>> {link0}\n\n<blockquote><b>Failed Reason:\n{str(e)}</b></blockquote>', disable_web_page_preview=True)
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(e)
        time.sleep(2)

    await m.reply_text(f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
    await m.reply_text(f"⋅ ─ list index ({raw_text}-{len(links)}) out of range ─ ⋅\n\n<blockquote><b>✨BATCH</b> » {b_name}✨</blockquote>\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")

@bot.on_message(filters.text & filters.private)
async def text_handler(bot: Client, m: Message):
    if m.from_user.is_bot:
        return
    links = m.text
    match = re.search(r'https?://\S+', links)
    if match:
        link = match.group(0)
    else:
        await m.reply_text("<blockquote>Invalid link format.</blockquote>")
        return
        
    editable = await m.reply_text(f"<blockquote>**🔹Processing your link...\n🔁Please wait...⏳**</blockquote>")
    await m.delete()

    await editable.edit(f"╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`{CREDIT}`]⚡⌋━━➣ ")
    input2: Message = await bot.listen(editable.chat.id, filters=filters.text & filters.user(m.from_user.id))
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete(True)
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
          
    raw_text4 = "PW_TOKEN"
    thumb = "/d"
    count =0
    arg =1
    try:
            Vxy = link.replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = Vxy

            name1 = links.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                params = {"url": f"{url}"}
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  
           
            elif 'videos.classplusapp' in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{raw_text4}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{raw_text4}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
                params = {"url": f"{url}"}
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url   = response.json()['url']

            elif "childId" in url and "parentId" in url:
                url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                vid_id =  url.split('/')[-2]
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"
                
            if ".pdf*" in url:
                url = f"https://dragoapi.vercel.app/pdf/{url}"
            
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:
                cc = f'🎞️𝐓𝐢𝐭𝐥𝐞 » `{name} [{res}].mp4`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                cc1 = f'📕𝐓𝐢𝐭𝐥𝐞 » `{name}`\n🔗𝐋𝐢𝐧𝐤 » <a href="{link}">__**CLICK HERE**__</a>\n\n🌟𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 » `{CREDIT}`'
                  
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        max_retries = 15  # Define the maximum number of retries
                        retry_delay = 4  # Delay between retries in seconds
                        success = False  # To track whether the download was successful
                        failure_msgs = []  # To keep track of failure messages
                        
                        for attempt in range(max_retries):
                            try:
                                await asyncio.sleep(retry_delay)
                                url = url.replace(" ", "%20")
                                scraper = cloudscraper.create_scraper()
                                response = scraper.get(url)

                                if response.status_code == 200:
                                    with open(f'{name}.pdf', 'wb') as file:
                                        file.write(response.content)
                                    await asyncio.sleep(retry_delay)  # Optional, to prevent spamming
                                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                                    os.remove(f'{name}.pdf')
                                    success = True
                                    break  # Exit the retry loop if successful
                                else:
                                    failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {response.status_code} {response.reason}")
                                    failure_msgs.append(failure_msg)
                                    
                            except Exception as e:
                                failure_msg = await m.reply_text(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                                failure_msgs.append(failure_msg)
                                await asyncio.sleep(retry_delay)
                                continue  # Retry the next attempt if an exception occurs

                        # Delete all failure messages if the PDF is successfully downloaded
                        for msg in failure_msgs:
                            await msg.delete()
                            
                        if not success:
                            # Send the final failure message if all retries fail
                            await m.reply_text(f"Failed to download PDF after {max_retries} attempts.\n⚠️**Downloading Failed**⚠️\n**Name** =>> {str(count).zfill(3)} {name1}\n**Url** =>> {link0}", disable_web_page_preview)
                            
                    else:
                        try:
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            os.system(download_cmd)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            time.sleep(e.x)
                            pass   

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=cc1)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=cc1)
                        count += 1
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        pass
                                
                elif 'encrypted.m' in url:    
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)    
                    await asyncio.sleep(1)  
                    pass

                elif 'drmcdni' in url or 'drm/wv' in url:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    await asyncio.sleep(1)
                    pass
     
                else:
                    Show = f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n" \
                           f"🔗𝐋𝐢𝐧𝐤 » {url}\n" \
                           f"✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}"
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    time.sleep(1)

            except Exception as e:
                    await m.reply_text(f"⚠️𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n🔗𝐋𝐢𝐧𝐤 » `{link}`\n\n__**⚠️Failed Reason »**__\n<blockquote>{str(e)}</blockquote>")
                    pass

    except Exception as e:
        await m.reply_text(str(e))




bot.run()
