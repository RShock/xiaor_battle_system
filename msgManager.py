
from .logger import Logger
from .tools.stream import Stream
from .buff import Buff
from .msgPack import MsgPack
from .enums import Trigger


class MsgManager:

    def __init__(self, logger: Logger):
        self.logger = logger
        self.buffs: dict[Trigger, list["Buff"]] = {}

    def register(self, buff: Buff):
        # self.logger.log(f"新增了buff:{buff}")
        if buff.trigger not in self.buffs:
            self.buffs[buff.trigger] = []
        self.buffs[buff.trigger].append(buff)
        self.buffs[buff.trigger] = sorted(self.buffs[buff.trigger], key=lambda b: b.get_priority())

    def send_msg(self, pack: MsgPack):
        def handle(buff, p):
            # 打断机制：一个已经附加的buff可能会因为其他buff无法执行（例如毒液攻击会取代普通攻击，这使得普通攻击无法执行）
            # 也就是简化的扭曲机制，把普攻扭曲成了毒液攻击，但是没法做到非常细节的扭曲。
            # 目前只有攻击会被打断，如果每个buff都需要判断是否打断，游戏速度会变慢很多
            if pack.check_trigger(Trigger.ACTIVE) or not pack.check_trigger(Trigger.ATTACK):  # 这里可以添加需要check的类型，减少运算量
                DEBUG = None
                if DEBUG:
                    if pack.check_trigger(DEBUG):
                        self.logger.debug_log(f"before{p.get_def()}")

                buff.handle(p)
                if DEBUG:
                    if pack.check_trigger(DEBUG):
                        self.logger.debug_log(f"after{p.get_def()}")

            else:
                _pack: MsgPack = MsgPack.active_pack().pack(p)
                self.send_msg(_pack)
                if _pack.get_allow():
                    buff.handle(p)
                # else:
                #     self.logger.log(f"{buff}被阻止了")

        # if pack.check_trigger(Trigger.ATTACK):
        #     self.logger.log(f"{pack.get_our()}atk")

        trigger = pack.data["trigger_type"]
        if trigger not in self.buffs:
            return
        for buff in self.buffs[trigger]:
            # self.logger.log(f"{buff} {pack.data['trigger_type']}")
            if not pack.check_trigger(buff.trigger):
                continue
            if not buff.check(pack):
                continue
            handle(buff, pack)

    # 回合结束时需要删除一些过期的buff
    def turn_end(self):
        for k, buff_list in self.buffs.items():
            tmp = []
            for buff in buff_list:
                if buff.get_time() == 9999:
                    tmp.append(buff)
                    continue
                buff.time_pass()
                if buff.get_time() > 0:
                    tmp.append(buff)
                elif buff.get_del_msg():
                    self.logger.log(buff.get_del_msg())
            self.buffs[k] = tmp

    def clean(self):
        self.buffs = {}
        pass

    def get_buff_stream(self) -> Stream["Buff"]:
        return Stream(self.buffs).flat_map(lambda k: Stream(self.buffs[k]))

#     # 很多逻辑是公共的，丢到这里来慢慢理清楚
#     def register_global_rules(self):
# # 受伤结算逻辑
# # 在造成伤害之后，敌方可能会有一些buff对其不同的伤害进行减伤，在这里统一处理
#         def handle_deal_damage(pack:MsgPack):
#             our = pack.get_our()
#             enemy = pack.get_enemy()
#             type = pack.get_damage_type()
#             # 我方增伤
