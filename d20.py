#!/usr/bin/python2

#Config
username = ""
password = ""
chatroom = ""

from jabberbot import JabberBot, botcmd
import random

class D20Bot(JabberBot):
    PING_FREQUENCY = 60

    @botcmd
    def roll(self,mess,args):
        argv = args.split()
        name = mess.getFrom().getNode()
        if name == 'opd20':
            name = mess.getFrom().getResource()
        res = []
        dice = map(int,argv[0].split('d'))
        for _ in range(dice[0]):
            res.append(random.randint(1,dice[1]))
        for i in argv[1:]:
            res.append(int(i))
        total = 0
        for i in res:
            total += i
        return ""+name+" rolled "+str(total)+" "+repr(res)

bot = D20Bot(username,password,**{'command_prefix':'//'})

if chatroom != "":
	bot.join_room(chatroom)

bot.serve_forever()
