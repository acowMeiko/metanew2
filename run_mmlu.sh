#!/bin/bash
# ==================== MMLU 数据集 DPO 数据生成 ====================
# 功能：处理 MMLU 所有数据文件（4个），生成统一的 DPO 数据
# 使用：bash run_mmlu.sh
# =================================================================

set -e  # 遇到错误立即退出

# ==================== GPU 配置 ====================
export CUDA_VISIBLE_DEVICES="3,4"  # 使用 GPU 3,4
export BATCH_SIZE=128              # vLLM 批处理大小（2张A800优化）
export MAX_WORKERS=30              # API 并发数（2张A800优化）

# ==================== 数据集配置 ====================
export DATASET_NAME="mmlu"
DATASET_DIR="dataset/mmlu_json"  # 使用 mmlu_json 目录
OUTPUT_DIR="output"
LOG_DIR="logs"

# 创建输出和日志目录
mkdir -p "${OUTPUT_DIR}"
mkdir -p "${LOG_DIR}"

# 时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${LOG_DIR}/mmlu_${TIMESTAMP}.log"

# 输出文件
export DPO_OUTPUT_FILE="${OUTPUT_DIR}/dpo_mmlu_all.jsonl"

echo "==========================================" | tee -a "${LOG_FILE}"
echo "MMLU 数据集 DPO 数据生成" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "GPU: ${CUDA_VISIBLE_DEVICES}" | tee -a "${LOG_FILE}"
echo "批次大小: ${BATCH_SIZE}" | tee -a "${LOG_FILE}"
echo "并发数: ${MAX_WORKERS}" | tee -a "${LOG_FILE}"
echo "输出文件: ${DPO_OUTPUT_FILE}" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"

# MMLU 数据文件列表
MMLU_FILES=(
    "auxiliary_train"
    "dev"
    "test"
    "validation"
)

echo "MMLU 共有 ${#MMLU_FILES[@]} 个数据文件" | tee -a "${LOG_FILE}"
echo "" | tee -a "${LOG_FILE}"

# 清空输出文件（如果存在）
> "${DPO_OUTPUT_FILE}"

# 处理每个 MMLU 文件
success_count=0
fail_count=0

for file in "${MMLU_FILES[@]}"; do
    echo "----------------------------------------" | tee -a "${LOG_FILE}"
    echo "处理文件 [$((success_count + fail_count + 1))/${#MMLU_FILES[@]}]: ${file}" | tee -a "${LOG_FILE}"
    echo "----------------------------------------" | tee -a "${LOG_FILE}"
    
    # 设置数据集路径
    export DATASET_PATH="${DATASET_DIR}/${file}.json"
    
    # 检查文件是否存在
    if [ ! -f "${DATASET_PATH}" ]; then
        echo "⚠️  警告: 文件不存在 - ${DATASET_PATH}，跳过" | tee -a "${LOG_FILE}"
        ((fail_count++))
        continue
    fi
    
    # 运行数据生成（输出会追加到同一个文件）
    echo "开始生成 DPO 数据..." | tee -a "${LOG_FILE}"
    
    if python stage_first.py 2>&1 | tee -a "${LOG_FILE}"; then
        echo "✅ 完成: ${file}" | tee -a "${LOG_FILE}"
        ((success_count++))
    else
        echo "❌ 失败: ${file}" | tee -a "${LOG_FILE}"
        ((fail_count++))
    fi
    
    echo "" | tee -a "${LOG_FILE}"
done

# 统计结果
echo "" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "MMLU 数据集处理完成" | tee -a "${LOG_FILE}"
echo "==========================================" | tee -a "${LOG_FILE}"
echo "成功: ${success_count}/${#MMLU_FILES[@]}" | tee -a "${LOG_FILE}"
echo "失败: ${fail_count}/${#MMLU_FILES[@]}" | tee -a "${LOG_FILE}"

if [ -f "${DPO_OUTPUT_FILE}" ]; then
    line_count=$(wc -l < "${DPO_OUTPUT_FILE}")
    file_size=$(du -h "${DPO_OUTPUT_FILE}" | cut -f1)
    echo "输出文件: ${DPO_OUTPUT_FILE}" | tee -a "${LOG_FILE}"
    echo "总数据量: ${line_count} 条" | tee -a "${LOG_FILE}"
    echo "文件大小: ${file_size}" | tee -a "${LOG_FILE}"
else
    echo "⚠️  警告: 未生成输出文件" | tee -a "${LOG_FILE}"
fi

echo "" | tee -a "${LOG_FILE}"
echo "日志文件: ${LOG_FILE}" | tee -a "${LOG_FILE}"
echo "🎉 完成！" | tee -a "${LOG_FILE}"
