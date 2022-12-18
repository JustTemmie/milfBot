import discord
from discord.ext import commands, tasks
from discord.errors import Forbidden
from discord.ext.commands import (
    CommandNotFound,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
)
import random

import requests
import re

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

import string

class events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, err, *args, **kwargs):
        await self.bot.get_channel(984577196616216616).send(f"{err}")
        
        if err == "on_command_error":
            await args[0].send("Sorry, something unexpected went wrong.")
            # raise
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            # await ctx.send("Sorry, I couldn't find that command")
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(
                f"One or more of the required arguments are missing, perhaps the help command could help you out? `{ctx.prefix}help {ctx.command}`"
            )

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(
                f"That command is on cooldown. Please try again in {exc.retry_after:,.2f} seconds.",
                delete_after=(exc.retry_after*1.05 + 0.7),
            )

        #      elif isinstance(exc.original, HTTPException):
        #          await ctx.send("Unable to send message.")

        elif hasattr(exc, "original"):
            # raise exc  # .original

            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have the permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot:
            return
        
        if "🥺" in ctx.content:
            linkIndex = 0
            urlChars = ["h", "t", "t", "p", " "]
            for char in ctx.content.lower():
                if linkIndex == 4 and char != ' ':
                    pass

                elif linkIndex <= 4 and char == urlChars[linkIndex]:
                    linkIndex += 1
                    if linkIndex == 5:
                        linkIndex = 0

                elif char in string.ascii_lowercase:
                    return
                
            if random.randint(0, 80) != 2:
                await ctx.reply("What the fuck is 🥺 use your words I don't speak bottom")
                return
            
            await ctx.reply(file=discord.File("bottom.png"))

    @commands.command(name="milf", description="sends a milf")
    async def milfCommand(self, ctx):
        if not ctx.channel.is_nsfw():
            return await ctx.reply("please use this command in a NSFW channel")
        
        await self.send_reddit(ctx.channel.id, "milf", True, 50)
    
    @commands.command(
        name="r",
        aliases=["red", "r/", "rslash", "reddit"],
        brief="sends something from the subreddit, if you don't specify one it will pick one from an internal list",
    )
    async def reddit_search(self, ctx, search=None):
        if not ctx.channel.is_nsfw():
            return await ctx.reply("please use this command in a NSFW channel")
        
        await ctx.channel.typing()
        if search == None:
            search = random.choice([
                "milf",
                "milfs",
                "rule34",
                "collegesluts",
                "collegeamateurs",
                "maturemilf",
                "nsfw_snapchat",
                "cellshots",
                "selfpix",
                "girlswithiphones",
                "freshfromtheshower",
                "xposing",
                "girlswithglasses",
                "seethru",
                "barelyclothed",
                "bottomless",
                "nopanties",
                "tightdresses",
                "asianhotties",
                "juicyasians",
                "nsfw_japan",
                "gonewild",
                "gonewildcurvy",
                "altgonewild",
                "publicflashing",
                "RealPublicNudity",
                "pegging",
            ])
        await self.send_reddit(ctx.channel.id, search, True, 50)
    
    async def send_reddit(self, channel, subreddit, imageRequired=False, limit=25):
        if self.bot.is_ready():
            try:
                req = requests.get(
                    f"http://reddit.com/r/{subreddit}/hot.json?limit={limit}",
                    headers={"User-agent": "Chrome"},
                )
                json = req.json()
                if "error" in json or json["data"]["after"] is None:
                    await self.bot.get_channel(channel).send(f"an error occured, no r/{subreddit} for now :(")
                    return

                req_len = len(json["data"]["children"])
                
                if imageRequired:
                    offset = random.randint(0, req_len)
                    for i in range(req_len):
                        i += offset
                        if i > req_len:
                            i -= req_len
                        
                        print(i)
                        post = json["data"]["children"][i]
                        url = post["data"]["url"] # can be image or post link
                        if re.match(r".*\.(jpg|png|gif)$", url):
                            break
                
                else:
                    rand = random.randrange(0, req_len)
                    post = json["data"]["children"][rand]
                    url = post["data"]["url"] # can be image or post link
                    
                              
                title = post["data"]["title"]
                author = "u/" + post["data"]["author"]
                subreddit = post["data"]["subreddit_name_prefixed"]
                link = "https://reddit.com" + post["data"]["permalink"]
                if "selftext" in post["data"]:
                    text = post["data"]["selftext"]  # may not exist
                    if len(text) >= 2000:
                        text = text[:2000].rsplit(" ", 1)[0] + " **-Snippet-**"
                    embed = discord.Embed(title=title, description=text, url=link)
                else:
                    embed = discord.Embed(title=title, url=link)
                
                if re.match(r".*\.(jpg|png|gif)$", url):
                    embed.set_image(url=url)

                embed.set_footer(text=f"By {author} in {subreddit}")
                
                await self.bot.get_channel(channel).send(embed=embed)
            
            except Exception as e:
                print(f"error in send_reddit: {e}")

async def setup(bot):
    await bot.add_cog(events(bot))
