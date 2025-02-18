import threading
import server
import discord
from discord.ext import commands
from google import genai
from google.genai import types
import PIL.Image
import io
import json
import os
import requests
# Load environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Google GenAI Client
client = genai.Client(api_key=f"{GEMINI_API_KEY}")

# Discord Bot Setup
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def analyze_id(image_bytes):
    """Analyze ID from image using Google Gemini API."""
    image = PIL.Image.open(io.BytesIO(image_bytes))
    #image = requests.get(image_url)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            """
            Extract the following details from the provided image of an identification document:
            Also make sure there are no inaccuracies
            - First Name (including middle name)
            - Last Name
            - Gender        
            - Date of Birth (format: YYYY-MM-DD)
            - Age (current year is 2025)
            - Address (must be full, **if not present, use a random address from the place of birth(with postcode)**)
            - Country code (must be two letters) for the issuing country of the document
            - ID Type (type of identification document)
            - ID Number (must meet the length according to the ID type)
        
            Provide the response in JSON format with keys:
            "first_name", "last_name", "gender", "date_of_birth", "age", "address", "country_code", "id_type", "id_number".

            Return JSON only without additional explanations.
            """,
            #types.Part.from_bytes(data=image.content, mime_type="image/jpeg")
            image
        ]
    )
    print(response.text)
    return response.text

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name='idinfo')
async def id_info(ctx):
    """Get ID info from the replied image."""
    if ctx.message.reference:
        replied_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        if replied_message.attachments:
           # if replied_message.attachments:
            attachment = replied_message.attachments[0]
            image_bytes = await attachment.read()

          #  await ctx.send("🔍 Processing image, please wait...")
        #else:
            #print("No image found in the replied message.")
            #attachment = replied_message.attachments[0]
            #image_bytes = await attachment.read()

            await ctx.send("🔍 Processing image, please wait...")
            try:
                result = await analyze_id(image_bytes)
                #json_result = json.loads(result)
                #formatted_result = json.dumps(json_result, indent=4)
                await ctx.send(f"🆔 **ID Information Extracted:**\n{result}")
            except Exception as e:
                await ctx.send(f"❌ Error extracting information: {e}")
        else:
            await ctx.send("⚠️ No image found in the replied message.")
    else:
        await ctx.send("⚠️ Please reply to a message containing an image using `!idinfo`.")

threading.Thread(target=server.app.run, kwargs={"host": "0.0.0.0", "port": 10000}).start()

bot.run(DISCORD_TOKEN)
