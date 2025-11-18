# data_utils.py

import json
import pandas as pd
from config import SAVE_EXCEL_PATH, SAVE_CSV_PATH

def load_data(excel_path):
    """加载Excel数据"""
    print("正在读取问题数据...")
    df = pd.read_excel(excel_path, sheet_name="Sheet1", engine="openpyxl")
    return df

def save_to_json(results, json_path):
    """保存为JSON格式"""
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"JSON保存完成 -> {json_path}")

def save_to_excel(results, original_df):
    """保存为Excel格式"""
    rows = []
    for qid, dist in results.items():
        row_data = original_df[original_df['input_id']==qid].iloc[0]
        row = {
            'input_id': qid,
            'qkey': row_data['qkey'],  # 添加qkey列
            'question_raw': row_data['question_raw']
        }
        for option, prob in dist.items():
            row[f'pred_{option}'] = prob
        rows.append(row)
    
    df_output = pd.DataFrame(rows)
    df_output.to_excel(SAVE_EXCEL_PATH, index=False, engine='openpyxl')
    print(f"Excel保存完成 -> {SAVE_EXCEL_PATH}")

def save_to_csv(results, original_df):
    """保存为CSV格式"""
    rows = []
    for qid, dist in results.items():
        row_data = original_df[original_df['input_id']==qid].iloc[0]
        row = {
            'input_id': qid,
            'qkey': row_data['qkey'],  # 添加qkey列
            'question_raw': row_data['question_raw']
        }
        for option, prob in dist.items():
            row[f'pred_{option}'] = prob
        rows.append(row)
    
    df_output = pd.DataFrame(rows)
    df_output.to_csv(SAVE_CSV_PATH, index=False)
    print(f"CSV保存完成 -> {SAVE_CSV_PATH}")

def save_all_results(results, original_df):
    """保存所有格式的结果"""
    save_to_json(results, SAVE_JSON_PATH)
    save_to_excel(results, original_df)
    save_to_csv(results, original_df)
