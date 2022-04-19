import os
import sys
import nextcord
from nextcord.ext import commands
import requests
import base64
from dotenv import dotenv_values
import json

config = {
    **os.environ,
    **dotenv_values(".env")
}

# test_guilds=[int(config.get("TEST_GUILD"))]

class Printer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.canPrint = True
        self.image_print_state = dict()

    @commands.command(name="toggle_print")
    async def toggle_print(self, ctx: commands.Context):
        if(self.admin_check(ctx.author.id)):
            self.canPrint = not self.canPrint
            await ctx.send(f'printing feature toggled {"on" if self.canPrint else "off"}')
        else: 
            await ctx.send("Sorry but you are not authorized to use this command")
    
    def admin_check(self, authorId: int):
        return any(authorId == id for id in json.loads(config.get("ADMIN_ID")))

    # @nextcord.slash_command(name="check_status", description="Please don't use this function")
    # async def check(self, inter:nextcord.Interaction):
    #     if(self.canPrint):
    #         isReady = self.isReady()
    #         await inter.response.send_message(f'i am {"ready" if isReady else "not ready"}')
    #     else:
    #         await self.send_not_available(inter) 

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error

    @nextcord.slash_command(name="print_image", description="print an image")
    async def print_image(self, inter:nextcord.Interaction, image: nextcord.Attachment = nextcord.SlashOption(name="image", description="image to print", required=True)):
        if(self.canPrint):
            if(image.content_type.startswith("image/")):
                await inter.send("Image received. Start printing")
                responseimage = requests.get(image.url)
                if(responseimage.status_code == 200):
                    if(self.canPrint):
                        encodedImage = base64.b64encode(s=responseimage.content).decode("utf-8")
                        await self.printer_print(inter= inter, text=encodedImage, type="image")
                    else: 
                        await inter.edit_original_message("Sorry the printing service is not available. Please try again later")
                else:
                    inter.edit_original_message("Something went wrong receiving your image. Please try again")
            else:
                await inter.send("That's not an image. Please send an image")
        else: 
            await self.send_not_available(inter)

    @nextcord.slash_command(name="print_message",  description="Print a text message", )
    async def print_message(self, inter: nextcord.Interaction, message: str = nextcord.SlashOption(name="message", description="text to print")): 
        if(self.canPrint):
            # if(self.isReady()):
                await inter.send(f"printing")
                await self.printer_print(inter=inter, text=message, type="text")
            # else: 
            #     await inter.response.send_message("printer currently not ready")
        else: 
            await self.send_not_available(inter=inter)

    async def printer_print(self, inter:nextcord.Interaction, text:str, type: str):
        body = {
        "author":f"{inter.user.display_name}",
        "origin": inter.channel.name if not isinstance(inter.channel, nextcord.channel.PartialMessageable) else "",
        "content": [
                {
                    "data": text,
                    "type": type
                }
            ]
        }
        printResponse = requests.post(f"{config.get('API_URL')}/print_zettel", json=body)
        if(printResponse.status_code == 200):
            await inter.edit_original_message(content="Printed sucessfully")
        else: 
            print(printResponse.content)
            await inter.edit_original_message(content='Something went wrong')

    async def send_not_available(self, inter: nextcord.Interaction):
        await inter.send("Sorry this feature is currently not available. Please try again later")

    def isReady(self):
        response = requests.get(f"{config.get('API_URL')}/ready")
        if(response.status_code == 200):
            return response.json()["ready"]
        else: 
            return False


bot = commands.Bot(command_prefix="/")
bot.add_cog(Printer(bot))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

@bot.event
async def on_ready():
    print("starting")


bot.run(config.get("DISCORD_TOKEN"))
