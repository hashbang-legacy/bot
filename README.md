bot
===


Irc bot


### Getting Started

[python3.x](https://www.python.org/downloads/) is the only requirement.

[make](http://www.gnu.org/software/make/) is optional (it's used as a runner/starter).

---

### Goals

- Minimal barrier to entry
- Language agnostic plugins
- Live hackable

---

### Using the bot

Firstly, edit the [config.json](https://github.com/hashbang/bot/blob/master/config.json) to your liking.

Next, run `make` (or `python main.py`). This will start the bot and you're now up and running.

---

### Writing a Plugin

The bot starts plugins listed in the config file upon startup.
