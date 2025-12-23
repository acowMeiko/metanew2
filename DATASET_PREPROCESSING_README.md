# Stage First - 多数据集 DPO 数据生成脚本

## 📋 概述

`stage_first.py` 是一个支持多种数据集格式的 DPO (Direct Preference Optimization) 训练数据生成脚本。

### 核心特性

- ✅ **多数据集支持**：支持 GSM8K, MATH, BBH, MMLU, SVAMP 等5种数据集
- ✅ **统一格式转换**：自动将不同格式转换为标准格式
- ✅ **易于扩展**：采用注册表模式，新增数据集只需3步
- ✅ **向后兼容**：完全兼容原有 deepscaler 格式
- ✅ **核心逻辑不变**：prepare_stage1 保持原有语义

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     main() 入口                              │
│  - 读取环境变量 (DATASET_NAME, DATASET_PATH)                │
│  - 选择加载方式                                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
         ┌─────────────────────────────────┐
         │   是否为注册的数据集？           │
         └──────┬──────────────────┬────────┘
                │ 是               │ 否
                ▼                  ▼
┌───────────────────────┐  ┌─────────────────┐
│  数据集适配层          │  │  原有加载逻辑   │
│  load_and_preprocess  │  │  (直接加载JSON)  │
└───────┬───────────────┘  └────────┬────────┘
        │                           │
        │ ┌─────────────────────┐   │
        ├─│ preprocess_gsm8k    │   │
        ├─│ preprocess_math     │   │
        ├─│ preprocess_bbh      │   │
        ├─│ preprocess_mmlu     │   │
        └─│ preprocess_svamp    │   │
          └─────────┬───────────┘   │
                    │               │
                    ▼               ▼
         ┌──────────────────────────────┐
         │  统一格式数据集               │
         │  [{"question": str,          │
         │    "answer": str}, ...]      │
         └──────────┬───────────────────┘
                    │
                    ▼
         ┌──────────────────────────────┐
         │  prepare_stage1(dataset)     │
         │  【核心逻辑，完全不变】        │
         │  - vLLM 推理                  │
         │  - API 生成 Chosen            │
         │  - 组装 DPO JSONL             │
         └──────────────────────────────┘
