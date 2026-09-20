import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Extended Tesla Financial Data including Year-Wise Ratio History
FINANCIAL_DATA = {
    "company_name": "Tesla, Inc.",
    "ticker": "TSLA (NASDAQ)",
    "ipo_date": "June 29, 2010 ($17/share)",
    
    # Historical Year-wise Ratios
    "annual_ratios": {
        "2010 (IPO)": {"pe": "N/A (Loss)", "ps": "25.4x", "pb": "8.2x", "roe": "-42.1%"},
        "2012":       {"pe": "N/A (Loss)", "ps": "11.2x", "pb": "14.1x", "roe": "-78.5%"},
        "2015":       {"pe": "N/A (Loss)", "ps": "7.8x",  "pb": "18.3x", "roe": "-81.2%"},
        "2018":       {"pe": "N/A (Loss)", "ps": "2.6x",  "pb": "11.7x", "roe": "-21.3%"},
        "2020 (1st Profitable Year)": {"pe": "1,100x", "ps": "22.5x", "pb": "33.8x", "roe": "4.8%"},
        "2021":       {"pe": "190.5x", "ps": "18.1x", "pb": "28.1x", "roe": "21.1%"},
        "2022":       {"pe": "38.2x",  "ps": "5.2x",  "pb": "9.4x",  "roe": "28.3%"},
        "2023":       {"pe": "68.4x",  "ps": "8.1x",  "pb": "11.2x", "roe": "27.9%"},
        "2024":       {"pe": "112.5x", "ps": "8.9x",  "pb": "10.8x", "roe": "11.2%"},
        "2025":       {"pe": "135.2x", "ps": "9.8x",  "pb": "11.4x", "roe": "12.8%"}
    },

    # Year-Wise Financial Matrix
    "annual_matrix": {
        "2010 (IPO)":  {"revenue": "$116.7M", "net_income": "-$154.3M", "cash_flow": "-$128.0M", "margin": "-132.2%"},
        "2012":        {"revenue": "$413.3M", "net_income": "-$396.2M", "cash_flow": "-$266.0M", "margin": "-95.8%"},
        "2015":        {"revenue": "$4.05B",  "net_income": "-$888.7M", "cash_flow": "-$524.0M", "margin": "-21.9%"},
        "2018":        {"revenue": "$21.46B", "net_income": "-$976.0M", "cash_flow": "+$2.10B",  "margin": "-4.5%"},
        "2020":        {"revenue": "$31.54B", "net_income": "+$721.0M", "cash_flow": "+$5.94B",  "margin": "2.28%"},
        "2021":        {"revenue": "$53.82B", "net_income": "+$5.52B",  "cash_flow": "+$11.50B", "margin": "10.25%"},
        "2022":        {"revenue": "$81.46B", "net_income": "+$12.58B", "cash_flow": "+$14.72B", "margin": "15.45%"},
        "2023":        {"revenue": "$96.77B", "net_income": "+$14.99B", "cash_flow": "+$13.25B", "margin": "15.49%"},
        "2024":        {"revenue": "$97.69B", "net_income": "+$7.12B",  "cash_flow": "+$14.85B", "margin": "7.28%"},
        "2025":        {"revenue": "$94.83B", "net_income": "+$3.81B",  "cash_flow": "+$14.75B", "margin": "4.01%"}
    },

    "balance_sheet": {
        "Total Assets": "$122.07 Billion",
        "Cash & Short Term Investments": "$36.56 Billion",
        "Total Debt": "$8.38 Billion",
        "Net Debt": "-$28.18 Billion (Net Cash Positive)",
        "Total Equity": "$73.68 Billion"
    },

    "segments": {
        "Automotive Sales & Leasing": "83.5%",
        "Energy Generation & Storage": "8.5%",
        "Services & Other": "8.0%"
    }
}

PREDEFINED_QUERIES = [
    "Show yearwise P/E ratio",
    "Show yearwise ratios history",
    "Show yearwise profit / net income",
    "Show full yearwise financial matrix",
    "When did Tesla list on NASDAQ?",
    "What is Tesla's Balance Sheet overview?"
]

