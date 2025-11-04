import requests
import json

# ========== 配置 ==========
API_KEY = "sk-f76caab6ef614fa9b6c368616a998022"          # 换成自己的
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL   = "deepseek-chat"   
# ==========================

def ask_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 1
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    if resp.status_code != 200:
        print("❌ 接口返回非 200：", resp.text)
        return "ERROR"
    try:
        return resp.json()["choices"][0]["message"]["content"].strip().upper()
    except (KeyError, IndexError) as e:
        print("❌ 解析失败，原始返回：", resp.text)
        return "ERROR"

# ---------------  中文题目池  ---------------
question_pool = [
    {
        "stem": "下列句子中，加点成语使用正确的一项是：",
        "choices": [
            "他迫不及待地打开电脑，准备继续打游戏。",
            "面对质疑，他不以为然地认真检讨。",
            "这篇文章美轮美奂地批评了社会现象。",
            "经过训练，小狗栩栩如生地坐下握手。"
        ]
    },
    {
        "stem": "小明的妈妈买了 6 个苹果，打算平均分给 3 个孩子，每人能分到几个？",
        "choices": ["2", "3", "6", "9"]
    },
    {
        "stem": "下列哪种做法可以有效节约家庭用电？",
        "choices": [
            "把空调温度调到 16 ℃",
            "离开房间时随手关灯",
            "电热水器 24 小时不断电",
            "把冰箱门打开给厨房降温"
        ]
    }
]
# ------------------------------------------

for idx, item in enumerate(question_pool, 1):
    stem = item["stem"]
    choices = item["choices"]
    choice_text = "\n".join([f"{chr(65+i)}) {c}" for i, c in enumerate(choices)])
    full_prompt = f"{stem}\n{choice_text}\n\n请只回答选项字母（A/B/C/D），不要输出其他内容。"

    print("=" * 60)
    print(f"[第 {idx} 题]")
    print(full_prompt)
    print("-" * 60)
    answer = ask_llm(full_prompt)
    print("模型答案 >>>", answer)
