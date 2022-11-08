from lagom import Container

from xiaor_battle_system.logger import Logger
from xiaor_battle_system.msgManager import MsgManager
from xiaor_battle_system.msgPack import MsgPack
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xiaor_battle_system.pokemon import Pokemon


class GameBoard:
    def __init__(self, logger: Logger, msg_manager: MsgManager):
        self.enemy = None
        self.our = None
        self.msg_manager = msg_manager
        self.logger = logger
        self.TURN_LIMIT = 50

    def add_ally(self, pokemon: "Pokemon"):
        self.our = pokemon

    def add_enemy(self, pokemon: "Pokemon"):
        self.enemy = pokemon

    def init(self):
        self.our.init()
        self.enemy.init()

    def get_enemy(self) -> "Pokemon":
        return self.enemy

    def battle(self):
        # 第一步比较速度
        our: "Pokemon" = self.our
        enemy: "Pokemon" = self.enemy
        cnt = 1

        while True:
            self.logger.log(f"第{cnt}回合")
            if our.SPD >= enemy.SPD:
                our.attack(enemy)
                if self.death_check(our, enemy):
                    return
                enemy.attack(our)
                if self.death_check(our, enemy):
                    return
            else:
                enemy.attack(our)
                if self.death_check(our, enemy):
                    return
                our.attack(enemy)
                if self.death_check(our, enemy):
                    return
            self.msg_manager.send_msg(MsgPack.turn_end_pack())
            self.msg_manager.turn_end()
            if self.death_check(our, enemy):
                return
            cnt += 1
            if cnt >= self.TURN_LIMIT:
                self.logger.log(f"{self.our.name}和{self.enemy.name}永远战斗在了一起...")
                return False

    def print_log(self):
        self.logger.print_log()

    def death_check(self, our: "Pokemon", enemy: "Pokemon") -> bool:
        # 死亡结算
        if our.hp <= 0:
            self.logger.log(f"{self.our.name}倒下了...")
            return True
        if enemy.hp <= 0:
            self.logger.log(f"{self.our.name}一口将{self.enemy.name}吞掉！")
            return True
        return False
