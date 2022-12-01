import unittest

from ..gameBoard import GameBoard
from ..logger import Logger
from ..msgManager import MsgManager
from ..pokemon import Pokemon
from ..tools.tools import get_container


# 这个测试明明是单元测试不知为何放进项目里就跑不了了 气死我了
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

        if self.result == '我方胜利':
            print(f"{self.pkm1.name}胜利")
        else:
            print(f"{self.pkm1.name}战败！")

    def test发烟测试(self):
        self.pkm1.MAX_HP = 30
        self.pkm2.MAX_HP = 30
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 10)
        self.assertEqual(self.pkm2.hp, 0)

    def test连击(self):
        self.pkm1.skillGroup = ["连击"]

        # pkm2.skillGroup = ["反击50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 1000)

    def test反击对连击正常反应(self):
        self.pkm1.skillGroup = ["连击"]
        self.pkm2.skillGroup = ["反击50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 790)
        self.assertEqual(self.pkm2.hp, 1000)

    def test03(self):
        self.pkm2.skillGroup = ["愈合1"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 937)

    def test测试2个回血技能(self):
        self.pkm2.skillGroup = ["愈合1", "长生"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 944)

    def test毒攻击(self):
        self.pkm1.skillGroup = ["毒液50"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 870)

    def test毒攻击无法被反击(self):
        self.pkm1.skillGroup = ["毒液50", "连击", "尖角10"]
        self.pkm2.skillGroup = ["反击"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 870)

    def test连击会导致攻击力归零(self):
        self.pkm1.skillGroup = ["毒液50", "连击"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 1000)

    def test剧毒之体(self):
        self.pkm1.skillGroup = ["毒液50", "剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 740)

    def test剧毒之体无法造成普通伤害(self):
        self.pkm1.skillGroup = ["剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 1000)

    def test剧毒之体回合结束会强制解毒(self):
        self.pkm1.skillGroup = ["毒液50"]
        self.pkm2.skillGroup = ["剧毒之体"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 1000)
        self.assertEqual(self.pkm2.hp, 930)

    def test猛毒(self):
        self.pkm1.skillGroup = ["毒液50", "猛毒200"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 610)

    def test惜别(self):
        self.pkm1.skillGroup = ["惜别"]
        self.pkm1.MAX_HP = 10
        self.pkm2.skillGroup = ["惜别"]
        self.pkm2.MAX_HP = 10
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 1)
        self.assertEqual(self.pkm2.hp, -9)

    def test暴怒(self):
        self.pkm1.skillGroup = ["惜别", "暴怒1000"]
        self.pkm1.hp = 1000
        self.pkm2.skillGroup = ["惜别", "暴怒1000"]
        self.pkm2.hp = 1000
        self.gameBoard.init()
        self.pkm1.hp = 1
        self.pkm2.hp = 1
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 1)
        self.assertEqual(self.pkm2.hp, -208)

    def test诅咒(self):
        self.pkm1.skillGroup = ["诅咒100"]
        self.pkm2.skillGroup = ["利爪100"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 1000)
        self.assertEqual(self.pkm2.hp, 930)

    def test抗毒(self):
        self.pkm1.skillGroup = ["毒液100"]
        self.pkm2.skillGroup = ["抗毒80"]
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 948)

    def test野性(self):
        self.pkm1.skillGroup = ["尖角10", "野性100"]
        self.pkm2.skillGroup = []
        self.gameBoard.init()
        self.result = self.gameBoard.battle()
        self.assertEqual(self.pkm1.hp, 930)
        self.assertEqual(self.pkm2.hp, 720)

if __name__ == '__main__':
    unittest.main()


def data_init(pkm: Pokemon):
    pkm.ATK = 20
    pkm.DEF = 10
    pkm.MAX_HP = 1000
    pkm.skillGroup = []
