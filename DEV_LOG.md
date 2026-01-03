# 开发日志 - 可爱记账 App

---

## 2026-01-03 OCR 超时和健壮性改进

### 问题描述
1. OCR 扫描经常超时（10秒限制太短）
2. 日期格式错误时没有正确使用当天日期
3. 首页刷新问题仍然存在

### 即将进行的修改
1. 增加 OCR API 超时时间到 60 秒
2. 添加图片压缩功能，减少上传时间
3. 修复日期验证逻辑
4. 添加重试机制
5. 改进前端错误处理

### 修复内容

#### 1. frontend/src/api/ai.ts - OCR API 改进
- 增加超时时间从 10 秒到 60 秒
- 添加图片压缩功能（>500KB 自动压缩）
- 添加重试机制（超时失败自动重试 2 次）
- 压缩后打印日志显示压缩效果

#### 2. frontend/src/components/record/PhotoScanner.vue - 日期验证和错误处理
- 添加 `validateAndFixDate()` 函数，统一处理日期格式
- OCR 返回后立即验证日期，无效日期自动使用当天
- 改进错误提示（超时、网络错误分别提示）
- 添加动态处理状态显示（压缩中、识别中、保存中）

#### 3. frontend/src/stores/transaction.ts - 响应式更新
- 使用 `[...data]` 创建新数组确保 Vue 响应式更新

#### 4. frontend/src/views/Home.vue - 强制刷新
- `onActivated` 总是调用 `initData()` 刷新数据

#### 5. frontend/src/api/transaction.ts - API 路径修复
- 添加尾部斜杠避免 307 重定向

#### 6. frontend/src/components/record/ManualForm.vue - 日期选择器修复
- 添加 CSS 使整个日期输入框可点击
- 添加日历图标
- 扩大点击区域到 48px 高度
- 使用 `router.replace('/')` 优化导航

---

## 2026-01-03 拍照识别OCR功能调试

### 问题描述
用户上传消费截图（微信支付账单），但系统没有识别出金额和商家信息。API 返回 `amount: 0.0`, `merchant: ""`。

### 问题分析
1. 后端 `/api/ai/scan-receipt` 接口返回了 `success: true` 但数据为空
2. 说明 `ai_vision_parse_receipt()` 函数调用失败或返回 None
3. 可能原因：
   - 视觉模型 API 调用失败
   - 模型返回格式不正确
   - 后端代码没有正确重载

### 第一次修复尝试
1. 杀死所有旧的 Python 进程（有多个服务器在监听 8000 端口）
2. 重新启动后端服务
3. 测试结果：Vision AI 调用成功，识别出商家"永旺"和分类"购物"
4. 但金额返回 0.0，AI 没有正确提取金额

### 即将进行的修改
1. 改进 Vision AI 的提示词，更明确地要求提取金额
2. 针对微信/支付宝支付截图优化提示词
3. 添加更多金额提取的上下文说明

### 第二次修复尝试
1. 改进了提示词，强调金额提取的重要性
2. 测试结果：仍然返回 amount: 0.0
3. 分析：7B 参数的视觉模型可能不够强大，无法准确读取截图中的金额

### 即将进行的修改（第三次）
1. 尝试使用更大的视觉模型 `Qwen/Qwen2.5-VL-72B-Instruct`
2. 或尝试专用的 OCR 模型 `deepseek-ai/DeepSeek-OCR`

### 第三次修复尝试
1. 切换到 72B 视觉模型
2. 测试结果：模型返回 `"amount": ""` (空字符串)，导致 float('') 解析错误
3. 分析：视觉模型对金额数字提取不稳定，可能需要：
   - 修复解析逻辑以处理空字符串
   - 尝试专用 OCR 模型

### 即将进行的修改（第四次）
1. 修复 amount 解析逻辑，处理空字符串情况
2. 尝试使用 DeepSeek-OCR 专用模型

### 第四次修复尝试
1. 修复了 amount 解析逻辑（处理空字符串）✓
2. 尝试 DeepSeek-OCR 模型 - 返回空响应（可能使用不同的API格式）
3. 所有VL模型都能识别商家、分类、日期，但金额始终为0或空

