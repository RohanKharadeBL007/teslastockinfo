import os
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

FINANCIAL_DATA = {
    "company_name": "Tesla, Inc.",
    "ticker": "TSLA",
    "exchange": "NASDAQ",
    "ipo_date": "June 29, 2010 ($17/share)",
    "kpis": {
        "market_cap": "$780.4B",
        "pe_ratio": "135.2x",
        "forward_pe": "68.4x",
        "rev_growth": "+18.2% YOY",
        "net_margin": "15.4%"
    },
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
        "Net Cash Position": "$28.18 Billion",
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
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: P/E Ratio = <b style='color:#e2e8f0;'>{data['pe']}</b>" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
        return "<div class='bot-heading'>📈 Tesla Historical P/E Ratio Trend:</div>" + "<br>".join(lines)
    
    lines = [f"• <b style='color:#38bdf8;'>{year}</b> — P/E: <b>{data['pe']}</b> | P/S: {data['ps']} | P/B: {data['pb']} | ROE: {data['roe']}" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
    return "<div class='bot-heading'>📊 Tesla Valuation History (2010–2025):</div>" + "<br>".join(lines)

def format_annual_matrix(metric_key=None, metric_label=None) -> str:
    if metric_key and metric_label:
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: <b style='color:#4ade80;'>{data[metric_key]}</b>" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
        return f"<div class='bot-heading'>💰 Tesla {metric_label} Trend:</div>" + "<br>".join(lines)
    
    rows = [f"• <b style='color:#38bdf8;'>{year}</b> — Rev: {data['revenue']} | Net: {data['net_income']} | Cash Flow: {data['cash_flow']} | Margin: {data['margin']}" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
    return "<div class='bot-heading'>📋 Complete Financial Matrix (2010–2025):</div>" + "<br>".join(rows)

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
        return f"<div class='bot-heading'>🏛️ Tesla Balance Sheet Highlights:</div>{bs_str}"

    elif "segment" in query or "breakdown" in query:
        seg_str = "<br>".join([f"• <b style='color:#94a3b8;'>{k}</b>: <b style='color:#4ade80;'>{v}</b>" for k, v in FINANCIAL_DATA["segments"].items()])
        return f"<div class='bot-heading'>⚡ Revenue Breakdown by Business Segment:</div>{seg_str}"

    elif "list" in query or "ipo" in query or "nasdaq" in query:
        return f"Tesla listed on NASDAQ on <b style='color:#38bdf8;'>{FINANCIAL_DATA['ipo_date']}</b> under ticker <b style='color:#ef4444;'>{FINANCIAL_DATA['ticker']}</b>."

    else:
        return (
            "I couldn't match that exact prompt. Select a preset below or try:<br>"
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
    <title>TSLA Financial Terminal</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-main: #0b0f17;
            --card-bg: #111827;
            --card-border: #1f293d;
            --accent-red: #e82127;
            --accent-cyan: #38bdf8;
            --accent-green: #22c55e;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-primary); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }

        .dashboard { width: 100%; max-width: 1100px; display: grid; grid-template-columns: 340px 1fr; gap: 20px; height: 860px; }

        /* Left Side Terminal Panel */
        .sidebar { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 24px; display: flex; flex-direction: column; gap: 20px; }
        .brand-header { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--card-border); padding-bottom: 16px; }
        .tesla-logo { font-size: 1.4rem; font-weight: 800; letter-spacing: 2px; color: var(--accent-red); display: flex; align-items: center; gap: 8px; }
        .ticker-badge { background: rgba(232, 33, 39, 0.15); border: 1px solid var(--accent-red); color: var(--accent-red); font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; }

        /* KPI Cards Grid */
        .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        .kpi-card { background: rgba(255, 255, 255, 0.02); border: 1px solid var(--card-border); border-radius: 12px; padding: 14px; }
        .kpi-title { font-size: 0.72rem; color: var(--text-secondary); text-transform: uppercase; font-weight: 600; letter-spacing: 0.5px; }
        .kpi-value { font-size: 1.15rem; font-weight: 700; margin-top: 4px; color: var(--text-primary); }
        .kpi-value.green { color: var(--accent-green); }
        .kpi-value.cyan { color: var(--accent-cyan); }

        /* Chart Area */
        .chart-box { background: rgba(255, 255, 255, 0.02); border: 1px solid var(--card-border); border-radius: 12px; padding: 14px; flex: 1; display: flex; flex-direction: column; }
        .chart-title { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 10px; }

        /* Main Chat Area */
        .chat-section { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
        .chat-header { background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid var(--card-border); padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; }
        .chat-title { font-size: 1rem; font-weight: 700; display: flex; align-items: center; gap: 10px; }
        .status-dot { width: 8px; height: 8px; background: var(--accent-green); border-radius: 50%; box-shadow: 0 0 10px var(--accent-green); }

        .chat-box { flex: 1; padding: 24px; overflow-y: auto; display: flex; flex-direction: column; gap: 16px; scrollbar-width: thin; scrollbar-color: var(--card-border) transparent; }
        
        .message { max-width: 85%; padding: 14px 18px; border-radius: 14px; font-size: 0.92rem; line-height: 1.6; }
        .user-message { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; align-self: flex-end; border-bottom-right-radius: 4px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2); }
        .bot-message { background: rgba(255, 255, 255, 0.03); color: #d1d5db; align-self: flex-start; border: 1px solid var(--card-border); border-bottom-left-radius: 4px; }
        .bot-heading { color: var(--accent-cyan); font-weight: 700; font-size: 0.98rem; margin-bottom: 8px; }

        /* Presets Area */
        .presets { padding: 12px 20px; background: rgba(0, 0, 0, 0.2); border-top: 1px solid var(--card-border); display: flex; flex-wrap: wrap; gap: 8px; }
        .preset-btn { background: rgba(255, 255, 255, 0.04); border: 1px solid var(--card-border); padding: 8px 14px; border-radius: 20px; font-size: 0.78rem; color: var(--text-secondary); cursor: pointer; font-weight: 500; transition: all 0.2s ease; }
        .preset-btn:hover { background: var(--accent-red); color: white; border-color: var(--accent-red); transform: translateY(-1px); }

        /* Input Area */
        .input-area { display: flex; padding: 18px 20px; border-top: 1px solid var(--card-border); background: rgba(0,0,0,0.3); gap: 10px; }
        .input-area input { flex: 1; background: rgba(255, 255, 255, 0.05); border: 1px solid var(--card-border); border-radius: 10px; padding: 12px 18px; color: white; outline: none; font-size: 0.9rem; transition: border-color 0.2s; }
        .input-area input:focus { border-color: var(--accent-cyan); }
        .input-area button { background: var(--accent-red); color: white; border: none; padding: 12px 24px; border-radius: 10px; cursor: pointer; font-weight: 700; font-size: 0.9rem; transition: all 0.2s ease; }
        .input-area button:hover { background: #c81e23; box-shadow: 0 0 15px rgba(232, 33, 39, 0.4); }

        @media (max-width: 900px) {
            .dashboard { grid-template-columns: 1fr; height: auto; }
            .sidebar { height: 400px; }
            .chat-section { height: 600px; }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Sidebar Terminal Panel -->
        <div class="sidebar">
            <div class="brand-header">
                <div class="tesla-logo">⚡ TESLA</div>
                <div class="ticker-badge">NASDAQ: TSLA</div>
            </div>

            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Market Cap</div>
                    <div class="kpi-value cyan">{{ kpis.market_cap }}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">P/E Ratio</div>
                    <div class="kpi-value">{{ kpis.pe_ratio }}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Rev Growth</div>
                    <div class="kpi-value green">{{ kpis.rev_growth }}</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Net Margin</div>
                    <div class="kpi-value green">{{ kpis.net_margin }}</div>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-title">REVENUE VS NET INCOME (2018-2025)</div>
                <canvas id="miniChart"></canvas>
            </div>
        </div>

        <!-- Right Side Screener Chat Terminal -->
        <div class="chat-section">
            <div class="chat-header">
                <div class="chat-title">
                    <div class="status-dot"></div>
                    Financial AI Screener Terminal
                </div>
                <span style="font-size:0.75rem; color:var(--text-secondary);">Real-Time Model Context</span>
            </div>

            <div class="chat-box" id="chat-box">
                <div class="message bot-message">
                    <div class="bot-heading">Welcome to the Tesla Interactive Terminal 🏎️</div>
                    Ask any question regarding Tesla's valuation ratios (P/E, P/S, P/B, ROE), revenue growth, profit margin trends, or balance sheet metrics.
                </div>
            </div>

            <div class="presets">
                {% for query in presets %}
                    <button class="preset-btn" onclick="sendPreset('{{ query }}')">{{ query }}</button>
                {% endfor %}
            </div>

            <div class="input-area">
                <input type="text" id="user-input" placeholder="Query P/E ratio, net income, cash flow, margins..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">EXECUTE</button>
            </div>
        </div>
    </div>

    <script>
        let chatHistory = [];

        // Render Chart.js Visualization
        const ctx = document.getElementById('miniChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['2018', '2020', '2021', '2022', '2023', '2024', '2025'],
                datasets: [
                    {
                        label: 'Revenue ($B)',
                        data: [21.46, 31.54, 53.82, 81.46, 96.77, 97.69, 94.83],
                        borderColor: '#38bdf8',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    },
                    {
                        label: 'Net Income ($B)',
                        data: [-0.97, 0.72, 5.52, 12.58, 14.99, 7.12, 3.81],
                        borderColor: '#22c55e',
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#9ca3af', font: { size: 10 } } } },
                scales: {
                    x: { ticks: { color: '#6b7280', font: { size: 9 } }, grid: { display: false } },
                    y: { ticks: { color: '#6b7280', font: { size: 9 } }, grid: { color: 'rgba(255,255,255,0.05)' } }
                }
            }
        });

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
                appendMessage('Error retrieving terminal response.', 'bot-message');
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
    return render_template_string(HTML_TEMPLATE, presets=PREDEFINED_QUERIES, kpis=FINANCIAL_DATA["kpis"])

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
