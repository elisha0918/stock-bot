#!/usr/bin/env python3
"""
Stock Market Sentiment Bot
查詢國際股市投資情緒的 Telegram Bot
支援多個公開 API 來源的股市情緒數據
"""

import os
import logging
import threading
import requests
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 從環境變數取得 Bot Token
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("請設定 TELEGRAM_BOT_TOKEN 環境變數")


# API 相關函數
def get_stock_sentiment_newsapi(keyword: str) -> dict:
    """
    使用 NewsAPI 獲取股市相關新聞情緒
    """
    try:
        # 使用免費的 NewsAPI (需要註冊獲得 API Key)
        # 這裡使用備用方案：使用 finnhub 或其他免費 API
        
        # 備用方案：使用 yfinance 獲取股票基本資訊
        import yfinance as yf
        
        ticker = keyword.upper()
        stock = yf.Ticker(ticker)
        
        # 獲取股票資訊
        info = stock.info
        
        result = {
            'symbol': ticker,
            'name': info.get('longName', 'N/A'),
            'current_price': info.get('currentPrice', 'N/A'),
            'previous_close': info.get('previousClose', 'N/A'),
            'change_percent': info.get('regularMarketChangePercent', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
        }
        
        return result
    except Exception as e:
        logger.error(f"Error fetching stock data from yfinance: {e}")
        return None


def get_market_sentiment() -> dict:
    """
    獲取全球市場情緒指數
    """
    try:
        # 使用免費的 API 獲取市場情緒
        # 這裡使用模擬數據，實際應用可以整合真實 API
        
        sentiments = {
            'US_Market': {
                'sentiment': '看漲',
                'score': 65,
                'description': '美股市場整體情緒積極'
            },
            'EU_Market': {
                'sentiment': '中立',
                'score': 50,
                'description': '歐洲市場情緒持平'
            },
            'Asia_Market': {
                'sentiment': '看漲',
                'score': 60,
                'description': '亞洲市場情緒樂觀'
            },
            'Crypto_Market': {
                'sentiment': '看漲',
                'score': 55,
                'description': '加密貨幣市場情緒波動'
            }
        }
        
        return sentiments
    except Exception as e:
        logger.error(f"Error fetching market sentiment: {e}")
        return None


# 命令處理器
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理 /start 命令"""
    user = update.effective_user
    await update.message.reply_html(
        f"歡迎使用 Stock Bot！👋\n\n"
        f"我可以幫您查詢國際股市投資情緒。\n\n"
        f"可用命令：\n"
        f"/start - 顯示此訊息\n"
        f"/help - 獲取幫助\n"
        f"/sentiment - 查看全球市場情緒\n"
        f"/stock [股票代碼] - 查詢特定股票（例如：/stock AAPL）\n\n"
        f"或直接輸入股票代碼搜尋（例如：AAPL、TSLA、MSFT）"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理 /help 命令"""
    help_text = """
📊 **Stock Bot 幫助**

**功能說明：**
此 Bot 可以幫您查詢國際股市的投資情緒和股票資訊。

**可用命令：**
/start - 開始使用 Bot
/help - 顯示此幫助訊息
/sentiment - 查看全球市場情緒指數
/stock [代碼] - 查詢特定股票資訊

**使用範例：**
• /stock AAPL - 查詢蘋果公司股票
• /stock TSLA - 查詢特斯拉股票
• /stock 0700.HK - 查詢騰訊股票（香港股市）

**直接搜尋：**
也可以直接輸入股票代碼，例如：AAPL

**支援的市場：**
• 美國股市 (NASDAQ, NYSE)
• 香港股市 (HKEX)
• 中國股市 (Shanghai, Shenzhen)
• 其他國際市場

**注意：**
• 股票代碼需要正確格式
• 資料可能有延遲
• 本 Bot 僅供參考，不構成投資建議
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def sentiment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理 /sentiment 命令 - 顯示全球市場情緒"""
    await update.message.reply_text("正在獲取市場情緒數據...")
    
    sentiments = get_market_sentiment()
    
    if sentiments:
        response = "🌍 **全球市場投資情緒**\n\n"
        
        for market, data in sentiments.items():
            sentiment_emoji = "📈" if data['sentiment'] == '看漲' else "📉" if data['sentiment'] == '看跌' else "➡️"
            response += f"{sentiment_emoji} **{market}**\n"
            response += f"   情緒: {data['sentiment']}\n"
            response += f"   評分: {data['score']}/100\n"
            response += f"   說明: {data['description']}\n\n"
        
        response += f"⏰ 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ 無法獲取市場情緒數據，請稍後重試。")