def format_yearwise_ratios(ratio_type="pe") -> str:
    """Formats year-by-year valuation ratios."""
    if ratio_type == "pe":
        lines = [f"• <b>{year}</b>: P/E Ratio = <b>{data['pe']}</b>" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
        return "<b>Tesla Year-by-Year P/E Ratio Trend:</b><br><br>" + "<br>".join(lines)
    
    lines = [f"• <b>{year}</b> — P/E: {data['pe']} | P/S: {data['ps']} | P/B: {data['pb']} | ROE: {data['roe']}" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
    return "<b>Tesla Year-by-Year Valuation Ratios History:</b><br><br>" + "<br>".join(lines)

def format_annual_matrix(metric_key=None, metric_label=None) -> str:
    """Formats annual financial metrics into HTML lists."""
    if metric_key and metric_label:
        lines = [f"• <b>{year}</b>: {data[metric_key]}" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
        return f"<b>Tesla Yearwise {metric_label}:</b><br><br>" + "<br>".join(lines)
    
    rows = [f"• <b>{year}</b> — Revenue: {data['revenue']} | Net Income: {data['net_income']} | Cash Flow: {data['cash_flow']} | Margin: {data['margin']}" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
    return "<b>Tesla Year-by-Year Financial Matrix (2010–2025):</b><br><br>" + "<br>".join(rows)

def contextual_chatbot(user_query: str, chat_history: list) -> str:
    """Enhanced query matching to support yearwise ratios and valuation trends."""
    query = user_query.strip().lower()

    # 1. Yearwise Ratio / P/E queries
    if ("ratio" in query or "pe" in query or "p/e" in query or "valuation" in query) and ("year" in query or "annual" in query or "history" in query or "trend" in query):
        if "pe" in query or "p/e" in query:
            return format_yearwise_ratios("pe")
        return format_yearwise_ratios("all")

    # 2. General P/E or Ratio query without explicit "year"
    elif "pe ratio" in query or "p/e ratio" in query or "pe" in query:
        return format_yearwise_ratios("pe")

    # 3. Yearwise Profit / Net Income
    elif ("profit" in query or "net income" in query or "income" in query or "earning" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("net_income", "Net Income / Profit")

    # 4. Yearwise Revenue
    elif ("revenue" in query or "sales" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("revenue", "Revenue")

    # 5. Yearwise Cash Flow
    elif ("cash flow" in query or "cashflow" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("cash_flow", "Operating Cash Flow")

    # 6. Full Financial Matrix
    elif "matrix" in query or "all metrics" in query or "full table" in query or ("yearwise" in query and "all" in query):
        return format_annual_matrix()

    # 7. Balance Sheet & Segments
    elif "balance sheet" in query or "asset" in query or "debt" in query or "equity" in query:
        bs_str = "<br>".join([f"• <b>{k}</b>: {v}" for k, v in FINANCIAL_DATA["balance_sheet"].items()])
        return f"<b>Tesla Balance Sheet Highlights:</b><br><br>{bs_str}"

    elif "segment" in query or "breakdown" in query:
        seg_str = "<br>".join([f"• <b>{k}</b>: {v}" for k, v in FINANCIAL_DATA["segments"].items()])
        return f"<b>Tesla Revenue Breakdown by Segment:</b><br><br>{seg_str}"

    # 8. Listing / IPO Date
    elif "list" in query or "ipo" in query or "nasdaq" in query:
        return f"Tesla listed on NASDAQ on <b>{FINANCIAL_DATA['ipo_date']}</b> under ticker <b>{FINANCIAL_DATA['ticker']}</b>."

    # 9. Fallback
    else:
        return (
            "Sorry, I couldn't recognize that exact request. Try asking for:<br>"
            "• <b>Yearwise P/E Ratio</b><br>"
            "• <b>Yearwise Ratios History</b><br>"
            "• <b>Yearwise Profit</b><br>"
            "• <b>Full Financial Matrix</b>"
        )

# Embedded Single-Page Frontend HTML & CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tesla Financial Screener Chatbot</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: #f1f5f9; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 580px; background: #ffffff; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); display: flex; flex-direction: column; height: 700px; border: 1px solid #e2e8f0; }
        .chat-header { background: #0f172a; color: #ffffff; padding: 16px 20px; border-top-left-radius: 10px; border-top-right-radius: 10px; font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; justify-content: space-between; }
        .chat-header span { font-size: 0.8rem; background: #e2e8f0; color: #0f172a; padding: 2px 8px; border-radius: 4px; }
        .chat-box { flex: 1; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; background: #ffffff; }
        .message { max-width: 88%; padding: 12px 16px; border-radius: 8px; font-size: 0.9rem; line-height: 1.5; }
        .user-message { background: #2563eb; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .bot-message { background: #f8fafc; color: #334155; align-self: flex-start; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; }
        .presets { padding: 12px 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; display: flex; flex-wrap: wrap; gap: 6px; }
        .preset-btn { background: #ffffff; border: 1px solid #cbd5e1; padding: 6px 12px; border-radius: 6px; font-size: 0.78rem; color: #334155; cursor: pointer; font-weight: 500; transition: all 0.15s ease-in-out; }
        .preset-btn:hover { background: #0f172a; color: white; border-color: #0f172a; }
        .input-area { display: flex; padding: 14px; border-top: 1px solid #e2e8f0; background: #ffffff; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; }
        .input-area input { flex: 1; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px; outline: none; font-size: 0.9rem; }
        .input-area button { background: #0f172a; color: white; border: none; padding: 10px 18px; margin-left: 8px; border-radius: 6px; cursor: pointer; font-weight: 600; }
        .input-area button:hover { background: #1e293b; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            📈 Tesla (TSLA) Screener
            <span>NASDAQ</span>
        </div>
        <div class="chat-box" id="chat-box">
            <div class="message bot-message">
                Welcome to the <b>Tesla Financial Assistant</b> 🚗.<br><br>
                Try asking:
                <br>• <i>Show yearwise P/E ratio</i>
                <br>• <i>Show yearwise ratios history</i>
                <br>• <i>Show yearwise profit</i>
            </div>
        </div>
        <div class="presets">
            {% for query in presets %}
                <button class="preset-btn" onclick="sendPreset('{{ query }}')">{{ query }}</button>
            {% endfor %}
        </div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask about yearwise PE ratio, ratios history, profit..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let chatHistory = [];

        function appendMessage(text, className) {
            const chatBox = document.getElementById('chat-box');
            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${className}`;
            msgDiv.innerHTML = text;
            chatBox.appendChild(msgDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            if (!message) return;

            appendMessage(message, 'user-message');
            input.value = '';

            chatHistory.push({ role: 'user', text: message });

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message, history: chatHistory })
                });
                const data = await response.json();
                
                appendMessage(data.response, 'bot-message');
                chatHistory.push({ role: 'bot', text: data.response });

            } catch (error) {
                appendMessage('Error reaching server.', 'bot-message');
            }
        }

        function sendPreset(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, presets=PREDEFINED_QUERIES)

@app.route("/chat", methods=["POST"])
def chat():
    payload = request.json or {}
    user_message = payload.get("message", "")
    chat_history = payload.get("history", [])

    bot_response = contextual_chatbot(user_message, chat_history)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
