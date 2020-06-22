import zane
from config import Config


if __name__ == "__main__":
    bot = zane.Zane.from_config(Config)
    bot.run()

