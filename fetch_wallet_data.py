import requests
import json
from typing import Any, Dict

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"  # Change to your backend API base URL
WALLET_ADDRESS = "7G8x9vQ2kL3p4s5t6u7v8w9x0y1z2a3b4c5d6e7f8g9h"  # Replace with target wallet
OUTPUT_FILE = "agent_input.json"

# --- Helper functions ---
def fetch(endpoint: str) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def sanitize_summary(data: Dict) -> Dict:
    return {
        "status": data.get("status", "ok"),
        "is_favorite": data.get("isFavorite", False),
        "total_pnl": data.get("totalPnl", 0.0),
        "win_rate": data.get("winRate", 0.0),
        "total_volume": data.get("totalVolume", 0.0),
        "days_active": data.get("daysActive", 0),
        "last_active_timestamp": data.get("lastActiveTimestamp", 0),
        "behavior_classification": data.get("behaviorClassification", "unknown"),
        "classification": data.get("classification", "normal")
    }

def sanitize_pnl(data: Dict) -> Dict:
    return {
        "realized_pnl": data.get("realizedPnl", 0.0),
        "swap_win_rate": data.get("swapWinRate", 0.0),
        "win_loss_count": data.get("winLossCount", "0/0 wins"),
        "avg_pl_trade": data.get("avgPLTrade", 0.0),
        "total_volume": data.get("totalVolume", 0.0),
        "total_sol_spent": data.get("totalSolSpent", 0.0),
        "total_sol_received": data.get("totalSolReceived", 0.0),
        "median_pl_token": data.get("medianPLToken", 0.0),
        "token_win_rate": data.get("tokenWinRate", 0.0),
        "weighted_efficiency_score": data.get("weightedEfficiencyScore", 0.0)
    }

def sanitize_behavior(data: Dict) -> Dict:
    return {
        "trading_style": data.get("tradingStyle"),
        "confidence_score": data.get("confidenceScore"),
        "buy_sell_ratio": data.get("buySellRatio"),
        "flipper_score": data.get("flipperScore"),
        "unique_tokens_traded": data.get("uniqueTokensTraded"),
        "total_trade_count": data.get("totalTradeCount"),
        "trading_frequency": data.get("tradingFrequency"),
        "token_preferences": data.get("tokenPreferences"),
        "risk_metrics": data.get("riskMetrics"),
        "percent_of_value_in_current_holdings": data.get("percentOfValueInCurrentHoldings")
    }

def sanitize_token_performance(data: Any) -> Any:
    # Limit to top 3 tokens by totalAmountIn (or any other metric)
    if not isinstance(data, list):
        return []
    sorted_tokens = sorted(data, key=lambda t: t.get("totalAmountIn", 0), reverse=True)[:3]
    return [
        {
            "token_address": t.get("tokenAddress"),
            "name": t.get("name"),
            "symbol": t.get("symbol"),
            "total_amount_in": t.get("totalAmountIn", 0.0),
            "total_amount_out": t.get("totalAmountOut", 0.0),
            "net_amount_change": t.get("netAmountChange", 0.0),
            "total_sol_spent": t.get("totalSolSpent", 0.0),
            "total_sol_received": t.get("totalSolReceived", 0.0),
            "net_sol_profit_loss": t.get("netSolProfitLoss", 0.0),
            "current_ui_balance": t.get("currentUiBalance"),
            "current_holdings_value_usd": t.get("currentHoldingsValueUsd"),
            "realized_pnl_sol": t.get("realizedPnlSol"),
            "unrealized_pnl_usd": t.get("unrealizedPnlUsd"),
            "price_usd": t.get("priceUsd")
        }
        for t in sorted_tokens
    ]

def sanitize_similarity(data: Dict) -> Dict:
    # Only include top 1 pair for brevity
    pairs = data.get("pairwiseSimilarities", [])
    top_pairs = pairs[:1] if pairs else []
    return {
        "pairwise_similarities": top_pairs,
        "unique_tokens_per_wallet": data.get("uniqueTokensPerWallet", {})
    }

def main():
    # Fetch data from API
    summary = fetch(f"/wallets/{WALLET_ADDRESS}/summary")
    pnl = fetch(f"/wallets/{WALLET_ADDRESS}/pnl-overview")
    behavior = fetch(f"/wallets/{WALLET_ADDRESS}/behavior")
    tokens = fetch(f"/wallets/{WALLET_ADDRESS}/token-performance")
    similarity = fetch(f"/wallets/{WALLET_ADDRESS}/similarity")

    # Sanitize and merge
    agent_input = {
        "wallet_address": WALLET_ADDRESS,
        "summary": sanitize_summary(summary or {}),
        "pnl_overview": sanitize_pnl(pnl or {}),
        "behavior": sanitize_behavior(behavior or {}),
        "token_performance": sanitize_token_performance(tokens or []),
        "similarity": sanitize_similarity(similarity or {}),
        "instruction": "Provide a comprehensive summary of this wallet's trading activity, performance, and any notable behavioral or risk patterns."
    }

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(agent_input, f, indent=2)
    print(f"Agent input saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main() 