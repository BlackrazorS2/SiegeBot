# Script creates and assigns channels and roles for rainbow 6 siege tournaments


import json
import os
import discord
from discord.ext import commands
from discord.utils import get
import asyncio


with open("token.json", "r") as foo:
    TOKEN = json.load(foo)
intents = discord.Intents.default()
intents.members = True
intents.dm_messages = True
client = commands.Bot(command_prefix='!', intents=intents) # command prefix is !
client.remove_command('help') # removes the default help command to replace it with a custom one
guildie = ""

@client.event
async def on_ready(): # as the bot boots up
    await client.change_presence(activity=discord.Game(name='!help for help!')) # status message is set to show the help command
    print('ready boss!') # prints a message to the terminal indicating that the bot is booted up

if not os.path.exists("Guilds.json"):
    with open("Guilds.json", "w") as f:
        data = {} # should be a dictionary of {GuildID: [[teamName, roleID, password],[teamName2, roleID, password]]}
        json.dump(data,f)
with open("Guilds.json", "r") as f:
    data = json.load(f)

def reload():
    with open("Guilds.json", "r") as f:
        info = json.load(f)
    return info
def checkGuild(guild):
    """Checks if the command was sent from a new guild or not, if not, make a new entry to the Guild file"""
    if guild in data.keys():
        pass
    else:
        data[guild] = []

async def createChannel(teamName):
    """When called, makes text and voice channels with the given team name"""
    data = reload()
    server = client.get_guild(int(guildie))
    #server = client.get_guild(discGuild)
    for cat in server.categories:
        if cat.name == "Teams":
            category = cat
            break
        else:
            category = None
    if category == None: 
        print("No team Category found, making one")
        category = await server.create_category("Teams")
        print("done\n")
    else:
        print("Category Teams already exists, no need to make a new one\n")
    ############^ this works
    ############v this sometimes does not
    # permissions for channels
    textOverwrites = {
        server.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False)
    }
    voiceOverwrites = {
        server.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)
    }
    print("Default permissions defined")
    role = get(server.roles, name=teamName)
    print("getting the role did not throw and error")
    # creating text
    creation = True #checks if we make the channel or not
    print("Looping through channels in the team category")
    for channel in category.channels:
        print(f"Am I making new channels? {creation}")
        if channel.name.lower() == teamName.lower():
            creation = False
        else:
            continue
    if creation:
        print("Making channels")
        textOverwrites[role] = discord.PermissionOverwrite(read_messages=True, view_channel=True, read_message_history=True, send_messages=True)
        print("Text channel permissions configured")
        await server.create_text_channel(teamName, overwrites=textOverwrites, category=category)
        print("Text channel made\n")
        voiceOverwrites[role] = discord.PermissionOverwrite(connect=True)
        print("Voice channel permissions configured")
        await server.create_voice_channel(teamName, overwrites=voiceOverwrites, category=category)
        print("Voice channel created")
        textOverwrites.pop(role, None)
        voiceOverwrites.pop(role, None)
    else:
        pass




@client.command()
async def makeTeam(ctx, teamName, password):
    """Makes a team"""
    data = reload()
    #server = client.get_guild(ctx.message.guild.id)
    server = client.get_guild(int(guildie))
    member = server.get_member(ctx.message.author.id)
    sender = ctx.message.author
    checkGuild(guildie)
    channel = str(ctx.message.channel) # Identifies where the command was sent from (a channel, a DM, etc)
    if channel == (f"Direct Message with {sender}"):  # if the command was sent from a DM:
        roleExist = get(server.roles, name=teamName)
        if roleExist:
            if roleExist in member.roles:
                await ctx.send("You already made this team and have the role!")
                return None
            else:
                await ctx.send("This team has already been created!")
                return None
        else:
            role = await server.create_role(name=teamName, hoist=True)
            print(f"Role {teamName} has been created")
            role.position = 3
            await member.add_roles(role)
            print(f"Role {teamName} has been added to {sender}\n")
            await ctx.send(f"Team {teamName} created with password {password}! DM a moderator to change the team color")

        data[guildie].append([teamName, role.id, password])
        print(data[guildie])
        print("Going to make channel:\n")
        await createChannel(teamName)
        print("Done making channels\n")
        print("Updating Guilds file")
        with open("Guilds.json", "w") as f:
            json.dump(data,f)
        print("done")
        
        
    else:
        await ctx.send("Command must be used in a direct message with the bot!")
        await ctx.message.delete()

