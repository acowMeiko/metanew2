# ==================== BBH & MMLU DPO数据生成流程 (PowerShell版本) ====================
# 功能：批量处理 BBH 和 MMLU 数据集，生成 DPO 训练数据
# 作者：AI Assistant
# 日期：2025-12-23
# ===================================================================================

$ErrorActionPreference = "Stop"  # 遇到错误立即停止

# ==================== 配置区 ====================
# GPU配置（根据实际情况修改）
$env:CUDA_VISIBLE_DEVICES = "3,4"

# 批处理配置
$env:BATCH_SIZE = "64"
$env:MAX_WORKERS = "20"

# 输出目录
$OUTPUT_DIR = "output"
$BBH_OUTPUT_DIR = Join-Path $OUTPUT_DIR "bbh"
$MMLU_OUTPUT_DIR = Join-Path $OUTPUT_DIR "mmlu"

# 创建输出目录
New-Item -ItemType Directory -Force -Path $BBH_OUTPUT_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $MMLU_OUTPUT_DIR | Out-Null

# 日志目录
$LOG_DIR = "logs"
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "BBH & MMLU DPO 数据生成流程" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GPU设备: $env:CUDA_VISIBLE_DEVICES"
Write-Host "批次大小: $env:BATCH_SIZE"
Write-Host "并发数: $env:MAX_WORKERS"
Write-Host "==========================================" -ForegroundColor Cyan

# ==================== BBH 数据集处理 ====================
Write-Host ""
Write-Host "==================== 第1部分：处理 BBH 数据集 ====================" -ForegroundColor Green
Write-Host ""

# BBH 任务列表（27个任务）
$BBH_TASKS = @(
    "boolean_expressions",
    "causal_judgement",
    "date_understanding",
    "disambiguation_qa",
    "dyck_languages",
    "formal_fallacies",
    "geometric_shapes",
    "hyperbaton",
    "logical_deduction_five_objects",
    "logical_deduction_seven_objects",
    "logical_deduction_three_objects",
    "movie_recommendation",
    "multistep_arithmetic_two",
    "navigate",
    "object_counting",
    "penguins_in_a_table",
    "reasoning_about_colored_objects",
    "ruin_names",
    "salient_translation_error_detection",
    "snarks",
    "sports_understanding",
    "temporal_sequences",
    "tracking_shuffled_objects_five_objects",
    "tracking_shuffled_objects_seven_objects",
    "tracking_shuffled_objects_three_objects",
    "web_of_lies",
    "word_sorting"
)

Write-Host "BBH 共有 $($BBH_TASKS.Count) 个任务"
Write-Host ""

$bbh_success_count = 0
$bbh_total_lines = 0

