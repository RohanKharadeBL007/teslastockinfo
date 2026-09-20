import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Tesla Financial Dataset
FINANCIAL_DATA = {
    "company_name": "Tesla, Inc.",
    "ticker": "TSLA (NASDAQ)",
    "ipo_date": "June 29, 2010 ($17/share)",
    
    "annual_ratios": {
        "2010 (IPO)": {"pe": "N/A (Loss)", "ps": "25.4x", "pb": "8.2x", "roe": "-42.1%"},
        "2012":       {"pe": "N/A (Loss)", "ps": "11.2x", "pb": "14.1x", "roe": "-78.5%"},
        "2015":       {"pe": "N/A (Loss)", "ps": "7.8x",  "pb": "18.3x", "roe": "-81.2%"},
        "2018":       {"pe": "N/A (Loss)", "ps": "2.6x",  "pb": "11.7x", "roe": "-21.3%"},
        "2020":       {"pe": "1,100x",    "ps": "22.5x", "pb": "33.8x", "roe": "4.8%"},
        "2021":       {"pe": "190.5x",    "ps": "18.1x", "pb": "28.1x", "roe": "21.1%"},
        "2022":       {"pe": "38.2x",     "ps": "5.2x",  "pb": "9.4x",  "roe": "28.3%"},
        "2023":       {"pe": "68.4x",     "ps": "8.1x",  "pb": "11.2x", "roe": "27.9%"},
        "2024":       {"pe": "112.5x",    "ps": "8.9x",  "pb": "10.8x", "roe": "11.2%"},
        "2025":       {"pe": "135.2x",    "ps": "9.8x",  "pb": "11.4x", "roe": "12.8%"}
    },

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
        "Cash & Equivalents": "$36.56 Billion",
        "Total Debt": "$8.38 Billion",
        "Net Cash Position": "$28.18 Billion (Positive)",
        "Stockholders Equity": "$73.68 Billion"
    },

    "segments": {
        "Automotive Sales & Leasing": "83.5%",
        "Energy Storage & Solar": "8.5%",
        "Services & Supercharging": "8.0%"
    }
}

PREDEFINED_QUERIES = [
    "Show yearwise P/E ratio",
    "Show yearwise ratios history",
    "Show yearwise profit",
    "Show full financial matrix",
    "What is Tesla's Balance Sheet?",
    "Show revenue breakdown"
]

