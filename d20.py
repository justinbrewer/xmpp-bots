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
	(args,comment) = tuple(args.split('#'))
        argv = args.split()
        name = mess.getFrom().getNode()
        if name == 'opd20':
            name = mess.getFrom().getResource()
        res = []
        for i in argv:
            dice = i.split('d')
            if len(dice) == 2:
                for _ in range(int(dice[0])):
                    res.append(random.randint(1,int(dice[1])))
            else:
                res.append(int(i))
        total = 0
        for i in res:
            total += i
        return ""+name+" rolled "+str(total)+" "+repr(res)+"\n"+comment

bot = D20Bot(username,password,**{'command_prefix':'//'})

if chatroom != "":
	bot.join_room(chatroom)

bot.serve_forever()
