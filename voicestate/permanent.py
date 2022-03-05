import discord

from utils import add_suffix


class Permanent:
    async def join(
        self,
        data,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> list:
        if str(after.channel.id) in data:
            await add_suffix(member, data[str(after.channel.id)]["suffix"])
            roles = []
            for i in data[str(after.channel.id)]["roles"]:
                try:
                    role = member.guild.get_role(int(i))
                    await member.add_roles(role)
                    roles.append(role)
                except:
                    pass
            return roles
        return None
