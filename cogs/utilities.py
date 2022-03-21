import discord
from discord import ApplicationContext
from discord.commands import Option, slash_command
from discord.ext import commands

from bot import MyClient
from views.url import Discord, Invite, TopGG, Website, Combination


class Utils(commands.Cog):
    def __init__(self, client: MyClient):
        self.client = client

    @slash_command(description="Use to mention a channel in chat")
    async def mention(
        self,
        ctx,
        channel: Option(
            (discord.VoiceChannel, discord.StageChannel), "select a channel"
        ),
    ):
        await ctx.respond(f"{channel.mention}")

    @slash_command(description="Gets an invite to the support server")
    async def discord(self, ctx: discord.ApplicationContext):
        await ctx.respond(
            content="To join our support server, click the link below", view=Discord()
        )

    @slash_command(description="Gets an invite for the bot")
    async def invite(self, ctx):
        await ctx.respond(
            content="To invite the bot, use the link below",
            view=Invite(),
        )

    @slash_command(description="Gets a link to the bot's Top.gg page")
    async def topgg(self, ctx):
        await ctx.respond(
            content="To visit the bot's Top.gg, click the link below", view=TopGG()
        )

    @slash_command(description="Gets info about the bot")
    async def about(self, ctx: ApplicationContext):
        embed = discord.Embed(title="About:", colour=discord.Colour.blue())

        embed.add_field(
            name="Server Count",
            value=f"{self.client.user.name} is in {len(self.client.guilds)} servers",
            inline=False,
        )
        try:
            embed.add_field(
                name="Shard Info",
                value=f"Shard {ctx.guild.shard_id}/{len(self.client.shards)}",
            )
        except:
            pass

        embed.add_field(
            name="Authors",
            value=f"cde#4572 [CDE90](https://github.com/CDE90) and SamHartland#9376 [DrWackyBob](https://github.com/DrWackyBob)",
            inline=False,
        )
        embed.set_author(
            name=f"{self.client.user}", icon_url=self.client.user.avatar.url
        )

        await ctx.respond(embed=embed, view=Combination())

    @slash_command(description="Help Command")
    async def help(self, ctx):
        embed = discord.Embed(
            title="VC Roles Help",
            description="We have moved our help page to https://www.vcroles.com where you can find a list of the bot's commands, how to use them, a basic setup guide and more!",
            colour=discord.Colour.light_grey(),
        )
        await ctx.respond(embed=embed, view=Website())


def setup(client: MyClient):
    client.add_cog(Utils(client))
