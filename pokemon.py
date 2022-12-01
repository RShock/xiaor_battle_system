import math
import random

from .tools.stream import Stream
from .logger import Logger
from .msgManager import MsgManager
from .msgPack import MsgPack
from .tools.tools import get_num
from .enums import Trigger, DamageType, BuffTag, BuffPriority
from .buff import new_buff
import uuid

from .gameBoard import GameBoard


class Pokemon:
    def __init__(self, msg_manager: MsgManager, logger: Logger, game_board: GameBoard):
        self.gameBoard: GameBoard = game_board
        self.logger: Logger = logger
        self.msg_manager: MsgManager = msg_manager
        self.name = "÷生"
        self.ATK = 20
        self.DEF = 10
        self.hp = 100  # 血量（随着战斗变化）
        self.MAX_HP = 100  # 血量上限
        self.SPD = 10  # 速度
        self.id = uuid.uuid1()
        self.lv = 1
        # 这两个外部不需要赋值
        self.CRIT = 0  # 暴击率
        self.CSD = 2  # 暴击伤害

        self.skillGroup = []
        self.tag: list[str] = []  # 存放战斗时的一些buff

    def __str__(self) -> str:
        return f"【{self.name} 技能列表:{self.skillGroup}】"

    def __eq__(self, other):
        return self.id == other.id

    def read_pokemon_data(self):
        return

    def add_tag(self, tag: str):
        self.tag.append(tag)

    def remove_tag(self, tag: str):
        self.tag.remove(tag)

    def check_tag(self, tag: str):
        return tag in self.tag

    @staticmethod
    def _attack(self, pack: MsgPack):
        our = pack.get_our()
        enemy = pack.get_enemy()
        # 基本伤害公式
        if pack.is_perfw():  # 结算穿透伤害
            tmp = our.get_atk()
        else:
            tmp = our.get_atk() - enemy.get_def()
        if tmp < 0:
            tmp = 0
        percent = pack.get_percent()
        dmg = tmp * percent // 100

        # 发送即将造成伤害的包，以此计算属性增减伤等属性
        pack2 = MsgPack.damage_pack(our, pack.get_enemy(), dmg, DamageType.NORMAL)
        self.msg_manager.send_msg(pack2)
        dmg = pack2.get_damage()
        # 暴击结算（暂且放在外面,后面复杂了可能移动到buff系统里面）
        crit = False
        if random.random() < self.get_crit()/100:
            dmg = round(dmg * self.get_csd())
            crit = True
        enemy.hp = round(enemy.hp - dmg, 1)
        if crit:
            msg = f"暴击💥！{our.name}对{enemy.name}造成{dmg}点伤害，{enemy.name}hp:{enemy.hp}"
        else:
            msg = f"{our.name}对{enemy.name}造成{dmg}点伤害，{enemy.name}hp:{enemy.hp}"
        self.logger.log(msg)
        # 被打了，再发一个包
        pack3 = MsgPack.taken_damage_pack(pack.get_enemy(), our, pack2.get_damage(), Trigger.ATTACK, DamageType.NORMAL)
        self.msg_manager.send_msg(pack3)

        if enemy.hp <= 0:
            return True
        return False

    def init(self):
        # 为每个角色注册普攻技能 普攻每个人都有
        def attack_handle(pack: MsgPack):
            Pokemon._attack(self, pack)
            return

        self.msg_manager.register(
            new_buff(self, Trigger.ATTACK)
            .name(f"{self.name}的【普攻】")
            .checker(is_self())
            .handler(attack_handle))

        # 等级对数值的影响（每升1级 1.1倍）
        self.change_atk("等级", multi_eval(lambda: math.pow(1.1, self.get_lv() - 1)))
        self.change_def("等级", multi_eval(lambda: math.pow(1.1, self.get_lv() - 1)))
        self.change_hp("等级", multi_eval(lambda: math.pow(1.1, self.get_lv() - 1)))

        # 为每个角色注册自己的独有技能
        Stream(self.skillGroup).for_each(lambda skill: self.init_skill(skill))
        self.hp = self.get_max_hp()  # 初始化生命值为最大生命值

    def attack(self, enemy: "Pokemon"):
        self.logger.log(f"{self.name}的攻击")
        self.msg_manager.send_msg(MsgPack.atk_pack().our(self).enemy(enemy))

    def get_atk(self):
        pack = MsgPack.get_atk_pack().atk(self.ATK).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_atk())

    def get_def(self):
        pack = MsgPack.get_def_pack().defe(self.DEF).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_def())

    def get_lv(self):
        pack = MsgPack.get_lv_pack().lv(self.lv).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_lv())

    def get_max_hp(self):
        pack = MsgPack.get_max_hp_pack().hp(self.MAX_HP).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_max_hp())

    def get_spd(self):
        pack = MsgPack.get_spd_pack().spd(self.SPD).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_spd())

    def get_life_inc_spd(self):
        pack = MsgPack.get_life_inc_spd_pack().life_inc_spd(1).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_life_inc_spd())


    # 获取当前暴击率
    def get_crit(self):
        pack = MsgPack.get_crit_pack().crit(self.CRIT).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_crit())

    def get_csd(self):
        pack = MsgPack.get_csd_pack().csd(self.CSD).our(self)
        self.msg_manager.send_msg(pack)
        return int(pack.get_csd())

    def init_skill(self, skill: str):
        num = get_num(skill)

        if skill.startswith("利爪"):
            self.logger.log(f"{self.name}的【利爪】发动了！攻击力增加了{num}%")
            self.change_atk(skill, add_percent(num))
            return

        if skill.startswith("尖角"):
            self.logger.log(f"{self.name}的【尖角】发动了！攻击力增加了{num}点")
            self.change_atk(skill, add_num(num))
            return

        if skill.startswith("鳞片"):
            self.logger.log(f"{self.name}的【鳞片】发动了！防御力增加了{num}点")
            self.change_def(skill, add_num(num))
            return

        if skill.startswith("机敏"):
            self.logger.log(f"{self.name}的【机敏】发动了！速度增加了{num}点")
            self.change_spd(skill, add_num(num))
            return

        if skill.startswith("肉质"):
            self.logger.log(f"{self.name}的【肉质】发动了！生命增加了{num}点")
            self.change_hp(skill, add_num(num))
            return

        if skill.startswith("毒液"):  # 攻击无法直接造成伤害，改为造成x%的真实伤害，持续2回合
            self.logger.log(f"{self.name}的【毒液】发动了！攻击方式变成{num}%持续2回合的真实伤害")

            def disable_normal_atk(pack: MsgPack):
                p: MsgPack = pack.get_pack()
                return pack.get_owner() == p.get_owner() and p.check_trigger(Trigger.ATTACK) and p.check_buff_name(
                    "【普攻】")

            def poison(pack: MsgPack):
                pack.not_allow()
                our: "Pokemon" = pack.get_pack().get_our()
                enemy: "Pokemon" = pack.get_pack().get_enemy()
                damage = our.get_atk() * num // 100  # 注意中毒计算的atk以施加毒的回合为准
                self.logger.log(f"{our.name}的攻击！{enemy.name}中毒了！受到每回合{damage}点的伤害（持续2回合）")

                def _(pack: MsgPack):
                    # 发送即将造成伤害的包，以此计算属性增减伤等属性
                    pack2 = MsgPack.damage_pack(our, pack.get_owner(), damage, DamageType.POISON)
                    self.msg_manager.send_msg(pack2)
                    enemy.hp -= pack2.get_damage()
                    # 受到伤害后发包，死亡结算也在这里进行，所以就算是无源伤害（被毒死）也得发
                    MsgPack.taken_damage_pack(pack.get_owner(), None, pack2.get_damage(), Trigger.TURN_END,
                                              DamageType.POISON)
                    self.logger.log(f"{enemy.name}中毒了，流失了{pack2.get_damage()}点血量，当前hp{enemy.hp}")

                # 毒buff会直接挂载在敌人身上（无源伤害），taken_damage_pack包的enemy参数会被设为空
                # 哪怕我方有无法造成伤害的debuff，毒也能正常工作
                self.msg_manager.register(new_buff(self, Trigger.TURN_END).owner(enemy).name("【中毒】").
                                          tag(BuffTag.POISON_DEBUFF).handler(_).time(2))

            self.msg_manager.register(
                new_buff(self, Trigger.ACTIVE).name(skill).checker(disable_normal_atk).handler(
                    poison))
            return

        if skill.startswith("连击"):
            self.logger.log(f"{self.name}的【连击】发动了！攻击力归零，但是每回合攻击2次！")
            # 攻击力归零
            self.change_atk(skill, multi(0))

            # 每回合攻击2次
            def attack_handle(pack: MsgPack):
                self.logger.log(f"{pack.get_owner().name}追加连击")
                Pokemon._attack(self, pack)

            self.msg_manager.register(
                new_buff(self, Trigger.ATTACK).name("【普攻】").checker(is_self()).handler(attack_handle))
            return

        if skill.startswith("反击"):
            self.logger.log(f"{self.name}的【反击】发动了！受到攻击造成的伤害时会以真实伤害反击，反击伤害为正常攻击的{num}%")

            def _handle(pack: MsgPack):
                pack.perfw().percent(num)
                self.logger.log(f"{pack.get_owner().name}的反击！")
                Pokemon._attack(self, pack)

            self.msg_manager.register(
                new_buff(self, Trigger.TAKEN_DAMAGE).name("【反击】").checker(is_self())
                .checker(lambda pack: pack.check_damage_taken_trigger(Trigger.ATTACK)).handler(_handle))
            return

        if skill.startswith("不屈"):
            self.logger.log(f"{self.name}的【不屈】发动了！最大生命值增加{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.GET_HP).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_max_hp(add_percent(num))))
            return

        if skill.startswith("野性"):
            self.logger.log(f"{self.name}的【野性】发动了！最终伤害增加+{num}%")
            self.change_damage("野性", add_percent(num))
            return
        # todo 尖牙
        if skill.startswith("尖牙"):
            self.logger.log(f"{self.name}的【尖牙】发动了！暴击率+{num}%")
            self.change_crit("尖牙", add_num(num))
            return
        if skill.startswith("坚韧"):
            self.logger.log(f"{self.name}的【坚韧】发动了！最大防御力增加{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.GET_DEF).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_def(add_percent(num))))
            return

        if skill.startswith("愈合"):
            self.logger.log(f"{self.name}的【愈合】发动了！每回合回复{num}点生命值")

            def gain_hp(pack):
                hp_gained = min(num * self.get_life_inc_spd(), self.MAX_HP - self.hp)
                self.hp += hp_gained
                self.logger.log(f"{pack.get_owner().name}的【愈合】发动了！回复了{hp_gained}点生命值({self.hp})")

            self.msg_manager.register(
                new_buff(self, Trigger.TURN_END).name(skill).handler(gain_hp))
            return

        if skill.startswith("长生"):
            self.logger.log(f"{self.name}的【长生】发动了！生命回复速+{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.GET_LIFE_INC_SPD).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_life_inc_spd(multi(2))))
            return

        if skill.startswith("攻击成长"):
            self.logger.log(f"{self.name}的【攻击成长】使其攻击增加了{self.get_lv() - 1} * {num}点")
            self.change_atk(skill, add_num(num * (self.get_lv() - 1)))
            return

        if skill.startswith("防御成长"):
            self.logger.log(f"{self.name}的【防御成长】使其防御增加了{self.get_lv() - 1} * {num}点")
            self.change_def(skill, add_num(num * (self.get_lv() - 1)))
            return

        if skill.startswith("地区霸主"):
            self.logger.log(f"看起来这片区域的主人出现了...")
            self.change_lv(skill, add_num(1))
            # 技能槽位的增加目前仅仅存在于设定之中，怪物的技能数量其实是填表决定的，并非靠这个技能获得
            return

        if skill.startswith("剧毒之体"):
            self.logger.log(f"{self.name}似乎很擅长用毒")
            # 造成的毒伤害加倍 非毒伤害归零
            self.msg_manager.register(
                new_buff(self, Trigger.DEAL_DAMAGE).name(skill).checker(is_self()).handler(
                    lambda pack: pack.damage(
                        pack.get_damage() * 2 if pack.check_damage_type(DamageType.POISON) else 0)))

            # 回合结束时，强制解除所有中毒debuff

            def del_poison_buff(pack: MsgPack):
                self.msg_manager.get_buff_stream() \
                    .filter(lambda b: b.check_tag(BuffTag.POISON_DEBUFF)) \
                    .filter(lambda b: b.check_owner(self)) \
                    .for_each(lambda b: b.mark_as_delete(f"{self.name}解除了自己中的毒"))

            self.msg_manager.register(
                new_buff(self, Trigger.TURN_END).name("剧毒之体解毒").handler(lambda pack: del_poison_buff(pack)))

            return

        if skill.startswith("猛毒"):
            self.logger.log(f"{self.name}的猛毒发动了！毒伤害增加了{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.DEAL_DAMAGE).name(skill).checker(is_self())
                .checker(lambda pack: pack.check_damage_type(DamageType.POISON))
                .handler(lambda pack: pack.damage(pack.get_damage() * (100 + num) / 100)))
            return

        if skill.startswith("暴怒"):
            self.logger.log(f"{self.name}的暴怒发动了！受伤越重伤害越高，最高增加{num}%！")

            def change_atk_by_anger(pack: MsgPack):
                our: Pokemon = pack.get_our()
                max_hp = our.get_max_hp()
                hp = pack.get_our().hp
                percent = (1 - hp / max_hp) * num
                pack.change_atk(add_percent(percent))

            self.msg_manager.register(
                new_buff(self, Trigger.GET_ATK).name(skill).checker(is_self()).handler(
                    lambda pack: change_atk_by_anger(pack)))
            return

        if skill.startswith("惜别"):
            TAG = "惜别已使用"

            def tear(pack: MsgPack):
                our: Pokemon = pack.get_our()
                if not our.check_tag(TAG) and our.hp <= 0:
                    self.logger.log(f"濒死之际，一股意志支撑{our.name}又活了过来")
                    our.hp = 1
                    our.add_tag(TAG)

            self.msg_manager.register(
                new_buff(self, Trigger.TAKEN_DAMAGE).name("惜别").checker(is_enemy()).handler(
                    lambda pack: tear(pack)
                )
            )
            return

        if skill.startswith("诅咒"):
            self.logger.log(f"{self.name}凝视着敌人，让它攻击力下降了{num}%")
            enemy = self.gameBoard.get_enemy()
            self.msg_manager.register(
                new_buff(self, Trigger.GET_ATK).name(skill).priority(BuffPriority.CHANGE_ATK_LAST)
                .checker(lambda pack: pack.get_our() == enemy).handler(
                    lambda pack: pack.change_atk(add_percent(-num))))
            return

        if skill.startswith("抗毒"):
            self.logger.log(f"{self.name}对毒有抵抗力，受到毒伤害降低{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.DEAL_DAMAGE).name("抗毒").checker(is_enemy())
                .priority(BuffPriority.CHANGE_DAMAGE_LAST)
                .checker(lambda pack: pack.check_damage_type(DamageType.POISON))
                .handler(lambda pack: pack.damage(pack.get_damage() * (100 - num) / 100)))
            return
        raise Exception(f"不认识的技能：{skill}")

    def change_atk(self: "Pokemon", skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_ATK).name(skill).checker(is_self()).handler(
                lambda pack: pack.change_atk(func)))

    def change_def(self: "Pokemon", skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_DEF).name(skill).checker(is_self()).handler(
                lambda pack: pack.change_def(func)))

    def change_hp(self: "Pokemon", skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_HP).name(skill).checker(is_self()).handler(
                lambda pack: pack.change_max_hp(func)))

    def change_lv(self: "Pokemon", skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_LV).name(skill).checker(is_self()).handler(
                lambda pack: pack.change_lv(func)))

    def change_damage(self, skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.DEAL_DAMAGE).name(skill).checker(is_self())
            .handler(lambda pack: pack.change_damage(func)))

    def change_spd(self, skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_SPD).name(skill).checker(is_self())
            .handler(lambda pack: pack.change_spd(func)))

    def change_crit(self, skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_CRIT).name(skill).checker(is_self())
            .handler(lambda pack: pack.change_crit(func)))

    def change_csd(self, skill, func):
        self.msg_manager.register(
            new_buff(self, Trigger.GET_CSD).name(skill).checker(is_self())
            .handler(lambda pack: pack.change_crit(func)))


#
# def check_id(name):
#     def _(pack: MsgPack):
#         return pack.check_name(name)
#
#     return _

def is_self():
    def _(pack: MsgPack):
        return pack.is_our_owner()

    return _


def is_enemy():
    def _(pack: MsgPack):
        return pack.is_enemy_owner()

    return _


def is_pokemon(p: Pokemon):
    def _(pack: MsgPack):
        return pack.get_our() == p

    return _


def add_num(num):
    def _(origin):
        return origin + num

    return _


def add_num_eval(func):
    def _(origin):
        return origin + func()

    return _


def multi(num):
    def _(origin):
        return origin * num

    return _


def multi_eval(func):
    def _(origin):
        return origin * func()

    return _


def add_percent(num):
    def _(origin):
        return origin * (1 + num / 100)

    return _
