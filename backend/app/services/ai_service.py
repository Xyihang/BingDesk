"""
AI 服务 - 使用智谱 GLM-4.7-Flash 模型解释塔罗牌
"""
import httpx
import asyncio
from typing import Optional
from loguru import logger

from app.config import settings


class AIService:
    """AI 服务类"""
    
    API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    MODEL = "glm-4-flash"  # 使用 GLM-4-Flash 模型（更稳定）
    FALLBACK_MODEL = "glm-4.7-flash"  # 备用模型
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # 重试间隔秒数（AI超时后等待5秒重试）
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def interpret_tarot_reading(
        self,
        reading_type: str,
        cards: list,
        question: Optional[str] = None
    ) -> str:
        """
        解释塔罗牌占卜结果
        
        Args:
            reading_type: 占卜类型（月度/每日/凯尔特十字）
            cards: 抽到的牌列表
            question: 用户问题（可选）
        
        Returns:
            AI 解释文本
        """
        # 构建提示词
        prompt = self._build_tarot_prompt(reading_type, cards, question)

        if not self.api_key:
            logger.warning("未配置 ZHIPU_API_KEY，使用本地备用解读")
            return self._get_fallback_interpretation(reading_type, cards)
        
        # 重试机制
        for attempt in range(self.MAX_RETRIES):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.API_URL,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}"
                        },
                        json={
                            "model": self.MODEL,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "你是一位专业的塔罗牌解读师，拥有深厚的塔罗牌知识和直觉解读能力。你的解读应该富有洞察力、温暖且富有启发性。请用中文回答。【重要规则】你的每一段解读的开头必须先用一句话明确说明当前整体运势/情况是好还是坏（例如：「整体运势偏吉」「当前情况较为不利」「运势向好」等），然后再展开详细解读。"
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            "temperature": 0.7,
                            "max_tokens": 2048
                        },
                        timeout=60.0
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    interpretation = data["choices"][0]["message"]["content"]
                    logger.info(f"AI 塔罗解读完成，类型: {reading_type}，尝试次数: {attempt + 1}")
                    return interpretation
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # 请求过于频繁，等待后重试
                    wait_time = self.RETRY_DELAY * (attempt + 1)
                    logger.warning(f"AI API 请求过于频繁（429），{wait_time}秒后重试（第{attempt + 1}次）...")
                    if attempt < self.MAX_RETRIES - 1:
                        await asyncio.sleep(wait_time)
                        continue
                logger.error(f"AI API HTTP 错误: {e.response.status_code} - {e.response.text}")
                break
            except Exception as e:
                logger.error(f"AI 解读失败（第{attempt + 1}次尝试）: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY)
                    continue
                break
        
        # 所有重试都失败，返回备用解读
        logger.warning(f"AI 解读在 {self.MAX_RETRIES} 次尝试后失败，使用备用解读")
        return self._get_fallback_interpretation(reading_type, cards)
    
    def _build_tarot_prompt(
        self,
        reading_type: str,
        cards: list,
        question: Optional[str]
    ) -> str:
        """构建塔罗牌解读提示词"""
        
        # 构建牌面信息
        cards_info = []
        for i, card in enumerate(cards, 1):
            position = "逆位" if card.get("is_reversed") else "正位"
            card_info = f"{i}. {card['name']}（{position}）- {card['meaning']}"
            cards_info.append(card_info)
        
        cards_text = "\n".join(cards_info)
        
        # 根据占卜类型构建不同的提示词
        if reading_type == "monthly":
            prompt = f"""请为以下月度塔罗牌占卜进行深度解读：

抽到的牌：
{cards_text}

{f"用户问题：{question}" if question else ""}

【重要要求】你的回复必须以一句话开头，明确说明这{len(cards)}个月的整体运势是好还是坏（例如：「整体运势偏吉，多数月份呈积极趋势」「整体运势不佳，需谨慎应对」），然后再展开详细解读。

请从以下几个方面进行解读：
1. 整体能量趋势分析
2. 每个月的具体指引和建议
3. 需要注意的关键时间点
4. 总体建议和行动指南

请用温暖、富有洞察力的语气，给出具体、实用的建议。"""

        elif reading_type == "daily":
            card = cards[0]
            position = "逆位" if card.get("is_reversed") else "正位"
            prompt = f"""请为今日塔罗牌进行解读：

今日牌：{card['name']}（{position}）
牌意：{card['meaning']}

【重要要求】你的回复必须以一句话开头，明确说明今日运势是好还是坏（例如：「今日运势偏吉」「今日运势不佳，需谨慎」「今日运势平稳」等），然后再展开详细解读。

请从以下几个方面解读：
1. 今日整体能量和主题
2. 今日可能遇到的机遇和挑战
3. 具体行动建议
4. 需要注意的事项

请给出温暖、实用的建议。"""

        elif reading_type == "celtic_cross":
            positions = [
                "当前状况", "阻碍/挑战", "潜意识", "过去", "未来", 
                "自我", "环境", "希望/恐惧", "外部影响", "最终结果"
            ]
            cards_with_positions = []
            for i, (card, position) in enumerate(zip(cards, positions), 1):
                card_position = "逆位" if card.get("is_reversed") else "正位"
                cards_with_positions.append(
                    f"{i}. {position}：{card['name']}（{card_position}）- {card['meaning']}"
                )
            
            prompt = f"""请为凯尔特十字牌阵进行深度解读：

牌阵位置及牌面：
{chr(10).join(cards_with_positions)}

【重要要求】你的回复必须以一句话开头，明确说明当前整体情况是好还是坏（例如：「整体情况偏吉，机遇大于挑战」「当前情况较为不利，需谨慎应对」），然后再展开详细解读。

请从以下几个方面解读：
1. 当前状况的核心分析
2. 面临的挑战和阻碍
3. 潜意识的影响
4. 过去的影响和未来的趋势
5. 自我认知和他人看法
6. 环境因素和外部影响
7. 希望与恐惧
8. 最终结果预测
9. 综合建议和行动指南

请给出全面、深入且实用的解读。"""
        
        else:
            prompt = f"""请解读以下塔罗牌：

{cards_text}

请给出整体解读和建议。"""
        
        return prompt
    
    def _get_fallback_interpretation(self, reading_type: str, cards: list) -> str:
        """获取备用解读（当 AI 服务失败时）"""
        header = "【当前使用的是备用解读】\n\nAI 服务暂时不可用（可能是访问量过大或网络问题），以下是基于牌面含义的基础解读：\n\n"
        
        if reading_type == "daily":
            card = cards[0]
            position = "逆位" if card.get("is_reversed") else "正位"
            content = f"今日抽到 {card['name']}（{position}），{card['meaning']}。请保持开放的心态，相信直觉的指引。"
            return header + content
        
        elif reading_type == "monthly":
            content = "月度运势显示，这段时间是自我成长和转变的重要时期。保持积极的心态，把握机遇，谨慎应对挑战。"
            return header + content
        
        elif reading_type == "celtic_cross":
            content = "凯尔特十字牌阵揭示了当前状况的多维度信息。建议你深入反思，倾听内心的声音，做出符合最高利益的选择。"
            return header + content
        
        content = "塔罗牌为你带来了重要的讯息。请静下心来，感受牌面传达的能量和指引。"
        return header + content


# 全局 AI 服务实例（密钥通过环境变量 ZHIPU_API_KEY 注入，避免提交到仓库）
ai_service = AIService(api_key=settings.ZHIPU_API_KEY or "")
