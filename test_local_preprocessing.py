"""
本地数据集预处理测试脚本

这个脚本可以在本地运行，不需要 GPU、vLLM 或 API 服务
仅测试数据集加载和预处理逻辑的正确性
"""

import json
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

# 模拟 logger（避免依赖 config）
class MockLogger:
    def info(self, msg):
        print(f"[INFO] {msg}")
    
    def warning(self, msg):
        print(f"[WARNING] {msg}")
    
    def error(self, msg, exc_info=False):
        print(f"[ERROR] {msg}")

# 临时替换 logger
import logging
logger = MockLogger()

# 导入预处理函数
from stage_first import (
    preprocess_gsm8k,
    preprocess_math,
    preprocess_bbh,
    preprocess_mmlu,
    preprocess_svamp,
    DATASET_PREPROCESSORS
)

# 修复 logger 引用
import stage_first
stage_first.logger = logger


def test_dataset_preprocessing(dataset_name: str, dataset_path: str, expected_count: int = None):
    """
    测试单个数据集的预处理功能
    
    Args:
        dataset_name: 数据集名称
        dataset_path: 数据集文件路径
        expected_count: 期望的数据条数（可选）
    
    Returns:
        (success, processed_data, error_msg)
    """
    print("\n" + "=" * 80)
    print(f"测试数据集: {dataset_name}")
    print(f"文件路径: {dataset_path}")
    print("=" * 80)
    
    path = Path(dataset_path)
    
    # 检查文件是否存在
    if not path.exists():
        error_msg = f"❌ 文件不存在: {dataset_path}"
        print(error_msg)
        return False, None, error_msg
    
    # 检查数据集是否支持
    if dataset_name not in DATASET_PREPROCESSORS:
        error_msg = f"❌ 不支持的数据集: {dataset_name}"
        print(error_msg)
        return False, None, error_msg
    
    try:
        # 1. 加载原始数据
        print("\n📂 加载原始数据...")
        if path.suffix == ".jsonl":
            raw_data = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        raw_data.append(json.loads(line))
            print(f"   ✅ 加载 JSONL 文件: {len(raw_data)} 行")
        elif path.suffix == ".json":
            with open(path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            if isinstance(raw_data, dict):
                print(f"   ✅ 加载 JSON 对象")
            else:
                print(f"   ✅ 加载 JSON 数组: {len(raw_data)} 条")
        else:
            error_msg = f"❌ 不支持的文件格式: {path.suffix}"
            print(error_msg)
            return False, None, error_msg
        
        # 2. 调用预处理函数
        print("\n🔄 执行预处理...")
        preprocessor = DATASET_PREPROCESSORS[dataset_name]
        processed_data = preprocessor(raw_data)
        print(f"   ✅ 预处理完成: {len(processed_data)} 条有效数据")
        
        # 3. 验证数据格式
        print("\n🔍 验证数据格式...")
        errors = []
        for i, item in enumerate(processed_data):
            # 检查是否为字典
            if not isinstance(item, dict):
                errors.append(f"第 {i} 条数据不是字典类型")
                continue
            
            # 检查必需字段
            if 'question' not in item:
                errors.append(f"第 {i} 条数据缺少 'question' 字段")
            if 'answer' not in item:
                errors.append(f"第 {i} 条数据缺少 'answer' 字段")
            
            # 检查字段类型
            if not isinstance(item.get('question'), str):
                errors.append(f"第 {i} 条数据的 'question' 不是字符串")
            if not isinstance(item.get('answer'), str):
                errors.append(f"第 {i} 条数据的 'answer' 不是字符串")
            
            # 检查字段是否为空
            if not item.get('question'):
                errors.append(f"第 {i} 条数据的 'question' 为空")
            if not item.get('answer'):
                errors.append(f"第 {i} 条数据的 'answer' 为空")
        
        if errors:
            print(f"   ⚠️  发现 {len(errors)} 个格式问题:")
            for error in errors[:5]:  # 只显示前5个
                print(f"      - {error}")
            if len(errors) > 5:
                print(f"      ... 还有 {len(errors) - 5} 个问题")
        else:
            print(f"   ✅ 所有数据格式正确!")
        
        # 4. 显示样本数据
        print("\n📋 样本数据 (前3条):")
        for i, item in enumerate(processed_data[:3]):
            print(f"\n   样本 {i+1}:")
            question = item['question']
            answer = item['answer']
            print(f"   Question: {question[:150]}{'...' if len(question) > 150 else ''}")
            print(f"   Answer:   {answer[:150]}{'...' if len(answer) > 150 else ''}")
        
        # 5. 统计信息
        print("\n📊 统计信息:")
        print(f"   - 原始数据量: {len(raw_data) if isinstance(raw_data, list) else '1 个对象'}")
        print(f"   - 有效数据量: {len(processed_data)}")
        if expected_count:
            print(f"   - 期望数据量: {expected_count}")
            if len(processed_data) == expected_count:
                print(f"   ✅ 数据量匹配!")
            else:
                print(f"   ⚠️  数据量不匹配!")
        
        avg_q_len = sum(len(item['question']) for item in processed_data) / len(processed_data)
        avg_a_len = sum(len(item['answer']) for item in processed_data) / len(processed_data)
        print(f"   - 平均问题长度: {avg_q_len:.1f} 字符")
        print(f"   - 平均答案长度: {avg_a_len:.1f} 字符")
        
        # 判断测试结果
        if errors:
            return False, processed_data, f"发现 {len(errors)} 个格式问题"
        else:
            return True, processed_data, None
        
    except Exception as e:
        error_msg = f"❌ 处理失败: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return False, None, error_msg


def run_all_tests():
    """运行所有数据集的测试"""
    
    print("\n" + "=" * 80)
    print("🧪 本地数据集预处理测试")
    print("=" * 80)
    print("\n说明: 本测试仅验证数据加载和格式转换，不需要 GPU/vLLM/API")
    
    # 定义测试用例
    test_cases = [
        {
            "name": "gsm8k",
            "path": "dataset/gsm8k/test.jsonl",
            "description": "GSM8K 数学应用题数据集"
        },
        {
            "name": "math",
            "path": "dataset/math/test.jsonl",
            "description": "MATH 高等数学题数据集"
        },
        {
            "name": "bbh",
            "path": "dataset/bbh/boolean_expressions.json",
            "description": "BBH Boolean Expressions 任务"
        },
        {
            "name": "mmlu",
            "path": "dataset/mmlu/test.json",
            "description": "MMLU 多选题数据集"
        },
        {
            "name": "svamp",
            "path": "dataset/svamp/test.json",
            "description": "SVAMP 数学应用题数据集"
        },
    ]
    
    results = {}
    total_tests = len(test_cases)
    passed_tests = 0
    
    # 运行所有测试
    for test_case in test_cases:
        name = test_case["name"]
        path = test_case["path"]
        description = test_case["description"]
        
        print(f"\n{'='*80}")
        print(f"📌 {description}")
        
        success, data, error = test_dataset_preprocessing(name, path)
        
        if success:
            results[name] = "✅ 通过"
            passed_tests += 1
        elif data is None:
            results[name] = "⚠️  跳过 (文件不存在或其他错误)"
        else:
            results[name] = "⚠️  部分通过 (有格式问题)"
    
    # 打印总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    for name, result in results.items():
        print(f"  {name:15s}: {result}")
    
    print("\n" + "-" * 80)
    print(f"  总计: {passed_tests}/{total_tests} 通过")
    
    if passed_tests == total_tests:
        print("\n  🎉 所有测试通过! 预处理逻辑工作正常。")
        print("  ✅ 可以在服务器上运行完整的 DPO 生成流程。")
    elif passed_tests > 0:
        print("\n  ⚠️  部分测试通过，请检查失败的数据集。")
    else:
        print("\n  ❌ 所有测试失败，请检查数据集文件是否存在。")
    
    print("=" * 80 + "\n")
    
    # 显示支持的数据集
    print("📋 当前支持的数据集:")
    for name in DATASET_PREPROCESSORS.keys():
        print(f"  - {name}")
    print()
    
    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_all_tests()
    
    # 退出码：0 表示所有测试通过，1 表示有测试失败
    sys.exit(0 if passed == total else 1)
