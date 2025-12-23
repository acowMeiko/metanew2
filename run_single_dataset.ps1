# ==================== 单数据集 DPO 数据生成脚本 ====================
# 功能：独立处理单个数据集，使用2张A800 GPU
# 使用方式：.\run_single_dataset.ps1 -DatasetName "bbh" -DatasetFile "boolean_expressions"
# =================================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$DatasetName,  # 数据集名称: bbh, mmlu, gsm8k, math, svamp
    
    [Parameter(Mandatory=$true)]
    [string]$DatasetFile,  # 数据文件名（不含扩展名）
    
    [string]$GPU = "3,4",  # GPU编号，默认3,4
    
    [int]$BatchSize = 128,  # vLLM批处理大小（2张A800可以调大）
    
    [int]$MaxWorkers = 30,  # API并发数（2张A800可以调大）
    
    [string]$OutputSubDir = ""  # 输出子目录（可选）
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "单数据集 DPO 数据生成" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "数据集: $DatasetName"
Write-Host "文件: $DatasetFile"
Write-Host "GPU: $GPU"
Write-Host "批次大小: $BatchSize"
Write-Host "并发数: $MaxWorkers"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ==================== 配置环境变量 ====================
$env:CUDA_VISIBLE_DEVICES = $GPU
$env:BATCH_SIZE = $BatchSize.ToString()
$env:MAX_WORKERS = $MaxWorkers.ToString()
$env:DATASET_NAME = $DatasetName

# 根据数据集类型确定文件扩展名
$extension = ".json"
if ($DatasetName -eq "gsm8k" -or $DatasetName -eq "math") {
    $extension = ".jsonl"
}

# 设置数据集路径
$env:DATASET_PATH = "dataset/$DatasetName/$DatasetFile$extension"

# 检查文件是否存在
if (-not (Test-Path $env:DATASET_PATH)) {
    Write-Host "❌ 错误: 数据集文件不存在 - $env:DATASET_PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 找到数据集文件: $env:DATASET_PATH" -ForegroundColor Green

# ==================== 创建输出目录 ====================
$OUTPUT_BASE = "output"
if ($OutputSubDir) {
    $OUTPUT_DIR = Join-Path $OUTPUT_BASE $OutputSubDir
} else {
    $OUTPUT_DIR = Join-Path $OUTPUT_BASE $DatasetName
}

New-Item -ItemType Directory -Force -Path $OUTPUT_DIR | Out-Null
Write-Host "✅ 输出目录: $OUTPUT_DIR" -ForegroundColor Green

# ==================== 创建日志目录 ====================
$LOG_DIR = "logs"
New-Item -ItemType Directory -Force -Path $LOG_DIR | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$log_file = Join-Path $LOG_DIR "${DatasetName}_${DatasetFile}_${timestamp}.log"

# ==================== 运行数据生成 ====================
Write-Host ""
Write-Host "开始生成 DPO 数据..." -ForegroundColor Yellow
Write-Host "日志文件: $log_file"
Write-Host ""

try {
    # 运行主程序并记录日志
    python stage_first.py 2>&1 | Tee-Object -FilePath $log_file
    
    # 检查输出文件
    $source_file = "output/dpo_final.jsonl"
    if (Test-Path $source_file) {
        # 移动到指定目录
        $output_file = Join-Path $OUTPUT_DIR "dpo_$DatasetFile.jsonl"
        Move-Item -Path $source_file -Destination $output_file -Force
        
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "✅ 生成完成！" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        
        # 统计数据量
        $line_count = (Get-Content $output_file).Count
        Write-Host "输出文件: $output_file"
        Write-Host "数据量: $line_count 条"
        
        # 显示文件大小
        $file_size = (Get-Item $output_file).Length
        $size_mb = [math]::Round($file_size / 1MB, 2)
        Write-Host "文件大小: $size_mb MB"
        
        Write-Host ""
        Write-Host "日志保存在: $log_file"
        
    } else {
        Write-Host ""
        Write-Host "❌ 错误: 未生成输出文件 output/dpo_final.jsonl" -ForegroundColor Red
        Write-Host "请查看日志文件: $log_file" -ForegroundColor Yellow
        exit 1
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ 处理失败: $_" -ForegroundColor Red
    Write-Host "请查看日志文件: $log_file" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🎉 完成！" -ForegroundColor Cyan
