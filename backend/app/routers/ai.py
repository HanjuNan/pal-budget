from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import re
import os
import requests
import asyncio
import base64
import json
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()

# AI API 配置 - SiliconFlow
# 请在环境变量中设置 AI_API_KEY，不要在代码中硬编码
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_API_BASE = os.getenv("AI_API_BASE", "https://api.siliconflow.cn/v1")
AI_MODEL = os.getenv("AI_MODEL", "Qwen/Qwen2.5-7B-Instruct")
AI_VISION_MODEL = os.getenv("AI_VISION_MODEL", "Qwen/Qwen3-VL-32B-Instruct")  # 更大的32B视觉模型
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"

# 线程池用于同步请求
executor = ThreadPoolExecutor(max_workers=4)


class VoiceParseRequest(BaseModel):
    text: str


class VoiceParseResponse(BaseModel):
    type: str
    amount: float
    category: str
    description: Optional[str] = None


class AIQueryRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = None


class AIConfigRequest(BaseModel):
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None


def sync_ai_request(url: str, headers: dict, json_data: dict, timeout: int = 60) -> Optional[dict]:
    """同步 AI 请求 - 禁用代理以避免连接问题"""
    try:
        # 禁用代理，直接连接
        response = requests.post(
            url,
            headers=headers,
            json=json_data,
            timeout=timeout,
            proxies={"http": None, "https": None}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"AI API error: {response.status_code} - {response.text[:500]}")
    except Exception as e:
        print(f"AI API error: {type(e).__name__}: {e}")
    return None


@router.post("/parse-voice", response_model=VoiceParseResponse)
async def parse_voice_text(request: VoiceParseRequest):
    """解析语音文本，提取金额、类别等信息"""
    text = request.text

    # 如果配置了 AI API，使用 AI 解析
    if AI_API_KEY or USE_OLLAMA:
        try:
            result = await ai_parse_transaction(text)
            if result:
                return VoiceParseResponse(**result)
        except Exception as e:
            print(f"AI parse error: {e}")

    # 回退到规则解析
    amount = 0.0
    category = "其他"
    transaction_type = "expense"

    # 提取金额
    amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:元|块|¥)?', text)
    if amount_match:
        amount = float(amount_match.group(1))

    # 判断收入还是支出
    if any(word in text for word in ['收入', '工资', '奖金', '收到', '进账']):
        transaction_type = "income"
        category = "工资"
    else:
        transaction_type = "expense"

    # 判断类别
    category_keywords = {
        '餐饮': ['吃', '餐', '饭', '午餐', '晚餐', '早餐', '外卖', '饮料', '咖啡', '奶茶'],
        '交通': ['车', '打车', '地铁', '公交', '油费', '停车', '高铁', '机票', '滴滴'],
        '购物': ['买', '购物', '超市', '淘宝', '京东', '商场', '衣服'],
        '娱乐': ['电影', '游戏', '唱歌', 'KTV', '旅游', '玩'],
        '住房': ['房租', '水电', '物业', '燃气'],
        '医疗': ['医院', '药', '看病', '体检'],
        '教育': ['书', '课程', '学费', '培训'],
        '通讯': ['话费', '网费', '流量'],
    }

    for cat, keywords in category_keywords.items():
        if any(kw in text for kw in keywords):
            category = cat
            break

    return VoiceParseResponse(
        type=transaction_type,
        amount=amount,
        category=category,
        description=text
    )


async def ai_parse_transaction(text: str) -> Optional[dict]:
    """使用 AI 解析交易信息"""
    prompt = f"""请从以下文本中提取记账信息，返回 JSON 格式：
文本："{text}"

请返回以下格式的 JSON（不要其他内容）：
{{"type": "expense 或 income", "amount": 数字, "category": "分类名称", "description": "备注"}}

分类选项：
- 支出：餐饮、交通、购物、娱乐、住房、医疗、教育、通讯、其他
- 收入：工资、奖金、兼职、投资、其他"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }
    json_data = {
        "model": AI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        sync_ai_request,
        f"{AI_API_BASE}/chat/completions",
        headers,
        json_data,
        30
    )

    if result:
        try:
            content = result["choices"][0]["message"]["content"]
            import json
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            print(f"Parse error: {e}")
    return None


@router.post("/scan-receipt")
async def scan_receipt(file: UploadFile = File(...)):
    """扫描小票/发票，使用 AI 视觉识别金额和商家"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="请上传图片文件")

    # 读取图片并转为 base64
    try:
        image_data = await file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')

        # 根据文件类型确定 MIME 类型
        mime_type = file.content_type or "image/jpeg"

    except Exception as e:
        print(f"Error reading image: {e}")
        raise HTTPException(status_code=400, detail="无法读取图片文件")

    # 如果配置了 AI API，使用视觉模型识别
    if AI_API_KEY:
        try:
            result = await ai_vision_parse_receipt(base64_image, mime_type)
            if result:
                return {
                    "success": True,
                    "data": result,
                    "message": "AI 识别成功"
                }
        except Exception as e:
            print(f"AI vision error: {e}")

    # 回退到空结果
    return {
        "success": True,
        "data": {
            "amount": 0.0,
            "merchant": "",
            "category": "购物",
            "date": "",
            "items": []
        },
        "message": "请手动编辑识别结果"
    }


