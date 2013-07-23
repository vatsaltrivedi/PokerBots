import unittest
from theHouse import PlayerProxy
from texasHoldEm import Dealer
from mock import create_autospec
from Xmpp import XmppMessenger
from mock import MagicMock

def createMessenger():
    mockMessenger = create_autospec(XmppMessenger)
    mockMessenger.evt_messageReceived = MagicMock()
    return mockMessenger

def createPlayer(name):
    return PlayerProxy(name, createMessenger())

class testTheRotationOfTheDeal(unittest.TestCase):

    def testDealsToPlayer(self):
        player = createPlayer('p1')
        player.yourGo = MagicMock()

        Dealer().deal([player])

        self.assertTrue(player.yourGo.called)

    def testDealsToNextPlayerWhenPlayerResponds(self):
        player = createPlayer('p1')
        nextPlayer = createPlayer('p2')
        nextPlayer.yourGo = MagicMock()

        Dealer().deal([player, nextPlayer])

        player.response.fire(player, 0)

        self.assertTrue(nextPlayer.yourGo.called)

    def testDealsToFirstPlayerWhenLastPlayerResponds(self):
        player = createPlayer('p1')
        player.yourGo = MagicMock()

    	nextPlayer = createPlayer('p2')

    	Dealer().deal([player, nextPlayer])

        player.response.fire(player, 0)
        nextPlayer.response.fire(nextPlayer, 0)

    	self.assertEqual(1, len(player.yourGo.mock_calls))

    def testTellsPlayerThatTheyAreOutIfTheyRespondOutOfTurn(self):
        player = createPlayer('p1')
        nextPlayer = createPlayer('p2')
        nextPlayer.outOfGame = MagicMock()
        nextPlayer.yourGo = MagicMock()

        Dealer().deal([player, nextPlayer])

        nextPlayer.response.fire(nextPlayer, 0)

        nextPlayer.outOfGame.assert_called_once_with()
        self.assertEqual(0, len(nextPlayer.yourGo.mock_calls))
               
class testRoundOfCalling(unittest.TestCase):
    
    def testSmallBlindFirst(self):
        player = createPlayer('p1')
        player.smallBlind = MagicMock()

        Dealer().deal([player])

        player.smallBlind.assert_called_once_with(5)
    
    def testBigBlindSecond(self):
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p2.bigBlind = MagicMock()

        Dealer().deal([p1, p2])

        p2.bigBlind.assert_called_once_with(10)
    
    def testThirdIsFirstToBet(self):
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p3 = createPlayer('p3')
        p3.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p3.yourGo.assert_called_once_with(10)
    
    def testFirstShouldBetTheDifference(self):
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p3 = createPlayer('p3')
        p1.yourGo = MagicMock()

        Dealer().deal([p1, p2, p3])

        p3.response.fire(p3, 10)

        p1.yourGo.assert_called_with(5)
    
    def testPlayerKickedOutForBettingLessThanMinimum(self):
        p1 = createPlayer('p1')
        p2 = createPlayer('p2')
        p3 = createPlayer('p3')
        p3.outOfGame = MagicMock()

        Dealer().deal([p1, p2, p3])

        p3.response.fire(p3, 9)

        p3.outOfGame.assert_called_once_with()

if __name__=="__main__":
    unittest.main()