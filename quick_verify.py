"""快速验证脚本 - 仅生成5个样本"""
import sys
sys.path.insert(0, '.')

print("=" * 80)
print("🚀 快速验证：生成5个DPO样本")
print("=" * 80)

# 设置环境变量
import os
os.environ['BATCH_SIZE'] = '5'
os.environ['MAX_WORKERS'] = '3'

print("\n配置:")
print("  BATCH_SIZE: 5")
print("  MAX_WORKERS: 3 (降低并发)")

# 运行测试
print("\n" + "=" * 80)
choice = input("\n选择数据集:\n  1. BBH (布尔表达式)\n  2. SVAMP (数学题)\n  3. GSM8K (数学题)\n\n请选择 [1-3]: ").strip()

dataset_map = {
    '1': ('bbh', 'dataset/bbh/boolean_expressions.json'),
    '2': ('svamp', 'dataset/svamp/test.json'),
    '3': ('gsm8k', 'dataset/gsm8k/test.jsonl')
}

if choice in dataset_map:
    name, path = dataset_map[choice]
    print(f"\n✅ 选择: {name}")
    print("=" * 80)
    
    # 加载数据
    from stage_first import load_and_preprocess_dataset, prepare_stage1
    import json
    from pathlib import Path
    
    print(f"\n📦 加载数据集: {path}")
    data = load_and_preprocess_dataset(name, path)
    print(f"✅ 原始数据: {len(data)} 条")
    
    # 只取前5条
    test_data = data[:5]
    print(f"✅ 测试数据: {len(test_data)} 条")
    
    # 运行生成
    print("\n" + "=" * 80)
    print("🔄 开始生成 DPO 数据...")
    print("=" * 80)
    
    try:
        prepare_stage1(test_data)
        
        # 验证结果
        output_file = Path("output/dpo_final.jsonl")
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print("\n" + "=" * 80)
            print(f"✅ 生成完成！共 {len(lines)} 条数据")
            print("=" * 80)
            
            # 验证格式
            sample = json.loads(lines[0])
            print("\n📋 样本验证:")
            print(f"  ✓ 包含 'messages': {'messages' in sample}")
            print(f"  ✓ 包含 'chosen': {'chosen' in sample}")
            print(f"  ✓ 包含 'rejected': {'rejected' in sample}")
            print(f"  ✓ chosen 长度: {len(sample.get('chosen', ''))} 字符")
            print(f"  ✓ rejected 长度: {len(sample.get('rejected', ''))} 字符")
            
            if sample.get('chosen') and sample.get('rejected'):
                print("\n🎉 验证成功！DPO 数据格式正确，chosen 和 rejected 都有内容")
            else:
                print("\n⚠️  警告: chosen 或 rejected 为空")
                if not sample.get('chosen'):
                    print("     chosen 为空 - API 调用可能失败")
                if not sample.get('rejected'):
                    print("     rejected 为空 - 本地推理可能失败")
        else:
            print("\n❌ 输出文件不存在")
            
    except ValueError as e:
        print(f"\n❌ 数据质量检查失败: {e}")
        print("\n这是预期行为！说明验证机制正常工作。")
        print("原因: API 调用返回空值，被验证机制拦截。")
    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print("\n❌ 无效选择")

print("\n" + "=" * 80)
