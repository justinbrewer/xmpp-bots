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

    def __init__(self):
        self.players = {}
        self.bet_order = []
        self.bets = {}
        self.bets_incremental = {}
        self.folds = []
        self.dealer = 0
        self.turn = 0
        self.raiser = None
        self.ante_amount = 1000
        self.ante_factor = 1.5
        self.ante_max = 50000

    def enter(self,name,amount):
        if name in self.players:
            return name + " is already in the game."
        if amount < 0:
            return "Please enter a positive amount."
        self.players[name] = amount
        self.bet_order.append(name)
        self.bets[name] = 0
        self.bets_incremental[name] = 0
        return name + " has entered with " + str(amount) + " chips."

    def check(self,name):
        if not name in self.players:
            return name + " is not in the game."
        if self.turn != None and self.bet_order[self.turn] != name:
            return "It is not your turn."
        if sum(self.bets_incremental.itervalues()) > 0:
            return "You need to call, raise, or fold."
        self.turn = (self.turn + 1) % len(self.players)
        return self.print_turn()

    def bet(self,name,amount):
        if not name in self.players:
            return name + " is not in the game."
        if self.turn != None and self.bet_order[self.turn] != name:
            return "It is not your turn."
        if sum(self.bets_incremental.itervalues()) > 0:
            return "You need to call, raise, or fold."
        if amount < (self.ante_amount / 2):
            return "Minimum bet is " + str(self.ante_amount / 2) + "."
        print "Before: " + str(self.bets_incremental)
        message = ""
        true_amount = min(self.players[name], amount)
        self.bets[name] = self.bets[name] + true_amount
        self.players[name] = self.players[name] - true_amount
        self.bets_incremental[name] = true_amount
        self.raiser = self.turn
        print "After: " + str(self.bets_incremental)
        message = message + name + " bet " + str(true_amount) + " chips."
        if self.players[name] == 0:
             message = message + "They are now all-in for " + str(self.bets[name]) + " chips."

        self.next_turn(self.turn + 1)
        return message + "\n" + self.print_turn()

    def call(self,name):
        if not name in self.players:
            return name + " is not in the game."
        if self.turn != None and self.bet_order[self.turn] != name:
            return "It is not your turn."
        print "Before: " + str(self.bets_incremental)
        amount = self.bets_incremental[self.bet_order[self.raiser]] - self.bets_incremental[name]
        true_amount = min(self.players[name], amount)
        self.bets[name] = self.bets[name] + true_amount
        self.players[name] = self.players[name] - true_amount
        self.bets_incremental[name] = true_amount + self.bets_incremental[name]
        print "After: " + str(self.bets_incremental)
        message = name + " bet " + str(true_amount) + " chips."
        if self.players[name] == 0:
             message = message + "They are now all-in for " + str(self.bets[name]) + " chips."

        self.next_turn(self.turn + 1)
        return message + "\n" + self.print_turn()

    def rise(self,name,amount):
        if not name in self.players:
            return name + " is not in the game."
        if self.turn != None and self.bet_order[self.turn] != name:
            return "It is not your turn."
        if amount < (self.ante_amount / 2):
            return "Minimum bet is " + str(self.ante_amount / 2) + "."
        print "Before: " + str(self.bets_incremental)
        amount = self.bets_incremental[self.bet_order[self.raiser]] - self.bets_incremental[name] + amount
        true_amount = min(self.players[name], amount)
        self.bets[name] = self.bets[name] + true_amount
        self.players[name] = self.players[name] - true_amount
        self.bets_incremental[name] = true_amount + self.bets_incremental[name]
        self.raiser = self.turn
        print "After: " + str(self.bets_incremental)
        message = name + " bet " + str(true_amount) + " chips."
        if self.players[name] == 0:
             message = message + "They are now all-in for " + str(self.bets[name]) + " chips."

        self.next_turn(self.turn + 1)
        return message + "\n" + self.print_turn()

    def all_in(self,name):
        if self.raiser != None:
            return self.rise(name,self.players[name])
        else:
            return self.bet(name,self.players[name])
            
    def fold(self,name):
        if not name in self.players:
            return name + " is not in the game."
        if self.turn != None and self.bet_order[self.turn] != name:
            return "It is not your turn."
        self.folds.append(name)
        self.next_turn(self.turn + 1)
        return self.print_turn()
    
    def win(self,name):
        if not name in self.players:
            return name + " is not in the game."

        entitlement = self.bets[name]
        amount = 0
        for k,v in self.bets.items():
            amount = amount + min(entitlement, v)
            self.bets[k] = max(v - entitlement, 0)
        self.players[name] = self.players[name] + amount

        if self.pot() == 0:
            self.dealer = (self.dealer + 1) % len(self.players)
            self.turn = self.dealer
            self.ante_amount = min(self.ante_max, int(self.ante_amount * self.ante_factor))
            self.raiser = None
            self.folds = []
            self.bets_incremental = dict.fromkeys(self.bets_incremental.iterkeys(), 0)

        message = name + " has won " + str(amount) + " chips."
        if self.pot() > 0:
            message = message + "\nThere are still " + str(self.pot()) + " chips in the pot."
        return message

    def ante(self):
        for k,v in self.players.items():
            self.bets[k] = self.bets[k] + min(self.ante_amount, v)
            self.players[k] = max(v - self.ante_amount, 0)
        return self.print_pot()

    def eject(self,name):
        self.players[name] = 0
        self.bets[name] = 0
        self.fold(name)
        self.next_turn(self.turn)
        return name + " ejected."

    def reset_pot(self):
        for k,v in self.bets.items():
            self.players[k] = self.players[k] + v
            self.bets[k] = 0
        self.folds = []
        self.bets_incremental = dict.fromkeys(self.bets_incremental.iterkeys(), 0)
        self.raiser = None
        self.turn = self.dealer
        return self.print_stats()

    def next_turn(self, turn):
        if self.turn == None:
            # No one can bet
            return
        
        self.turn = turn % len(self.players)

        if len(self.folds) == len(self.players):
            # Everyone has folded (lol)
            self.turn = None
            return

        if sum(self.players.itervalues()) == 0:
            # Everyone is all-in
            self.turn = None
            return
        
        if self.raiser != None and self.turn == self.raiser:
            # Finished a round of betting, go to top of round
            self.bets_incremental = dict.fromkeys(self.bets_incremental.iterkeys(), 0)
            self.raiser = None
            self.next_turn(self.dealer)
            return
        
        if self.players[self.bet_order[self.turn]] == 0 or self.bet_order[self.turn] in self.folds:
            # This player has folded or is out of the game
            self.next_turn(self.turn + 1)
            return

    def pot(self):
        return sum(self.bets.itervalues())

    def print_pot(self):
        result = ""
        for k,v in self.bets.items():
            if self.players[k] == 0:
                result = result + k + " is all-in for " + str(v) + " chips."
            else:
                result = result + k + " has bet " + str(v) + " chips."
            if k in self.folds:
                result = result + " " + k + " has folded."
            result = result + "\n"
            
        return result

    def print_turn(self):
        if self.turn == None:
            return "No one can bet."
        elif self.raiser == None and self.turn == self.dealer:
            return "Top of the round. " + self.bet_order[self.turn] + "'s turn."
        else:
            return self.bet_order[self.turn] + "'s turn."

    def print_stats(self):
        result = "\n\n"
        for k,v in self.players.items():
            result = result + k + " has " + str(v) + " chips.\n"
        return result + "\n\n" + self.print_pot()

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
        return self.game.enter(self.who(mess), int(args))

    @botcmd
    def ante(self,mess,args):
        return self.game.ante()

    @botcmd
    def turn(self,mess,args):
        return self.game.print_turn()

    @botcmd
    def check(self,mess,args):
        return self.game.check(self.who(mess))
    
    @botcmd
    def bet(self,mess,args):
        return self.game.bet(self.who(mess), int(args))

    @botcmd
    def call(self,mess,args):
        return self.game.call(self.who(mess))

    @botcmd
    def rise(self,mess,args):
        return self.game.rise(self.who(mess), int(args))

    @botcmd
    def all_in(self,mess,args):
        return self.game.all_in(self.who(mess))

    @botcmd
    def fold(self,mess,args):
        return self.game.fold(self.who(mess))

    @botcmd
    def win(self,mess,args):
        return self.game.win(args)

    @botcmd
    def pot(self,mess,args):
        return self.game.print_pot()

    @botcmd
    def stats(self,mess,args):
        return self.game.print_stats()

    @botcmd
    def eject(self,mess,args):
        return self.game.eject(args)

    @botcmd
    def reset_pot(self,mess,args):
        return self.game.reset_pot()

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
