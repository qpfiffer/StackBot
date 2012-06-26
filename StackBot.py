#!/usr/bin/python

from irc.client import nm_to_n 
import irc.bot
import json
import string
import redis

config_file_name = "config.txt"

class StackBot(irc.bot.SingleServerIRCBot):
    def __init__(self): 
        # Load of configuration stuff.
        self.config_file_handle = open(config_file_name, "r")
        self.config_json = json.load(self.config_file_handle)
        self.config_file_handle.close()

        # Redis stuff
        self.redis_handler = redis.Redis('localhost')

        # Config stuff handled at runtime
        self.server = [(self.config_json["server"], 6667)]
        self.nickname = self.config_json["nickname"]        
        self.realname = self.config_json["realname"]
        self.channel = self.config_json["channel"]
        self.password = self.config_json["password"] 

        # Initialize:
        irc.bot.SingleServerIRCBot.__init__(self, self.server, self.nickname, self.realname)
        
        self.commands = ['Commands can be prefaced with stack or ' + self.nickname, 'stats: Prints some stack stats (users, stack depth, etc.)', 'mystack: Prints your own stack', 'push <text>: Pushes <text> onto your stack.', 'help: Really? Come on.', 'pop: Pops the top item of the stack'] 
       
    def on_welcome(self, c, e):
        c.join(self.channel, key=self.password)

    def on_pubmsg(self, c, e):
        arguments = e.arguments()[0]

        if self.nickname in arguments or 'stack' in arguments:
            # Make sure they were talking to us, and then print
            # their stack to the channel.
            user = nm_to_n(e.source())
            self.do_command(arguments, c, user, self.channel)

    def on_privmsg(self, c, e):
        # If this was a private message, just send the stack
        # to that user.
        user = nm_to_n(e.source())
        self.do_command(e.arguments()[0], c, user, user)

    def print_stack(self, connection, user, channel):
        i = 0
        user_items = self.redis_handler.lrange(user, 0, -1)
        for item in user_items:
            connection.privmsg(self.channel, "%(item_index)i:%(item_text)s" % {"item_index": i, "item_text": item})
            i = i+1
        
    def do_command(self, command, connection, user, channel):
        to_lowered = string.lower(command)
        if 'stats' in to_lowered:
           print "Not implemented." 
           return

        elif 'mystack' in to_lowered:
            self.print_stack(connection, user, channel)

        elif 'push' in to_lowered:
            stack_item = command.partition('push')[2]

            users_stack = self.redis_handler.lrange(user, 0, -1)
            self.redis_handler.rpush(user, stack_item)

            connection.privmsg(channel, "Added%(item)s to %(user)s\'s stack." % {"item": stack_item, "user": user})
            return

        elif 'help' in to_lowered:
            for item in self.commands:
                connection.privmsg(channel, item)
            return

        elif 'pop' in to_lowered:
            self.redis_handler.rpop(user)
            self.print_stack(connection, user, channel)
            
            return

def main():
    bot = StackBot()
    bot.start()

if __name__ == "__main__":
    main()
