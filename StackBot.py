#!/usr/bin/python

from irc.client import nm_to_n 
import irc.bot
import json
import string

config_file_name = "config.txt"

class StackBot(irc.bot.SingleServerIRCBot):
    def __init__(self): 
        # Load of configuration stuff.
        self.config_file_handle = open(config_file_name, "r")
        self.config_json = json.load(self.config_file_handle)
        self.config_file_handle.close()

        self.server = [(self.config_json["server"], 6667)];
        self.nickname = self.config_json["nickname"]        
        self.realname = self.config_json["realname"]
        self.channel = self.config_json["channel"]
        self.password = self.config_json["password"] 

        # Initialize:
        irc.bot.SingleServerIRCBot.__init__(self, self.server, self.nickname, self.realname)
        
        self.user_to_stack = {'nobody': ['nothing.', 'Get some work done.']}
        self.commands = ['stats: Prints some stack stats (users, stack depth, etc.)', 'mystack: Prints your own stack', 'push <text>: Pushes <text> onto your stack.', 'help: Really? Come on.', 'pop: Pops the top item of the stack'] 
       
    def on_welcome(self, c, e):
        c.join(self.channel, key=self.password)

    def on_pubmsg(self, c, e):
        if self.nickname in e.arguments()[0]:
            # Make sure they were talking to us, and then print
            # their stack to the channel.
            user = nm_to_n(e.source())
            self.do_command(e.arguments()[0], c, user, self.channel)

    def on_privmsg(self, c, e):
        # If this was a private message, just send the stack
        # to that user.
        user = nm_to_n(e.source())
        self.do_command(e.arguments()[0], c, user, user)

    def print_stack(self, connection, user, channel):
        i = 0
        # We need to reverse the stack, because everything happens at the end
        # instead of the front.
        self.user_to_stack[user].reverse()
        for item in self.user_to_stack[user]:
            connection.privmsg(self.channel, "%(item_index)i:%(item_text)s" % {"item_index": i, "item_text": item})
            i = i+1
        # Make sure we put it back the way we found it:
        self.user_to_stack[user].reverse()
        
    def do_command(self, command, connection, user, channel):
        to_lowered = string.lower(command)
        if 'stats' in to_lowered:
           print "Not implemented." 
           return
        elif 'mystack' in to_lowered:
            if user in self.user_to_stack.keys():
                self.print_stack(connection, user, channel)
            else:
                connection.privmsg(channel, "You're not in the stack yet.")
        elif 'push' in to_lowered:
            stack_item = command.partition('push')

            if user in self.user_to_stack.keys():
                self.user_to_stack[user].append(stack_item[2])
            else:
                self.user_to_stack[user] = [stack_item[2]]

            connection.privmsg(channel, "Added%(item)s to %(user)s\'s stack." % {"item": stack_item[2], "user": user})
            return
        elif 'help' in to_lowered:
            for item in self.commands:
                connection.privmsg(channel, item)
            return

        elif 'pop' in to_lowered:
            if user in self.user_to_stack.keys() and len(self.user_to_stack[user]) > 0:
                    self.user_to_stack[user].pop()
                    self.print_stack(connection, user, channel)
                    return

            connection.privmsg(channel, "Nothing to pop, %(user)s." % {"user": user})
            return

def main():
    bot = StackBot()
    bot.start()

if __name__ == "__main__":
    main()
