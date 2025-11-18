# main.py

import os
import ast
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM

from config import *
from prompts import get_chat_messages
from distribution import parse_model_output
from data_utils import load_data, save_all_results

def load_model():
    """加载模型和tokenizer"""
    print("正在加载Qwen2.5-7B模型...")
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        device_map="auto" if device=="cuda" else None,
        torch_dtype=torch.float16 if device=="cuda" else torch.float32
    )
    print("模型加载完成！")
    return tok, model

def predict_one(tok, model, q_raw, mapping):
    """预测单个问题的分布"""
    messages = get_chat_messages(q_raw, mapping)
    
    try:
        # 应用聊天模板
        text = tok.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tok(text, return_tensors="pt").to(model.device)
        
        # 更新生成配置
        gen_config = GENERATION_CONFIG.copy()
        gen_config["pad_token_id"] = tok.eos_token_id
        
        with torch.no_grad():
            out_ids = model.generate(
                **inputs,
                **gen_config
            )
        
        reply = tok.decode(out_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        
        # 解析模型输出
        dist = parse_model_output(reply, mapping)
        return dist
        
    except Exception as e:
        print(f"预测过程中出错: {e}")
        # 返回均匀分布（去掉refused后）
        from distribution import remove_refused_and_renormalize
        uni_dist = remove_refused_and_renormalize({k: 1.0 for k in mapping}, mapping)
        return uni_dist

def main():
    """主函数"""
    # 创建输出目录
    os.makedirs("./output", exist_ok=True)
    
    # 加载模型
    tok, model = load_model()
    
    # 读取数据
    df = load_data(EXCEL_PATH)
    
    results = {}
    
    print("开始预测...")
    for _, row in tqdm(df.iterrows(), total=len(df)):
        try:
            qid = row["input_id"]
            q_raw = row["question_raw"]
            mapping = ast.literal_eval(row["mapping"])
            
            # 预测分布
            dist = predict_one(tok, model, q_raw, mapping)
            results[qid] = dist
            
            # 打印第一个问题的结果作为示例
            if len(results) == 1:
                print(f"\n第一个问题预测结果示例:")
                print(f"问题ID: {qid}")
                print(f"问题Key: {row['qkey']}")
                print(f"问题: {q_raw}")
                print(f"预测分布: {dist}")
                print(f"概率总和: {sum(dist.values()):.4f}")
                
        except Exception as e:
            print(f"处理问题 {qid} 时出错: {e}")
            continue
    
    # 保存所有结果
    save_all_results(results, df)
    
    # 打印统计信息
    print(f"\n=== 预测完成 ===")
    print(f"总问题数: {len(results)}")
    print(f"输出文件:")
    print(f"  - JSON: {SAVE_JSON_PATH}")
    print(f"  - Excel: {SAVE_EXCEL_PATH}")
    print(f"  - CSV: {SAVE_CSV_PATH}")

if __name__ == "__main__":
    main()
