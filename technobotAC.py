from javascript import require, On
import threading
from datetime import datetime
import mysql.connector
import time
import random

mineflayer = require("mineflayer")

bot = None
nInEnd = 0

config = open("config.txt", mode="r", encoding="utf-8")
config_lines = config.readlines()
nickname = config_lines[0].replace("nickname=", "").replace("\r", "").replace("\n", "").replace(" ", "")
portal = config_lines[1].replace("portal=", "").replace("\r", "").replace("\n", "").replace(" ", "")
auto_chat_file = config_lines[2].replace("auto_chat_file=", "").replace("\r", "").replace("\n", "").replace(" ", "")

print(nickname)
print(portal)
print("Через ввод в консоли можно выполнять команды бота (начинаются с .) а также писать от имени бота в чат.")
print("При заходе на сервер чтобы он зашёл на выбранный вами портал, введите .join")

auto_chat_enabled = False
auto_chat = {}

clan_inviting = False
auto_chatgame = False
repitition_player = None

portals = {
	"epsilon": 10,
	"yota": 11,
	"delta": 12,
	"sigma": 13,
	"alpha": 14,
	"beta": 15,
	"gamma": 16,
	"omega": 21,
	"hydra": 22,
	"omicron": 23
}

def consoleInput():
	while True:
		global bot
		inp = input()

		if inp.startswith(".online"):
			online = ""
			for player in bot.players:
				online += player + "  "

			print(online)

		elif inp == ".bypass":
			bot.end()
			bot = None
			startNewBot()

		elif inp == ".join":
			bot.activateItem(False)

		elif inp == ".toggle_autoChat":
			global auto_chat_enabled
			auto_chat_enabled = not auto_chat_enabled
			print(f"Авто-чат переключен на {str(auto_chat_enabled)}")

		elif inp == ".toggle_clanInviting":
			global clan_inviting
			clan_inviting = not clan_inviting
			print(f"Авто-приглашение переключено на {str(clan_inviting)}")

		elif inp == ".toggle_autoChatGame":
			global auto_chatgame
			auto_chatgame = not auto_chatgame
			print(f"Авто-чат-игра переключено на {str(auto_chatgame)}")

		elif inp.startswith(".repeat "):
			global repitition_player
			playerName = inp[8:]
			if (len(playerName) < 3): return

			if (repitition_player == "off"):
				repitition_player = None
				print("Повторение сообщений за игроками прекращено.")

			repitition_player = playerName
			print(f"Повторение сообщений за игроком {str(repitition_player)}.")
			
		elif inp.startswith("."):
			print("???")
		else:
			bot.chat(inp)

def messageHandle(message):
	global bot
	global auto_chat_enabled, auto_chatgame, clan_inviting
	global repitition_player

	if auto_chatgame and "Chat Game » Решите пример:" in message:
		parts = message.split(" ")
		num1 = int(parts[5])
		operator = parts[6]
		num2  = int(parts[7].replace(".", ""))
		result = 0

		if operator == "+":
			result = num1 + num2
		elif operator == "-":
			result = num1 - num2
		elif operator == "*":
			result = num1 * num2
		elif operator == "/":
			result = num1 / num2

		bot.chat("!" + str(result) + " я никому не дам решать данные примеры.")

	elif auto_chat_enabled:
		for key, value in auto_chat.items():
			strings = key.split("&&")
			replies = value.split("||")

			for string in strings:
				if string in message:
					strings.remove(string)
			if len(strings) == 0:
				random_reply = random.choice(replies)
				if "(arg0)" in random_reply:
					random_reply = random_reply.replace("(arg0)", message.split(" ")[0].replace(",", ""))
				if "(arg1)" in random_reply:
					random_reply = random_reply.replace("(arg1)", message.split(" ")[1].replace(",", ""))
				if "(arg2)" in random_reply:
					random_reply = random_reply.replace("(arg2)", message.split(" ")[2].replace(",", ""))
				if "(arg3)" in random_reply:
					random_reply = random_reply.replace("(arg3)", message.split(" ")[3].replace(",", ""))
				if "(arg4)" in random_reply:
					random_reply = random_reply.replace("(arg4)", message.split(" ")[4].replace(",", ""))
				if "(arg5)" in random_reply:
					random_reply = random_reply.replace("(arg5)", message.split(" ")[5].replace(",", ""))
				if "(username)" in random_reply:
					random_reply = random_reply.replace("(username)", bot.username)
				if "(playername)" in random_reply:
					nickname = None
					parts = random_reply.split(" ")

					if "[" in parts[1]: nickname = parts[2]
					elif "[" in parts[2]: nickname = parts[3]
					elif "[" in parts[3]: nickname = parts[4]

					random_reply.replace("(playerName)", nickname)
				for action in random_reply.split("&&"):
					if not action.startswith("."):
						time.sleep(0.4)
						bot.chat(action)
						pass
					elif ".bypass" in action:
						bot.end()
						bot = None
						startNewBot()
					elif ".join" in action:
						bot.activateItem(False)
				break

	elif "→" in message:
		nickname = findNickname(message)
		if nickname == None: return

		if nickname == repitition_player:
			bot.chat("!" + message.split("→ ")[1])
			return

		if clan_inviting:
			bot.chat(f"/c invite {nickname}")

	elif "› Игрок " in message:
		bot.chat("/c invite " + message.split(" ")[3])


def findNickname(msg):
	parts = msg.split(" ")
	if "[" in parts[1] and not "[" in parts[2]: return parts[2]
	if "[" in parts[2] and not "[" in parts[3]: return parts[3]
	if "[" in parts[3] and not "[" in parts[4]: return parts[4]
	if "[" in parts[4] and not "[" in parts[5]: return parts[5]
	return None

def startNewBot():
	global nInEnd
	global bot
	global nickname
	global portal
	nInEnd += 1

	botname = nickname
	if nInEnd > 1: botname += str(nInEnd)

	bot = mineflayer.createBot({
		"host": "mc.mineblaze.net",
		"username": botname
	})

	@On(bot, "message")
	def msgHandler(this, message, *args):
		msg = message.getText()

		print(msg)
		messageHandle(msg)

	@On(bot, "windowOpen")
	def windowHandler(this, message, *args):
		bot.clickWindow(portals[portal], 0, 0)


if __name__ == "__main__":
	console_thread = threading.Thread(target=consoleInput)
	console_thread.start()

	startNewBot()

	with open(auto_chat_file, mode="r", encoding="utf-8") as file:
		lines = file.readlines()
		for line in lines:
			if line.startswith("#"): continue
			elif ",," in line:
				split = line.split(",,")
				auto_chat[split[0].replace("\"", "")] = split[1].replace("\"", "")

