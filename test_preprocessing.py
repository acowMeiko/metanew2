"""
数据集预处理验证脚本

用于快速测试各个数据集的预处理函数是否工作正常
不运行完整的 DPO 生成流程，仅验证数据加载和格式转换
"""

import json
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from stage_first import (
    load_and_preprocess_dataset,
    DATASET_PREPROCESSORS
)

def test_dataset(dataset_name: str, dataset_path: str, sample_size: int = 3):
    """
    测试单个数据集的预处理
    
    Args:
        dataset_name: 数据集名称
        dataset_path: 数据集路径
        sample_size: 显示的样本数量
    """
    print("=" * 80)
    print(f"测试数据集: {dataset_name}")
    print(f"文件路径: {dataset_path}")
    print("=" * 80)
    
    try:
        # 加载并预处理数据
        processed_data = load_and_preprocess_dataset(dataset_name, dataset_path)
        
        print(f"✅ 加载成功！")
        print(f"📊 数据总数: {len(processed_data)} 条")
        print(f"\n📝 前 {min(sample_size, len(processed_data))} 条样本:\n")
        
        # 显示样本
        for i, item in enumerate(processed_data[:sample_size]):
            print(f"--- 样本 {i+1} ---")
            print(f"Question: {item['question'][:200]}...")  # 只显示前200字符
            print(f"Answer: {item['answer'][:200]}...")
            print()
        
        # 验证格式
        print("🔍 格式验证:")
        all_valid = True
        for i, item in enumerate(processed_data):
            if not isinstance(item.get('question'), str):
                print(f"  ❌ 第 {i} 条数据的 'question' 不是字符串")
                all_valid = False
            if not isinstance(item.get('answer'), str):
                print(f"  ❌ 第 {i} 条数据的 'answer' 不是字符串")
                all_valid = False
            if not item.get('question'):
                print(f"  ❌ 第 {i} 条数据的 'question' 为空")
                all_valid = False
            if not item.get('answer'):
                print(f"  ❌ 第 {i} 条数据的 'answer' 为空")
                all_valid = False
        
        if all_valid:
            print("  ✅ 所有数据格式正确！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有数据集的验证测试"""
    
    print("\n" + "=" * 80)
    print("数据集预处理验证测试")
    print("=" * 80 + "\n")
    
    # 定义测试用例
    test_cases = [
        ("gsm8k", "dataset/gsm8k/test.jsonl"),
        ("math", "dataset/math/test.jsonl"),
        ("bbh", "dataset/bbh/boolean_expressions.json"),
        ("mmlu", "dataset/mmlu/test.json"),
        ("svamp", "dataset/svamp/test.json"),
    ]
    
    results = {}
    
    for dataset_name, dataset_path in test_cases:
        path = Path(dataset_path)
        if not path.exists():
            print(f"⚠️  跳过 {dataset_name}: 文件不存在 ({dataset_path})")
            results[dataset_name] = "跳过"
            print()
            continue
        
        success = test_dataset(dataset_name, dataset_path)
        results[dataset_name] = "✅ 通过" if success else "❌ 失败"
        print()
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    for dataset_name, result in results.items():
        print(f"  {dataset_name:15s}: {result}")
    print("=" * 80 + "\n")
    
    # 显示支持的数据集列表
    print("📋 当前支持的数据集:")
    for name in DATASET_PREPROCESSORS.keys():
        print(f"  - {name}")
    print()


if __name__ == "__main__":
    main()
