# ========================================
# 小批次测试脚本 (PowerShell)
# ========================================
# 从每个数据集提取前128条数据并运行测试

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🧪 小批次测试脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n说明:" -ForegroundColor Yellow
Write-Host "  - 测试批次大小: 128 条 (一个批次)" -ForegroundColor Gray
Write-Host "  - 创建测试数据集并运行完整流程" -ForegroundColor Gray
Write-Host "  - 快速验证端到端功能`n" -ForegroundColor Gray

# 检查 Python
Write-Host "🔍 检查环境..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor White
} catch {
    Write-Host "  ❌ Python 未安装" -ForegroundColor Red
    exit 1
}

# 检查脚本文件
if (-not (Test-Path "test_small_batch.py")) {
    Write-Host "`n❌ 错误: 找不到 test_small_batch.py" -ForegroundColor Red
    exit 1
}

# 显示菜单
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "选择测试模式" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  1. 交互式模式 - 选择要测试的数据集" -ForegroundColor White
Write-Host "  2. 快速测试 - 测试 BBH (最小数据集)" -ForegroundColor White
Write-Host "  3. 全部测试 - 测试所有数据集" -ForegroundColor White
Write-Host "  q. 退出" -ForegroundColor White
Write-Host "========================================`n" -ForegroundColor Cyan

$choice = Read-Host "请选择 (1/2/3/q)"

switch ($choice) {
    "1" {
        Write-Host "`n🚀 启动交互式测试..." -ForegroundColor Green
        python test_small_batch.py
    }
    "2" {
        Write-Host "`n🚀 快速测试 BBH 数据集..." -ForegroundColor Green
        Write-Host "  - 提取前 128 条数据" -ForegroundColor Gray
        Write-Host "  - 运行完整 DPO 流程`n" -ForegroundColor Gray
        
        # 直接运行 stage_first.py，但先创建小数据集
        python -c @"
import json
from pathlib import Path
import sys
sys.path.insert(0, '.')
from stage_first import load_and_preprocess_dataset

# 加载并截取前128条
data = load_and_preprocess_dataset('bbh', 'dataset/bbh/boolean_expressions.json')
small_data = data[:128]

# 保存
Path('data/test_small_batch').mkdir(parents=True, exist_ok=True)
with open('data/test_small_batch/bbh_test_128.json', 'w', encoding='utf-8') as f:
    json.dump(small_data, f, ensure_ascii=False, indent=2)

print(f'✅ 已创建测试数据: {len(small_data)} 条')
"@

        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n✅ 测试数据已创建" -ForegroundColor Green
            Write-Host "🚀 开始运行 DPO 生成流程...`n" -ForegroundColor Green
            
            # 设置环境变量并运行
            $env:DATASET_NAME = "deepscaler"
            $env:DATASET_PATH = "data/test_small_batch/bbh_test_128.json"
            python stage_first.py
        }
    }
    "3" {
        Write-Host "`n🚀 测试所有数据集..." -ForegroundColor Green
        Write-Host "  ⚠️  这将需要较长时间`n" -ForegroundColor Yellow
        
        # 使用 Python 脚本的 all 选项
        Write-Host "all" | python test_small_batch.py
    }
    "q" {
        Write-Host "`n👋 已退出`n" -ForegroundColor Gray
        exit 0
    }
    default {
        Write-Host "`n❌ 无效的选择: $choice`n" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n✅ 完成!`n" -ForegroundColor Green
