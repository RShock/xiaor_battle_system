from xiaor_battle_system.enums import Trigger, DamageType


class MsgPack:
    def __init__(self) -> None:
        self.data = {}  # 数据

    def atk(self, atk) -> "MsgPack":
        self.data["atk"] = atk
        return self

    def defe(self, defe) -> "MsgPack":
        self.data["def"] = defe
        return self

    def spd(self, spd) -> "MsgPack":
        self.data["spd"] = spd
        return self

    def hp(self, hp) -> "MsgPack":
        self.data["hp"] = hp
        return self

    def life_inc_spd(self, spd) -> "MsgPack":
        self.data["life_inc_spd"] = spd
        return self

    def trigger_type(self, trigger_type) -> "MsgPack":
        if self.data.get("trigger_type") is not None:
            print("警告...")
        self.data["trigger_type"] = trigger_type
        return self

    def get_atk(self) -> int:
        return self.data["atk"]

    def change_atk(self, apply) -> None:
        self.data["atk"] = apply(self.get_atk())

    def get_def(self) -> int:
        return self.data["def"]

    def change_def(self, apply) -> None:
        self.data["def"] = apply(self.get_def())

    def get_hp(self) -> int:
        return self.data["hp"]

    def change_hp(self, apply) -> None:
        self.data["hp"] = apply(self.get_hp())

    def change_spd(self, apply) -> None:
        self.data["spd"] = apply(self.get_spd())

    def change_life_inc_spd(self, apply) -> None:
        self.data["life_inc_spd"] = apply(self.get_life_inc_spd())

    def get_spd(self) -> int:
        return self.data["spd"]

    def check_name(self, name) -> bool:
        return self.data["name"] == name

    def check_id(self, ID) -> bool:
        return self.data["our"].id == ID

    def is_our_owner(self) -> bool:
        return self.data["our"].id == self.data["buff_owner"].id

    def check_enemy_id(self, ID) -> bool:
        return self.data["enemy"].id == ID

    def is_enemy_owner(self) -> bool:
        return self.data["enemy"].id == self.data["buff_owner"].id

    def check_trigger(self, trigger) -> bool:
        return self.data["trigger_type"] == trigger

    def get_name(self) -> str:
        return self.data["name"]

    def get_allow(self) -> bool:
        return self.data.get("allow", True)

    def not_allow(self):
        self.data["allow"] = False

    def pack(self, pack) -> "MsgPack":
        self.data["pack"] = pack
        return self

    def get_pack(self):
        return self.data["pack"]

    def our(self, our: "Pokemon") -> "MsgPack":
        self.data["our"] = our
        self.data["name"] = our.name
        return self

    def enemy(self, enemy) -> "MsgPack":
        self.data["enemy"] = enemy
        return self

    def get_our(self):
        return self.data["our"]

    def get_enemy(self):
        return self.data["enemy"]

    def get_buff_name(self):
        return self.data["buff_name"]

    def buff_name(self, buff_name: str):
        self.data["buff_name"] = buff_name
        return self

    def buff_owner(self, buff_owner):
        self.data["buff_owner"] = buff_owner
        return self

    def owner(self):
        return self.data["buff_owner"]

    def check_owner(self, owner):
        return owner.id == self.data["buff_owner"].id

    def check_buff_name(self, buff_name: str):
        return self.data["buff_name"].__contains__(buff_name)

    # 开启穿透伤害（来自attack）
    def perfw(self) -> "MsgPack":
        self.data["perfw"] = True
        return self

    def is_perfw(self):
        return self.data.get("perfw", False)

    # 最终伤害系数（来自attack）
    def percent(self, num) -> "MsgPack":
        self.data["percent"] = num
        return self

    def get_percent(self) -> float:
        return self.data.get("percent", 100)

    # 受到的伤害（来自be_attack）
    def damage(self, num) -> "MsgPack":
        self.data["damage"] = int(num)
        return self

    def get_damage(self) -> int:
        return self.data["damage"]

    def get_life_inc_spd(self):
        return self.data["life_inc_spd"]

    def damage_type(self, damage_type):
        self.data["damage_type"] = damage_type
        return self

    def check_damage_type(self, type):
        return self.data["damage_type"] == type

    def __str__(self) -> str:
        return f"{self.data}"

    @staticmethod
    def builder() -> "MsgPack":
        return MsgPack()

    @staticmethod
    def get_atk_pack():
        return MsgPack.builder().trigger_type(Trigger.GET_ATK)

    @staticmethod
    def get_def_pack():
        return MsgPack.builder().trigger_type(Trigger.GET_DEF)

    @staticmethod
    def get_hp_pack():
        return MsgPack.builder().trigger_type(Trigger.GET_HP)

    @staticmethod
    def get_life_inc_spd_pack():
        return MsgPack.builder().trigger_type(Trigger.GET_LIFE_INC_SPD)

    @staticmethod
    def active_pack():
        return MsgPack.builder().trigger_type(Trigger.ACTIVE)

    @staticmethod
    def atk_pack():
        return MsgPack.builder().trigger_type(Trigger.ATTACK)

    @staticmethod
    def turn_end_pack():
        return MsgPack.builder().trigger_type(Trigger.TURN_END)

    @staticmethod
    def be_atk_pack():
        return MsgPack.builder().trigger_type(Trigger.BE_ATTACK)

    @staticmethod
    def damage_pack(our, enemy, num, type: DamageType = DamageType.NORMAL):
        return MsgPack.builder().trigger_type(Trigger.DEAL_DAMAGE).damage_type(type).damage(num).our(our).enemy(enemy)
