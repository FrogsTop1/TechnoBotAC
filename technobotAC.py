from javascript import require, On
import threading
from datetime import datetime
import mysql.connector
import time
import random

mineflayer = require('mineflayer')

bot = None
nInEnd = 0

config = open('config.txt', mode='r', encoding='utf-8')
config_lines = config.readlines()
nickname = config_lines[0].replace('nickname=', '').replace('\r', '').replace('\n', '').replace(' ', '')
portal = config_lines[1].replace('portal=', '').replace('\r', '').replace('\n', '').replace(' ', '')
auto_chat_file = config_lines[2].replace('auto_chat_file=', '').replace('\r', '').replace('\n', '').replace(' ', '')

print(nickname)
print(portal)
print('Через ввод в консоли можно выполнять команды бота (начинаются с .) а также писать от имени бота в чат.')
print('При заходе на сервер чтобы он зашёл на выбранный вами портал, введите .join')

auto_chat_enabled = False
auto_chat = {}

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
		inp = input()

		if inp.startswith(".online"):
			online = ''
			for player in bot.players:
				online += player + "  "

			print(online)
		elif inp == '.join':
			bot.activateItem(False)

		elif inp == ".toggleAutoChat":
			global auto_chat_enabled
			auto_chat_enabled = not auto_chat_enabled
			print("Авто-чат переключен на " + str(auto_chat_enabled))
			
		elif inp.startswith("."):
			print("???")
		else:
			bot.chat(inp)

def msgReply(message):
	global bot
	global auto_chat_enabled
	if "Chat Game » Решите пример:" in message:
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
			result == num1 * num2
		elif operator == "/":
			result == num1 / num2

		bot.chat("!" + str(result) + ' easy peasy.')

	elif (auto_chat_enabled):
		for key, value in auto_chat.items():
			strings = key.split("&&")
			replies = value.split("||")

			for string in strings:
				if string in message:
					strings.remove(string)
			if len(strings) == 0:
				random_reply = random.choice(replies)
				if '(arg0)' in random_reply:
					random_reply = random_reply.replace('(arg0)', message.split(' ')[0].replace(',', ''))
				if '(arg1)' in random_reply:
					random_reply = random_reply.replace('(arg1)', message.split(' ')[1].replace(',', ''))
				if '(arg2)' in random_reply:
					random_reply = random_reply.replace('(arg2)', message.split(' ')[2].replace(',', ''))
				if '(arg3)' in random_reply:
					random_reply = random_reply.replace('(arg3)', message.split(' ')[3].replace(',', ''))
				if '(arg4)' in random_reply:
					random_reply = random_reply.replace('(arg4)', message.split(' ')[4].replace(',', ''))
				if '(arg5)' in random_reply:
					random_reply = random_reply.replace('(arg5)', message.split(' ')[5].replace(',', ''))
				if '(username)' in random_reply:
					random_reply = random_reply.replace('(username)', bot.username)
				if '(playername)' in random_reply:
					nickname = None
					parts = random_reply.split(' ')

					if '[' in parts[1]: nickname = parts[2]
					elif '[' in parts[2]: nickname = parts[3]
					elif '[' in parts[3]: nickname = parts[4]

					random_reply.replace('(playername)', nickname)
				for action in random_reply.split('&&'):
					if not action.startswith('.'):
						time.sleep(0.4)
						bot.chat(action)
						pass
					elif '.bypass' in action:
						bot.end()
						bot = None
						startNewBot()
					elif '.join' in action:
						bot.activateItem(False)
				break

def startNewBot():
	global nInEnd
	global bot
	global nickname
	global portal
	nInEnd += 1

	bot = mineflayer.createBot({
		'host': 'mc.mineblaze.net',
		'username': nickname + str(nInEnd)
	})

	@On(bot, 'message')
	def msgHandler(this, message, *args):
		msg = message.getText()

		print(msg)
		msgReply(msg)

	@On(bot, 'windowOpen')
	def windowHandler(this, message, *args):
		bot.clickWindow(portals[portal], 0, 0)


if __name__ == '__main__':
	console_thread = threading.Thread(target=consoleInput)
	console_thread.start()

	startNewBot()

	with open(auto_chat_file, mode='r', encoding='utf-8') as file:
		lines = file.readlines()
		for line in lines:
			if line.startswith('#'): continue
			elif ',,' in line:
				split = line.split(',,')
				auto_chat[split[0].replace("\"", "")] = split[1].replace("\"", "")

