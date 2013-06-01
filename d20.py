#!/usr/bin/python2

#Config
username = ""
password = ""
chatrooms = []

from jabberbot import JabberBot, botcmd
import random
import logging
logging.basicConfig()

class D20Bot(JabberBot):
    PING_FREQUENCY = 60

    @botcmd
    def roll(self,mess,args):
        args,comment = (args.split('#',1)+[''])[:2]
        comment = ' '+comment if comment != '' else ''
        
        if mess.getFrom().getStripped() in chatrooms:
            name = mess.getFrom().getResource()
        else:
            name = mess.getFrom().getNode()
        
        argv = args.split()
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
        return ""+name+" rolled "+str(total)+" "+repr(res)+comment

    @botcmd
    def r(self,mess,args):
        return self.roll(mess,"1d20 "+args)

bot = D20Bot(username,password,**{'command_prefix':'//'})

for i in chatrooms:
	bot.join_room(i)

bot.serve_forever()
