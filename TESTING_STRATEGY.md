# 测试策略文档

## 📋 测试需求分析

### 代码依赖项
根据 `stage_first.py` 分析，完整运行需要：

| 依赖 | 需求 | 可本地测试 | 说明 |
|------|------|-----------|------|
| **数据加载** | 数据集文件 | ✅ 是 | 只需要数据文件即可 |
| **数据预处理** | Python 标准库 | ✅ 是 | 无特殊依赖 |
| **vLLM 推理** | GPU + vLLM + 模型 | ❌ 否 | 需要服务器环境 |
| **API 调用** | 外部 API 服务 | ❌ 否 | 需要服务器环境 |
| **DPO 生成** | 完整流程 | ❌ 否 | 需要服务器环境 |

---

## 🎯 测试方案

### 方案一：本地测试（推荐先执行）⭐

**测试范围：** 数据集加载和预处理逻辑

**优点：**
- ✅ 无需 GPU
- ✅ 无需模型
- ✅ 无需 API
- ✅ 快速验证（秒级）
- ✅ 可立即执行

**测试内容：**
1. 数据文件是否存在
2. 数据加载是否正确（JSON/JSONL）
3. 预处理函数是否工作
4. 输出格式是否符合要求 `{"question": str, "answer": str}`
5. 字段完整性检查

**执行方式：**
```powershell
# 运行本地测试
python test_local_preprocessing.py
```

**预期输出：**
```
✅ 所有测试通过! 预处理逻辑工作正常。
✅ 可以在服务器上运行完整的 DPO 生成流程。
```

---

### 方案二：服务器端到端测试（本地测试通过后）

**测试范围：** 完整 DPO 数据生成流程

**需求：**
- ✅ GPU 环境
- ✅ vLLM 模型加载
- ✅ API 服务可用
- ✅ 足够的磁盘空间

**测试方式：**

#### 1. 小数据集测试（推荐）
选择数据量小的数据集先测试：

```powershell
# BBH 单任务（约 250 条数据）
$env:DATASET_NAME = "bbh"
$env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
python stage_first.py
```

**预期时间：** 根据 GPU 性能，约 10-30 分钟

#### 2. 中等数据集测试
```powershell
# SVAMP（约 1000 条数据）
$env:DATASET_NAME = "svamp"
$env:DATASET_PATH = "dataset/svamp/test.json"
python stage_first.py
```

#### 3. 大数据集测试
```powershell
# GSM8K（约 1300 条数据）
$env:DATASET_NAME = "gsm8k"
$env:DATASET_PATH = "dataset/gsm8k/test.jsonl"
python stage_first.py
```

---

## 🚀 推荐测试流程

### 第一步：本地预检查 ✅ **立即可做**

```powershell
# 1. 运行本地测试脚本
python test_local_preprocessing.py

# 预期结果：
# ✅ 所有数据集加载正常
# ✅ 格式转换正确
# ✅ 无报错
```

**如果本地测试失败：**
- 检查数据集文件是否存在
- 检查文件路径是否正确
- 查看错误信息，修复预处理逻辑

---

### 第二步：服务器环境检查 ⚙️ **服务器环境**

```powershell
# 1. 检查 Python 环境
python --version  # 需要 Python 3.8+

# 2. 检查依赖包
python -c "import json; import pathlib; print('✅ 标准库正常')"

# 3. 检查 vLLM（如果需要）
python -c "import vllm; print('✅ vLLM 可用')"

# 4. 检查模型路径
ls /home/share/hcz/qwen2.5-14b-awq
```

---

### 第三步：小数据集端到端测试 🧪 **服务器环境**

```powershell
# 使用 BBH 单任务（最小数据集）
$env:DATASET_NAME = "bbh"
$env:DATASET_PATH = "dataset/bbh/boolean_expressions.json"
$env:BATCH_SIZE = "8"  # 小批次，降低显存需求
python stage_first.py
```

**验证项：**
1. ✅ 数据加载日志正常
2. ✅ 看到 `[数据集适配层]` 相关日志
3. ✅ vLLM 推理运行正常
4. ✅ API 调用正常
5. ✅ 生成 `output/dpo_final.jsonl`
6. ✅ 输出格式正确

**检查输出：**
```powershell
# 查看生成的文件
ls output/dpo_final.jsonl

# 查看第一条数据
Get-Content output/dpo_final.jsonl -TotalCount 1 | ConvertFrom-Json | ConvertTo-Json -Depth 10

# 检查格式是否为：
# {
#   "messages": [...],
#   "rejected_response": "..."
# }
```

---

### 第四步：全量测试 🚀 **服务器环境**

