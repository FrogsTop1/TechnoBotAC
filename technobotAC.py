from javascript import require, On
import asyncio
import random

import bot_config

mineflayer = require("mineflayer")

bot = None
bypass_count = 0

print(bot_config.nickname)
print(bot_config.portal)
print("""
    Через ввод в консоли можно выполнять команды бота (начинаются с .) а также писать от имени бота в чат.
    При заходе на сервер чтобы он зашёл на выбранный вами портал, введите .join
    """)


async def console_input(bot):
    while True:
        user_input = input()

        if user_input == ".end":
            bot.end()
            exit()

        elif user_input == ".join":
            bot.activateItem(False)

        elif user_input == ".bypass":
            bot.end()
            bot = None
            setup_bot()

        elif user_input.startswith(".online"):
            online = ""
            for player in bot.players:
                online += player + "  "

            print(online)

        elif user_input == ".toggle autoChat":
            bot_config.auto_chat = not bot_config.auto_chat
            print(f"Авто-чат переключен на {bot_config.auto_chat}")

        elif user_input == ".toggle autoClanInviting":
            bot_config.clan_inviting = not bot_config.auto_clan_inviting
            print(f"Авто-приглашение переключено на {bot_config.auto_clan_inviting}")

        elif user_input == ".toggle autoChatGame":
            bot_config.auto_chatgame = not bot_config.auto_chat_game
            print(f"Авто-чат-игра переключено на {bot_config.auto_chat_game}")

        elif user_input.startswith(".repeat "):
            target = user_input[8:]
            if len(target) < 3:
                return

            if target == "off":
                bot_config.repetition_target = None
                print("Повторение сообщений за игроками прекращено.")
                return

            bot_config.repetition_target = target
            print(f"Повторение сообщений за игроком {target}.")

        elif user_input.startswith("."):
            print("Неизвестная команда.")
        else:
            bot.chat(user_input)


def setup_bot():
    global bot
    global bypass_count
    bypass_count += 1

    bot_name = bot_config.nickname
    if bypass_count > 1:
        bot_name += str(bypass_count)

    bot = mineflayer.createBot({
        "host": "mc.mineblaze.net",
        "username": bot_name
    })

    @On(bot, "message")
    def msg_handler(this, message, *args):
        msg = message.getText()

        print(msg)
        handle_message(msg)

    @On(bot, "windowOpen")
    def window_handler(this, message, *args):
        bot.clickWindow(bot_config.portal_numbers[bot_config.portal], 0, 0)


def handle_message(message):
    global bot
    if bot_config.auto_chat:
        for key, value in bot_config.auto_chat_data.items():
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
                if "(bot_name)" in random_reply:
                    random_reply = random_reply.replace("(bot_name)", bot.username)
                if "(nickname)" in random_reply:
                    nickname = extract_nickname(message)
                    random_reply.replace("(playerName)", nickname)

                for action in random_reply.split("&&"):
                    if not action.startswith("."):
                        time.sleep(0.4)
                        bot.chat(action)

                    elif ".bypass" in action:
                        bot.end()
                        bot = None
                        setup_bot()

                    elif ".join" in action:
                        bot.activateItem(False)
                break

    if bot_config.auto_chat_game and "Chat Game » Решите пример:" in message:
        parts = message.split(" ")
        num1 = int(parts[5])
        operator = parts[6]
        num2 = int(parts[7].replace(".", ""))
        result = 0

        if operator == "+":
            result = num1 + num2
        elif operator == "-":
            result = num1 - num2
        elif operator == "*":
            result = num1 * num2
        elif operator == "/":
            result = num1 / num2

        bot.chat(f"!{result} я никому не дам решать данные примеры.")

    elif "→" in message:
        nickname = extract_nickname(message)
        if nickname == None: return

        if nickname == bot_config.repetition_target:
            bot.chat("!" + message.split("→ ")[1])
            return

        if bot_config.auto_clan_inviting:
            bot.chat(f"/c invite {nickname}")

    elif "› Игрок " in message and bot_config.auto_clan_inviting:
        bot.chat("/c invite " + message.split(" ")[3])


def extract_nickname(msg):
    parts = msg.split(" ")
    if "[" in parts[1] and not "[" in parts[2]:
        return parts[2]
    elif "[" in parts[2] and not "[" in parts[3]:
        return parts[3]
    elif "[" in parts[3] and not "[" in parts[4]:
        return parts[4]
    elif "[" in parts[4] and not "[" in parts[5]:
        return parts[5]
    return None


if __name__ == "__main__":
    setup_bot()
    asyncio.run(console_input(bot))

    with open(bot_config.auto_chat_file, mode="r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith("#"):
                continue
            elif ",," in line:
                split = line.split(",,")
                bot_config.auto_chat_data[split[0].replace("\"", "")] = split[1].replace("\"", "")