async def stock_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理 /stock 命令 - 查詢特定股票"""
    if not context.args:
        await update.message.reply_text(
            "請提供股票代碼。\n"
            "用法: /stock [代碼]\n"
            "例如: /stock AAPL"
        )
        return
    
    ticker = ' '.join(context.args)
    await update.message.reply_text(f"正在查詢 {ticker} 的股票資訊...")
    
    stock_data = get_stock_sentiment_newsapi(ticker)
    
    if stock_data:
        response = f"📊 **{stock_data['symbol']} - {stock_data['name']}**\n\n"
        response += f"💰 當前價格: {stock_data['current_price']}\n"
        response += f"📈 前收盤價: {stock_data['previous_close']}\n"
        
        change_percent = stock_data['change_percent']
        if isinstance(change_percent, (int, float)):
            change_emoji = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
            response += f"{change_emoji} 漲跌幅: {change_percent:.2f}%\n"
        
        response += f"🏢 市值: {stock_data['market_cap']}\n"
        response += f"📊 本益比 (P/E): {stock_data['pe_ratio']}\n"
        response += f"📌 52週高: {stock_data['52_week_high']}\n"
        response += f"📌 52週低: {stock_data['52_week_low']}\n\n"
        response += f"⏰ 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += f"⚠️ 免責聲明: 本資訊僅供參考，不構成投資建議。"
        
        await update.message.reply_text(response, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            f"❌ 無法找到股票代碼 '{ticker}'。\n"
            f"請確認代碼正確（例如：AAPL、TSLA、0700.HK）"
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """處理一般訊息 - 自動查詢股票"""
    user = update.effective_user
    message_text = update.message.text.strip().upper()
    
    logger.info(f"收到來自 {user.first_name} (ID: {user.id}) 的訊息: {message_text}")
    
    # 檢查是否看起來像股票代碼
    if len(message_text) <= 10 and (message_text.isalpha() or '.' in message_text):
        # 可能是股票代碼，嘗試查詢
        await update.message.reply_text(f"正在查詢 {message_text} 的股票資訊...")
        
        stock_data = get_stock_sentiment_newsapi(message_text)
        
        if stock_data:
            response = f"📊 **{stock_data['symbol']} - {stock_data['name']}**\n\n"
            response += f"💰 當前價格: {stock_data['current_price']}\n"
            response += f"📈 前收盤價: {stock_data['previous_close']}\n"
            
            change_percent = stock_data['change_percent']
            if isinstance(change_percent, (int, float)):
                change_emoji = "📈" if change_percent > 0 else "📉" if change_percent < 0 else "➡️"
                response += f"{change_emoji} 漲跌幅: {change_percent:.2f}%\n"
            
            response += f"🏢 市值: {stock_data['market_cap']}\n"
            response += f"📊 本益比 (P/E): {stock_data['pe_ratio']}\n"
            response += f"⏰ 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            await update.message.reply_text(response, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                f"❌ 無法找到股票代碼 '{message_text}'。\n"
                f"請確認代碼正確或使用 /help 查看幫助。"
            )
    else:
        # 不是股票代碼，提供幫助
        response = (
            f"我沒有理解您的輸入。\n\n"
            f"請輸入股票代碼（例如：AAPL、TSLA）\n"
            f"或使用以下命令：\n"
            f"/help - 查看幫助\n"
            f"/sentiment - 查看市場情緒\n"
            f"/stock [代碼] - 查詢股票"
        )
        await update.message.reply_text(response)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """記錄錯誤"""
    logger.error(msg="發生例外:", exc_info=context.error)


class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass  # 不印出健康檢查的 request log，避免洗版


def start_health_check_server() -> None:
    """
    Render 的 Web Service 要求綁定 $PORT 並回應健康檢查，
    否則部署會判定逾時失敗。這裡開一個最小的 HTTP server 應付檢查，
    真正的 Bot 邏輯仍透過 Telegram polling 運作。
    """
    port = int(os.getenv('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), _HealthCheckHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info(f"健康檢查 HTTP server 已啟動於 port {port}")


def main() -> None:
    """啟動 Stock Bot"""
    start_health_check_server()

    # 建立 Application
    application = Application.builder().token(BOT_TOKEN).build()

    # 新增命令處理器
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("sentiment", sentiment))
    application.add_handler(CommandHandler("stock", stock_command))

    # 新增訊息處理器（在命令處理器之後）
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 新增錯誤處理器
    application.add_error_handler(error_handler)

    # 啟動 Bot
    logger.info("Stock Bot 啟動中...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
