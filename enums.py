from enum import Enum


# 触发器：buff触发的时机
class Trigger(Enum):
    ACTIVE = 0  # 某个触发器触发
    ATTACK = 1  # 攻击
    BE_ATTACK = 2  # 被攻击
    GET_ATK = 3  # 计算攻击时
    GET_DEF = 4  # 计算防御时
    GET_SPD = 5  # 计算速度时
    GET_HP = 6  # 计算生命时
    TURN_END = 7  # 回合结束时
    GET_LIFE_INC_SPD = 8  # 计算生命回复速度时
    DEAL_DAMAGE = 9 # 即将造成伤害


class DamageType(Enum):
    NORMAL = 0  # 普通伤害
    POISON = 1  # 毒伤害
    BURN = 2   # 燃烧伤害
    REAL = 3   # 真实伤害


class BuffTag(Enum):
    POISON_DEBUFF = 0  # 中毒类