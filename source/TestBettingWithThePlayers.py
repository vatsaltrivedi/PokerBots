from theHouse import PlayerProxy
from texasHoldEm import Card
from texasHoldEm import InteractsWithPlayers
import unittest
from texasHoldEm import TakesBets
from FakeMessaging import StubMessenger


class testA_TellingThePlayersToBet(unittest.TestCase):

    def setUp(self):
        print 'Telling the players to bet,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        for player in self.inter.players:
            player.cards(['any cards'])
        self.tb = TakesBets(self.inter)

    def testA_tellTheFirstPlayerToTakeTheirGo(self):
        '''tell the first player to take their go'''
        self.tb.fromPlayers()

        self.assertEqual(('p1', 'GO'), self.msngr.lastMessage)

    def testB_tellTheSecondPlayerToTakeTheirGo(self):
        '''tell the second player to take their go'''
        self.msngr.bet('p1', 10)
        self.tb.fromPlayers()

        self.assertEqual(('p2', 'GO'), self.msngr.lastMessage)

    def testC_backToFirstPlayerAfterTheLast(self):
        '''moves back to the first player after the last'''
        self.msngr.bet('p1', 10).bet('p2', 20)
        self.tb.fromPlayers()

        self.assertEqual(('p1', 'GO'), self.msngr.lastMessage)

    def testD_skipsPlayerThatAreNotPlaying(self):
        '''skips player that are not playing'''
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        self.msngr.join('p3')

        self.inter.players[1].cards(['any cards'])
        self.inter.players[2].cards(['any cards'])

        self.tb = TakesBets(self.inter)
        self.tb.fromPlayers()

        self.assertEqual(('p2', 'GO'), self.msngr.lastMessage)


class testB_DecidingWhenAllBetsAreTaken(unittest.TestCase):

    def onBetsTaken(self, sender, args=None):
        self.betsTaken = True

    def setUp(self):
        print 'deciding when all bets are taken,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        for player in self.inter.players:
            player.cards(['any cards'])
        self.tb = TakesBets(self.inter)
        self.tb.evt_betsTaken += self.onBetsTaken
        self.betsTaken = False

    def testA_takenIfBetIsCalledByAll(self):
        '''not if a player has raised'''
        self.msngr.bet('p1', 10).bet('p2', 10)
        self.tb.fromPlayers()

        self.assertTrue(self.betsTaken)

    def testB_notIfPlayerHasRaised(self):
        '''not if a player has raised'''
        self.msngr.bet('p1', 10).bet('p2', 20)
        self.tb.fromPlayers()

        self.assertFalse(self.betsTaken)

    def testC_doneIfRaiseIsCalled(self):
        '''done if raise is called by all others'''
        self.msngr.bet('p1', 10).bet('p2', 20).bet('p1', 10)
        self.tb.fromPlayers()

        self.assertTrue(self.betsTaken)

    def testD_doneWhenNoPlayerHasChipsLeft(self):
        '''done when only one player has chips left'''
        self.msngr.bet('p1', 1000).bet('p2', 1000)
        self.tb.fromPlayers()

        self.assertTrue(self.betsTaken)

    def testE_doneImmediatelyIfNoneOfThePlayersHasChips(self):
        '''done immediately of none of the players has chips'''
        for player in self.inter.players:
            player.chips = 0
        self.tb.fromPlayers()

        self.assertTrue(self.betsTaken)


class testC_WhenDownToOnePlayer(unittest.TestCase):

    def onBetsTaken(self, sender, args=None):
        self.betsTaken = True

    def setUp(self):
        print 'When down to one player,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.msngr.join('p1')
        self.msngr.join('p2')
        self.inter.players[0].cards(['any cards'])
        self.tb = TakesBets(self.inter)
        self.tb.evt_betsTaken += self.onBetsTaken
        self.betsTaken = False

        self.tb.fromPlayers()

    def testA_allBetsAreTaken(self):
        '''all bets are taken'''
        self.assertTrue(self.betsTaken)


class testD_PlayerFolding(unittest.TestCase):

    def setUp(self):
        print 'A player folding,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        for player in self.inter.players:
            player.cards(['any cards'])

        self.msngr.bet('p1', 2).bet('p2', 0)

        self.tb.fromPlayers()

    def testA_playerIsToldTheyAreOut(self):
        '''the player is told that they are out'''
        self.assertTrue(('p2', 'OUT FOLD') in self.msngr.sentMessages)

    def testB_thePlayerIsNotPlaying(self):
        '''the player is not playing'''
        self.assertFalse(self.inter.players[1].isPlaying())


class testE_PlayerBetsMoreThanTheyHave(unittest.TestCase):

    def setUp(self):
        print 'Player bets more than they have,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        for player in self.inter.players:
            player.cards(['any cards'])

        self.msngr.bet('p1', 2000)

        self.tb.fromPlayers()

    def testA_kickThePlayerOut(self):
        '''kick the player out'''
        outMessage = 'OUT OVERDRAWN'
        self.assertTrue(('p1', outMessage) in self.msngr.sentMessages)

    def testB_playerIsOut(self):
        '''the player is out'''
        self.assertFalse(self.inter.players[0].isPlaying())

    def testC_takePlayersChips(self):
        '''take the players chips'''
        self.assertEqual(self.inter.players[0].chips, 0)


