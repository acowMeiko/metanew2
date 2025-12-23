# 快速参考指南 (Quick Reference)

## 🎯 立即开始

### 本地测试（无需 GPU）✅ **现在就可以做**

```powershell
# 方式1：运行快速测试脚本
.\run_local_test.ps1

# 方式2：直接运行测试
python test_local_preprocessing.py
```

**结果**: 所有 5 个数据集测试通过 ✅

---

## 📊 测试结果摘要

| 项目 | 结果 |
|------|------|
| **本地测试** | ✅ 5/5 通过 |
| **数据加载** | ✅ 正常 |
| **格式转换** | ✅ 正确 |
| **代码逻辑** | ✅ 无误 |
| **可用性** | ✅ 可在服务器使用 |

---

## 🚀 服务器使用（需要 GPU）

### 方法 1: 使用环境变量（推荐）

```bash
# GSM8K 数据集
export DATASET_NAME=gsm8k
export DATASET_PATH=dataset/gsm8k/test.jsonl
python stage_first.py

# MATH 数据集
export DATASET_NAME=math
export DATASET_PATH=dataset/math/test.jsonl
python stage_first.py

# BBH 数据集（最小，推荐首次测试）
export DATASET_NAME=bbh
export DATASET_PATH=dataset/bbh/boolean_expressions.json
export BATCH_SIZE=8
python stage_first.py
```

### 方法 2: 使用默认配置（原有数据）

```bash
# 使用 data/original_data/merged_all_levels.json
python stage_first.py
```

---

## 📋 支持的数据集

| 数据集 | 说明 | 数据量 | 命令 |
|--------|------|--------|------|
| **gsm8k** | 数学应用题 | 1,319 | `DATASET_NAME=gsm8k` |
| **math** | 高等数学题 | 500 | `DATASET_NAME=math` |
| **bbh** | 推理任务 | 250 | `DATASET_NAME=bbh` |
| **mmlu** | 多选题 | 14,042 | `DATASET_NAME=mmlu` |
| **svamp** | 数学应用题 | 300 | `DATASET_NAME=svamp` |

---

## 🔧 首次服务器测试建议

```bash
# 1. 使用最小数据集（BBH，250条）
export DATASET_NAME=bbh
export DATASET_PATH=dataset/bbh/boolean_expressions.json

# 2. 降低批次大小
export BATCH_SIZE=8

# 3. 运行
python stage_first.py

# 4. 检查输出
ls -lh output/dpo_final.jsonl
head -1 output/dpo_final.jsonl | jq .
```

**预期时间**: 10-30 分钟

---

## ✅ 验证清单

### 本地验证 ✅ 已完成
- [x] 数据加载正常
- [x] 格式转换正确
- [x] 无错误输出
- [x] 所有数据集通过

### 服务器验证 ⚙️ 待执行
- [ ] 小数据集测试（BBH）
- [ ] 查看日志输出
- [ ] 验证 DPO 文件生成
- [ ] 检查输出格式

---

## 📚 文档索引

| 文档 | 用途 | 何时查看 |
|------|------|---------|
| **TEST_RESULTS.md** | 测试结果报告 | 查看测试详情 |
| **TESTING_STRATEGY.md** | 测试策略指南 | 规划测试方案 |
| **DATASET_PREPROCESSING_README.md** | 完整使用文档 | 详细功能说明 |
| **QUICK_START.md** | 快速开始 | 5分钟上手 |
| **MODIFICATION_GUIDE.md** | 修改说明 | 了解代码结构 |

---

## ❓ 常见问题

### Q: 本地测试和服务器测试的区别？
**A**: 
- **本地测试**: 只验证数据加载和格式转换（已完成✅）
- **服务器测试**: 运行完整 DPO 生成流程（需要 GPU）

### Q: 一定要在服务器测试吗？
**A**: 
- 本地测试已验证预处理逻辑正确✅
- 服务器测试验证 vLLM/API 完整流程
- 可直接使用，首次建议用小数据集验证

### Q: 推荐的测试顺序？
**A**: 
1. ✅ 本地测试（已完成）
2. 🔄 服务器小数据集（BBH 250条）
3. 🔄 服务器其他数据集（可选）

### Q: 如何确认服务器测试成功？
**A**: 检查三点：
1. 日志显示 `[数据集适配层]` 相关信息
2. 生成 `output/dpo_final.jsonl` 文件
3. JSONL 格式正确（每行一个JSON，包含 `messages` 和 `rejected_response`）

---

## 🎉 总结

✅ **本地测试全部通过**  
✅ **预处理逻辑验证正确**  
✅ **代码可以直接使用**  
✅ **建议服务器先用 BBH 小数据集测试**

---

**需要帮助？** 查看 `TESTING_STRATEGY.md` 获取详细指南。
