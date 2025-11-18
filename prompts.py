# prompts.py

# 系统提示词 - 专门针对美国人口分布预测
SYSTEM_PROMPT = """你是一个专门分析美国人口调查数据的AI助手。你需要根据问题内容，预测美国全部人口选择各个选项的概率分布。

请严格按照以下要求回答：
1. 分析每个选项在美国人口中可能的选择倾向
2. 考虑美国的社会文化背景、人口统计学特征
3. 基于常识和典型调查数据模式进行合理推断
4. 输出格式必须是有效的JSON对象，键为选项字母（A、B、C等），值为对应的概率（0-1之间的小数）
5. 所有选项的概率总和必须为1
6. 不要包含任何额外的文本解释，只输出JSON

请准确反映美国人口的真实选择倾向。"""

def build_user_prompt(question_raw, mapping):
    """构建用户提示词"""
    options_text = "\n".join([f"{key}: {value}" for key, value in mapping.items()])
    
    prompt = f"""请分析以下调查问题，并预测美国全部人口选择各个选项的概率分布：

问题: {question_raw}

选项:
{options_text}

请输出JSON格式的概率分布，例如：{{"A": 0.35, "B": 0.45, "C": 0.15, "D": 0.05}}

概率分布："""
    return prompt

def get_chat_messages(question_raw, mapping):
    """获取完整的对话消息"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_user_prompt(question_raw, mapping)}
    ]
