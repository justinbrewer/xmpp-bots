#!/usr/bin/python2

#Config
username = ""
password = ""
chatrooms = []

from jabberbot import JabberBot, botcmd
import random
import logging
logging.basicConfig()

class BetGame():
    players = {}
    bet_order = []
    bets = {}
    dealer = 0
    turn = 0

    def enter(self,name,amount):
        if name in self.players:
            return False
        self.players[name] = amount
        self.bet_order.append(name)
        self.bets[name] = 0
        return True

    def bet(self,name,amount):
        if not name in self.players:
            return False
        if self.bet_order[self.turn] != name:
            return False

        if self.players[name] > amount:
            self.players[name] = self.players[name] - amount
            self.bets[name] = self.bets[name] + amount
            result = True
        else:
            self.bets[name] = self.bets[name] + self.players[name]
            self.players[name] = 0
            result = self.bets[name]

        self.turn = (self.turn + 1) % len(self.players)
        return result

    def win(self,name):
        if not name in self.players:
            return False

        entitlement = self.bets[name]
        amount = 0
        for k,v in self.bets.items():
            amount = amount + min(entitlement, v)
            self.bets[k] = max(v - entitlement, 0)
        self.players[name] = self.players[name] + amount
        return amount

    def pot(self):
        return sum(self.bets.itervalues())

class D20Bot(JabberBot):
    PING_FREQUENCY = 60

    game = None

    @botcmd
    def begin_game(self,mess,args):
        if self.game != None:
            return "A game is already in session. Use /end_game to end first."
        self.game = BetGame()
        return None

    @botcmd
    def end_game(self,mess,args):
        self.game = None
        return "Game ended."

    @botcmd
    def enter(self,mess,args):
        name = self.who(mess)
        amount = int(args)
        if self.game.enter(name, amount):
            return "" + name + " entered with " + str(amount) + " chips."
        else:
            return "" + name + " is already in the game."

    @botcmd
    def bet(self,mess,args):
        name = self.who(mess)
        amount = int(args)
        result = self.game.bet(name, amount)
        if result == True:
            return "" + name + " bet " + str(amount) + " chips."
        elif result == False:
            return "It is not your turn to bet."
        else:
            return "" + name + " bet " + str(amount) + " chips. They are now all-in for " + str(result) + " chips."

    @botcmd
    def win(self,mess,args):
        result = self.game.win(args)
        if result == False:
            return "" + args + " is not in the game."
        else:
            pot = self.game.pot()
            potmsg = ""
            if pot > 0:
                potmsg = " There are still " + str(pot) + " chips in the pot."
            return "" + args + " won " + str(result) + " chips." + potmsg

    def rolls(self,mess,args):
        args,comment = (args.split('#',1)+[''])[:2]
        comment = ' '+comment if comment != '' else ''

        if mess.getFrom().getStripped() in chatrooms:
            name = mess.getFrom().getResource()
        else:
            name = mess.getFrom().getNode()

        if args.find('{') > -1:
            results = []

            start = args.index('{')
            end = args.index('}')

            seq = args[start+1:end].split(',')
            for i in seq:
                results = results + self.rolls(mess,args[:start]+i+args[end+1:])
            return results

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
        return [""+name+" rolled "+str(total)+" "+repr(res)+comment]

    @botcmd
    def roll(self,mess,args):
        res = self.rolls(mess,args)
        if len(res) > 1:
            comment = (args.split('#',1)+[''])[1]
            message = ''
            count = 1
            for i in res:
                message = message+'\n('+str(count)+') '+i
                count = count + 1
            if comment != '':
                message = message + '\n' + comment
            return message
        else:
            return res[0]

    @botcmd
    def r(self,mess,args):
        return self.roll(mess,"1d20 "+args)

    @botcmd
    def sr(self,mess,args):
        args,comment = (args.split('#',1)+[''])[:2]
        return self.r(mess,'{'+','.join(args.split())+'}#'+comment)

    def who(self, mess):
        if mess.getFrom().getStripped() in chatrooms:
            return mess.getFrom().getResource()
        else:
            return mess.getFrom().getNode()

bot = D20Bot(username,password,**{'command_prefix':'/'})

for i in chatrooms:
	bot.join_room(i)

bot.serve_forever()