def format_yearwise_ratios(ratio_type="pe") -> str:
    if ratio_type == "pe":
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: P/E Ratio = <b style='color:#f8fafc;'>{data['pe']}</b>" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
        return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📈 Tesla Historical P/E Ratio Trend:</div>" + "<br>".join(lines)
    
    lines = [f"• <b style='color:#38bdf8;'>{year}</b> — P/E: <b>{data['pe']}</b> | P/S: {data['ps']} | P/B: {data['pb']} | ROE: {data['roe']}" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
    return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📊 Tesla Valuation History (2010–2025):</div>" + "<br>".join(lines)

def format_annual_matrix(metric_key=None, metric_label=None) -> str:
    if metric_key and metric_label:
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: <b style='color:#4ade80;'>{data[metric_key]}</b>" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
        return f"<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>💰 Tesla {metric_label} Trend:</div>" + "<br>".join(lines)
    
    rows = [f"• <b style='color:#38bdf8;'>{year}</b> — Rev: {data['revenue']} | Net: {data['net_income']} | Cash Flow: {data['cash_flow']} | Margin: {data['margin']}" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
    return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📋 Complete Financial Matrix (2010–2025):</div>" + "<br>".join(rows)

def contextual_chatbot(user_query: str, chat_history: list) -> str:
    query = user_query.strip().lower()

    if ("ratio" in query or "pe" in query or "p/e" in query or "valuation" in query) and ("year" in query or "annual" in query or "history" in query or "trend" in query):
        if "pe" in query or "p/e" in query:
            return format_yearwise_ratios("pe")
        return format_yearwise_ratios("all")

    elif "pe ratio" in query or "p/e ratio" in query or "pe" in query:
        return format_yearwise_ratios("pe")

    elif ("profit" in query or "net income" in query or "income" in query or "earning" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("net_income", "Net Income / Profit")

    elif ("revenue" in query or "sales" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("revenue", "Revenue")

    elif ("cash flow" in query or "cashflow" in query) and ("year" in query or "annual" in query or "history" in query):
        return format_annual_matrix("cash_flow", "Operating Cash Flow")

    elif "matrix" in query or "all metrics" in query or "full" in query or "financial" in query:
        return format_annual_matrix()

    elif "balance sheet" in query or "asset" in query or "debt" in query or "equity" in query:
        bs_str = "<br>".join([f"• <b style='color:#94a3b8;'>{k}</b>: <b style='color:#38bdf8;'>{v}</b>" for k, v in FINANCIAL_DATA["balance_sheet"].items()])
        return f"<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>🏛️ Tesla Balance Sheet Highlights:</div>{bs_str}"

    elif "segment" in query or "breakdown" in query:
        seg_str = "<br>".join([f"• <b style='color:#94a3b8;'>{k}</b>: <b style='color:#4ade80;'>{v}</b>" for k, v in FINANCIAL_DATA["segments"].items()])
        return f"<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>⚡ Revenue Breakdown by Business Segment:</div>{seg_str}"

    elif "list" in query or "ipo" in query or "nasdaq" in query:
        return f"Tesla listed on NASDAQ on <b style='color:#38bdf8;'>{FINANCIAL_DATA['ipo_date']}</b> under ticker <b style='color:#e82127;'>{FINANCIAL_DATA['ticker']}</b>."

    else:
        return (
            "I couldn't recognize that exact prompt. Try clicking a quick prompt below or ask:<br>"
            "• <b>Show yearwise P/E ratio</b><br>"
            "• <b>Show yearwise profit</b><br>"
            "• <b>Show full financial matrix</b>"
        )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tesla (TSLA) AI Financial Assistant</title>
    <style>
        :root {
            --bg-color: #0b0f17;
            --card-bg: #111827;
            --card-border: #1f293d;
            --accent-red: #e82127;
            --accent-cyan: #38bdf8;
            --accent-green: #22c55e;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        body { background-color: var(--bg-color); color: var(--text-primary); height: 100vh; display: flex; justify-content: center; align-items: center; padding: 16px; }

        .chat-container {
            width: 100%;
            max-width: 680px;
            height: 780px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }

        /* Header */
        .chat-header {
            background: rgba(15, 23, 42, 0.8);
            border-bottom: 1px solid var(--card-border);
            padding: 18px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-brand { display: flex; align-items: center; gap: 12px; }
        .logo-icon { font-size: 1.3rem; color: var(--accent-red); font-weight: 900; }
        .bot-title { font-size: 1.05rem; font-weight: 700; letter-spacing: 0.3px; }
        .ticker-pill { background: rgba(232, 33, 39, 0.15); border: 1px solid var(--accent-red); color: var(--accent-red); font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 12px; }

        /* Chat Body */
        .chat-box {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scrollbar-width: thin;
            scrollbar-color: var(--card-border) transparent;
        }

        .message {
            max-width: 85%;
            padding: 14px 18px;
            border-radius: 14px;
            font-size: 0.92rem;
            line-height: 1.6;
        }
        .user-message {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #ffffff;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
        }
        .bot-message {
            background: rgba(255, 255, 255, 0.03);
            color: #cbd5e1;
            align-self: flex-start;
            border: 1px solid var(--card-border);
            border-bottom-left-radius: 4px;
        }

        /* Preset Buttons */
        .presets {
            padding: 12px 18px;
            background: rgba(0, 0, 0, 0.2);
            border-top: 1px solid var(--card-border);
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .preset-btn {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--card-border);
            padding: 7px 13px;
            border-radius: 20px;
            font-size: 0.78rem;
            color: var(--text-secondary);
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .preset-btn:hover {
            background: var(--accent-red);
            color: #ffffff;
            border-color: var(--accent-red);
        }

        /* Input Bar */
        .input-area {
            display: flex;
            padding: 16px 18px;
            border-top: 1px solid var(--card-border);
            background: rgba(0, 0, 0, 0.3);
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 12px 16px;
            color: #ffffff;
            outline: none;
            font-size: 0.9rem;
            transition: border-color 0.2s;
        }
        .input-area input:focus { border-color: var(--accent-cyan); }
        .input-area button {
            background: var(--accent-red);
            color: #ffffff;
            border: none;
            padding: 12px 22px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 700;
            font-size: 0.88rem;
            transition: background-color 0.2s ease;
        }
        .input-area button:hover { background: #c81e23; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-brand">
                <span class="logo-icon">⚡</span>
                <span class="bot-title">Tesla Financial AI</span>
            </div>
            <span class="ticker-pill">TSLA</span>
        </div>

        <div class="chat-box" id="chat-box">
            <div class="message bot-message">
                <b style="color:var(--accent-cyan);">Welcome to Tesla Financial Assistant 🏎️</b><br><br>
                Ask questions about yearwise valuation ratios (P/E, P/S, P/B), revenue trends, net income history, or balance sheet metrics.
            </div>
        </div>

        <div class="presets">
            {% for query in presets %}
                <button class="preset-btn" onclick="sendPreset('{{ query }}')">{{ query }}</button>
            {% endfor %}
        </div>

        <div class="input-area">
            <input type="text" id="user-input" placeholder="Ask about yearwise PE ratio, profit, cash flow..." onkeypress="handleKeyPress(event)">
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
                appendMessage('Error retrieving response.', 'bot-message');
            }
        }

        function sendPreset(text) {
            document.getElementById('user-input').value = text;
            sendMessage();
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') sendMessage();
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
