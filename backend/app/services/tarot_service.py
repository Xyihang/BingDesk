"""
塔罗牌服务 - 提供 1-12 个月的占卜功能
"""
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from loguru import logger
from app.services.ai_service import ai_service


MAJOR_ARCANA_DATA = {
    0: {
        "name": "愚者",
        "upright": "新的开始、冒险精神、天真无邪、信仰的飞跃、自由自在",
        "reversed": "鲁莽冲动、缺乏计划、冒险失败、犹豫不决、被欺骗"
    },
    1: {
        "name": "魔术师",
        "upright": "创造力、意志力、技巧、自信、资源充足、心想事成",
        "reversed": "操纵欺骗、能力不足、投机取巧、缺乏自信、浪费才能"
    },
    2: {
        "name": "女祭司",
        "upright": "直觉敏锐、内在智慧、神秘、潜意识、静待时机",
        "reversed": "忽视直觉、信息隐藏、表面化、过于理性、内心混乱"
    },
    3: {
        "name": "女皇",
        "upright": "丰饶富足、母性关怀、自然之美、感官享受、创造力旺盛",
        "reversed": "依赖他人、创造力匮乏、过度溺爱、忽视自我、物质困顿"
    },
    4: {
        "name": "皇帝",
        "upright": "权威领导、结构秩序、稳定掌控、父性保护、坚定意志",
        "reversed": "独裁专制、僵化固执、过度控制、权力滥用、缺乏弹性"
    },
    5: {
        "name": "教皇",
        "upright": "传统信仰、精神导师、道德指引、教育启迪、群体归属",
        "reversed": "叛逆反传统、打破常规、教条主义、个人信念、非主流"
    },
    6: {
        "name": "恋人",
        "upright": "爱情甜蜜、和谐关系、重要选择、价值观一致、心灵契合",
        "reversed": "感情失衡、错误选择、价值观冲突、分离背叛、内心矛盾"
    },
    7: {
        "name": "战车",
        "upright": "胜利前进、坚定决心、克服困难、自律自控、雄心壮志",
        "reversed": "失去方向、缺乏自制、挫败失败、攻击性、内心矛盾"
    },
    8: {
        "name": "力量",
        "upright": "内在力量、勇气耐心、温柔坚定、自我掌控、以柔克刚",
        "reversed": "自我怀疑、软弱无力、缺乏勇气、恐惧失控、暴力倾向"
    },
    9: {
        "name": "隐士",
        "upright": "内省独处、寻求真理、精神指引、谨慎审慎、智慧沉淀",
        "reversed": "孤立封闭、逃避现实、过度固执、拒绝帮助、内心恐惧"
    },
    10: {
        "name": "命运之轮",
        "upright": "命运转折、好运来临、因果循环、时机成熟、人生新阶段",
        "reversed": "抗拒变化、运势低迷、错失良机、打破恶性循环、命运考验"
    },
    11: {
        "name": "正义",
        "upright": "公平公正、因果报应、真相大白、法律事务、平衡决策",
        "reversed": "不公正待遇、偏见不公、逃避责任、法律纠纷、内心失衡"
    },
    12: {
        "name": "倒吊人",
        "upright": "换位思考、自我牺牲、静待转机、放下执念、灵性觉醒",
        "reversed": "无谓牺牲、拖延不决、自私利己、拒绝放手、徒劳无功"
    },
    13: {
        "name": "死神",
        "upright": "重大转变、结束旧阶段、告别过去、凤凰涅槃、深层蜕变",
        "reversed": "抗拒改变、停滞不前、恐惧结束、无法放手、拖延转型"
    },
    14: {
        "name": "节制",
        "upright": "平衡和谐、适度节制、耐心等待、自我疗愈、灵肉合一",
        "reversed": "失衡极端、过度放纵、缺乏耐心、内心冲突、目标模糊"
    },
    15: {
        "name": "恶魔",
        "upright": "物质束缚、欲望沉迷、执念成瘾、恐惧控制、阴暗面",
        "reversed": "打破束缚、重获自由、觉醒解脱、面对阴暗、克服成瘾"
    },
    16: {
        "name": "塔",
        "upright": "突变崩塌、真相揭露、结构瓦解、觉醒启示、根基动摇",
        "reversed": "避免灾难、延迟变故、恐惧改变、死守旧制、内在变革"
    },
    17: {
        "name": "星星",
        "upright": "希望光明、灵感涌现、内心宁静、精神信仰、美好愿景",
        "reversed": "失去希望、缺乏信心、创意枯竭、孤独绝望、脱离现实"
    },
    18: {
        "name": "月亮",
        "upright": "潜意识浮现、幻觉迷惑、内心不安、直觉梦境、隐藏真相",
        "reversed": "释放恐惧、拨云见日、走出迷茫、面对幻象、恢复清明"
    },
    19: {
        "name": "太阳",
        "upright": "成功喜悦、活力充沛、光明正大、自信乐观、万事顺遂",
        "reversed": "暂时低落、过度乐观、延迟的成功、缺乏热情、自我膨胀"
    },
    20: {
        "name": "审判",
        "upright": "觉醒重生、自我反省、接受召唤、因果结算、人生新篇",
        "reversed": "自我怀疑、拒绝反省、逃避审视、错过召唤、内疚自责"
    },
    21: {
        "name": "世界",
        "upright": "圆满完成、目标达成、整合统一、世界旅行、功德圆满",
        "reversed": "功亏一篑、缺乏收尾、未完成感、拖延闭合、视野局限"
    }
}

