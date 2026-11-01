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
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: P/E = <b style='color:#f8fafc;'>{data['pe']}</b>" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
        return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📈 Tesla Historical P/E Ratio:</div>" + "<br>".join(lines)
    
    lines = [f"• <b style='color:#38bdf8;'>{year}</b> — P/E: <b>{data['pe']}</b> | P/S: {data['ps']} | P/B: {data['pb']} | ROE: {data['roe']}" for year, data in FINANCIAL_DATA["annual_ratios"].items()]
    return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📊 Tesla Valuation History:</div>" + "<br>".join(lines)

def format_annual_matrix(metric_key=None, metric_label=None) -> str:
    if metric_key and metric_label:
        lines = [f"• <b style='color:#38bdf8;'>{year}</b>: <b style='color:#4ade80;'>{data[metric_key]}</b>" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
        return f"<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>💰 Tesla {metric_label} Trend:</div>" + "<br>".join(lines)
    
    rows = [f"• <b style='color:#38bdf8;'>{year}</b> — Rev: {data['revenue']} | Net: {data['net_income']} | Cash Flow: {data['cash_flow']} | Margin: {data['margin']}" for year, data in FINANCIAL_DATA["annual_matrix"].items()]
    return "<div style='color:#38bdf8; font-weight:700; margin-bottom:8px;'>📋 Complete Financial Matrix:</div>" + "<br>".join(rows)

def contextual_chatbot(user_query: str, chat_history: list) -> str:
    query = user_query.strip().lower()
    
    if
