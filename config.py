# config.py

import torch

# 路径配置
MODEL_PATH = "./model/qwen/Qwen2.5-7B-Instruct"
EXCEL_PATH = "./data/question.xlsx"
SAVE_JSON_PATH = "./output/pred_distribution.json"
SAVE_EXCEL_PATH = "./output/pred_distribution.xlsx"
SAVE_CSV_PATH = "./output/pred_distribution.csv"

# 设备配置
device = "cuda" if torch.cuda.is_available() else "cpu"

# 模型生成参数
GENERATION_CONFIG = {
    "max_new_tokens": 512,
    "do_sample": False,
    "temperature": 0.1,
    "pad_token_id": None  # 将在运行时设置
}