MINOR_ARCANA_DATA = {
    "权杖": {
        1:  {"name": "权杖王牌", "upright": "新计划启动、创造力爆发、灵感降临、行动力强、充满激情", "reversed": "计划延迟、创意受阻、缺乏动力、方向不明、能量分散"},
        2:  {"name": "权杖二", "upright": "规划未来、掌控全局、个人力量、长远眼光、决策时刻", "reversed": "缺乏规划、优柔寡断、注意力分散、计划受阻、视野狭窄"},
        3:  {"name": "权杖三", "upright": "拓展视野、前景广阔、领导能力、等待回报、海外机遇", "reversed": "延迟挫折、计划出错、缺乏远见、失望受挫、阻碍重重"},
        4:  {"name": "权杖四", "upright": "庆祝丰收、家庭和谐、稳定基础、里程碑达成、安居乐业", "reversed": "过渡期不安、缺乏归属、庆祝推迟、家庭冲突、基础不稳"},
        5:  {"name": "权杖五", "upright": "竞争冲突、意见分歧、激烈辩论、挑战考验、多方角力", "reversed": "冲突化解、达成共识、避免争端、内部纷争、妥协让步"},
        6:  {"name": "权杖六", "upright": "胜利凯旋、公众认可、自信满满、好消息传来、升职加薪", "reversed": "失败挫折、名声受损、缺乏认可、自负傲慢、跌落谷底"},
        7:  {"name": "权杖七", "upright": "坚守立场、捍卫权益、面对挑战、竞争中胜出、毅力考验", "reversed": "放弃抵抗、力不从心、被压垮、失去立场、退缩让步"},
        8:  {"name": "权杖八", "upright": "快速行动、消息传来、进展迅速、旅行出差、事态加速", "reversed": "延迟等待、计划放缓、内部混乱、消息延误、受阻停滞"},
        9:  {"name": "权杖九", "upright": "坚韧不拔、最后考验、伤痕累累但不放弃、警惕防备、积蓄力量", "reversed": "疲惫不堪、重负压身、偏执固执、防御过度、需要休息"},
        10: {"name": "权杖十", "upright": "重担在身、责任重大、过度劳累、接近完成、独自承担", "reversed": "放下重担、学会委托、减轻负担、推卸责任、不堪重负"},
        11: {"name": "权杖侍从", "upright": "热情洋溢、新消息、充满好奇、探索精神、学习新事物", "reversed": "幼稚冲动、方向不明、好消息延迟、缺乏耐心、注意力不集中"},
        12: {"name": "权杖骑士", "upright": "勇敢前进、冒险行动、充满冲劲、追求目标、势不可挡", "reversed": "鲁莽冲动、急躁冒进、计划不周、脾气暴躁、方向迷失"},
        13: {"name": "权杖王后", "upright": "自信独立、热情似火、直觉敏锐、魅力四射、温暖关怀", "reversed": "嫉妒猜忌、控制欲强、情绪不稳、自私自利、缺乏安全感"},
        14: {"name": "权杖国王", "upright": "领导才能、创业精神、魅力权威、远见卓识、大胆决策", "reversed": "独断专行、冲动霸道、不切实际、滥用权力、缺乏耐心"},
    },
    "圣杯": {
        1:  {"name": "圣杯王牌", "upright": "新感情萌芽、情感丰盈、直觉灵感、爱的种子、心灵满足", "reversed": "情感空虚、错失良机、感情受挫、压抑情感、创意枯竭"},
        2:  {"name": "圣杯二", "upright": "爱情结合、伙伴关系、心灵相通、和谐共处、合作愉快", "reversed": "感情失衡、分离破裂、信任危机、误解隔阂、自我封闭"},
        3:  {"name": "圣杯三", "upright": "欢庆聚会、友谊深厚、社交愉快、团队合作、好消息", "reversed": "社交过度、流言蜚语、孤立排挤、过度享乐、第三者的介入"},
        4:  {"name": "圣杯四", "upright": "冥想沉思、不满现状、错失机会、需要内省、情感倦怠", "reversed": "觉醒行动、抓住机会、摆脱冷漠、新动机、重新振作"},
        5:  {"name": "圣杯五", "upright": "失落悲伤、后悔自责、损失痛苦、但仍有希望、情感打击", "reversed": "走出伤痛、接受现实、向前看、自我疗愈、释怀放下"},
        6:  {"name": "圣杯六", "upright": "美好回忆、怀旧温情、童年时光、纯真快乐、重逢团聚", "reversed": "沉溺过去、不切实际的幻想、无法释怀、逃避现实、回忆束缚"},
        7:  {"name": "圣杯七", "upright": "幻想诱惑、白日梦境、多种选择、需要面对现实、物质诱惑", "reversed": "清醒决断、做出选择、抛弃幻想、面对现实、目标明确"},
        8:  {"name": "圣杯八", "upright": "放弃追寻、离开不再适合的、灵性探索、寻找更深意义、转身离开", "reversed": "漂泊不定、恐惧改变、留恋不舍、不敢离开、原地踏步"},
        9:  {"name": "圣杯九", "upright": "心想事成、美梦成真、物质精神双丰收、满足幸福、愿望达成", "reversed": "贪婪不知足、物质主义、空虚感、期望过高、不切实际"},
        10: {"name": "圣杯十", "upright": "家庭幸福、情感圆满、和谐美满、天伦之乐、爱的巅峰", "reversed": "家庭矛盾、关系破裂、完美表象下的裂痕、期望落空、不和谐"},
        11: {"name": "圣杯侍从", "upright": "浪漫多情、创意灵感、情感消息、温柔善良、学习艺术", "reversed": "情绪化、不成熟、情感幼稚、幻想不实、创意受阻"},
        12: {"name": "圣杯骑士", "upright": "浪漫追求、魅力迷人、跟随心声、理想主义、创意行动", "reversed": "虚假浪漫、不切实际、情绪操控、嫉妒心强、逃避承诺"},
        13: {"name": "圣杯王后", "upright": "温柔包容、直觉超强、情感丰富、慈悲怜悯、治愈力量", "reversed": "情绪不稳、过度敏感、依赖他人、情感操控、内心不安"},
        14: {"name": "圣杯国王", "upright": "情感成熟、智慧包容、外交才能、平衡情感与理性、内心平静", "reversed": "情感压抑、操控他人、冷酷无情、滥用情感、内心封闭"},
    },
    "宝剑": {
        1:  {"name": "宝剑王牌", "upright": "清晰思维、新想法突破、真相揭露、果断决策、正义胜利", "reversed": "思维混乱、误解冲突、滥用智力、信息有误、恶意攻击"},
        2:  {"name": "宝剑二", "upright": "艰难抉择、陷入僵局、回避决定、内心交战、需要权衡", "reversed": "信息过载、做出决定、释放压力、打破僵局、不再逃避"},
        3:  {"name": "宝剑三", "upright": "心碎悲伤、背叛伤害、情感痛苦、真相刺痛、深切悲痛", "reversed": "走出伤痛、释放痛苦、自我疗愈、原谅放手、恢复期"},
        4:  {"name": "宝剑四", "upright": "休息恢复、冥想沉思、养精蓄锐、暂时退隐、精神充电", "reversed": "倦怠不安、无法放松、急于行动、焦虑不安、恢复缓慢"},
        5:  {"name": "宝剑五", "upright": "冲突争端、赢了面子输了里子、不光彩的胜利、敌意纷争", "reversed": "和解妥协、放下争端、接受失败、旧怨化解、选择和平"},
        6:  {"name": "宝剑六", "upright": "逐渐恢复、离开困境、过渡期、渡过难关、寻求平静", "reversed": "旧伤未愈、无法逃离、困境持续、顽固不化、拒绝帮助"},
        7:  {"name": "宝剑七", "upright": "策略谋划、偷巧取巧、暗中行事、需要谨慎、小心陷阱", "reversed": "坦诚面对、放弃投机、悔过自新、阴谋败露、回归正途"},
        8:  {"name": "宝剑八", "upright": "自我限制、受困束缚、无力感、视野狭窄、被恐惧囚禁", "reversed": "重获自由、打破枷锁、看清真相、自我解放、恢复力量"},
        9:  {"name": "宝剑九", "upright": "焦虑噩梦、内心煎熬、精神痛苦、过度担忧、失眠不安", "reversed": "噩梦将醒、焦虑缓解、走出阴霾、希望初现、最坏的已过去"},
        10: {"name": "宝剑十", "upright": "彻底结束、痛苦终结、触底反弹、背叛伤害、黎明前的黑暗", "reversed": "无法放手、苟延残喘、拒绝结束、绝处逢生、缓慢恢复"},
        11: {"name": "宝剑侍从", "upright": "求知好学、警觉观察、新消息、思维敏捷、求真精神", "reversed": "流言蜚语、恶意中伤、思维幼稚、间谍行为、信息错误"},
        12: {"name": "宝剑骑士", "upright": "果决行动、思维敏捷、追求真相、快速决策、直言不讳", "reversed": "鲁莽言语、好斗攻击、计划不周、思维偏激、言辞伤人"},
        13: {"name": "宝剑王后", "upright": "独立理性、直觉敏锐、公正不阿、智慧洞察、边界清晰", "reversed": "冷酷无情、过于苛刻、情感疏离、尖酸刻薄、心肠狠毒"},
        14: {"name": "宝剑国王", "upright": "理性权威、法律智慧、公正判断、清晰思维、专业能力", "reversed": "滥用权力、冷酷操控、独裁专制、法律问题、不公正"},
    },
    "星币": {
        1:  {"name": "星币王牌", "upright": "新的财务机遇、物质丰收、踏实开始、播下种子、稳定根基", "reversed": "错失机会、财务不稳、缺乏规划、投资失误、物质匮乏"},
        2:  {"name": "星币二", "upright": "平衡多任务、灵活应变、财务决策、适应变化、优先排序", "reversed": "失衡混乱、无法兼顾、财务分散、过度承诺、计划不周"},
        3:  {"name": "星币三", "upright": "团队合作、技能精进、专业成长、工匠精神、项目进展", "reversed": "缺乏合作、工作平庸、技能不足、沟通不畅、目标模糊"},
        4:  {"name": "星币四", "upright": "财务安全、保守储蓄、控制资源、安全感、稳定积累", "reversed": "吝啬守财、过度贪婪、错失投资、物质执着、不愿分享"},
        5:  {"name": "星币五", "upright": "财务困难、贫穷匮乏、失业困境、需要帮助、冬天来临", "reversed": "困境改善、财务恢复、找到帮助、逐步好转、走出低谷"},
        6:  {"name": "星币六", "upright": "慷慨施予、公平分配、财富分享、慈善捐赠、收入丰厚", "reversed": "债务纠纷、不公平分配、吝啬小气、过度付出、财务不均"},
        7:  {"name": "星币七", "upright": "耐心等待、长期投资、辛勤耕耘、等待收获、评估进展", "reversed": "急于求成、投资失败、缺乏耐心、浪费精力、方向错误"},
        8:  {"name": "星币八", "upright": "专注技能、精雕细琢、勤奋努力、专业提升、学徒精神", "reversed": "缺乏目标、工作倦怠、技能停滞、敷衍了事、野心不足"},
        9:  {"name": "星币九", "upright": "财务独立、享受成果、物质丰盛、自律自足、品味生活", "reversed": "过度消费、孤独空虚、物质不满足、财务不安全、自我放纵"},
        10: {"name": "星币十", "upright": "家族财富、长期稳定、世代传承、财务自由、家庭繁荣", "reversed": "家族纠纷、遗产争端、财务不稳定、家庭矛盾、挥霍败家"},
        11: {"name": "星币侍从", "upright": "学习理财、新机会、踏实努力、研究探索、财务消息", "reversed": "缺乏进展、学习缓慢、不切实际、财务短视、懒惰懈怠"},
        12: {"name": "星币骑士", "upright": "踏实稳进、勤奋可靠、耐心坚持、目标明确、稳步推进", "reversed": "过于保守、停滞不前、缺乏冒险、固执己见、进展缓慢"},
        13: {"name": "星币王后", "upright": "务实能干、财务精通、舒适享受、母性温暖、安全感强", "reversed": "物质至上、嫉妒自私、过度关注外表、忽视精神、财务焦虑"},
        14: {"name": "星币国王", "upright": "财务成功、商业才能、稳重可靠、物质富裕、经验丰富", "reversed": "贪婪守财、固执保守、物质主义、风险厌恶、管理不善"},
    },
}

