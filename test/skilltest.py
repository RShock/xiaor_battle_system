from lagom import Container

from xiaor_battle_system.gameBoard import GameBoard
from xiaor_battle_system.logger import Logger
from xiaor_battle_system.msgManager import MsgManager
from xiaor_battle_system.pokemon import Pokemon
from xiaor_battle_system.tools.stream import Stream
from xiaor_battle_system.tools.tools import get_container

import unittest

class TestCases(unittest.TestCase):
    container = None
    logger = None
    msgManager = None
    gameBoard = None

    @classmethod
    def setUpClass(cls) -> None:
        # print('每个用例前置')
        cls.container = get_container()
        # 单例声明
        cls.logger = cls.container[Logger] = Logger()
        cls.msgManager = cls.container[MsgManager] = MsgManager(cls.container[Logger])
        cls.gameBoard = cls.container[GameBoard] = GameBoard(cls.container[Logger], cls.container[MsgManager])


    def setUp(self) -> None:
        self.gameBoard = self.container[GameBoard]
        self.gameBoard.TURN_LIMIT = 8
        self.pkm1 = self.container[Pokemon]
        self.pkm2 = self.container[Pokemon]

        data_init(self.pkm1)
        self.pkm1.name = "小白菜"
        data_init(self.pkm2)
        self.pkm2.name = "小黄瓜"

        self.gameBoard.add_ally(self.pkm1)
        self.gameBoard.add_enemy(self.pkm2)

    def tearDown(self) -> None:
        # print('每个用例的后置')
        self.gameBoard.print_log()
        self.msgManager.clean()
        self.logger.clean()

        if self.result:
            print(f"{self.pkm1.name}胜利")
        else:
            print(f"{self.pkm1.name}战败！")

    def test连击(self):
        self.pkm1.skillGroup = ["连击"]

        # pkm2.skillGroup = ["反击50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 1000)

    def test反击对连击正常反应(self):
        self.pkm1.skillGroup = ["连击"]
        self.pkm2.skillGroup = ["反击50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 790)
        self.assertEqual(self.pkm2.HP, 1000)

    def test03(self):
        self.pkm2.skillGroup = ["愈合1"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 937)

    def test测试2个回血技能(self):
        self.pkm2.skillGroup = ["愈合1","长生"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 944)

    def test毒攻击(self):
        self.pkm1.skillGroup = ["毒液50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 870)

    def test毒攻击无法被反击(self):
        self.pkm1.skillGroup = ["毒液50", "连击", "利爪10"]
        self.pkm2.skillGroup = ["反击"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 870)

    def test连击会导致攻击力归零(self):
        self.pkm1.skillGroup = ["毒液50", "连击"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 1000)

    def test剧毒之体(self):
        self.pkm1.skillGroup = ["毒液50", "剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 740)

    def test剧毒之体无法造成普通伤害(self):
        self.pkm1.skillGroup = ["剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 930)
        self.assertEqual(self.pkm2.HP, 1000)

    def test剧毒之体回合结束会强制解毒(self):
        self.pkm1.skillGroup = ["毒液50"]
        self.pkm2.skillGroup = ["剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.HP, 1000)
        self.assertEqual(self.pkm2.HP, 930)


if __name__ == '__main__':
    unittest.main()


def data_init(pkm: Pokemon):
    pkm.ATK = 20
    pkm.DEF = 10
    pkm.HP = 1000
    pkm.skillGroup = []
