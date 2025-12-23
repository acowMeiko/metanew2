"""
DPO 训练数据生成脚本 (Stage 1)

【功能说明】
本脚本用于生成 DPO (Direct Preference Optimization) 训练数据。
核心流程：Baseline → Diff → Principles → Chosen → DPO JSONL

【架构设计】
1. 数据集适配层 (Dataset Preprocessing Layer)
   - 支持多种数据集格式
   - 统一转换为标准格式: {"question": str, "answer": str}
   - 采用注册表模式，易于扩展

2. 核心处理流程 (prepare_stage1)
   - 保持原有逻辑不变
   - 分3个阶段：vLLM推理 → API生成Chosen → 组装DPO数据

【支持的数据集】
- gsm8k: 数学应用题 (question, answer)
- math: 高等数学题 (problem → question, answer)
- bbh: Big-Bench Hard 推理任务 (examples[*].input → question, target → answer)
- mmlu: 多选题 (full_question or question+choices → question, choices[answer_idx] → answer)
- svamp: 数学应用题 (Body+Question → question, Answer → answer)
- deepscaler: 原有格式 (兼容旧逻辑)

【使用方式】
1. 使用新数据集：
   export DATASET_NAME=gsm8k
   export DATASET_PATH=dataset/gsm8k/test.jsonl
   python stage_first.py

2. 使用原有数据集（默认）：
   python stage_first.py

【扩展新数据集】
1. 在数据集适配层实现预处理函数: preprocess_xxx(raw_data) -> List[Dict[str, str]]
2. 注册到 DATASET_PREPROCESSORS: {"xxx": preprocess_xxx}
3. 无需修改其他代码

【注意事项】
- prepare_stage1 的核心逻辑完全保持不变
- DPO 输出格式不变
- 支持断点续传
"""

from asyncio.log import logger
import json
import config
from pathlib import Path
from typing import List, Dict, Any, Callable
from module.execute_module import batch_answer_questions_directly,concurrent_generate_chosen
from module.plan_module import batch_generate_difference_list, batch_generate_principles
import logging  
import os
from tqdm import tqdm

# ==================== 常量定义 ====================
OUTPUTS_DIR = Path(config.output_dir)

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== 数据集适配层 (Dataset Preprocessing Layer) ====================
# 此部分负责将不同格式的数据集统一转换为标准格式: {"question": str, "answer": str}
# 新增数据集时只需: 1) 实现预处理函数  2) 注册到 DATASET_PREPROCESSORS
# ==================================================================================

