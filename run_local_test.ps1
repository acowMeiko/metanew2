# ========================================
# 快速本地测试脚本
# ========================================
# 用于快速验证数据集预处理逻辑
# 无需 GPU、模型或 API 服务

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🧪 数据集预处理本地测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n说明:" -ForegroundColor Yellow
Write-Host "  本测试仅验证数据加载和格式转换逻辑" -ForegroundColor Gray
Write-Host "  不需要 GPU、vLLM 或 API 服务" -ForegroundColor Gray
Write-Host "  测试通过后可在服务器上运行完整流程`n" -ForegroundColor Gray

# 检查 Python 环境
Write-Host "🔍 检查 Python 环境..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ Python: $pythonVersion" -ForegroundColor White
} catch {
    Write-Host "  ❌ Python 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查测试脚本是否存在
if (-not (Test-Path "test_local_preprocessing.py")) {
    Write-Host "`n❌ 错误: 找不到 test_local_preprocessing.py" -ForegroundColor Red
    exit 1
}

# 检查数据集目录
Write-Host "`n🔍 检查数据集目录..." -ForegroundColor Green
$datasets = @(
    @{name="GSM8K"; path="dataset/gsm8k/test.jsonl"},
    @{name="MATH"; path="dataset/math/test.jsonl"},
    @{name="BBH"; path="dataset/bbh/boolean_expressions.json"},
    @{name="MMLU"; path="dataset/mmlu/test.json"},
    @{name="SVAMP"; path="dataset/svamp/test.json"}
)

$foundCount = 0
foreach ($ds in $datasets) {
    if (Test-Path $ds.path) {
        Write-Host "  ✅ $($ds.name): $($ds.path)" -ForegroundColor White
        $foundCount++
    } else {
        Write-Host "  ⚠️  $($ds.name): 文件不存在" -ForegroundColor Yellow
    }
}

if ($foundCount -eq 0) {
    Write-Host "`n❌ 错误: 未找到任何数据集文件" -ForegroundColor Red
    Write-Host "   请确保数据集文件存在于正确的路径" -ForegroundColor Gray
    exit 1
} else {
    Write-Host "`n  找到 $foundCount / $($datasets.Count) 个数据集文件" -ForegroundColor Cyan
}

# 运行测试
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "▶️  开始运行测试..." -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 执行测试脚本
$testResult = $LASTEXITCODE
python test_local_preprocessing.py
$testResult = $LASTEXITCODE

# 显示结果
Write-Host "`n========================================" -ForegroundColor Cyan

if ($testResult -eq 0) {
    Write-Host "✅ 测试完成: 所有检查通过!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n📋 下一步建议:" -ForegroundColor Yellow
    Write-Host "  1. 预处理逻辑已验证正确" -ForegroundColor White
    Write-Host "  2. 可以在服务器上运行完整的 DPO 生成流程" -ForegroundColor White
    Write-Host "  3. 建议先用小数据集测试（如 BBH）:" -ForegroundColor White
    Write-Host "`n     `$env:DATASET_NAME = `"bbh`"" -ForegroundColor Gray
    Write-Host "     `$env:DATASET_PATH = `"dataset/bbh/boolean_expressions.json`"" -ForegroundColor Gray
    Write-Host "     python stage_first.py" -ForegroundColor Gray
    Write-Host "`n  4. 详细测试策略请查看: TESTING_STRATEGY.md`n" -ForegroundColor White
} else {
    Write-Host "⚠️  测试完成: 发现一些问题" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "`n📋 建议:" -ForegroundColor Yellow
    Write-Host "  1. 查看上方的错误信息" -ForegroundColor White
    Write-Host "  2. 检查数据集文件是否存在" -ForegroundColor White
    Write-Host "  3. 确认文件格式是否正确（JSON/JSONL）" -ForegroundColor White
    Write-Host "  4. 查看 TESTING_STRATEGY.md 获取帮助`n" -ForegroundColor White
}

Write-Host "========================================`n" -ForegroundColor Cyan
