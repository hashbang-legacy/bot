(echo '{
  "args":["#test", "Message"],
  "command":"PRIVMSG",
  "prefix":"user!name@ip",
  "raw": ":user!name@ip PRIVMSG #test :term"
}' | tr -d "\n"; echo "") | bash start.sh