# 处理每个 BBH 任务
foreach ($task in $BBH_TASKS) {
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "处理 BBH 任务: $task" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    
    # 设置输入输出路径
    $env:DATASET_NAME = "bbh"
    $env:DATASET_PATH = "dataset/bbh/$task.json"
    
    # 检查文件是否存在
    if (-not (Test-Path $env:DATASET_PATH)) {
        Write-Host "⚠️  警告: 文件不存在 - $env:DATASET_PATH，跳过" -ForegroundColor Yellow
        continue
    }
    
    # 设置输出文件路径（通过修改config中的输出路径）
    $DPO_OUTPUT_FILE = Join-Path $BBH_OUTPUT_DIR "dpo_$task.jsonl"
    
    # 运行数据生成
    Write-Host "开始生成 DPO 数据..."
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $log_file = Join-Path $LOG_DIR "bbh_${task}_${timestamp}.log"
    
    try {
        python stage_first.py 2>&1 | Tee-Object -FilePath $log_file
        
        # 移动生成的文件
        $source_file = "output/dpo_final.jsonl"
        if (Test-Path $source_file) {
            Move-Item -Path $source_file -Destination $DPO_OUTPUT_FILE -Force
            Write-Host "✅ 完成: $task -> $DPO_OUTPUT_FILE" -ForegroundColor Green
            
            # 统计数据量
            $line_count = (Get-Content $DPO_OUTPUT_FILE).Count
            Write-Host "   数据量: $line_count 条"
            
            $bbh_success_count++
            $bbh_total_lines += $line_count
        } else {
            Write-Host "❌ 错误: 未生成输出文件" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 处理失败: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host ""
Write-Host "✅ BBH 数据集处理完成！" -ForegroundColor Green
Write-Host "成功处理: $bbh_success_count/$($BBH_TASKS.Count) 个任务"
Write-Host "总数据量: $bbh_total_lines 条"
Write-Host "输出目录: $BBH_OUTPUT_DIR"
Write-Host ""

# ==================== MMLU 数据集处理 ====================
Write-Host ""
Write-Host "==================== 第2部分：处理 MMLU 数据集 ====================" -ForegroundColor Green
Write-Host ""

# MMLU 数据文件列表
$MMLU_FILES = @(
    "auxiliary_train",
    "dev",
    "test",
    "validation"
)

Write-Host "MMLU 共有 $($MMLU_FILES.Count) 个数据文件"
Write-Host ""

$mmlu_success_count = 0
$mmlu_total_lines = 0

# 处理每个 MMLU 文件
foreach ($file in $MMLU_FILES) {
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host "处理 MMLU 文件: $file" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    
    # 设置输入输出路径
    $env:DATASET_NAME = "mmlu"
    $env:DATASET_PATH = "dataset/mmlu/$file.json"
    
    # 检查文件是否存在
    if (-not (Test-Path $env:DATASET_PATH)) {
        Write-Host "⚠️  警告: 文件不存在 - $env:DATASET_PATH，跳过" -ForegroundColor Yellow
        continue
    }
    
    # 设置输出文件
    $DPO_OUTPUT_FILE = Join-Path $MMLU_OUTPUT_DIR "dpo_$file.jsonl"
    
    # 运行数据生成
    Write-Host "开始生成 DPO 数据..."
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $log_file = Join-Path $LOG_DIR "mmlu_${file}_${timestamp}.log"
    
    try {
        python stage_first.py 2>&1 | Tee-Object -FilePath $log_file
        
        # 移动生成的文件
        $source_file = "output/dpo_final.jsonl"
        if (Test-Path $source_file) {
            Move-Item -Path $source_file -Destination $DPO_OUTPUT_FILE -Force
            Write-Host "✅ 完成: $file -> $DPO_OUTPUT_FILE" -ForegroundColor Green
            
            # 统计数据量
            $line_count = (Get-Content $DPO_OUTPUT_FILE).Count
            Write-Host "   数据量: $line_count 条"
            
            $mmlu_success_count++
            $mmlu_total_lines += $line_count
        } else {
            Write-Host "❌ 错误: 未生成输出文件" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 处理失败: $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

Write-Host ""
Write-Host "✅ MMLU 数据集处理完成！" -ForegroundColor Green
Write-Host "成功处理: $mmlu_success_count/$($MMLU_FILES.Count) 个文件"
Write-Host "总数据量: $mmlu_total_lines 条"
Write-Host "输出目录: $MMLU_OUTPUT_DIR"
Write-Host ""

# ==================== 汇总统计 ====================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "数据生成汇总" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "BBH 数据集:" -ForegroundColor White
Write-Host "  成功任务: $bbh_success_count/$($BBH_TASKS.Count)"
Write-Host "  总数据量: $bbh_total_lines 条"

Write-Host ""
Write-Host "MMLU 数据集:" -ForegroundColor White
Write-Host "  成功文件: $mmlu_success_count/$($MMLU_FILES.Count)"
Write-Host "  总数据量: $mmlu_total_lines 条"

Write-Host ""
Write-Host "总计: $($bbh_total_lines + $mmlu_total_lines) 条 DPO 训练数据"
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "🎉 全部处理完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