```

---

## 📦 支持的数据集

| 数据集 | 原始格式 | Question 来源 | Answer 来源 | 说明 |
|--------|----------|--------------|-------------|------|
| **gsm8k** | JSONL | `question` | `answer` | 数学应用题，已是标准格式 |
| **math** | JSONL | `problem` | `answer` | 高等数学题，需字段映射 |
| **bbh** | JSON | `examples[*].input` | `examples[*].target` | Big-Bench Hard，遍历 examples |
| **mmlu** | JSON | `full_question` 或 `question+choices` | `choices[answer_idx]` | 多选题，需组合问题和选项 |
| **svamp** | JSON | `Body + Question` | `Answer` (转字符串) | 数学应用题，需拼接问题 |
| **deepscaler** | JSON | `problem` 或 `question` | `answer` | 原有格式（默认） |

---

## 🚀 使用方法

### 方法 1: 使用环境变量（推荐）

**处理 GSM8K 数据集：**
```powershell
$env:DATASET_NAME = "gsm8k"
$env:DATASET_PATH = "dataset/gsm8k/test.jsonl"
python stage_first.py
```

**处理 MATH 数据集：**
```powershell
$env:DATASET_NAME = "math"
$env:DATASET_PATH = "dataset/math/test.jsonl"
python stage_first.py
```

**处理 BBH 数据集（单个任务）：**
```powershell
$env:DATASET_NAME = "bbh"
$env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
python stage_first.py
```

**处理 MMLU 数据集：**
```powershell
$env:DATASET_NAME = "mmlu"
$env:DATASET_PATH = "dataset/mmlu/test.json"
python stage_first.py
```

**处理 SVAMP 数据集：**
```powershell
$env:DATASET_NAME = "svamp"
$env:DATASET_PATH = "dataset/svamp/test.json"
python stage_first.py
```

### 方法 2: 使用默认配置（兼容原有逻辑）

```powershell
python stage_first.py
```
默认使用 `data/original_data/merged_all_levels.json`

### 方法 3: 使用示例脚本（交互式）

```powershell
.\run_stage_first_examples.ps1
```
脚本会展示所有示例并提供交互式选择。

---

## 🔧 扩展新数据集

只需 **3 步**，无需修改核心逻辑：

### Step 1: 实现预处理函数

在 `stage_first.py` 的数据集适配层中添加：

```python
def preprocess_new_dataset(raw_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    预处理新数据集
    
    原始格式: {...}
    目标格式: {"question": str, "answer": str}
    """
    logger.info(f"预处理新数据集: {len(raw_data)} 条")
    return [
        {
            "question": item.get("your_question_field", ""),
            "answer": item.get("your_answer_field", "")
        }
        for item in raw_data
        if item.get("your_question_field") and item.get("your_answer_field")
    ]
```

### Step 2: 注册到预处理器表

```python
DATASET_PREPROCESSORS: Dict[str, Callable] = {
    "gsm8k": preprocess_gsm8k,
    "math": preprocess_math,
    "bbh": preprocess_bbh,
    "mmlu": preprocess_mmlu,
    "svamp": preprocess_svamp,
    "new_dataset": preprocess_new_dataset,  # 新增这行
}
```

### Step 3: 使用新数据集

```powershell
$env:DATASET_NAME = "new_dataset"
$env:DATASET_PATH = "dataset/new_dataset/data.json"
python stage_first.py
```

**完成！** 无需修改其他任何代码。

---

## 📝 数据格式说明

### 输入格式（多样）

不同数据集有不同的原始格式，例如：

**GSM8K (JSONL):**
```jsonl
{"question": "Janet's ducks lay 16 eggs...", "answer": "Janet sells 9 eggs..."}
```

**MATH (JSONL):**
```jsonl
{"problem": "Convert the point (0,3)...", "answer": "\\left( 3, \\frac{\\pi}{2} \\right)"}
```

**BBH (JSON):**
```json
{
  "examples": [
    {"input": "not ( True ) and ( True ) is", "target": "False"},
    {"input": "True and not not ( not False ) is", "target": "True"}
  ]
}
```

**MMLU (JSON):**
```json
[
  {
    "question": "Find the degree for the given field extension...",
    "choices": ["0", "4", "2", "6"],
    "answer": "B",
    "answer_idx": 1
  }
]
```

### 输出格式（统一）

所有数据集经过预处理后统一为：

```json
[
  {
    "question": "问题内容",
    "answer": "答案内容"
  }
]
```

### DPO 最终格式（不变）

```jsonl
{"messages": [...], "rejected_response": "..."}
{"messages": [...], "rejected_response": "..."}
```

---

## ⚙️ 配置参数

通过环境变量配置：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DATASET_NAME` | 数据集名称 | `deepscaler` |
| `DATASET_PATH` | 数据集路径 | `data/original_data/merged_all_levels.json` |
| `BATCH_SIZE` | vLLM 批处理大小 | `64` |
| `MAX_WORKERS` | API 并发数 | `20` |
| `SAVE_FREQUENCY` | 保存频率 | `50` |

---

## 🔍 关键代码解析

### 1. 预处理器注册表

```python
DATASET_PREPROCESSORS: Dict[str, Callable] = {
    "gsm8k": preprocess_gsm8k,
    "math": preprocess_math,
    # ...
}
```

采用字典映射，避免大量 if/elif，易于扩展。

### 2. 统一加载接口

```python
def load_and_preprocess_dataset(dataset_name: str, dataset_path: str) -> List[Dict[str, str]]:
    """数据集适配入口"""
    preprocessor = DATASET_PREPROCESSORS[dataset_name]
    processed_data = preprocessor(raw_data)
    return processed_data
```

统一入口，自动调用对应预处理器。

### 3. main 函数分支逻辑

```python
if dataset_name in DATASET_PREPROCESSORS:
    # 新逻辑：使用数据集适配层
    dataset = load_and_preprocess_dataset(dataset_name, dataset_path)
else:
    # 原有逻辑：直接加载（兼容）
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
```

保持向后兼容，原有代码仍可正常运行。

---

## ⚠️ 注意事项

### 强约束（请务必遵守）

- ✅ **不修改 `prepare_stage1` 核心逻辑**：该函数内部流程完全保持不变
- ✅ **不复制五份 pipeline**：所有数据集共用同一处理流程
- ✅ **不修改 DPO 输出格式**：下游实验依赖该格式
- ✅ **不引入全局副作用**：预处理函数纯函数化

### 字段假设

- **question**: 必须是 `str` 类型，表示完整问题描述
- **answer**: 必须是 `str` 类型，表示答案（数字需转字符串）

### 鲁棒性考虑

所有预处理函数都包含：
- 字段存在性检查 (`item.get(...)`)
- 空值过滤 (`if question and answer`)
- 类型转换 (`str(answer)`)

---

## 📊 处理流程

```
┌─────────────┐
│ 原始数据集   │ (各种格式)
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ 数据集适配层     │ (统一转换)
│ - 字段映射       │
│ - 格式转换       │
│ - 鲁棒性处理     │
└──────┬──────────┘
       │
       ▼
┌────────────────────┐
│ 统一格式数据        │ {"question": str, "answer": str}
└──────┬─────────────┘
       │
       ▼
┌──────────────────────────┐
│ prepare_stage1           │
│ 阶段1: vLLM 批量推理      │
│  - Baseline 答案          │
│  - 差异分析              │
│  - Rejected 原则          │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 阶段2: API 并发生成       │
│  - Chosen 原则            │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 阶段3: 组装并保存         │
│  - DPO JSONL 格式         │
└──────────────────────────┘
```

---

## 🐛 常见问题

### Q1: 如何处理大文件？
A: 脚本支持断点续传，通过 `dpo_progress.json` 记录进度。

### Q2: 新增数据集需要修改多少代码？
A: 只需新增一个预处理函数（约10-30行）并注册，其他代码完全不变。

### Q3: 如何验证预处理是否正确？
A: 查看日志中的 `[数据集适配层]` 部分，会显示加载和预处理的详细信息。

### Q4: 原有的 deepscaler 数据还能用吗？
A: 完全兼容！不设置环境变量时默认使用原有逻辑。

### Q5: 如何处理多个 BBH 任务文件？
A: 每个任务文件单独运行，或编写脚本批量处理所有任务。

---

## 📚 相关文件

- `stage_first.py` - 主脚本（已重构）
- `run_stage_first_examples.ps1` - 示例运行脚本
- `DATASET_PREPROCESSING_README.md` - 本文档
- `config.py` - 配置文件
- `module/execute_module.py` - vLLM 推理模块
- `module/plan_module.py` - API 生成模块

---

## 📄 许可

本项目遵循原有项目的许可协议。

---

## 🤝 贡献

如需新增数据集支持，请：
1. 实现预处理函数
2. 注册到 `DATASET_PREPROCESSORS`
3. 提交 PR 并附上示例数据

---

**最后更新**: 2025-12-23
