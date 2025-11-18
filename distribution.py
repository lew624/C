# distribution.py

import json
import re
from prompts import get_chat_messages

def remove_refused_and_renormalize(dist, mapping):
    """去掉refused选项并重新归一化"""
    # 获取所有选项键
    all_options = list(mapping.keys())
    
    # 删除最后一个选项是'refused'的情况
    refused_keywords = ['refused', 'Refused', 'REFUSED', '拒绝', '不知道', '不清楚', 'Not sure', 'not sure']
    
    last_option = all_options[-1] if all_options else None
    last_option_text = mapping.get(last_option, '').lower() if last_option else ''
    
    has_refused = False
    for option_key, option_text in mapping.items():
        option_text_lower = option_text.lower()
        if any(keyword.lower() in option_text_lower for keyword in refused_keywords):
            has_refused = True
            break
    
    if has_refused:
        filtered_options = []
        for option in all_options:
            option_text = mapping.get(option, '').lower()
            if not any(keyword.lower() in option_text for keyword in refused_keywords):
                filtered_options.append(option)
    else:
        filtered_options = all_options
    
    # 创建新的分布，只包含过滤后的选项
    new_dist = {}
    total_prob = 0.0
    
    for option in filtered_options:
        if option in dist:
            new_dist[option] = dist[option]
            total_prob += dist[option]
    
    # 重新归一化
    if total_prob > 0:
        for option in new_dist:
            new_dist[option] = new_dist[option] / total_prob
    else:
        # 如果所有概率都是0，均匀分布
        uniform_prob = 1.0 / len(filtered_options) if filtered_options else 1.0
        for option in filtered_options:
            new_dist[option] = uniform_prob
    
    return new_dist

def extract_json_from_text(text):
    """从文本中提取JSON字符串"""
    # 尝试找到JSON对象
    json_pattern = r'\{[^{}]*"[^{}]*"[^{}]*\}'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # 返回最长的匹配（可能是最完整的JSON）
        return max(matches, key=len)
    
    # 如果没有找到标准JSON，尝试找到包含数字键值对的部分
    fallback_pattern = r'\{[^{}]*:[^{}]*\}'
    matches = re.findall(fallback_pattern, text)
    if matches:
        return max(matches, key=len)
    
    return None

def parse_model_output(reply, mapping):
    """解析模型输出为概率分布"""
    # 清理回复文本
    reply = reply.strip()
    
    # 提取JSON
    json_str = extract_json_from_text(reply)
    
    if json_str:
        try:
            dist = json.loads(json_str)
            # 确保所有键都是字符串，值都是数字
            dist = {str(k): float(v) for k, v in dist.items()}
            
            # 检查是否包含所有mapping中的选项
            for option in mapping:
                if option not in dist:
                    dist[option] = 0.0
            
            # 归一化
            total = sum(dist.values())
            if total <= 0:
                raise ValueError("概率总和为0")
            
            dist = {k: v/total for k, v in dist.items()}
            
            # 去掉refused选项并重新归一化
            dist = remove_refused_and_renormalize(dist, mapping)
            return dist
            
        except Exception as e:
            print(f"JSON解析错误: {e}")
            print(f"原始回复: {reply}")
    
    # 如果JSON解析失败，尝试从文本中提取数字
    print(f"无法解析JSON，尝试从文本提取: {reply[:100]}...")
    dist = {}
    for option in mapping:
        # 在回复中查找选项的概率提示
        option_pattern = rf'{option}.*?(\d+\.?\d*)'
        matches = re.findall(option_pattern, reply, re.IGNORECASE)
        if matches:
            try:
                dist[option] = float(matches[0]) / 100.0  # 假设是百分比
            except:
                dist[option] = 0.0
        else:
            dist[option] = 0.0
    
    # 如果成功提取到一些概率
    if any(v > 0 for v in dist.values()):
        total = sum(dist.values())
        if total > 0:
            dist = {k: v/total for k, v in dist.items()}
            # 去掉refused选项并重新归一化
            dist = remove_refused_and_renormalize(dist, mapping)
            return dist
    
    # 如果所有方法都失败，返回均匀分布（去掉refused后）
    print(f"所有方法失败，使用均匀分布")
    uni_dist = remove_refused_and_renormalize({k: 1.0 for k in mapping}, mapping)
    return uni_dist
