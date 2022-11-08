from enum import Enum, IntEnum


# 触发器：buff触发的时机
class Trigger(Enum):
    ACTIVE = 0  # 某个触发器触发
    ATTACK = 1  # 攻击
    # BE_ATTACK = 2  # 被攻击
    GET_ATK = 3  # 计算攻击时
    GET_DEF = 4  # 计算防御时
    GET_SPD = 5  # 计算速度时
    GET_HP = 6  # 计算生命时
    TURN_END = 7  # 回合结束时
    GET_LIFE_INC_SPD = 8  # 计算生命回复速度时
    DEAL_DAMAGE = 9  # 即将造成伤害（约定如果是体力流失，owner是空的）
    TAKEN_DAMAGE = 10  # 受到伤害（包括体力流失，一般用于计算死亡事件）


class DamageType(Enum):
    NORMAL = 0  # 普通伤害
    POISON = 1  # 毒伤害
    BURN = 2  # 燃烧伤害
    REAL = 3  # 真实伤害


class BuffTag(Enum):
    POISON_DEBUFF = 0  # 中毒类


class BuffPriority(IntEnum):
    NORMAL = 1
    CHANGE_ATK_NORMAL = 1  # 修改攻击力，标准优先级
    CHANGE_ATK_LAST = 2  # 修改攻击力，最后优先级
    CHANGE_DAMAGE_LAST = 2   # 修改伤害，最后优先级