async def ai_vision_parse_receipt(base64_image: str, mime_type: str) -> Optional[dict]:
    """使用 AI 视觉模型解析收据图片"""
    prompt = """这是一张支付截图或消费账单。请告诉我：

1. 支付金额是多少？（只写数字，如：48.40）
2. 商家名称是什么？
3. 属于什么消费类别？（餐饮/购物/交通/娱乐/其他）

请用以下JSON格式回答：
{"amount": 48.40, "merchant": "商家名", "category": "购物", "date": ""}

重要提示：请仔细看图片中显示的金额数字（¥符号后面的数字），并准确填写到amount字段中。"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }

    json_data = {
        "model": AI_VISION_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 200
    }

    print(f"Calling Vision AI: {AI_API_BASE}/chat/completions with model {AI_VISION_MODEL}")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        sync_ai_request,
        f"{AI_API_BASE}/chat/completions",
        headers,
        json_data,
        60
    )

    if result:
        try:
            content = result["choices"][0]["message"]["content"]
            print(f"Vision AI response: {content}")

            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())

                # 安全地解析金额，处理空字符串和无效值
                amount_val = parsed.get("amount", 0)
                try:
                    amount = float(amount_val) if amount_val not in [None, "", "null"] else 0.0
                except (ValueError, TypeError):
                    amount = 0.0

                # 如果金额为0，尝试从原始响应中提取数字
                if amount == 0.0:
                    # 查找类似 48.40 或 ¥48.40 的金额格式
                    price_patterns = [
                        r'¥\s*(\d+\.?\d*)',  # ¥48.40
                        r'(\d+\.\d{2})\s*元',  # 48.40元
                        r'"amount"[:\s]*(\d+\.?\d*)',  # "amount": 48.40
                        r'金额[是为：:\s]*(\d+\.?\d*)',  # 金额是48.40
                        r'(\d{1,6}\.\d{2})',  # 任何小数格式 48.40
                    ]
                    for pattern in price_patterns:
                        price_match = re.search(pattern, content)
                        if price_match:
                            try:
                                extracted = float(price_match.group(1))
                                if 0.01 <= extracted <= 100000:  # 合理的金额范围
                                    amount = extracted
                                    print(f"Extracted amount from text: {amount}")
                                    break
                            except ValueError:
                                continue

                return {
                    "amount": amount,
                    "merchant": parsed.get("merchant", "") or "",
                    "category": parsed.get("category", "购物") or "购物",
                    "date": parsed.get("date", "") or "",
                    "items": []
                }
        except Exception as e:
            print(f"Vision parse error: {e}")

    return None


@router.post("/chat")
async def ai_chat(request: AIQueryRequest):
    """AI 理财助手对话"""
    query = request.query
    history = request.history or []

    # 如果配置了 AI API，使用真实 AI
    if AI_API_KEY or USE_OLLAMA:
        try:
            reply = await ai_chat_completion(query, history)
            if reply:
                return {"reply": reply, "ai_powered": True}
        except Exception as e:
            print(f"AI chat error: {e}")

    # 回退到预设回复
    responses = {
        "本月花费分析": "根据您本月的消费记录，餐饮支出占比最高，建议适当控制外卖频率，可以节省不少开支哦~ 🐷",
        "省钱建议": "建议您：\n1. 📝 记录每笔支出，了解消费习惯\n2. 💰 设定月度预算\n3. 🛒 减少冲动消费\n4. 🎁 多利用优惠活动",
        "理财建议": "建议将收入分为：\n• 50% 日常开支\n• 30% 储蓄\n• 20% 投资理财\n\n先建立应急基金，再考虑其他投资方式~ 📈"
    }

    # 关键词匹配
    for key, value in responses.items():
        if key in query or any(k in query for k in key):
            return {"reply": value, "ai_powered": False}

    reply = f"收到您的问题啦~ 目前 AI 助手还在学习中，暂时无法回答「{query}」\n\n💡 提示：配置 AI_API_KEY 环境变量可启用智能回复功能"

    return {"reply": reply, "ai_powered": False}


async def ai_chat_completion(query: str, history: List[dict]) -> Optional[str]:
    """调用 AI API 进行对话"""
    system_prompt = """你是一个可爱的记账助手"小猪"🐷，帮助用户管理财务、分析消费习惯、提供理财建议。

你的特点：
- 说话友善、可爱，适当使用 emoji
- 提供实用的理财建议
- 分析消费数据时给出具体建议
- 鼓励用户养成良好的记账习惯

回复要求：
- 简洁明了，重点突出
- 适当分段，易于阅读
- 给出具体可操作的建议"""

    messages = [{"role": "system", "content": system_prompt}]

    # 添加历史记录
    for h in history[-6:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})

    messages.append({"role": "user", "content": query})

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_API_KEY}"
    }
    json_data = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    print(f"Calling AI API: {AI_API_BASE}/chat/completions with model {AI_MODEL}")

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        sync_ai_request,
        f"{AI_API_BASE}/chat/completions",
        headers,
        json_data,
        60
    )

    if result:
        try:
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Parse error: {e}")
    return None


@router.get("/config")
async def get_ai_config():
    """获取 AI 配置状态"""
    return {
        "configured": bool(AI_API_KEY),
        "api_base": AI_API_BASE,
        "model": AI_MODEL,
        "vision_model": AI_VISION_MODEL,
        "use_ollama": USE_OLLAMA,
        "ollama_available": False  # Ollama 未启用
    }
