# 快速开始指南 (Quick Start)

## 🚀 5分钟快速上手

### 前置条件
- Python 3.7+
- 已安装依赖（见 `requirements.txt`）
- 配置文件 `config.py` 正确设置

---

## 步骤 1: 验证预处理功能

运行验证脚本，确保所有数据集预处理正常：

```powershell
python test_preprocessing.py
```

**预期输出：**
```
========================================
数据集预处理验证测试
========================================

测试数据集: gsm8k
✅ 加载成功！
📊 数据总数: 1320 条
...
✅ 所有数据格式正确！
```

---

## 步骤 2: 选择一个数据集运行

### 方式 A: 使用示例脚本（推荐）

```powershell
.\run_stage_first_examples.ps1
```

然后选择一个数据集（1-6）。

### 方式 B: 手动设置环境变量

**处理 GSM8K（最简单）：**
```powershell
$env:DATASET_NAME = "gsm8k"
$env:DATASET_PATH = "dataset/gsm8k/test.jsonl"
python stage_first.py
```

**处理 BBH（单个任务）：**
```powershell
$env:DATASET_NAME = "bbh"
$env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
python stage_first.py
```

---

## 步骤 3: 查看输出

处理完成后，检查输出文件：

```powershell
# 查看 DPO 数据文件
Get-Content output/dpo_final.jsonl -TotalCount 3

# 查看日志
Get-Content logs/stage_first.log -Tail 50
```

---

## 📊 处理流程说明

```
开始
  ↓
加载数据集 (根据 DATASET_NAME)
  ↓
预处理 → 统一格式 {"question": str, "answer": str}
  ↓
阶段1: vLLM 批量推理 (Baseline + Diff + Rejected)
  ↓
阶段2: API 并发生成 (Chosen)
  ↓
阶段3: 组装并保存为 DPO JSONL
  ↓
完成！
```

---

## 🔧 常用配置

### 调整批处理大小
```powershell
$env:BATCH_SIZE = "32"  # 默认 64
```

### 调整 API 并发数
```powershell
$env:MAX_WORKERS = "10"  # 默认 20
```

### 指定自定义输出路径
编辑 `config.py`：
```python
dpo_final_file = "output/my_custom_output.jsonl"
```

---

## 📝 各数据集特点

| 数据集 | 数据量 | 文件格式 | 处理时间估算 |
|--------|--------|----------|-------------|
| gsm8k | ~1300 | JSONL | 中 |
| math | ~500 | JSONL | 短 |
| bbh (单任务) | ~250 | JSON | 短 |
| mmlu | ~20万 | JSON | 长 ⚠️ |
| svamp | ~1200 | JSON | 中 |

**注意：** MMLU 数据量极大，建议：
1. 使用子集测试
2. 增加 `BATCH_SIZE` 和 `MAX_WORKERS`
3. 使用断点续传功能

---

## 🛠️ 常见问题速查

### Q: "文件不存在"错误
**A:** 检查 `DATASET_PATH` 是否正确，使用相对路径或绝对路径。

### Q: "不支持的数据集"错误
**A:** 确保 `DATASET_NAME` 是以下之一：
- `gsm8k`, `math`, `bbh`, `mmlu`, `svamp`

### Q: 如何处理所有 BBH 任务？
**A:** 编写循环脚本：
```powershell
Get-ChildItem dataset/bbh/*.json | ForEach-Object {
    $env:DATASET_NAME = "bbh"
    $env:DATASET_PATH = $_.FullName
    python stage_first.py
}
```

### Q: 如何恢复中断的任务？
**A:** 脚本支持自动断点续传，只需再次运行相同命令。

---

## 📚 下一步

1. **查看完整文档**: `DATASET_PREPROCESSING_README.md`
2. **了解扩展方法**: 参考 README 中的"扩展新数据集"章节
3. **查看重构总结**: `REFACTORING_SUMMARY.md`

---

## 🎯 快速命令参考

```powershell
# 验证预处理
python test_preprocessing.py

# 使用示例脚本
.\run_stage_first_examples.ps1

# 处理 GSM8K
$env:DATASET_NAME="gsm8k"; $env:DATASET_PATH="dataset/gsm8k/test.jsonl"; python stage_first.py

# 处理 MATH
$env:DATASET_NAME="math"; $env:DATASET_PATH="dataset/math/test.jsonl"; python stage_first.py

# 处理 BBH
$env:DATASET_NAME="bbh"; $env:DATASET_PATH="dataset/bbh/boolean_expressions.json"; python stage_first.py

# 处理 MMLU (小心数据量大)
$env:DATASET_NAME="mmlu"; $env:DATASET_PATH="dataset/mmlu/test.json"; python stage_first.py

# 处理 SVAMP
$env:DATASET_NAME="svamp"; $env:DATASET_PATH="dataset/svamp/test.json"; python stage_first.py

# 使用默认数据集
python stage_first.py
```

---

**准备好了吗？开始你的第一次运行！** 🚀

```powershell
python test_preprocessing.py
```