SUIT_ELEMENT = {
    "权杖": "火",
    "圣杯": "水",
    "宝剑": "风",
    "星币": "土"
}


class TarotCard:
    """塔罗牌类"""

    def __init__(self, name: str, number: int, suit: str = None, is_major: bool = True):
        self.name = name
        self.number = number
        self.suit = suit
        self.is_major = is_major
        self.upright_meaning = ""
        self.reversed_meaning = ""

    def to_dict(self, is_reversed: bool = False) -> Dict[str, Any]:
        return {
            "name": self.name,
            "number": self.number,
            "suit": self.suit,
            "is_major": self.is_major,
            "is_reversed": is_reversed,
            "meaning": self.reversed_meaning if is_reversed else self.upright_meaning,
            "upright_meaning": self.upright_meaning,
            "reversed_meaning": self.reversed_meaning,
            "position": "reversed" if is_reversed else "upright"
        }


class TarotService:
    """塔罗牌服务"""

    def __init__(self):
        self.deck = self._create_deck()

    def _create_deck(self) -> List[TarotCard]:
        """创建 78 张塔罗牌"""
        deck = []

        for num, data in MAJOR_ARCANA_DATA.items():
            card = TarotCard(data["name"], num, is_major=True)
            card.upright_meaning = data["upright"]
            card.reversed_meaning = data["reversed"]
            deck.append(card)

        for suit, cards_data in MINOR_ARCANA_DATA.items():
            for num, data in cards_data.items():
                card = TarotCard(data["name"], num, suit=suit, is_major=False)
                card.upright_meaning = data["upright"]
                card.reversed_meaning = data["reversed"]
                deck.append(card)

        return deck

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.deck)
        logger.info("塔罗牌已洗好")

    def draw_cards(self, count: int = 1, allow_reversed: bool = True) -> List[Dict[str, Any]]:
        if count > len(self.deck):
            raise ValueError(f"牌组中只有{len(self.deck)}张牌，无法抽取{count}张")

        self.shuffle()
        drawn_cards = []

        for i in range(count):
            card = self.deck[i]
            is_reversed = allow_reversed and random.random() < 0.3
            drawn_cards.append(card.to_dict(is_reversed))

        self.deck = self._create_deck()

        logger.info(f"抽取了{count}张塔罗牌")
        return drawn_cards

    async def monthly_reading(self, months: int = 1, question: Optional[str] = None) -> Dict[str, Any]:
        if months < 1 or months > 12:
            raise ValueError("月数必须在 1-12 之间")

        self.shuffle()

        monthly_cards = []
        for month in range(1, months + 1):
            card = self.deck[(month - 1) % len(self.deck)]
            is_reversed = random.random() < 0.3
            monthly_cards.append({
                "month": month,
                "card": card.to_dict(is_reversed)
            })

        upright_count = sum(1 for m in monthly_cards if not m["card"]["is_reversed"])
        overall_fortune = "吉" if upright_count > months / 2 else "凶"

        cards_for_ai = [m["card"] for m in monthly_cards]
        ai_interpretation = await ai_service.interpret_tarot_reading(
            reading_type="monthly",
            cards=cards_for_ai,
            question=question
        )

        result = {
            "period": f"{months}个月",
            "start_date": datetime.now().strftime("%Y-%m-%d"),
            "overall_fortune": overall_fortune,
            "monthly_readings": monthly_cards,
            "summary": self._generate_summary(monthly_cards, months),
            "ai_interpretation": ai_interpretation
        }

        logger.info(f"完成{months}个月的塔罗牌占卜（含AI解读）")
        return result

    def _generate_summary(self, monthly_cards: List[Dict], months: int) -> str:
        upright_count = sum(1 for m in monthly_cards if not m["card"]["is_reversed"])

        if upright_count >= months * 0.8:
            return "这段时间整体运势非常好，大部分时间都是正位牌，象征着顺利和成功。"
        elif upright_count >= months * 0.6:
            return "这段时间运势较好，虽然偶有波折，但总体趋势向上。"
        elif upright_count >= months * 0.4:
            return "这段时间运势平稳，有起有落，需要谨慎应对。"
        elif upright_count >= months * 0.2:
            return "这段时间挑战较多，逆位牌较多，建议保持耐心，谨慎行事。"
        else:
            return "这段时间运势较低，需要特别注意，避免重大决策，以守为主。"

    async def daily_reading(self) -> Dict[str, Any]:
        self.shuffle()
        card = self.draw_cards(1)[0]

        ai_interpretation = await ai_service.interpret_tarot_reading(
            reading_type="daily",
            cards=[card]
        )

        result = {
            "type": "daily",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "card": card,
            "ai_interpretation": ai_interpretation
        }

        logger.info(f"完成每日塔罗占卜（含AI解读）")
        return result

    async def celtic_cross_reading(self) -> Dict[str, Any]:
        spread_positions = [
            "当前状况",
            "阻碍/挑战",
            "潜意识",
            "过去",
            "未来",
            "自我",
            "环境",
            "希望/恐惧",
            "外部影响",
            "最终结果"
        ]

        self.shuffle()
        cards = self.draw_cards(10)

        ai_interpretation = await ai_service.interpret_tarot_reading(
            reading_type="celtic_cross",
            cards=cards
        )

        reading = {
            "spread": "凯尔特十字",
            "cards": [
                {"position": pos, "card": card}
                for pos, card in zip(spread_positions, cards)
            ],
            "summary": "凯尔特十字是一个全面的牌阵，揭示了问题的各个方面。",
            "ai_interpretation": ai_interpretation
        }

        logger.info(f"完成凯尔特十字牌阵占卜（含AI解读）")
        return reading
