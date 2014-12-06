from bot import Bot
from bot.plugins import DebugPlugin, ScriptStarterPlugin


if __name__ == "__main__":
    try:
        config = {
            "host": "og.hashbang.sh",
            "port": 4445,
            "nick": "[bot]",
            "password": "hashbangbot:password",
            "plugins": ['example']
        }

        bot = Bot(config)
        bot.loadPlugin(DebugPlugin)
        bot.loadPlugin(ScriptStarterPlugin(config['plugins']))
        bot.loop()

        print("Regular Exit")
    except:
        print("Exceptional exit:")
        raise

