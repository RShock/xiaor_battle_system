from typing import List

from xiaor_battle_system.logger import Logger
from xiaor_battle_system.tools.stream import Stream
from xiaor_battle_system.buff import Buff
from xiaor_battle_system.msgPack import MsgPack
from xiaor_battle_system.enums import Trigger


class MsgManager:

    def __init__(self, logger: Logger):
        self.logger = logger
        self.buffs: list["Buff"] = []

    def register(self, buff):
        # self.logger.log(f"新增了buff:{buff}")
        self.buffs.append(buff)

    def send_msg(self, pack: MsgPack):
        def handle(buff, p):
            if pack.check_trigger(Trigger.ACTIVE) or not pack.check_trigger(Trigger.ATTACK):  # 这里可以添加需要check的类型，减少运算量
                buff.handle(p)
            else:
                _pack: MsgPack = MsgPack.active_pack().pack(p)
                self.send_msg(_pack)
                if _pack.get_allow():
                    buff.handle(p)
                else:
                    self.logger.log(f"{buff}被阻止了")

        # if pack.check_trigger(Trigger.ATTACK):
        #     self.logger.log(f"{pack.get_our()}atk")
        for buff in self.buffs:
            # self.logger.log(f"{buff} {pack.data['trigger_type']}")
            if not pack.check_trigger(buff.trigger):
                continue
            if not buff.check(pack):
                continue
            handle(buff, pack)
        # Stream(self.buffs).filter(
        #     lambda buff: pack.check_trigger(buff.trigger)
        # ).filter(
        #     lambda buff: buff.check(pack)
        # ).for_each(
        #     lambda buff: handle(buff, pack)
        # )

    # 回合结束时需要删除一些过期的buff
    def turn_end(self):
        tmp = []
        for buff in self.buffs:
            if buff.get_time() == 9999:
                tmp.append(buff)
                continue
            buff.time_pass()
            if buff.get_time() > 0:
                tmp.append(buff)
            elif buff.get_del_msg():
                self.logger.log(buff.get_del_msg())


        self.buffs = tmp

    def clean(self):
        self.buffs = []
        pass

    def get_buff_stream(self) -> Stream["Buff"]:
        return Stream(self.buffs)

#     # 很多逻辑是公共的，丢到这里来慢慢理清楚
#     def register_global_rules(self):
# # 受伤结算逻辑
# # 在造成伤害之后，敌方可能会有一些buff对其不同的伤害进行减伤，在这里统一处理
#         def handle_deal_damage(pack:MsgPack):
#             our = pack.get_our()
#             enemy = pack.get_enemy()
#             type = pack.get_damage_type()
#             # 我方增伤