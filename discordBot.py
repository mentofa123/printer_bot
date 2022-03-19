import os
import sys
import nextcord
from nextcord.ext import commands
import requests
import base64
from dotenv import load_dotenv
from typing import Union

load_dotenv()

test_guilds=[int(os.getenv("TEST_GUILD"))]

class Printer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.canPrint = True

    @commands.command(name="toggle_print")
    async def toggle_print(self, ctx: commands.Context):
        self.canPrint = not self.canPrint
        await ctx.message.delete()
        await ctx.send(f'printing feature toggled {"on" if self.canPrint else "off"}')
    
    @nextcord.slash_command(guild_ids=test_guilds, name="check_status", description="Please don't use this function")
    async def check(self, inter:nextcord.Interaction):
        if(self.canPrint):
            isReady = self.isReady()
            await inter.response.send_message(f'i am {"ready" if isReady else "not ready"}')
        else:
            await self.send_not_available(inter) 

    @nextcord.slash_command(name="print_image", guild_ids=test_guilds, description="print an image")
    async def print_image(self, inter:nextcord.Interaction, deleteimage: bool = nextcord.SlashOption(name="deleteimage", description="delete Image after printing", required=False, default=False)):
        if(self.canPrint):
            await inter.send("please send an image or type 'abort' to abort this process")
            await inter.followup.fetch_message(inter.channel.last_message_id)
            message: nextcord.Message = await self.bot.wait_for("message", check=self.check_for_image(inter.user, inter.channel.id))
            if(message.content.lower() == "abort"):
                await inter.edit_original_message(content="aborted image printing")
                if(deleteimage):
                    await message.delete() 
            else:
                await inter.edit_original_message(content="image received. Start printing")
                response = requests.get(message.attachments[0].url if len(message.attachments) == 1 else message.stickers[0].url)
                if(response.status_code == 200):
                    if(self.canPrint):
                        encodedImage = base64.b64encode(s=response.content).decode("utf-8")
                        await self.printer_print(inter=inter, text=encodedImage, type="image")
                        if(deleteimage):
                            await message.delete()
                    else:
                        await inter.edit_original_message(content="sorry the printing service is not available")
                else: 
                   await inter.edit_original_message(content="Oh something went wrong while receiving the image please try again")
        else: 
            await self.send_not_available(inter)

    def check_for_image(self, author: Union[nextcord.User, nextcord.Member,  None] , channelId: int):
        def inner_check(message: nextcord.Message):
            if(message.author.id == author.id and message.channel.id == channelId):
                if(message.content.lower() == "abort"):
                    return True
                elif (len(message.attachments) == 1 and message.attachments[0].content_type.startswith("image/")):
                    return True
                elif(len(message.stickers) == 1):
                    return True
                else:
                    return False
            else: 
                return False
        return inner_check

    @nextcord.slash_command(name="print_message", guild_ids=test_guilds, description="Print a text message", )
    async def print_text(self, inter: nextcord.Interaction, text: str = nextcord.SlashOption(name="text", description="text to print")): 
        if(self.canPrint):
            # if(self.isReady()):
                await inter.send("printing")
                await self.printer_print(inter=inter, text=text, type="text")
            # else: 
            #     await inter.response.send_message("printer currently not ready")
        else: 
            await self.send_not_available(inter=inter)

    async def printer_print(self, inter:nextcord.Interaction, text:str, type: str):
        body = {
        "author":f"{inter.user.display_name}",
        "origin": inter.channel.name,
        "content": [
                {
                    "data": text,
                    "type": type
                }
            ]
        }
        printResponse = requests.post(f"{os.getenv('API_URL')}/print_zettel", json=body)
        if(printResponse.status_code == 200):
            await inter.edit_original_message(content="Printed sucessfully")
        else: 
            print(printResponse.content)
            await inter.edit_original_message(content='Something went wrong')

    async def send_not_available(self, inter: nextcord.Interaction):
        await inter.send("Sorry this feature is currently not available")

    def isReady(self):
        response = requests.get(f"{os.getenv('API_URL')}/ready")
        if(response.status_code == 200):
            return response.json()["ready"]
        else: 
            return False


bot = commands.Bot(command_prefix="/")
bot.add_cog(Printer(bot))

@bot.event
async def on_ready():
    print("starting")

@bot.event 
async def on_error(event, arg):
    #TODO send message to myself when an error pops up
    print(sys.exc_info())

bot.run(os.getenv("DISCORD_TOKEN"))
