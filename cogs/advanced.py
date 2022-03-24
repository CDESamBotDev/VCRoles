import json
import os

import discord
import requests
from discord.commands import Option, slash_command
from discord.ext import commands

from bot import MyClient
from utils import Permissions


class Advanced(commands.Cog):
    def __init__(self, client: MyClient):
        self.client = client

    async def parse_initial(
        self,
        ctx: discord.ApplicationContext,
        data: dict[str, dict],
        guild: discord.Guild,
    ):
        # data = {
        #     "all": {"roles": ["!787740836364025887"], "suffix": "Test", "reverse_roles": ["!932022185315409942"]},
        #     "category": {"758392649979265025": {"roles": ["932022185315409942"], "!suffix": ""}, "!758392649979265026": {}},
        #     "stage": {"944261529908436992": {"suffix": "Test"}},
        #     "permanent": {},
        #     "!voice": {}
        # }
        for key, value in data.items():
            print(f"{key=}, {value=}")
            if key.startswith("!"):
                # Unlink all
                self.client.redis.r.hdel(
                    f"{guild.id}:linked", f"{key.removeprefix('!')}"
                )
            elif key in ["category", "stage", "permanent", "voice"]:
                # Check data
                await self.parse_channels(ctx, value, key, guild)
            elif key == "all":
                # Check data
                await self.parse_links(ctx, value, key, guild)

    async def parse_channels(
        self,
        ctx: discord.ApplicationContext,
        data: dict,
        key: str,
        guild: discord.Guild,
    ):
        for channel, links in data.items():
            print(f"{channel=}, {links=}")
            if channel.startswith("!"):
                # Unlink channel
                linked_data = self.client.redis.get_linked(key, guild.id)
                try:
                    linked_data.pop(channel.removeprefix("!"))
                except:
                    pass
                self.client.redis.update_linked(key, guild.id, linked_data)
            else:
                try:
                    int(channel)
                    # channel is id
                except:
                    # channel is name
                    # so make new

                    try:
                        if key == "category":
                            ch = await guild.create_category_channel(
                                name=channel, reason="Auto-created by advanced link"
                            )
                        elif key == "stage":
                            ch = await guild.create_stage_channel(
                                name=channel, reason="Auto-created by advanced link"
                            )
                        elif key == "permanent" or key == "voice":
                            ch = await guild.create_voice_channel(
                                name=channel, reason="Auto-created by advanced link"
                            )
                        channel = str(ch.id)
                    except:
                        continue
                # Check data
                linked_data = self.client.redis.get_linked(key, guild.id)
                if channel not in linked_data:
                    linked_data[channel] = {
                        "roles": [],
                        "suffix": "",
                        "reverse_roles": [],
                    }
                self.client.redis.update_linked(key, guild.id, linked_data)

                await self.parse_links(ctx, links, key, guild, channel)

    async def parse_links(
        self,
        ctx: discord.ApplicationContext,
        data: dict,
        key: str,
        guild: discord.Guild,
        channel_id: str = None,
    ):
        def get_data_to_edit(linked_data: dict, channel_id: str):
            if channel_id:
                return linked_data[channel_id]
            else:
                return linked_data

        def combine_edit_data(
            linked_data: dict, linked_data_edit: dict, channel_id: str
        ):
            if channel_id:
                linked_data[channel_id] = linked_data_edit
            else:
                linked_data = linked_data_edit
            return linked_data

        # Check data
        # data = {"roles": ["!787740836364025887"], "suffix": "Test", "reverse_roles": ["!932022185315409942"]}
        for linktype, value in data.items():
            print(f"{linktype=}, {value=}")
            if linktype.startswith("!") and linktype.endswith(
                ("roles", "reverse_roles", "suffix")
            ):
                # Unlink all in linktype
                linked_data = self.client.redis.get_linked(key, guild.id)
                linked_data_edit = get_data_to_edit(linked_data, channel_id)

                if linktype.endswith(("roles", "reverse_roles")):
                    linked_data_edit[linktype] = []
                else:
                    linked_data_edit[linktype] = ""

                linked_data = combine_edit_data(
                    linked_data, linked_data_edit, channel_id
                )
                self.client.redis.update_linked(key, guild.id, linked_data)
            elif linktype in ["roles", "reverse_roles", "suffix"]:
                linked_data = self.client.redis.get_linked(key, guild.id)
                linked_data_edit = get_data_to_edit(linked_data, channel_id)

                if linktype == "roles" or linktype == "reverse_roles":
                    for role in value:
                        print(f"{role=}")
                        if role.startswith("!"):
                            # Unlink role
                            try:
                                linked_data_edit[linktype].remove(
                                    role.removeprefix("!")
                                )
                            except:
                                pass
                        else:
                            # Link role
                            try:
                                # role is id
                                int(role)
                            except:
                                # role is name
                                # so get id/make new
                                done = False
                                for r in guild.roles:
                                    if r.name == role:
                                        role = str(r.id)
                                        done = True
                                # make new channel
                                if not done:
                                    r = await guild.create_role(
                                        name=role,
                                        reason="Auto-created by advanced link",
                                    )
                                    role = str(r.id)

                            linked_data_edit[linktype].append(role)
                            print(f"{linked_data_edit=}")
                elif linktype == "suffix":
                    linked_data_edit[linktype] = value
                linked_data = combine_edit_data(
                    linked_data, linked_data_edit, channel_id
                )
                self.client.redis.update_linked(key, guild.id, linked_data)

    @slash_command(guild_ids=[758392649979265024])
    @Permissions.has_permissions(administrator=True)
    async def advanced(
        self,
        ctx: discord.ApplicationContext,
        attachment: Option(
            discord.Attachment, "Select a valid link file", required=True
        ),
    ):
        """
        Command for advanced users. Allows you to add/remove/edit a large number of links at once.
        """  ### Needs to be able to parse json successfully to extract data to be added/edited/removed
        await ctx.defer()
        if not ctx.guild:
            return await ctx.respond("This command can only be used in a server.")
        if not attachment.content_type.startswith("application/json"):
            return await ctx.respond("Incorrect JSON format")

        try:
            # data = requests.request("GET", attachment.url).json()
            data = requests.get(attachment.url).json()
        except json.decoder.JSONDecodeError:
            return await ctx.respond("Incorrect JSON format")
        except requests.JSONDecodeError:
            return await ctx.respond("Incorrect JSON format")
        except:
            return await ctx.respond("Unknown error")

        if not isinstance(data, dict):
            return await ctx.respond("Incorrect JSON format")

        guild = await self.client.fetch_guild(ctx.guild.id)

        await self.parse_initial(ctx, data, guild)

        await ctx.respond("Done")

    @slash_command(guild_ids=[758392649979265024])
    @Permissions.has_permissions(administrator=True)
    async def export(self, ctx: discord.ApplicationContext):
        """
        Command for advanced users. Allows you to export all links to a file.
        """
        await ctx.defer()
        if not ctx.guild:
            return await ctx.respond("This command can only be used in a server.")

        guild = await self.client.fetch_guild(ctx.guild.id)

        data = {}
        for type in ["all", "category", "permanent", "stage", "voice"]:
            data[type] = self.client.redis.get_linked(type, guild.id)

        with open(f"{ctx.guild.id}.json", "w") as f:
            json.dump(data, f, indent=4)

        with open(f"{ctx.guild.id}.json", "rb") as f:
            await ctx.respond(
                "Here is the exported data.", file=discord.File(f, "data.json")
            )

        os.remove(f"{ctx.guild.id}.json")


def setup(client: MyClient):
    client.add_cog(Advanced(client))
