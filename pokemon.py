from xiaor_battle_system.tools.stream import Stream
from xiaor_battle_system.logger import Logger
from xiaor_battle_system.msgManager import MsgManager
from xiaor_battle_system.msgPack import MsgPack
from xiaor_battle_system.tools.tools import get_num
from xiaor_battle_system.enums import Trigger, DamageType, BuffTag
from xiaor_battle_system.buff import new_buff
import uuid


class Pokemon:
    def __init__(self, msg_manager: MsgManager, logger: Logger):
        self.logger = logger
        self.msg_manager = msg_manager
        self.name = "÷生"
        self.ATK = 20
        self.DEF = 10
        self.HP = 100
        self.MAX_HP = 100
        self.SPD = 10  # 速度
        self.id = uuid.uuid1()
        self.lv = 1

        self.skillGroup = []

    def __str__(self) -> str:
        return f"【{self.name} 技能列表:{self.skillGroup}】"

    def read_pokemon_data(self):
        return

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
        # enemy.HP -= dmg
        pack2 = MsgPack.damage_pack(our, pack.owner(), dmg, DamageType.NORMAL)
        self.msg_manager.send_msg(pack2)
        enemy.HP -= pack2.get_damage()
        self.logger.log(f"{our.name}对{enemy.name}造成了{dmg}点伤害，{enemy.name}还有{enemy.HP}点血")
        if pack.check_trigger(Trigger.ATTACK):
            self.msg_manager.send_msg(MsgPack.be_atk_pack().our(enemy).enemy(our).damage(dmg))

        if enemy.HP <= 0:
            return True
        return False

    def init(self):
        def attack_handle(pack: MsgPack):
            Pokemon._attack(self, pack)
            return

        # 普攻每个人都有
        self.msg_manager.register(
            new_buff(self, Trigger.ATTACK)
            .name(f"{self.name}的【普攻】")
            .checker(is_self())
            .handler(attack_handle))

        Stream(self.skillGroup).for_each(lambda skill: self.init_skill(skill))
        self.HP = self.MAX_HP = self.get_hp()

    def attack(self, enemy: "Pokemon"):
        self.logger.log(f"{self.name}的攻击")
        self.msg_manager.send_msg(MsgPack.atk_pack().our(self).enemy(enemy))

    def get_atk(self):
        pack = MsgPack.get_atk_pack().atk(self.ATK).our(self)
        self.msg_manager.send_msg(pack)
        return pack.get_atk()

    def get_def(self):
        pack = MsgPack.get_def_pack().defe(self.DEF).our(self)
        self.msg_manager.send_msg(pack)
        return pack.get_def()

    def get_hp(self):
        pack = MsgPack.get_hp_pack().hp(self.HP).our(self)
        self.msg_manager.send_msg(pack)
        return pack.get_hp()

    def get_life_inc_spd(self):
        pack = MsgPack.get_life_inc_spd_pack().life_inc_spd(1).our(self)
        self.msg_manager.send_msg(pack)
        return pack.get_life_inc_spd()

    def init_skill(self, skill: str):
        num = get_num(skill)

        if skill.startswith("利爪"):
            self.logger.log(f"{self.name}的【利爪】发动了！攻击力增加了{num}点")
            change_atk(self, skill, add_num(num))
            return

        if skill.startswith("尖角"):
            self.logger.log(f"{self.name}的【尖角】发动了！攻击力增加了{num}点")
            change_atk(self, skill, add_num(num))
            return

        if skill.startswith("鳞片"):
            self.logger.log(f"{self.name}的【鳞片】发动了！防御力增加了{num}点")
            change_def(self, skill, add_num(num))
            return

        if skill.startswith("机敏"):
            self.logger.log(f"{self.name}的【机敏】发动了！速度增加了{num}点")

            self.msg_manager.register(
                new_buff(self, Trigger.GET_SPD).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_spd(add_num(num))))
            return

        if skill.startswith("肉质"):
            self.logger.log(f"{self.name}的【肉质】发动了！生命增加了{num}点")
            change_hp(self, skill, add_num(num))
            return

        if skill.startswith("毒液"):  # 攻击无法直接造成伤害，改为造成x%的真实伤害，持续2回合
            self.logger.log(f"{self.name}的【毒液】发动了！攻击方式变成{num}%持续2回合的真实伤害")

            def disable_normal_atk(pack):
                p: MsgPack = pack.get_pack()
                return p.check_name(self.name) and p.check_trigger(Trigger.ATTACK) and p.check_buff_name("【普攻】")

            def poison(pack: MsgPack):
                pack.not_allow()
                our: "Pokemon" = pack.get_pack().get_our()
                enemy: "Pokemon" = pack.get_pack().get_enemy()
                damage = our.get_atk() * num // 100  # 注意中毒计算的atk以施加毒的回合为准
                self.logger.log(f"{our.name}的攻击！{enemy.name}中毒了！受到每回合{damage}点的伤害（持续2回合）")

                def _(pack: MsgPack):
                    pack = MsgPack.damage_pack(our, pack.owner(), damage, DamageType.POISON)
                    self.msg_manager.send_msg(pack)
                    enemy.HP -= pack.get_damage()
                    self.logger.log(f"{enemy.name}中毒了，流失了{pack.get_damage()}点血量，当前hp{enemy.HP}")

                self.msg_manager.register(new_buff(self, Trigger.TURN_END).owner(enemy).name("【中毒】").
                                          tag(BuffTag.POISON_DEBUFF).handler(_).time(2))

            self.msg_manager.register(
                new_buff(self, Trigger.ACTIVE).name(skill).checker(disable_normal_atk).handler(
                    poison))
            return

        if skill.startswith("连击"):
            self.logger.log(f"{self.name}的【连击】发动了！攻击力归零，但是每回合攻击2次！")
            # 攻击力归零
            change_atk(self, skill, multi(0))

            # 每回合攻击2次
            def attack_handle(pack: MsgPack):
                self.logger.log(f"{pack.owner().name}追加连击")
                Pokemon._attack(self, pack)

            self.msg_manager.register(
                new_buff(self, Trigger.ATTACK).name("【普攻】").checker(is_self()).handler(attack_handle))
            return

        if skill.startswith("反击"):
            self.logger.log(f"{self.name}的【反击】发动了！受到攻击造成的伤害时会以真实伤害反击，反击伤害为正常攻击的{num}%")

            def _handle(pack: MsgPack):
                pack.perfw().percent(num)
                self.logger.log(f"{pack.owner().name}的反击！")
                Pokemon._attack(self, pack)

            self.msg_manager.register(
                new_buff(self, Trigger.BE_ATTACK).name("【反击】").checker(is_self()).handler(_handle))
            return

        if skill.startswith("不屈"):
            self.logger.log(f"{self.name}的【不屈】发动了！最大生命值增加{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.GET_HP).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_hp(add_percent(num))))
            return

        if skill.startswith("野性"):
            self.logger.log(f"{self.name}的【野性】发动了！最大攻击力增加{num}%")
            self.msg_manager.register(
                new_buff(self, Trigger.GET_ATK).name(skill).checker(is_self()).handler(
                    lambda pack: pack.change_atk(add_percent(num))))
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
                hp_gained = min(num * self.get_life_inc_spd(), self.MAX_HP - self.HP)
                self.HP += hp_gained
                self.logger.log(f"{pack.owner().name}的【愈合】发动了！回复了{hp_gained}点生命值({self.HP})")

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
            self.logger.log(f"{self.name}的【攻击成长】使其攻击增加了{self.lv - 1} * {num}点")
            change_atk(self, skill, add_num(num * (self.lv - 1)))
            return

        if skill.startswith("防御成长"):
            self.logger.log(f"{self.name}的【攻击成长】使其防御增加了{self.lv - 1} * {num}点")
            change_def(self, skill, add_num(num * (self.lv - 1)))
            return

        if skill.startswith("地区霸主"):
            self.logger.log(f"看起来这片区域的主人出现了...")
            change_atk(self, skill, multi(1.331))   # 相当于高3级的敌人(1.1^3)
            change_def(self, skill, multi(1.331))
            change_hp(self, skill, multi(1.331))
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
                self.msg_manager.get_buff_stream()\
                    .filter(lambda b: b.check_tag(BuffTag.POISON_DEBUFF))\
                    .filter(lambda b: b.check_owner(self))\
                    .for_each(lambda b: b.mark_as_delete(f"{self.name}解除了自己中的毒"))

            self.msg_manager.register(
                new_buff(self, Trigger.TURN_END).name("剧毒之体解毒").handler(lambda pack: del_poison_buff(pack)))

            return

        raise Exception(f"不认识的技能：{skill}")


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


def add_num(num):
    def _(origin):
        return origin + num

    return _


def multi(num):
    def _(origin):
        return int(origin * num)

    return _


def add_percent(num):
    def _(origin):
        return int(origin * (1 + num / 100))

    return _


def change_atk(self: Pokemon, skill, func):
    self.msg_manager.register(
        new_buff(self, Trigger.GET_ATK).name(skill).checker(is_self()).handler(
            lambda pack: pack.change_atk(func)))


def change_def(self, skill, func):
    self.msg_manager.register(
        new_buff(self, Trigger.GET_DEF).name(skill).checker(is_self()).handler(
            lambda pack: pack.change_def(func)))


def change_hp(self, skill, func):
    self.msg_manager.register(
        new_buff(self, Trigger.GET_HP).name(skill).checker(is_self()).handler(
            lambda pack: pack.change_hp(func)))
