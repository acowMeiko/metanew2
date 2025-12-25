# GPU分配说明

## 为什么不能同时运行多个数据集？

**问题原因：**
1. vLLM使用全局单例模式，一个Python进程只能有一个vLLM实例
2. 多个进程同时初始化vLLM时会争夺GPU资源
3. 新进程启动会导致旧进程的GPU上下文失效，造成第一个任务退出

## 解决方案

### 方案1：使用不同的GPU（推荐）✅

为每个数据集分配独立的GPU组，避免资源冲突：

| 数据集 | GPU | 脚本 | 预计时间 |
|--------|-----|------|----------|
| BBH | 0,1 | `run_bbh.sh` | ~6小时 (27任务) |
| GSM8K | 2,3 | `run_gsm8k.sh` | ~2小时 |
| MATH | 4,5 | `run_math.sh` | ~1小时 |
| MMLU | 6,7 | `run_mmlu.sh` | ~12小时 (4文件) |
| SVAMP | 0,1 | `run_svamp.sh` | ~30分钟 |

**并行运行命令：**
```bash
# 自动化并行启动（推荐）
bash run_parallel_all.sh

# 或手动启动
nohup bash run_bbh.sh > run_bbh.out 2>&1 &
nohup bash run_mmlu.sh > run_mmlu.out 2>&1 &
nohup bash run_gsm8k.sh > run_gsm8k.out 2>&1 &
nohup bash run_math.sh > run_math.out 2>&1 &
```

**监控命令：**
```bash
# 查看所有运行的脚本
ps aux | grep "run_.*\.sh"

# 查看GPU使用情况
nvidia-smi

# 实时监控日志
tail -f run_bbh.out
tail -f run_mmlu.out
tail -f run_gsm8k.out
tail -f run_math.out
```

### 方案2：顺序运行（GPU不足时）

如果GPU数量少于8个，建议顺序运行：

```bash
bash run_all_datasets.sh
```

这个脚本会依次处理所有数据集，完成一个再开始下一个。

### 方案3：分批并行运行

如果只有4个GPU（2组），可以分批运行：

**第一批：**
```bash
nohup bash run_bbh.sh > run_bbh.out 2>&1 &    # GPU 0,1
nohup bash run_mmlu.sh > run_mmlu.out 2>&1 &  # GPU 2,3
```

**第二批（等第一批完成后）：**
```bash
nohup bash run_gsm8k.sh > run_gsm8k.out 2>&1 & # GPU 0,1
nohup bash run_math.sh > run_math.out 2>&1 &   # GPU 2,3
```

## 修改GPU分配

如果需要使用不同的GPU，编辑对应脚本的`CUDA_VISIBLE_DEVICES`变量：

```bash
# 例如让BBH使用GPU 4,5
export CUDA_VISIBLE_DEVICES="4,5"
```

## 当前配置

所有脚本已配置为：
- ✅ 使用独立的GPU组
- ✅ 输出到独立的子文件夹
- ✅ 独立的日志文件
- ✅ 支持并行运行

## 输出文件结构

```
output/
├── bbh/
│   ├── dpo_boolean_expressions.jsonl
│   ├── dpo_causal_judgement.jsonl
│   └── ... (最多27个文件)
├── mmlu/
│   ├── dpo_auxiliary_train.jsonl
│   ├── dpo_dev.jsonl
│   ├── dpo_test.jsonl
│   └── dpo_validation.jsonl
├── gsm8k/
│   └── dpo_gsm8k.jsonl
├── math/
│   └── dpo_math.jsonl
└── svamp/
    └── dpo_svamp.jsonl
```

## 注意事项

1. **确保GPU可用**：运行前检查 `nvidia-smi` 确认GPU未被占用
2. **内存要求**：每个vLLM实例需要约30-40GB显存（使用2张80GB A800）
3. **进程隔离**：每个脚本运行在独立的Python进程中
4. **日志监控**：定期检查日志文件，确保没有OOM或其他错误
5. **中断恢复**：如果中断，删除对应的输出文件后重新运行即可

## 故障排查

**问题：第二个脚本启动后第一个退出**
- 原因：GPU冲突
- 解决：确保`CUDA_VISIBLE_DEVICES`设置不重复

**问题：OOM（内存不足）**
- 原因：BATCH_SIZE太大
- 解决：降低`BATCH_SIZE`（如从128降到64）

**问题：进程卡死**
- 原因：可能某个样本太长
- 解决：已添加prompt长度检测，会自动跳过超长样本
