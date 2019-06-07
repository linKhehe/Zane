import zane.bot


if __name__ == '__main__':
    with open("token.txt", "r") as f:
        token = f.read()
    zane.bot.Bot().run(token)
