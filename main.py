from bot import Bot
from bot.plugins import PingPlugin, ScriptStarterPlugin
import json
import os

CONFIG_PATH = 'config.json'
CONFIG_EXAMPLE_PATH = 'config.json.example'

if __name__ == "__main__":

    if not os.path.exists(CONFIG_PATH):
        print("No config file found! Creating config based on config.json.example ...")

        if not os.path.exists(CONFIG_EXAMPLE_PATH):
            print("No example config found! Create your own config.json.")

        else:
            import shutil
            shutil.copy2(CONFIG_EXAMPLE_PATH, CONFIG_PATH)
            print("config.json created! Check it over and start the bot again.")

    else:
        try:
            config = json.loads(open(CONFIG_PATH).read())

            bot = Bot(config)
            bot.loadPlugin(PingPlugin)
            bot.loadPlugin(ScriptStarterPlugin(config['plugins']))
            bot.loop()

            print("Regular Exit")
        except:
            print("Exceptional exit:")
            raise

