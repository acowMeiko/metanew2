# 小批次测试指南

## 📋 概述

为了快速验证完整的 DPO 生成流程，我创建了小批次测试工具，从每个数据集提取前 **128 条**数据（一个批次）进行测试。

---

## 🎯 为什么是 128 条？

- ✅ **正好一个批次**：默认 `BATCH_SIZE=64`，128条可以完整测试2个批次
- ✅ **快速验证**：大约 5-15 分钟即可完成
- ✅ **覆盖完整流程**：包含所有3个阶段（vLLM → API → 保存）
- ✅ **节省资源**：显存占用小，适合首次测试

---

## 🚀 使用方式

### 方式 1: Python 交互式脚本（推荐本地）

```powershell
# Windows PowerShell
python test_small_batch.py
```

**特点**：
- 交互式菜单
- 可选择单个或全部数据集
- 自动创建测试数据
- 详细的进度显示

**使用步骤**：
1. 运行脚本
2. 查看可用数据集列表
3. 输入数字选择数据集，或输入 `all` 测试全部
4. 等待完成

---

### 方式 2: PowerShell 快速脚本（推荐 Windows）

```powershell
.\run_small_batch_test.ps1
```

**特点**：
- 提供3种模式
- 快速测试模式（仅 BBH）
- 彩色输出
- 简单易用

**菜单选项**：
1. **交互式模式** - 调用 Python 脚本
2. **快速测试** - 直接测试 BBH（最快，推荐首次使用）
3. **全部测试** - 测试所有数据集
4. **退出**

---

### 方式 3: Bash 脚本（推荐服务器）

```bash
# 先给脚本执行权限
chmod +x test_small_batch.sh

# 运行
./test_small_batch.sh
```

**特点**：
- 适合 Linux 服务器
- 完整的菜单系统
- 批量处理
- 结果汇总

**菜单选项**：
1. **快速测试** - 仅 BBH
2. **创建测试数据** - 只创建不运行
3. **测试全部** - 创建并测试所有
4. **测试指定** - 选择单个数据集
5. **退出**

---

## 📦 测试数据集

脚本会自动从以下数据集提取前 128 条：

| 数据集 | 原始路径 | 原始数量 | 测试数量 |
|--------|---------|---------|---------|
| **BBH** | `dataset/bbh/boolean_expressions.json` | ~250 | 128 |
| **SVAMP** | `dataset/svamp/test.json` | ~300 | 128 |
| **GSM8K** | `dataset/gsm8k/test.jsonl` | ~1,319 | 128 |
| **MATH** | `dataset/math/test.jsonl` | ~500 | 128 |

测试数据保存在：`data/test_small_batch/`

---

## 🎯 推荐测试流程

### 首次测试（服务器）

```bash
# 1. 运行快速测试（BBH，最小数据集）
./test_small_batch.sh
# 选择: 1 (快速测试)

# 2. 检查输出
ls -lh output/dpo_final.jsonl
head -1 output/dpo_final.jsonl | jq .

# 3. 如果成功，测试其他数据集
./test_small_batch.sh
# 选择: 3 (测试全部)
```

**预期时间**：
- BBH (128条): 5-15 分钟
- 全部 4 个数据集 (512条): 20-60 分钟

---

### 本地准备（Windows）

```powershell
# 1. 创建测试数据（不运行完整流程）
python test_small_batch.py
# 选择创建数据选项

# 2. 验证数据格式
Get-Content data\test_small_batch\bbh_test_128.json | ConvertFrom-Json | Select -First 1

# 3. 将测试数据上传到服务器
# 然后在服务器上运行测试
```

---

## 📊 输出说明

### 测试数据输出

```
data/test_small_batch/
├── bbh_test_128.json       # BBH 测试数据
├── svamp_test_128.json     # SVAMP 测试数据
├── gsm8k_test_128.json     # GSM8K 测试数据
└── math_test_128.json      # MATH 测试数据
```

每个文件格式：
```json
[
  {
    "question": "问题内容...",
    "answer": "答案内容..."
  },
  ...
]
```

### DPO 输出

```
output/
├── dpo_final.jsonl         # 最终 DPO 数据
└── vllm_cache.json         # vLLM 缓存（如果有）
```

---

## ✅ 验证检查项

测试完成后，检查：

### 1. 日志输出
```
✅ 看到 [数据集适配层] 相关日志
✅ 预处理完成: 128 条有效数据
✅ 阶段1完成: vLLM 推理
✅ 阶段2完成: API 生成 Chosen
✅ 阶段3完成: 保存 JSONL
```

