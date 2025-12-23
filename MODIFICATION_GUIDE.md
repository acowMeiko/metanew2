# Stage First 重构修改说明 (Modification Guide)

## 📋 修改概览

本次重构为 `stage_first.py` 添加了多数据集支持，同时完全保持核心逻辑不变。

---

## ✅ 修改的文件

### 1. **stage_first.py** (主脚本)

#### 修改类型：重构 + 扩展

#### 主要修改：

**A. 导入和常量（行 1-63）**
- ✅ 添加文件头部文档（45行）
- ✅ 添加 `from typing import List, Dict, Any, Callable`
- ✅ 修复 `from tqdm import tqdm` 导入
- ✅ 添加 `OUTPUTS_DIR = Path(config.output_dir)`

**B. 数据集适配层（行 64-247）⭐ 新增**
- ✅ `preprocess_gsm8k()` - GSM8K 预处理函数
- ✅ `preprocess_math()` - MATH 预处理函数
- ✅ `preprocess_bbh()` - BBH 预处理函数
- ✅ `preprocess_mmlu()` - MMLU 预处理函数
- ✅ `preprocess_svamp()` - SVAMP 预处理函数
- ✅ `DATASET_PREPROCESSORS` - 预处理器注册表
- ✅ `load_and_preprocess_dataset()` - 统一加载接口

**C. 原有逻辑（行 248-523）✅ 完全不变**
- ✅ `batch_answer_questions()` - 保持不变
- ✅ `batch_generate_differences()` - 保持不变
- ✅ `batch_generate_principles_local()` - 保持不变
- ✅ `prepare_stage1()` - **核心函数，完全不变**

**D. main 函数（行 524-609）⭐ 修改**
- ✅ 添加环境变量读取 (`DATASET_NAME`, `DATASET_PATH`)
- ✅ 添加数据集加载分支逻辑
- ✅ 保持向后兼容

---

## 📁 新增的文件

### 1. **DATASET_PREPROCESSING_README.md**
完整的数据集预处理文档，包含：
- 架构设计说明
- 支持的数据集列表
- 使用方法和示例
- 扩展新数据集的详细指南
- 常见问题解答

### 2. **run_stage_first_examples.ps1**
PowerShell 示例脚本，提供：
- 6 个预设示例（5个新数据集 + 1个默认）
- 交互式选择界面
- 自动设置环境变量
- 彩色输出

### 3. **test_preprocessing.py**
验证脚本，用于：
- 快速测试所有预处理函数
- 验证数据格式正确性
- 显示样本数据
- 不运行完整 DPO 流程

### 4. **REFACTORING_SUMMARY.md**
重构总结文档，包含：
- 完成任务清单
- 代码结构说明
- 设计原则验证
- 使用示例
- 扩展示例

### 5. **QUICK_START.md**
快速开始指南，提供：
- 5分钟上手步骤
- 快速命令参考
- 常见问题速查
- 配置说明

### 6. **MODIFICATION_GUIDE.md** (本文件)
修改说明文档

---

## 🎯 核心设计模式

### 1. 注册表模式 (Registry Pattern)

**目的：** 避免大量 if/elif，使代码易于扩展

**实现：**
```python
DATASET_PREPROCESSORS: Dict[str, Callable] = {
    "gsm8k": preprocess_gsm8k,
    "math": preprocess_math,
    "bbh": preprocess_bbh,
    "mmlu": preprocess_mmlu,
    "svamp": preprocess_svamp,
}
```

**使用：**
```python
preprocessor = DATASET_PREPROCESSORS[dataset_name]
processed_data = preprocessor(raw_data)
```

### 2. 策略模式 (Strategy Pattern)

**目的：** 不同数据集使用不同的预处理策略

**实现：**
```python
def load_and_preprocess_dataset(dataset_name: str, dataset_path: str):
    preprocessor = DATASET_PREPROCESSORS[dataset_name]  # 选择策略
    return preprocessor(raw_data)  # 执行策略
```

### 3. 适配器模式 (Adapter Pattern)

**目的：** 将不同格式的数据统一适配为标准格式

**实现：**
```python
def preprocess_xxx(raw_data) -> List[Dict[str, str]]:
    # 各种格式 → {"question": str, "answer": str}
    return processed_data
```

---

## 🔍 关键代码位置

### 数据集适配入口

**文件：** `stage_first.py`  
**行数：** 64-247  
**函数：** `load_and_preprocess_dataset()`

这是所有新数据集的入口点，负责：
1. 检查数据集是否支持
2. 加载原始文件（JSON/JSONL）
3. 调用对应的预处理器
4. 返回统一格式数据

### 核心处理流程（不变）

**文件：** `stage_first.py`  
**行数：** 279-523  
**函数：** `prepare_stage1()`

这是原有的核心逻辑，**完全不变**，包括：
- 阶段1: vLLM 批量推理
- 阶段2: API 并发生成 Chosen
- 阶段3: 组装并保存 DPO JSONL