### 问题分析
- VL模型能识别文字内容（商家名、分类）
- 但无法准确提取数字金额
- 可能原因：提示词格式问题，或模型对数字提取能力有限

### 即将进行的修改（第五次）
1. 尝试更简化的提示词，专注于金额提取
2. 使用 Qwen3-VL 更新的模型
3. 添加后处理逻辑，从响应文本中提取数字

### 第五次修复尝试 - 成功！ ✓
1. 切换到 `Qwen/Qwen3-VL-32B-Instruct` 模型
2. 简化了提示词
3. 添加了金额后处理逻辑（从文本中提取数字）
4. 使用更清晰的账单图片 (zhangdan1.jpg) 测试

**测试结果**：
```json
{
  "amount": 48.4,
  "merchant": "永旺",
  "category": "购物",
  "date": "昨天 晚上10:18"
}
```

### 结论
- Qwen3-VL-32B 模型能够正确识别微信支付账单
- 图片质量影响识别准确度
- OCR 功能现已正常工作

---

## 2026-01-03 首页账单刷新问题 (第二次调试)

### 问题描述
添加交易后，首页仍然不显示新添加的记录。数据库中确认数据已保存（ID 107, 108, 109 都有永旺 48.4 的记录）。

### 问题分析
1. 服务器日志显示 307 重定向：
   - `GET /api/transactions?limit=50` → 307 Redirect
   - `GET /api/transactions/?limit=50` → 200 OK
2. 前端 API 调用 `/transactions` 没有尾部斜杠
3. 后端 FastAPI 路由定义为 `/transactions/` 有尾部斜杠
4. 307 重定向可能导致 axios 处理异常或请求参数丢失

### 即将进行的修改
1. 修改前端 API 调用，添加尾部斜杠以匹配后端路由
2. 避免不必要的 307 重定向

### 修复内容
1. **frontend/src/api/transaction.ts** - 修复 API 路径
   - `getTransactions`: `/transactions` → `/transactions/`
   - `createTransaction`: `/transactions` → `/transactions/`
   - 消除 307 重定向，直接请求正确的路径

2. **frontend/src/stores/transaction.ts** - 改进数据刷新
   - `fetchTransactions` 使用 `[...data]` 创建新数组
   - 确保 Vue 响应式系统检测到数据变化

3. **frontend/src/views/Home.vue** - 强制刷新数据
   - `onActivated` 回调总是调用 `initData()`
   - 移除条件判断，确保每次返回首页都刷新

4. **frontend/src/components/record/PhotoScanner.vue** - 优化导航
   - 使用 `router.replace('/')` 替代 `router.push('/')`
   - 减少等待时间到 1 秒

---

## 2026-01-03 首页账单刷新问题

### 问题描述
拍照识别添加账单成功后，首页的账单列表没有自动刷新显示新添加的记录。

### 即将进行的修改
1. 检查 transaction store 的 addTransaction 方法是否刷新数据
2. 确保首页在返回时重新加载数据

### 修复内容
1. **PhotoScanner.vue** - 修复日期格式问题
   - OCR 返回 "昨天 晚上10:18" 这样的日期，不是有效格式
   - 添加日期格式校验，无效日期自动使用今天的日期
   - 支持 YYYY/MM/DD 转换为 YYYY-MM-DD

2. **transaction.ts** - 改进 addTransaction 方法
   - 添加交易后重新获取完整的交易列表 `fetchTransactions()`
   - 确保数据同步刷新

3. **transactions.py** - 修复排序问题（根本原因！）
   - 原来只按 `date DESC` 排序，同一天的交易顺序不固定
   - 改为 `date DESC, id DESC` 排序，确保最新添加的交易在最前面

### 测试结果
```json
[
  {"amount": 48.4, "description": "永旺", "id": 108},  // 最新
  {"amount": 48.4, "description": "永旺", "id": 107},
  {"amount": 100.0, "description": "永旺超市", "id": 106},
  ...
]
```

---