### 2. 输出文件
```bash
# 检查文件存在
ls output/dpo_final.jsonl

# 检查行数（应该是 128 行）
wc -l output/dpo_final.jsonl

# 检查格式
head -1 output/dpo_final.jsonl | jq 'keys'
# 应输出: ["messages", "rejected_response"]
```

### 3. 数据格式
```bash
# 查看第一条完整数据
head -1 output/dpo_final.jsonl | jq .

# 验证 messages 结构
head -1 output/dpo_final.jsonl | jq '.messages | length'
# 应输出: 3 (system, user, assistant)

# 验证 rejected_response
head -1 output/dpo_final.jsonl | jq '.rejected_response' -r
# 应输出: 原则内容
```

---

## 🐛 常见问题

### Q1: 如何只创建测试数据不运行？

**A**: 使用 Bash 脚本的选项 2：
```bash
./test_small_batch.sh
# 选择: 2 (创建所有测试数据集)
```

或手动执行：
```python
python -c "
from stage_first import load_and_preprocess_dataset
import json
data = load_and_preprocess_dataset('bbh', 'dataset/bbh/boolean_expressions.json')
with open('test_bbh.json', 'w') as f:
    json.dump(data[:128], f, ensure_ascii=False, indent=2)
"
```

---

### Q2: 如何修改测试批次大小？

**A**: 编辑脚本开头的 `TEST_BATCH_SIZE` 或 `BATCH_SIZE` 变量：

```python
# test_small_batch.py
TEST_BATCH_SIZE = 64  # 改为 64 或其他数字
```

```bash
# test_small_batch.sh
BATCH_SIZE=64  # 改为 64 或其他数字
```

---

### Q3: 测试失败怎么办？

**A**: 检查以下内容：

1. **vLLM 阶段失败**：
   ```bash
   # 检查 GPU 显存
   nvidia-smi
   
   # 降低批次大小
   export BATCH_SIZE=8
   ```

2. **API 阶段失败**：
   ```bash
   # 检查 API 配置
   python -c "import config; print(config.STRONG_MODEL_API_URL)"
   
   # 测试 API 连接
   curl -X POST $STRONG_MODEL_API_URL \
     -H "Authorization: Bearer $STRONG_MODEL_KEY" \
     -d '{"model":"DeepSeek-R1","messages":[{"role":"user","content":"test"}]}'
   ```

3. **内存不足**：
   ```bash
   # 使用更小的批次
   export BATCH_SIZE=4
   ./test_small_batch.sh
   ```

---

### Q4: 可以并行测试多个数据集吗？

**A**: 不建议，因为：
- vLLM 会占用全部 GPU
- API 有并发限制
- 可能导致输出文件冲突

建议按顺序测试。

---

## 📈 性能参考

基于 NVIDIA A100 40GB：

| 数据集 | 数量 | vLLM 阶段 | API 阶段 | 总耗时 |
|--------|------|----------|---------|--------|
| BBH | 128 | 2-5 min | 3-8 min | 5-15 min |
| SVAMP | 128 | 2-5 min | 3-8 min | 5-15 min |
| GSM8K | 128 | 2-5 min | 3-8 min | 5-15 min |
| MATH | 128 | 2-5 min | 3-8 min | 5-15 min |

**总计 (512条)**: 约 20-60 分钟

---

## 🎯 下一步

测试通过后：

1. ✅ **处理完整数据集**
   ```bash
   export DATASET_NAME=gsm8k
   export DATASET_PATH=dataset/gsm8k/test.jsonl
   python stage_first.py
   ```

2. ✅ **批量处理多个数据集**
   ```bash
   for ds in gsm8k math svamp; do
       export DATASET_NAME=$ds
       export DATASET_PATH=dataset/$ds/test.jsonl
       python stage_first.py
   done
   ```

3. ✅ **使用生成的 DPO 数据训练模型**

---

## 📚 相关文档

- **完整文档**: `DATASET_PREPROCESSING_README.md`
- **测试策略**: `TESTING_STRATEGY.md`
- **测试结果**: `TEST_RESULTS.md`
- **快速参考**: `QUICK_REFERENCE.md`

---

**立即开始测试**:

```bash
# 服务器（推荐）
./test_small_batch.sh

# Windows
.\run_small_batch_test.ps1

# 或直接使用 Python
python test_small_batch.py
```

🎉 祝测试顺利！