### 数据集选择逻辑

**文件：** `stage_first.py`  
**行数：** 524-609  
**函数：** `main()`

修改后的 main 函数，负责：
1. 读取环境变量 (`DATASET_NAME`, `DATASET_PATH`)
2. 判断是否使用数据集适配层
3. 调用 `prepare_stage1()`

---

## 📊 代码行数统计

| 部分 | 行数 | 类型 | 说明 |
|------|------|------|------|
| 文件头文档 | 45 | 新增 | 架构和使用说明 |
| 导入和常量 | 18 | 修改 | 修复导入，添加常量 |
| 数据集适配层 | 184 | 新增 | 5个预处理器 + 注册表 + 加载器 |
| 批量推理函数 | 31 | 不变 | 原有逻辑 |
| prepare_stage1 | 245 | **不变** | **核心逻辑完全不变** |
| main 函数 | 86 | 修改 | 添加数据集选择逻辑 |
| **总计** | **609** | - | - |

**新增代码占比：** ~37%  
**修改代码占比：** ~17%  
**不变代码占比：** ~46%

---

## 🚦 向后兼容性

### ✅ 完全兼容原有用法

**原有用法（默认）：**
```powershell
python stage_first.py
```
自动使用 `data/original_data/merged_all_levels.json`

**原有用法（指定文件）：**
```powershell
$env:DATASET_PATH = "data/my_custom_data.json"
python stage_first.py
```

### ✅ 原有数据格式仍然支持

如果数据格式为 deepscaler 风格（包含 `problem`/`question` 和 `answer` 字段），仍然可以直接使用，无需预处理。

---

## 🔧 扩展性

### 新增数据集成本

| 步骤 | 工作量 | 代码量 |
|------|--------|--------|
| 实现预处理函数 | 5-10 分钟 | 10-30 行 |
| 注册到表 | 1 分钟 | 1 行 |
| 测试验证 | 2-5 分钟 | 0 行 |
| **总计** | **8-16 分钟** | **11-31 行** |

### 扩展示例代码

参见 `REFACTORING_SUMMARY.md` 中的"扩展新数据集示例 (AQuA)"。

---

## ⚠️ 注意事项

### 必须遵守的约束

1. ✅ **不修改 `prepare_stage1` 函数**
   - 该函数为核心逻辑，下游依赖其语义
   
2. ✅ **不修改 DPO 输出格式**
   - 输出格式为 JSONL，每行一个 JSON 对象
   - 结构为 `{"messages": [...], "rejected_response": "..."}`

3. ✅ **预处理函数必须返回标准格式**
   - `[{"question": str, "answer": str}, ...]`
   - 所有字段必须是非空字符串

4. ✅ **保持向后兼容**
   - 原有调用方式不能被破坏
   - 默认行为不能改变

### 字段假设

- **question**: 必须包含完整的问题描述（含选项、上下文等）
- **answer**: 必须是最终答案的字符串表示（含解析步骤更佳）

---

## 📝 环境变量说明

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `DATASET_NAME` | str | `"deepscaler"` | 数据集名称 |
| `DATASET_PATH` | str | `config.original_data_file` | 数据集文件路径 |
| `BATCH_SIZE` | int | `64` | vLLM 批处理大小 |
| `MAX_WORKERS` | int | `20` | API 并发线程数 |
| `SAVE_FREQUENCY` | int | `50` | 保存频率（条数） |

---

## 🧪 测试建议

### 1. 验证预处理正确性
```powershell
python test_preprocessing.py
```

### 2. 小数据集测试
先用小数据集（如 BBH 单任务）测试完整流程：
```powershell
$env:DATASET_NAME = "bbh"
$env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
python stage_first.py
```

### 3. 检查输出格式
```powershell
Get-Content output/dpo_final.jsonl -TotalCount 1 | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

---

## 📚 文档索引

- **完整文档**: `DATASET_PREPROCESSING_README.md`
- **快速开始**: `QUICK_START.md`
- **重构总结**: `REFACTORING_SUMMARY.md`
- **修改说明**: `MODIFICATION_GUIDE.md` (本文件)
- **示例脚本**: `run_stage_first_examples.ps1`
- **验证脚本**: `test_preprocessing.py`

---

## 🎓 设计理念

### 关注点分离 (Separation of Concerns)

- **数据集适配层**: 负责格式转换
- **核心处理流程**: 负责 DPO 数据生成
- **main 函数**: 负责流程调度

### 开放封闭原则 (Open-Closed Principle)

- **对扩展开放**: 新增数据集只需注册
- **对修改封闭**: 核心逻辑不需修改

### 单一职责原则 (Single Responsibility Principle)

- 每个预处理函数只负责一种数据集
- 每个函数功能单一，易于测试

---

**重构完成时间**: 2025-12-23  
**兼容性**: 100% 向后兼容  
**测试状态**: 待验证（请运行 `test_preprocessing.py`）

---

如有疑问，请参考其他文档或查看代码中的详细注释。