def preprocess_gsm8k(raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    预处理 GSM8K 数据集
    
    原始格式: {"question": str, "answer": str}
    目标格式: {"question": str, "answer": str}
    
    GSM8K 已经是标准格式，无需转换
    """
    logger.info(f"预处理 GSM8K 数据集: {len(raw_data)} 条")
    return [
        {
            "question": item.get("question", ""),
            "answer": item.get("answer", "")
        }
        for item in raw_data
        if item.get("question") and item.get("answer")
    ]


def preprocess_math(raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    预处理 MATH 数据集
    
    原始格式: {"problem": str, "answer": str, ...}
    目标格式: {"question": str, "answer": str}
    
    需要将 "problem" 字段映射为 "question"
    """
    logger.info(f"预处理 MATH 数据集: {len(raw_data)} 条")
    return [
        {
            "question": item.get("problem", ""),
            "answer": item.get("answer", "")
        }
        for item in raw_data
        if item.get("problem") and item.get("answer")
    ]


def preprocess_bbh(raw_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    预处理 BBH (Big-Bench Hard) 数据集
    
    原始格式: {"examples": [{"input": str, "target": str}, ...], ...}
    目标格式: {"question": str, "answer": str}
    
    BBH 数据集中每个文件包含多个 examples
    """
    examples = raw_data.get("examples", [])
    logger.info(f"预处理 BBH 数据集: {len(examples)} 条")
    return [
        {
            "question": example.get("input", ""),
            "answer": example.get("target", "")
        }
        for example in examples
        if example.get("input") and example.get("target")
    ]


def preprocess_mmlu(raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    预处理 MMLU 数据集
    
    原始格式: {
        "question": str,
        "choices": [str, str, str, str],
        "answer": "A"/"B"/"C"/"D",
        "answer_idx": int,
        "full_question": str (可选)
    }
    目标格式: {"question": str, "answer": str}
    
    优先使用 full_question；否则拼接 question + choices
    答案使用 choices[answer_idx] 或映射 answer 字母到选项
    """
    logger.info(f"预处理 MMLU 数据集: {len(raw_data)} 条")
    processed = []
    
    for item in raw_data:
        # 提取问题
        question = item.get("full_question")
        if not question:
            # 如果没有 full_question，则拼接 question + choices
            q = item.get("question", "")
            choices = item.get("choices", [])
            if q and choices:
                choices_text = "\n".join([f"{chr(65+i)}. {choice}" for i, choice in enumerate(choices)])
                question = f"{q}\n{choices_text}"
        
        # 提取答案
        answer = ""
        if "answer_idx" in item and "choices" in item:
            # 使用 answer_idx 直接索引
            idx = item["answer_idx"]
            choices = item["choices"]
            if 0 <= idx < len(choices):
                answer = choices[idx]
        elif "answer" in item and "choices" in item:
            # 将字母答案映射到选项
            answer_letter = item["answer"]
            choices = item["choices"]
            # A=0, B=1, C=2, D=3
            idx = ord(answer_letter.upper()) - ord('A')
            if 0 <= idx < len(choices):
                answer = choices[idx]
        
        if question and answer:
            processed.append({
                "question": question,
                "answer": answer
            })
    
    return processed


def preprocess_svamp(raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    预处理 SVAMP 数据集
    
    原始格式: {
        "Body": str,
        "Question": str,
        "Answer": float,
        ...
    }
    目标格式: {"question": str, "answer": str}
    
    需要拼接 Body + Question 作为问题，将 Answer 转为字符串
    """
    logger.info(f"预处理 SVAMP 数据集: {len(raw_data)} 条")
    processed = []
    
    for item in raw_data:
        body = item.get("Body", "").strip()
        question = item.get("Question", "").strip()
        answer = item.get("Answer")
        
        # 拼接 Body 和 Question
        full_question = f"{body} {question}".strip() if body else question
        
        # 将数字答案转为字符串
        if full_question and answer is not None:
            processed.append({
                "question": full_question,
                "answer": str(answer)
            })
    
    return processed


# 数据集预处理器注册表
# 新增数据集时，只需在此处注册对应的预处理函数
DATASET_PREPROCESSORS: Dict[str, Callable] = {
    "gsm8k": preprocess_gsm8k,
    "math": preprocess_math,
    "bbh": preprocess_bbh,
    "mmlu": preprocess_mmlu,
    "svamp": preprocess_svamp,
}


def load_and_preprocess_dataset(dataset_name: str, dataset_path: str) -> List[Dict[str, str]]:
    """
    加载并预处理数据集（数据集适配入口）
    
    此函数是数据集适配层的统一入口，负责：
    1. 根据文件扩展名加载原始数据
    2. 调用对应的预处理器转换为统一格式
    3. 返回标准格式的数据集供 prepare_stage1 使用
    
    Args:
        dataset_name: 数据集名称 (gsm8k/math/bbh/mmlu/svamp)
        dataset_path: 数据集文件路径
    
    Returns:
        标准格式的数据集: [{"question": str, "answer": str}, ...]
    
    Raises:
        ValueError: 如果数据集名称不支持或文件格式不支持
    """
    logger.info("=" * 60)
    logger.info(f"[数据集适配层] 开始加载数据集: {dataset_name}")
    logger.info(f"[数据集适配层] 文件路径: {dataset_path}")
    logger.info("=" * 60)
    
    # 检查数据集是否支持
    if dataset_name not in DATASET_PREPROCESSORS:
        raise ValueError(
            f"不支持的数据集: {dataset_name}。"
            f"支持的数据集: {list(DATASET_PREPROCESSORS.keys())}"
        )
    
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"数据集文件不存在: {dataset_path}")
    
    # 根据文件扩展名加载原始数据
    try:
        if path.suffix == ".jsonl":
            # JSONL 格式：每行一个 JSON 对象
            raw_data = []
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        raw_data.append(json.loads(line))
            logger.info(f"[数据集适配层] 已加载 JSONL 文件: {len(raw_data)} 条")
        elif path.suffix == ".json":
            # JSON 格式：单个 JSON 对象或数组
            with open(path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            logger.info(f"[数据集适配层] 已加载 JSON 文件")
        else:
            raise ValueError(f"不支持的文件格式: {path.suffix}，仅支持 .json 和 .jsonl")
    except Exception as e:
        logger.error(f"[数据集适配层] 加载文件失败: {e}", exc_info=True)
        raise
    
    # 调用对应的预处理器
    preprocessor = DATASET_PREPROCESSORS[dataset_name]
    try:
        processed_data = preprocessor(raw_data)
        logger.info(f"[数据集适配层] 预处理完成: {len(processed_data)} 条有效数据")
        logger.info(f"[数据集适配层] 数据格式已统一为: {{'question': str, 'answer': str}}")
        logger.info("=" * 60)
        return processed_data
    except Exception as e:
        logger.error(f"[数据集适配层] 预处理失败: {e}", exc_info=True)
        raise


# ==================== 原有逻辑：批量推理函数 ====================
# 以下函数为原有逻辑，保持不变
# ============================================================

def batch_answer_questions(questions: List[str]) -> List[str]:
    """
    批量生成Baseline答案（使用本地vLLM）
    
    Args:
        questions: 问题列表
    
    Returns:
        答案列表
    """
    logger.info(f"批量生成Baseline答案: {len(questions)} 条")
    return batch_answer_questions_directly(questions)


def batch_generate_differences(questions: List[str], preds: List[str], labels: List[str]) -> List[str]:
    """
    批量生成差异分析（使用本地vLLM）
    
    Args:
        questions: 问题列表
        preds: 预测答案列表
        labels: 标准答案列表
    
    Returns:
        差异分析列表
    """
    logger.info(f"批量生成差异分析: {len(questions)} 条")
    return batch_generate_difference_list(questions, preds, labels)


def batch_generate_principles_local(questions: List[str], diffs: List[str], model: str = "weak") -> List[str]:
    """
    批量生成原则（使用本地vLLM）
    
    Args:
        questions: 问题列表
        diffs: 差异分析列表
        model: 模型类型（"weak" 使用本地模型）
    
    Returns:
        原则列表
    """
    logger.info(f"批量生成原则（弱模型）: {len(questions)} 条")
    return batch_generate_principles(questions, diffs, model=model)
def prepare_stage1(dataset):
    """
    生成DPO训练数据
    Args:
        dataset: 输入数据集
    """
    logger.info("=" * 60)
    logger.info("Step 1: 开始生成DPO数据")
    logger.info("=" * 60)
    progress_file = Path(config.dpo_progress_file)
    dpo_file = Path(config.dpo_final_file)
    
    if progress_file.exists():
        try:
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            start_idx = progress.get('processed_count', 0)
            logger.info(f"发现已有进度，将从第 {start_idx} 项开始继续处理")
        except Exception as e:
            logger.error(f"读取进度文件失败: {e}，将从头开始")
            start_idx = 0
    else:
        start_idx = 0
        logger.info("未发现已有进度，将从头开始处理")
        # 如果重新开始，清空现有JSONL文件
        if dpo_file.exists():
            dpo_file.unlink()
    # 从上次中断的位置继续处理
    try:
        # 准备所有待处理数据
        all_data = []
        for i in range(start_idx, len(dataset)):
            item = dataset[i]
            # 兼容 problem/question 字段
            question = item.get("problem") or item.get("question", "")
            label = item.get("answer", "")
            
            if not question or not label:
                logger.warning(f"第 {i} 项数据缺少problem/question或answer，跳过")
                continue
            
            all_data.append({
                'index': i,
                'question': question,
                'label': label
            })
        total_items = len(all_data)
        logger.info(f"共需处理 {total_items} 条数据，批次大小: {config.batch_size}")
        
        
        logger.info("=" * 60)
        logger.info("阶段1/3: vLLM分批本地推理（所有数据）")
        logger.info("=" * 60)

        all_baseline_answers = []
        all_diffs = []
        all_rejected = []
        for batch_start in range(0, total_items, config.BATCH_SIZE):
            batch_end = min(batch_start + config.BATCH_SIZE, total_items)
            batch_data = all_data[batch_start:batch_end]
            
            logger.info(f"处理批次 [{batch_start+1}-{batch_end}/{total_items}]")
            
            # 批量获取问题列表
            questions = [item['question'] for item in batch_data]
            labels = [item['label'] for item in batch_data]
            
            # 批量推理：Baseline answers
            logger.info(f"  → 生成Baseline答案 ({len(questions)} 条)...")
            baseline_answers = batch_answer_questions(questions)
            all_baseline_answers.extend(baseline_answers)
            
            # 批量推理：Difference analysis
            logger.info(f"  → 生成差异分析 ({len(questions)} 条)...")
            diffs = batch_generate_differences(questions, baseline_answers, labels)
            all_diffs.extend(diffs)
            
            # 批量推理：Rejected responses
            logger.info(f"  → 生成Rejected原则 ({len(questions)} 条)...")
            rejected_list = batch_generate_principles_local(questions, diffs, model="weak")
            all_rejected.extend(rejected_list)
            
            logger.info(f"批次 [{batch_start+1}-{batch_end}] 本地推理完成")
        
        logger.info(f"阶段1完成: 共生成 {len(all_baseline_answers)} 条本地推理结果")
    except Exception as e:
        logger.error(f"生成DPO数据时发生错误: {e}", exc_info=True)
        raise
    vllm_cache_file = OUTPUTS_DIR / "vllm_cache.json"
    logger.info(f"保存vLLM处理结果到: {vllm_cache_file}")
    vllm_cache_data = {
        'all_data': all_data,
        'all_baseline_answers': all_baseline_answers,
        'all_diffs': all_diffs,
        'all_rejected': all_rejected,
        'total_items': total_items
    }
    vllm_cache_file.parent.mkdir(parents=True, exist_ok=True)
    with open(vllm_cache_file, 'w', encoding='utf-8') as f:
        json.dump(vllm_cache_data, f, indent=2, ensure_ascii=False)
    logger.info("vLLM处理结果已安全保存")
           # ===== 阶段2: 并发调用API处理所有数据（分批） =====
    logger.info("=" * 60)
    logger.info("阶段2/3: API并发生成Chosen（分批处理）")
    logger.info("=" * 60)
    
    all_questions = [item['question'] for item in all_data]
    all_chosen = []
    
    # 计算API批次大小（避免一次性并发过多）
    api_batch_size = config.MAX_WORKERS # 例如15个worker，每批1500条
    total_api_batches = (len(all_questions) + api_batch_size - 1) // api_batch_size
    
    logger.info(f"API分批处理: 每批 {api_batch_size} 条，共 {total_api_batches} 批")
    
    for api_batch_idx in range(0, len(all_questions), api_batch_size):
        api_batch_end = min(api_batch_idx + api_batch_size, len(all_questions))
        batch_questions = all_questions[api_batch_idx:api_batch_end]
        batch_diffs = all_diffs[api_batch_idx:api_batch_end]
        
        logger.info(f"API批次 [{api_batch_idx+1}-{api_batch_end}/{len(all_questions)}] 开始处理...")
        batch_chosen = concurrent_generate_chosen(batch_questions, batch_diffs, max_workers=config.MAX_WORKERS)
        
        # 验证返回长度
        assert len(batch_chosen) == len(batch_questions), \
            f"API批次返回长度不匹配: 期望 {len(batch_questions)}, 实际 {len(batch_chosen)}"
        
        # 检查空值比例
        empty_count = sum(1 for c in batch_chosen if not c)
        if empty_count > 0:
            logger.warning(f"⚠️  批次中有 {empty_count}/{len(batch_chosen)} 个空响应")
        
        all_chosen.extend(batch_chosen)
        
        logger.info(f"API批次 [{api_batch_idx+1}-{api_batch_end}] 完成")
    
    logger.info(f"阶段2完成: 共生成 {len(all_chosen)} 条Chosen结果")
    
    # ✅ 全局验证
    logger.info("开始数据质量检查...")
    assert len(all_chosen) == len(all_data), \
        f"Chosen数量不匹配: 期望 {len(all_data)}, 实际 {len(all_chosen)}"
    
    # 检查空值
    empty_indices = [i for i, c in enumerate(all_chosen) if not c]
    if empty_indices:
        logger.error(f"❌ 发现 {len(empty_indices)} 个空chosen值")
        logger.error(f"   空值索引（前10个）: {empty_indices[:10]}")
        raise ValueError(f"有 {len(empty_indices)} 个chosen为空，无法生成有效DPO数据")
    
    logger.info(f"✅ 数据质量检查通过: {len(all_chosen)} 条chosen全部非空")
    
    # ===== 阶段3: 组装所有DPO数据并保存为JSONL =====
    logger.info("=" * 60)
    logger.info("阶段3/3: 组装DPO数据并保存为JSONL格式")
    logger.info("=" * 60)
    
    # ✅ 预检查所有列表长度
    logger.info("预检查数据完整性...")
    assert len(all_data) == len(all_diffs) == len(all_rejected) == len(all_chosen), \
        f"数据长度不一致: data={len(all_data)}, diffs={len(all_diffs)}, " \
        f"rejected={len(all_rejected)}, chosen={len(all_chosen)}"
    
    # 检查非空率
    non_empty_chosen = sum(1 for c in all_chosen if c)
    non_empty_rejected = sum(1 for r in all_rejected if r)
    logger.info(f"Chosen非空率: {non_empty_chosen}/{len(all_chosen)} ({non_empty_chosen/len(all_chosen)*100:.1f}%)")
    logger.info(f"Rejected非空率: {non_empty_rejected}/{len(all_rejected)} ({non_empty_rejected/len(all_rejected)*100:.1f}%)")
    
    if non_empty_chosen < len(all_chosen) * 0.9:
        logger.error(f"❌ Chosen非空率过低: {non_empty_chosen/len(all_chosen)*100:.1f}%")
        raise ValueError("Chosen数据质量不足，建议检查API配置")
    
    logger.info("✅ 数据完整性检查通过")
    
    # 确保输出目录存在
    dpo_file.parent.mkdir(parents=True, exist_ok=True)
    # 打开文件以追加模式（如果是续传）或写入模式（如果是新开始）
    file_mode = 'a' if start_idx > 0 else 'w'
    
    saved_count = 0
    with open(dpo_file, file_mode, encoding='utf-8') as f:
        for idx, item in enumerate(tqdm(all_data, desc="组装并保存JSONL")):
            i = item['index']
            question = item['question']
            diff = all_diffs[idx]
            rejected = all_rejected[idx]
            chosen = all_chosen[idx]
            
            # 构建符合DPO训练格式的数据
            dpo_item = {
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates reusable problem-solving principles."
                    },
                    {
                        "role": "user",
                        "content": f"Input: Question: {question}\nError Points: {diff}\nOutput: Reusable principles"
                    },
                    {
                        "role": "assistant",
                        "content": chosen
                    }
                ],
                "rejected_response": rejected
            }
            
            # 写入JSONL格式（每行一个JSON对象）
            f.write(json.dumps(dpo_item, ensure_ascii=False) + '\n')
            saved_count += 1
            
            # 定期刷新缓冲区并保存进度
            if saved_count % config.SAVE_FREQUENCY == 0:
                f.flush()  # 确保数据写入磁盘
                logger.info(f"已保存 {saved_count}/{total_items} 条到JSONL")
                
                # 保存进度
                progress_file.parent.mkdir(parents=True, exist_ok=True)
                with open(progress_file, 'w', encoding='utf-8') as pf:
                    json.dump({
                        'processed_count': i + 1,
                        'total_count': len(dataset),
                        'last_processed_index': i
                    }, pf, indent=2)

    logger.info(f"DPO数据生成完成: {dpo_file}")
    logger.info(f"共保存 {saved_count} 条数据到JSONL格式")
        
    # 处理完成后删除进度文件
    if progress_file.exists():
        progress_file.unlink()
    

def main():
    """
    主函数：支持多数据集加载和处理
    
    使用方式：
    1. 通过环境变量指定数据集：
       export DATASET_NAME=gsm8k
       export DATASET_PATH=dataset/gsm8k/test.jsonl
       python stage_first.py
    
    2. 默认使用 original_data 文件（兼容旧逻辑）
    """
    # ==================== 数据集选择逻辑 ====================
    # 支持通过环境变量指定数据集，或使用默认的 original_data
    # =======================================================
    
    dataset_name = os.getenv('DATASET_NAME', 'deepscaler')  # 默认为 deepscaler（原有格式）
    dataset_path = os.getenv('DATASET_PATH', config.original_data_file)
    
    logger.info("=" * 60)
    logger.info(f"数据集名称: {dataset_name}")
    logger.info(f"数据集路径: {dataset_path}")
    logger.info("=" * 60)
    
    input_file = Path(dataset_path)
    if not input_file.exists():
        logger.error(f"输入文件不存在: {input_file}")
        print(f"[✘] 错误: 输入文件不存在 - {input_file}")
        return
    
    try:
        # ==================== 数据集加载分支 ====================
        # 如果是支持的数据集名称，使用数据集适配层
        # 否则使用原有的直接加载逻辑（兼容 deepscaler 格式）
        # =======================================================
        
        if dataset_name in DATASET_PREPROCESSORS:
            # 新逻辑：使用数据集适配层
            logger.info(f"使用数据集适配层加载: {dataset_name}")
            dataset = load_and_preprocess_dataset(dataset_name, dataset_path)
        else:
            # 原有逻辑：直接加载 JSON 文件（兼容 deepscaler 等格式）
            logger.info(f"使用原有逻辑加载数据集: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
        
        logger.info(f"数据集加载成功，共 {len(dataset)} 条数据")
        
    except Exception as e:
        logger.error(f"加载数据集失败: {e}", exc_info=True)
        print(f"[✘] 错误: 无法加载数据集 - {e}")
        return
    
    # ==================== 核心处理流程（保持不变） ====================
    # 此处调用的 prepare_stage1 函数完全不变
    # 数据集已在上方被统一转换为标准格式
    # =================================================================
    prepare_stage1(dataset)


if __name__ == "__main__":
    main()