class testF_PlayerPlacesBetOutOfTurn(unittest.TestCase):

    def setUp(self):
        print 'a player places a bet out of turn,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        for player in self.inter.players:
            player.cards(['any cards'])

        self.msngr.bet('p2', 1000)

        self.tb.fromPlayers()

    def testA_theBetShouldBeIgnored(self):
        '''the bet should be ignored'''
        self.assertFalse('BET p2 1000' in self.msngr.allMessages)

    def testB_thePlayerIsKickedOut(self):
        '''the player is kicked out'''
        self.assertFalse(self.inter.players[1].isPlaying())

    def testC_takeThePlayersChips(self):
        '''take the players chips'''
        self.assertEqual(self.inter.players[1].chips, 0)

    def testD_kickOutThePlayer(self):
        '''kick out the player'''
        self.assertTrue(('p2', 'OUT OUT_OF_TURN') in self.msngr.allMessages)


class testG_PlayerSendsNonNumericMessage(unittest.TestCase):

    def setUp(self):
        print 'a player sends a non numeric message,', self.shortDescription()
        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        for player in self.inter.players:
            player.cards(['any cards'])

        self.msngr.bet('p1', 'XX')

        self.tb.fromPlayers()

    def testA_theBetShouldBeIgnored(self):
        '''the bet should be ignored'''
        self.assertFalse('BET p1 XX' in self.msngr.allMessages)

    def testB_takeThePlayersCards(self):
        '''take the players cards'''
        self.assertFalse(self.inter.players[0].isPlaying())

    def testC_takeThePlayersChips(self):
        '''take the players chips'''
        self.assertEqual(self.inter.players[0].chips, 0)

    def testD_kickOutThePlayer(self):
        '''kick out the player'''
        outMessage = 'OUT NOT_A_NUMBER'
        self.assertTrue(('p1', outMessage) in self.msngr.allMessages)


class testG_SplittingUpThePotBetweenTheWinners(unittest.TestCase):

    def setUp(self):
        print 'Splitting the pot between the winners,', self.shortDescription()

    def testA_withoutSidePotsTheTopRankedPlayerWinsAll(self):
        '''without side pots the top ranked player wins all'''

        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('winner')
        self.msngr.join('loser')

        self.inter.players[0].cards(cards('14C,14D,2C,3H,4S'))
        self.inter.players[1].cards(cards('2C,3D,5C,9D,13S'))

        self.msngr.bet('winner', 5).bet('loser', 5)

        self.tb.fromPlayers()

        self.tb.distributeWinnings()

        self.assertEqual(self.inter.players[0].chips, 1005)
        self.assertEqual(self.inter.players[1].chips, 995)

    def testB_theTopRankedPlayerCannotWinMoreThanAllowed(self):
        '''if a player is only in a side pot, that is all they can win'''

        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('winsSidePot')
        self.msngr.join('loser')

        self.inter.players[0].cards(cards('14C,14D,2C,3H,4S'))
        self.inter.players[1].cards(cards('2C,3D,5C,9D,13S'))

        self.inter.players[0].chips = 5
        self.inter.players[1].chips = 10

        self.msngr.bet('winsSidePot', 5).bet('loser', 10)

        self.tb.fromPlayers()

        self.tb.distributeWinnings()

        self.assertEqual(self.inter.players[0].chips, 10)
        self.assertEqual(self.inter.players[1].chips, 5)

    def testC_splittingThePot(self):
        '''players will split the pot if they are ranked the same'''

        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('tiedA')
        self.msngr.join('tiedB')

        self.inter.players[0].cards(cards('14C,14D,2C,3H,4S'))
        self.inter.players[1].cards(cards('14C,14D,2C,3H,4S'))

        self.msngr.bet('tiedA', 1000).bet('tiedB', 1000)

        self.tb.fromPlayers()

        self.tb.distributeWinnings()

        self.assertEqual(self.inter.players[0].chips, 1000)
        self.assertEqual(self.inter.players[1].chips, 1000)

    def testD_shouldAnnounceTheWinners(self):
        '''should announce the winners of the game'''

        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        self.inter.players[0].cards(cards('14C,14D,2C,3H,4S'))
        self.inter.players[1].cards(cards('6S,4H,3C,2D,2C'))

        self.msngr.bet('p1', 1000).bet('p2', 1000)

        self.tb.fromPlayers()

        self.tb.distributeWinnings()

        self.assertEqual(self.msngr.wonMessages,
                         ['WON p1 p2 1000 14C,14D,4S,3H,2C pairHand',
                          'WON p1 p1 1000 14C,14D,4S,3H,2C pairHand',
                          'WON p2 p1 0 2D,2C,6S,4H,3C pairHand',
                          'WON p2 p2 0 2D,2C,6S,4H,3C pairHand'])

    def testE_shouldOnlyDistributeToPlayersInTheGame(self):
        '''should only distribute the winnings to players in the game'''

        self.msngr = StubMessenger()
        self.inter = InteractsWithPlayers(self.msngr)
        self.tb = TakesBets(self.inter)

        self.msngr.join('p1')
        self.msngr.join('p2')

        self.inter.players[0].cards(cards('14C,14D,2C,3H,4S'))
        self.inter.players[1].cards(cards('6S,4H,3C,2D,2C'))

        self.msngr.bet('p1', 1000).bet('p2', 0)

        self.tb.fromPlayers()

        self.tb.distributeWinnings()

        self.assertEqual(self.msngr.wonMessages,
                         ['WON p1 p2 0 14C,14D,4S,3H,2C pairHand',
                          'WON p1 p1 1000 14C,14D,4S,3H,2C pairHand'])


def createPlayer(name, chips=0, cards=[]):
    player = PlayerProxy(name, chips)
    player.parse = lambda x: x
    player.fromMe = lambda x: True
    player.cards(cards)

    return player


def cards(items):
    return map(lambda x: Card(int(x[0:-1]), x[-1]), items.split(','))


if __name__ == "__main__":
    unittest.main()
