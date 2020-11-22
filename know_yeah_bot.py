import discord
import requests
import json
from bs4 import BeautifulSoup


token = ""
prefix = '!'
colors = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ruby", "Unrated"]


class Command:
    def __init__(self, names, args, operation):
        self.__names = names
        self.__args = args
        self.__operation = operation

    def __str__(self):
        ret = "[ "
        for i in range(len(self.__names)):
            ret += self.__names[i]
            if i != len(self.__names) - 1:
                ret += '/'

        for arg in self.__args:
            ret += ' ' + '<' + arg + '>'
        return ret + " ]"

    def run(self, args):
        if len(args) < len(self.__args):
            return None
        if len(self.__args) == 0:
            return self.__operation()
        return self.__operation(args)

    @property
    def names(self):
        return self.__names


class CommandManager:
    def __init__(self):
        self.__commands = []

    def add_command(self, command):
        self.__commands += [command]

    def run(self, cmd, args):
        for command in self.__commands:
            for name in command.names:
                if name == cmd:
                    return command.run(args)
        return None

    def get_commands(self):
        ret = ""
        for i in range(len(self.__commands)):
            ret += str(self.__commands[i])
            if i != len(self.__commands) - 1:
                ret += ", "
        return ret


client = discord.Client()
command_manager = CommandManager()


def init_command_manager():
    command_manager.add_command(Command(["명령어", "commands"], [], command_manager.get_commands))

    def problem_operation(args):
        if not args[0].isdigit():
            return None

        url = "https://solved.ac/search?query=%s" % args[0]
        request = requests.get(url)
        bs_object = BeautifulSoup(request.text, "html.parser")

        problems = json.loads(str(bs_object.body.contents[1].contents[0]))["props"]["pageProps"]["result"]["problems"]
        if len(problems) == 0:
            return None

        problem = problems[0]
        level = problem["level"] - 1
        color = colors[int(level / 5)] if level >= 0 else colors[-1]
        tier = str(5 - level % 5) if level >= 0 else ''
        return "%s번: %s - %s %s" % (args[0], problem["title"], color, tier)\
            + '\n' + "https://www.acmicpc.net/problem/%s" % args[0]
    command_manager.add_command(Command(["문제", "problem"], ["number"], problem_operation))


init_command_manager()


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


@client.event
async def on_message(message):
    if message.author == client.user or message.author.bot:
        return

    prefix_msg = message.content[0:len(prefix)]
    separated_msg = message.content[len(prefix):]
    if prefix_msg == prefix:  # prefixed commands
        if len(separated_msg) <= 0:
            return

        split_msg = separated_msg.split()
        cmd = split_msg[0]
        args = split_msg[1:]

        sending_msg = command_manager.run(cmd, args)
        if sending_msg is not None:
            await message.channel.send(sending_msg)

    else:  # prefixless commands
        for word in ["너구리" "Neogulee"]:
            if word in message.content:
                return

        archiving_words = ["대학원", "연구실", "랩", "머학원"]
        detected_word = None
        for word in archiving_words:
            if word in message.content:
                detected_word = word
                break

        if detected_word is not None:
            await message.channel.send("감지된 단어: {}\n```{}: {}```"
                                       .format(detected_word, message.author, message.content))
            return

        question_words = ["클린", "뉴비", "늅", "민초"]
        detected_word = None
        cnt = 0
        for word in question_words:
            if word in message.content:
                detected_word = word
                cnt += 1

        agree_words = ["변태", "굇수"]
        detected_word = None
        for word in agree_words:
            if word in message.content:
                detected_word = word
                break

        if detected_word is not None:
            await message.channel.send("ㅇㅈ")
        return

client.run(token)