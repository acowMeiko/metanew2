# ========================================
# Stage First 数据集处理示例脚本
# ========================================
# 本脚本展示如何使用 stage_first.py 处理不同数据集

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stage First 数据集处理示例" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ========================================
# 示例 1: 处理 GSM8K 数据集
# ========================================
Write-Host "`n[示例 1] 处理 GSM8K 数据集" -ForegroundColor Yellow
Write-Host "数据格式: JSONL, 字段: question, answer" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="gsm8k"' -ForegroundColor White
Write-Host '  $env:DATASET_PATH="dataset/gsm8k/test.jsonl"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 示例 2: 处理 MATH 数据集
# ========================================
Write-Host "`n[示例 2] 处理 MATH 数据集" -ForegroundColor Yellow
Write-Host "数据格式: JSONL, 字段: problem, answer" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="math"' -ForegroundColor White
Write-Host '  $env:DATASET_PATH="dataset/math/test.jsonl"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 示例 3: 处理 BBH 数据集
# ========================================
Write-Host "`n[示例 3] 处理 BBH 数据集 (单个任务)" -ForegroundColor Yellow
Write-Host "数据格式: JSON, 字段: examples[].input, examples[].target" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="bbh"' -ForegroundColor White
Write-Host '  $env:DATASET_PATH="dataset/bbh/boolean_expressions.json"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 示例 4: 处理 MMLU 数据集
# ========================================
Write-Host "`n[示例 4] 处理 MMLU 数据集" -ForegroundColor Yellow
Write-Host "数据格式: JSON, 字段: question, choices, answer/answer_idx" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="mmlu"' -ForegroundColor White
Write-Host '  $env:DATASET_PATH="dataset/mmlu/test.json"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 示例 5: 处理 SVAMP 数据集
# ========================================
Write-Host "`n[示例 5] 处理 SVAMP 数据集" -ForegroundColor Yellow
Write-Host "数据格式: JSON, 字段: Body, Question, Answer" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="svamp"' -ForegroundColor White
Write-Host '  $env:DATASET_PATH="dataset/svamp/test.json"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 示例 6: 使用默认数据集 (原有逻辑)
# ========================================
Write-Host "`n[示例 6] 使用默认数据集 (兼容原有逻辑)" -ForegroundColor Yellow
Write-Host "数据路径: data/original_data/merged_all_levels.json" -ForegroundColor Gray
Write-Host "命令:" -ForegroundColor Green
Write-Host '  python stage_first.py' -ForegroundColor White
Write-Host "或:" -ForegroundColor Green
Write-Host '  $env:DATASET_NAME="deepscaler"' -ForegroundColor White
Write-Host '  python stage_first.py' -ForegroundColor White

# ========================================
# 交互式选择
# ========================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "要运行其中一个示例吗？" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "请选择 (1-6)，或按 Enter 跳过:" -ForegroundColor Yellow
$choice = Read-Host

switch ($choice) {
    "1" {
        Write-Host "`n正在运行: GSM8K 示例..." -ForegroundColor Green
        $env:DATASET_NAME = "gsm8k"
        $env:DATASET_PATH = "dataset/gsm8k/test.jsonl"
        python stage_first.py
    }
    "2" {
        Write-Host "`n正在运行: MATH 示例..." -ForegroundColor Green
        $env:DATASET_NAME = "math"
        $env:DATASET_PATH = "dataset/math/test.jsonl"
        python stage_first.py
    }
    "3" {
        Write-Host "`n正在运行: BBH 示例..." -ForegroundColor Green
        $env:DATASET_NAME = "bbh"
        $env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
        python stage_first.py
    }
    "4" {
        Write-Host "`n正在运行: MMLU 示例..." -ForegroundColor Green
        $env:DATASET_NAME = "mmlu"
        $env:DATASET_PATH = "dataset/mmlu/test.json"
        python stage_first.py
    }
    "5" {
        Write-Host "`n正在运行: SVAMP 示例..." -ForegroundColor Green
        $env:DATASET_NAME = "svamp"
        $env:DATASET_PATH = "dataset/svamp/test.json"
        python stage_first.py
    }
    "6" {
        Write-Host "`n正在运行: 默认数据集..." -ForegroundColor Green
        python stage_first.py
    }
    default {
        Write-Host "`n已跳过。" -ForegroundColor Gray
    }
}

Write-Host "`n完成！" -ForegroundColor Green
