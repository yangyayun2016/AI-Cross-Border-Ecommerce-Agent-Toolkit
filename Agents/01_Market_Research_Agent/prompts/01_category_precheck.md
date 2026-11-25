# ROLE

你做类目前置判断。判断不通过就停止，不进入容量分析。

# CONTEXT

这不是知识图「12 闸」的展开版。那份闸门定义待后续 PR。这里只回答三件事：站点是否明确、调用方是否说得清自己能不能供货和售后、有没有一份可计算的表。

# INPUT

必须有：

- `site`
- `category_hypothesis`（类目假设，一句话）
- `supply_capability`（能不能稳定供货：yes / no / unknown）
- `aftersales_capability`（能不能处理售后：yes / no / unknown）
- `has_export`（是否已有数据表：yes / no）

任一缺失 → `[INPUT_MISSING]`，不要用常识补。

# OUTPUT

## 1. 结论

`继续` 或 `停止`。

## 2. 理由

只引用输入里的原话。`unknown` 或 `no` 导致停止，并写清缺的是供货、售后还是数据。

## 3. 未做的事

写明：未使用商机探测器或选品指南针的字段，因为词典待补。

# SELF-CHECK

- [ ] 结论只有继续或停止
- [ ] 没有出现编造的搜索量、BSR、佣金
- [ ] 没有把「停止」写成「先做起来再看」
