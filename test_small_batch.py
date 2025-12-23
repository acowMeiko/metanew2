"""
小批次测试脚本

从每个数据集中提取前128条数据进行测试
用于快速验证完整的 DPO 生成流程
"""

import json
from pathlib import Path
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from stage_first import load_and_preprocess_dataset, prepare_stage1
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试批次大小
TEST_BATCH_SIZE = 128

# 定义要测试的数据集
TEST_DATASETS = [
    {
        "name": "bbh",
        "path": "dataset/bbh/boolean_expressions.json",
        "description": "BBH Boolean Expressions (推理任务)"
    },
    {
        "name": "svamp",
        "path": "dataset/svamp/test.json",
        "description": "SVAMP (数学应用题)"
    },
    {
        "name": "gsm8k",
        "path": "dataset/gsm8k/test.jsonl",
        "description": "GSM8K (数学应用题)"
    },
    {
        "name": "math",
        "path": "dataset/math/test.jsonl",
        "description": "MATH (高等数学题)"
    },
]


def create_small_test_dataset(dataset_name: str, dataset_path: str, output_path: str):
    """
    创建小测试数据集（前128条）
    
    Args:
        dataset_name: 数据集名称
        dataset_path: 原始数据集路径
        output_path: 输出路径
    """
    logger.info("=" * 80)
    logger.info(f"处理数据集: {dataset_name}")
    logger.info(f"原始路径: {dataset_path}")
    logger.info("=" * 80)
    
    # 检查文件是否存在
    if not Path(dataset_path).exists():
        logger.warning(f"⚠️  数据集文件不存在，跳过: {dataset_path}")
        return None
    
    try:
        # 加载并预处理数据
        full_dataset = load_and_preprocess_dataset(dataset_name, dataset_path)
        logger.info(f"✅ 原始数据量: {len(full_dataset)} 条")
        
        # 取前128条
        small_dataset = full_dataset[:TEST_BATCH_SIZE]
        logger.info(f"✅ 测试数据量: {len(small_dataset)} 条")
        
        # 保存为JSON格式
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(small_dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ 已保存到: {output_path}")
        logger.info(f"📊 样本预览:")
        logger.info(f"   Question: {small_dataset[0]['question'][:100]}...")
        logger.info(f"   Answer: {small_dataset[0]['answer'][:100]}...")
        
        return small_dataset
        
    except Exception as e:
        logger.error(f"❌ 处理失败: {e}", exc_info=True)
        return None


def run_test_for_dataset(dataset_name: str, test_data_path: str, description: str):
    """
    对单个数据集运行测试
    
    Args:
        dataset_name: 数据集名称
        test_data_path: 测试数据路径
        description: 数据集描述
    """
    logger.info("\n" + "=" * 80)
    logger.info(f"🧪 开始测试: {description}")
    logger.info("=" * 80)
    
    try:
        # 加载测试数据
        with open(test_data_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        logger.info(f"📊 测试数据量: {len(dataset)} 条")
        
        # 运行完整的 DPO 生成流程
        prepare_stage1(dataset)
        
        logger.info(f"✅ {dataset_name} 测试完成!")
        return True
        
    except Exception as e:
        logger.error(f"❌ {dataset_name} 测试失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("🧪 小批次测试脚本")
    print("=" * 80)
    print(f"\n测试批次大小: {TEST_BATCH_SIZE} 条")
    print(f"测试数据集数量: {len(TEST_DATASETS)}")
    print("\n说明:")
    print("  1. 从每个数据集提取前128条数据")
    print("  2. 保存为测试数据文件")
    print("  3. 运行完整的 DPO 生成流程")
    print("  4. 验证端到端功能")
    print("\n" + "=" * 80)
    
    # 步骤1: 创建测试数据集
    print("\n📦 步骤1: 创建测试数据集\n")
    
    test_data_dir = Path("data/test_small_batch")
    test_datasets_info = []
    
    for ds in TEST_DATASETS:
        output_path = test_data_dir / f"{ds['name']}_test_{TEST_BATCH_SIZE}.json"
        
        result = create_small_test_dataset(
            dataset_name=ds['name'],
            dataset_path=ds['path'],
            output_path=str(output_path)
        )
        
        if result:
            test_datasets_info.append({
                "name": ds['name'],
                "path": str(output_path),
                "description": ds['description'],
                "count": len(result)
            })
    
    if not test_datasets_info:
        print("\n❌ 没有成功创建任何测试数据集")
        return
    
    print("\n" + "=" * 80)
    print(f"✅ 成功创建 {len(test_datasets_info)} 个测试数据集")
    print("=" * 80)
    
    # 步骤2: 选择要测试的数据集
    print("\n📋 可用的测试数据集:")
    for i, ds in enumerate(test_datasets_info, 1):
        print(f"  {i}. {ds['name']:10s} - {ds['description']} ({ds['count']} 条)")
    
    print("\n" + "=" * 80)
    print("请选择要测试的数据集:")
    print("  输入数字 (1-{})，或 'all' 测试全部，或 'q' 退出".format(len(test_datasets_info)))
    print("=" * 80)
    
    choice = input("\n请选择: ").strip().lower()
    
    if choice == 'q':
        print("\n👋 已退出")
        return
    
    # 步骤3: 运行测试
    print("\n" + "=" * 80)
    print("🚀 步骤2: 运行 DPO 生成测试")
    print("=" * 80)
    
    results = {}
    
    if choice == 'all':
        # 测试所有数据集
        for ds in test_datasets_info:
            success = run_test_for_dataset(
                dataset_name=ds['name'],
                test_data_path=ds['path'],
                description=ds['description']
            )
            results[ds['name']] = success
    else:
        # 测试单个数据集
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(test_datasets_info):
                ds = test_datasets_info[idx]
                success = run_test_for_dataset(
                    dataset_name=ds['name'],
                    test_data_path=ds['path'],
                    description=ds['description']
                )
                results[ds['name']] = success
            else:
                print(f"\n❌ 无效的选择: {choice}")
                return
        except ValueError:
            print(f"\n❌ 无效的输入: {choice}")
            return
    
    # 打印总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    for name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name:15s}: {status}")
    
    passed = sum(1 for s in results.values() if s)
    total = len(results)
    
    print("\n" + "-" * 80)
    print(f"  总计: {passed}/{total} 通过")
    print("=" * 80)
    
    # 检查输出文件
    output_file = Path("output/dpo_final.jsonl")
    if output_file.exists():
        print(f"\n✅ 输出文件已生成: {output_file}")
        print(f"📊 文件大小: {output_file.stat().st_size / 1024:.2f} KB")
        
        # 显示第一条数据
        print("\n📋 输出样本 (第1条):")
        with open(output_file, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            sample = json.loads(first_line)
            print(json.dumps(sample, indent=2, ensure_ascii=False)[:500] + "...")
    
    print("\n✅ 测试完成!\n")


if __name__ == "__main__":
    main()
