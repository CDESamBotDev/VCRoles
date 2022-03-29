import discord
from discord.commands import Option, SlashCommandGroup, slash_command
from discord.ext import commands

from bot import MyClient
from utils import Permissions, handle_data_deletion


class Linking(commands.Cog):
    def __init__(self, client: MyClient):
        self.client = client

    suffix_commands = SlashCommandGroup(
        "suffix", "Suffix to add to the end of usernames"
    )
    reverse_commands = SlashCommandGroup("reverse", "Reverse roles")

    @slash_command(description="Use to link channels with roles")
    @Permissions.has_permissions(administrator=True)
    async def link(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
        role: Option(discord.Role, "Select a role to link"),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            data[str(channel.id)] = {"roles": [], "suffix": "", "reverse_roles": []}

        if str(role.id) not in data[str(channel.id)]["roles"]:
            data[str(channel.id)]["roles"].append(str(role.id))

            self.client.redis.update_linked(channel_type, ctx.guild.id, data)

            await ctx.respond(f"Linked {channel.mention} with role: `@{role.name}`")

            member = ctx.guild.get_member(self.client.user.id)
            if member.top_role.position < role.position:
                await ctx.send(f"Please ensure my highest role is above `@{role.name}`")
        else:
            await ctx.respond(f"The channel and role are already linked.")

        return self.client.incr_counter("link")

    @slash_command(description="Use to unlink a channel from a role")
    @Permissions.has_permissions(administrator=True)
    async def unlink(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
        role: Option(discord.Role, "Select a role to link"),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            return await ctx.respond(f"The channel and role are not linked.")

        if str(role.id) in data[str(channel.id)]["roles"]:
            try:
                data[str(channel.id)]["roles"].remove(str(role.id))

                data = handle_data_deletion(data, str(channel.id))

                self.client.redis.update_linked(channel_type, ctx.guild.id, data)

                await ctx.respond(
                    f"Unlinked {channel.mention} and role: `@{role.name}`"
                )
            except:
                return await ctx.respond(
                    f"There was an error unlinking the channel and role."
                )

        else:
            await ctx.respond(f"The channel and role are not linked.")

        return self.client.incr_counter("unlink")

    @suffix_commands.command(description="Use to set a suffix for a channel")
    @Permissions.has_permissions(administrator=True)
    async def add(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
        suffix: Option(str, "Add a suffix to the end of usernames"),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            data[str(channel.id)] = {"roles": [], "suffix": "", "reverse_roles": []}

        data[str(channel.id)]["suffix"] = suffix

        self.client.redis.update_linked(channel_type, ctx.guild.id, data)

        await ctx.respond(f"Set the suffix for {channel.mention} to `{suffix}`")

        return self.client.incr_counter("add_suffix")

    @suffix_commands.command(description="Use to remove a suffix for a channel")
    @Permissions.has_permissions(administrator=True)
    async def remove(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            return await ctx.respond(f"The channel has no associated rules.")

        data[str(channel.id)]["suffix"] = ""

        data = handle_data_deletion(data, str(channel.id))

        self.client.redis.update_linked(channel_type, ctx.guild.id, data)

        await ctx.respond(f"Removed the suffix for {channel.mention}")

        return self.client.incr_counter("remove_suffix")

    @reverse_commands.command(description="Use to add a reverse role link", name="link")
    @Permissions.has_permissions(administrator=True)
    async def reverse_link(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
        role: Option(discord.Role, "Select a role to link"),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            data[str(channel.id)] = {"roles": [], "suffix": "", "reverse_roles": []}

        if str(role.id) not in data[str(channel.id)]["reverse_roles"]:
            data[str(channel.id)]["reverse_roles"].append(str(role.id))

            self.client.redis.update_linked(channel_type, ctx.guild.id, data)

            await ctx.respond(f"Linked {channel.mention} with role: `@{role.name}`")

            member = ctx.guild.get_member(self.client.user.id)
            if member.top_role.position < role.position:
                await ctx.send(f"Please ensure my highest role is above `@{role.name}`")
        else:
            await ctx.respond(f"The channel and role are already linked.")

        return self.client.incr_counter("reverse_link")

    @reverse_commands.command(
        description="Use to remove a reverse role link", name="unlink"
    )
    @Permissions.has_permissions(administrator=True)
    async def reverse_unlink(
        self,
        ctx: discord.ApplicationContext,
        channel: Option(
            (discord.CategoryChannel, discord.VoiceChannel, discord.StageChannel),
            "Select a channel to link",
        ),
        role: Option(discord.Role, "Select a role to link"),
    ):

        if isinstance(channel, discord.CategoryChannel):
            channel_type = "category"
        elif isinstance(channel, discord.VoiceChannel):
            channel_type = "voice"
        elif isinstance(channel, discord.StageChannel):
            channel_type = "stage"

        data = self.client.redis.get_linked(channel_type, ctx.guild.id)

        try:
            data[str(channel.id)]
        except:
            return await ctx.respond(f"The channel has no associated rules.")

        if str(role.id) in data[str(channel.id)]["reverse_roles"]:
            try:
                data[str(channel.id)]["reverse_roles"].remove(str(role.id))

                data = handle_data_deletion(data, str(channel.id))

                self.client.redis.update_linked(channel_type, ctx.guild.id, data)

                await ctx.respond(
                    f"Unlinked {channel.mention} and role: `@{role.name}`"
                )
            except:
                return await ctx.respond(
                    f"There was an error unlinking the channel and role."
                )

        else:
            await ctx.respond(f"The channel and role are not linked.")

        return self.client.incr_counter("reverse_unlink")


def setup(client: MyClient):
    client.add_cog(Linking(client))