```powershell
# 依次测试所有数据集
$datasets = @(
    @{name="gsm8k"; path="dataset/gsm8k/test.jsonl"},
    @{name="math"; path="dataset/math/test.jsonl"},
    @{name="svamp"; path="dataset/svamp/test.json"}
)

foreach ($ds in $datasets) {
    Write-Host "测试 $($ds.name)..." -ForegroundColor Green
    $env:DATASET_NAME = $ds.name
    $env:DATASET_PATH = $ds.path
    python stage_first.py
}
```

---

## 📊 测试检查清单

### 本地测试检查项 ✅
- [ ] `test_local_preprocessing.py` 运行无报错
- [ ] 所有5个数据集都能正确加载
- [ ] 输出格式符合 `{"question": str, "answer": str}`
- [ ] 样本数据显示正常
- [ ] 统计信息合理

### 服务器测试检查项 ⚙️
- [ ] Python 环境正常
- [ ] vLLM 可用
- [ ] 模型路径正确
- [ ] GPU 可用且显存充足
- [ ] API 服务可访问

### 端到端测试检查项 🧪
- [ ] 日志中看到 `[数据集适配层]` 标识
- [ ] 预处理完成日志：`预处理完成: XXX 条有效数据`
- [ ] vLLM 批量推理正常运行
- [ ] API 调用成功
- [ ] 生成 `output/dpo_final.jsonl`
- [ ] JSONL 格式正确
- [ ] 每行都是有效的 JSON 对象
- [ ] 包含 `messages` 和 `rejected_response` 字段

---

## 🐛 常见问题和解决方案

### 问题 1：文件不存在
```
❌ 文件不存在: dataset/xxx/test.jsonl
```

**解决：**
```powershell
# 检查文件是否存在
ls dataset/gsm8k/test.jsonl

# 如果不存在，检查路径或下载数据集
```

### 问题 2：导入错误
```
ModuleNotFoundError: No module named 'xxx'
```

**解决：**
```powershell
# 安装缺失的包
pip install xxx
```

### 问题 3：vLLM 显存不足
```
OutOfMemoryError: CUDA out of memory
```

**解决：**
```powershell
# 降低批次大小
$env:BATCH_SIZE = "8"  # 或更小
python stage_first.py
```

### 问题 4：预处理格式错误
```
⚠️ 发现 X 个格式问题
```

**解决：**
1. 查看具体错误信息
2. 检查对应的 `preprocess_xxx()` 函数
3. 修复字段映射逻辑
4. 重新运行本地测试

---

## 📝 测试报告模板

### 本地测试报告
```
测试时间: 2025-12-23
测试环境: Windows 本地
测试脚本: test_local_preprocessing.py

测试结果:
  ✅ gsm8k  : 通过 (1319 条数据)
  ✅ math   : 通过 (500 条数据)
  ✅ bbh    : 通过 (250 条数据)
  ✅ mmlu   : 通过 (14042 条数据)
  ✅ svamp  : 通过 (1000 条数据)

结论: 所有预处理逻辑工作正常，可以在服务器上测试。
```

### 服务器测试报告
```
测试时间: 2025-12-23
测试环境: 服务器 GPU 环境
测试数据集: bbh/boolean_expressions (250 条)

阶段1 (vLLM 推理): ✅ 完成
  - Baseline 答案生成: 正常
  - 差异分析生成: 正常
  - Rejected 原则生成: 正常

阶段2 (API Chosen): ✅ 完成
  - API 调用成功: 250/250

阶段3 (组装保存): ✅ 完成
  - 生成文件: output/dpo_final.jsonl
  - 数据条数: 250
  - 格式验证: 正确

结论: 端到端流程正常，可以处理其他数据集。
```

---

## 🎯 测试建议

### 立即可做（本地）：
1. ✅ **运行 `test_local_preprocessing.py`**
   - 验证数据加载和格式转换
   - 无需 GPU/模型/API
   - 耗时：< 1 分钟

### 需要服务器环境：
2. ⚙️ **小数据集测试（BBH）**
   - 验证完整流程
   - 数据量小，快速验证
   - 耗时：约 10-30 分钟

3. 🚀 **全量测试（可选）**
   - 所有数据集
   - 生产环境验证
   - 耗时：数小时

---

## ✅ 总结

**推荐测试顺序：**

1. **本地测试** → 验证预处理逻辑（立即可做）
2. **服务器小测试** → 验证完整流程（BBH 单任务）
3. **服务器全量测试** → 生产环境验证（可选）

**本地测试通过后，即可确认：**
- ✅ 所有预处理函数正确
- ✅ 数据格式转换正确
- ✅ 代码逻辑无误
- ✅ 可以放心在服务器上运行

---

**立即执行本地测试：**
```powershell
python test_local_preprocessing.py
```