@client.command()
async def renameTeam(ctx, teamName, newName, password):
    """Renames a given team with a new name"""
    data = reload()
    #server = client.get_guild(ctx.message.guild.id)
    server = client.get_guild(int(guildie))
    member = server.get_member(ctx.message.author.id)
    sender = ctx.message.author
    channel = str(ctx.message.channel) # Identifies where the command was sent from (a channel, a DM, etc)
    if channel == (f"Direct Message with {sender}"):  # if the command was sent from a DM:
        checkGuild(server)
        roleExist = get(server.roles, name=teamName)
        if roleExist:
            if roleExist in member.roles:
                await roleExist.edit(name=newName)
                for i, teamlist in enumerate(data[guildie]):
                    if teamName == teamlist[0] and password == teamlist[2]:
                        print(f"Replacing {data[guildie][i][0]} with {newName}")
                        data[guildie][i][0] = newName
                        print(f"Done, new data to verify {data}\n")
                        print(f"Update the guilds file with the new name")
                        with open("Guilds.json", "w") as f:
                            json.dump(data, f)
                        print("Done")
                        await ctx.send("Team name edited!")
                        return True
                    else:
                        pass
            else:
                await ctx.send("You have to be part of the team to change its name!")
        else:
            await ctx.send("Team doesn't exist!")
    else:
        await ctx.send("Command must be used in a direct message with the bot!")
        await ctx.message.delete()

@client.command()
async def joinTeam(ctx, teamName, password):
    """Join an existing team, the person who made the team does not need to join"""
    data = reload()
    #server = client.get_guild(ctx.message.guild.id)
    server = client.get_guild(int(guildie))
    member = server.get_member(ctx.message.author.id)
    sender = ctx.message.author
    channel = str(ctx.message.channel) # Identifies where the command was sent from (a channel, a DM, etc)
    if channel == (f"Direct Message with {sender}"):  # if the command was sent from a DM:
        checkGuild(server)
        roleExist = get(server.roles, name=teamName)
        if roleExist:
            for teamlist in data[guildie]:
                if teamName == teamlist[0] and password == teamlist[2]: # basically if teamname and password match
                    await member.add_roles(roleExist)
                    await ctx.send(f"Team {teamName} joined!")
                    return True
                else:
                    pass
        else:
            await ctx.send("Team doesn't exist!")
    else:
        await ctx.send("Command must be used in a direct message with the bot!")
        await ctx.message.delete()

@client.command()
async def leaveTeam(ctx, teamName):
    """Leave and existing team"""
    data = reload()
    #server = client.get_guild(ctx.message.guild.id)
    server = client.get_guild(int(guildie))
    member = server.get_member(ctx.message.author.id)

    checkGuild(server)
    roleExist = get(server.roles, name=teamName)
    if roleExist:
        if roleExist in member.roles:
            await member.remove_roles(roleExist)
            await ctx.send(f"Left team {teamName}!")
        else:
            await ctx.send("You aren't part of that team!")
    else:
        await ctx.send("Team doesn't exist!")


@client.command()
async def teamList(ctx, *teams):
    """Lists all team names, if a team name(s) is given, it will list the members for each"""
    data = reload()
    #server = client.get_guild(ctx.message.guild.id)
    server = client.get_guild(int(guildie))
    base_string = ""
    checkGuild(server)
    if len(teams) > 0:
        for team in teams:
            base_string += f"__{team}__: \n\t"
            role = get(server.roles, name=team)
            if role:
                for member in role.members:
                    try:
                        username = member.nick # collect the nickname of each id
                    except:
                        username = member.display_name # just get the username
                    if username == None: # if the user doesn't have a nickname
                        username = member.display_name # just get the username
                    base_string+= f"- {username}\n"
            else:
                base_string += "- Team doesn't exist \n"
    else:
        for teamlist in data[guildie]:
            team = teamlist[0]
            #print(team)
            base_string += f"{team}\n\n"

    emb = discord.Embed(description=base_string+" ", color=0x00fffd)
    emb.set_author(name="Teams", icon_url="https://cdn.discordapp.com/avatars/798707948926533674/b1a940ccfa219827bb1660c5e9888123.webp?size=256")
    await ctx.send(embed=emb)

@client.command()
async def help(ctx):
    """lists all commands"""
    message =   (
                "Arguments in <> refer to required arguments, [] refers to optional ones, multi-word arguments need to be in quotations\n"
                "- <required> [optional] \"Team Name\" \n\n"
                "__Commands in direct messages only__:\n"
                "- **!makeTeam** <Team Name> <password> - Makes a team with given name and password\n\n"
                "- **!joinTeam** <Team Name> <password> - Joins a made team provided the password is correct\n\n"
                "- **!renameTeam** <Old Team Name> <New Name> <password> - renames team\n\n"
                "__Commands that can be run anywhere__:\n"
                "- **!leaveTeam** <Team Name> - leaves the given team\n\n"
                "- **!teamList** [teams] - list all current teams, specific team names can be given to list their members\n\n"
                "- **!help** - brings up this menu!"
                )
    emb = discord.Embed(description=message, color=0x39e600)
    emb.set_author(name="Help Menu!", icon_url="https://cdn.discordapp.com/avatars/798707948926533674/b1a940ccfa219827bb1660c5e9888123.webp?size=256")
    await ctx.send(embed=emb)

if __name__ == "__main__":
    client.run(TOKEN)


