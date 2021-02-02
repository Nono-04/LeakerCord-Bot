import json
import traceback
import requests
import aiofiles
import aiohttp
import discord
from discord.ext import commands, tasks

res = requests.get('https://api.nitestats.com/v1/epic/bearer')
json = res.json()
token = json['accessToken']


class ini(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.check.start()
        except Exception as ex:
            print(ex)
            self.check.stop()
            self.check.start()

    @tasks.loop(seconds=150)
    async def check(self):
        await self.client.wait_until_ready()
        async with aiohttp.ClientSession() as cs:
            parameter = {"Authorization": f"bearer 046856a662684c6991aacd64d73b168e"} #change token value to {token} if you dont want to update it every couple of hours
            async with cs.get(
                    'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/cloudstorage/system', headers=parameter) as data:
                if data.status != 200:
                    return
                new = await data.json()
        for i in new:
            async with aiohttp.ClientSession() as cs:
                parameter = {"Authorization": f"bearer 046856a662684c6991aacd64d73b168e"} #change token value to {token} if you dont want to update it every couple of hours
                async with cs.get(
                        f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/cloudstorage/system/{i["uniqueFilename"]}', headers=parameter) as data:
                    if data.status != 200:
                        continue
                    try:
                        oldd = await (
                            await aiofiles.open(f"Cache/ini/{i['filename']}", mode='r', encoding="utf8")).read()
                    except:
                        oldd = ""
                    text = str(await data.text())
                    templist = []
                    changes = ""
                    for oldline in oldd.splitlines():
                        if oldline not in text.splitlines():
                            if oldline == "":
                                continue
                            changes += f"- {oldline}\n"

                    for line in text.splitlines():
                        if line in oldd.splitlines():
                            continue
                        else:
                            changes += f"+ {line}\n"
                    templist.append(changes)
                    for i2 in templist:
                        if i2 == "":
                            continue
                        if len(i2) > 1500:
                            async with aiofiles.open("Cache/temp.txt", mode="w", encoding="utf8") as file:
                                await file.write(str(i2))
                            file = discord.File("Cache/temp.txt")
                            await self.client.get_channel(743191744161775758).send( #changed channel id to the leaker cord ini updates channel
                                f"{role} Detected Changes in **{i['filename']}**", file=file)
                        else:
                            await self.client.get_channel(743191744161775758).send( #changed channel id to the leaker cord ini updates channel
                                f"Detected changes in **{i['filename']}**\n```diff\n{i2}\n```")
                    async with aiofiles.open(f"Cache/ini/{i['filename']}", mode="w", encoding="utf8") as file:
                        await file.write(text)
        print("Fertig")

    def cog_unload(self):
        self.check.stop()
        try:
            self.client.unload_extension("cogs.ini")
        except:
            pass
        try:
            self.client.load_extension("cogs.ini")
        except:
            pass


def setup(client):
    client.add_cog(ini(client))
