import requests
import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3001/api/v1")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "DNfuF1L62WWyW3pNakVkyGGFzVVhj4Yr52jSmdTyeBHm")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "agent_input_gake.json")
API_KEY = os.getenv("API_KEY")

# Date range for full period analysis (optional - set to None for all-time data)
START_DATE = os.getenv("START_DATE")  # Format: "2024-01-01"
END_DATE = os.getenv("END_DATE")      # Format: "2024-12-31"

# --- Helper functions ---
def fetch(endpoint: str, api_key: Optional[str] = None, params: Optional[Dict] = None) -> Any:
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def sanitize_summary(data: Dict) -> Dict:
    return {
        "status": data.get("status", "ok"),
        "is_favorite": False,  # Not available in summary response
        "total_pnl": data.get("latestPnl", 0.0),
        "win_rate": data.get("tokenWinRate", 0.0),
        "total_volume": 0.0,  # Not available in summary response
        "days_active": data.get("daysActive", 0),
        "last_active_timestamp": data.get("lastActiveTimestamp", 0),
        "behavior_classification": data.get("behaviorClassification", "unknown"),
        "classification": data.get("classification", "normal")
    }

def sanitize_pnl(data: Dict) -> Dict:
    # The PNL overview returns { allTimeData: {...}, periodData: {...} }
    # We want to use allTimeData for comprehensive analysis
    pnl_data = data.get("allTimeData", {})
    
    return {
        "realized_pnl": pnl_data.get("realizedPnl", 0.0),
        "swap_win_rate": pnl_data.get("swapWinRate", 0.0),
        "win_loss_count": pnl_data.get("winLossCount", "0/0 wins"),
        "avg_pl_trade": pnl_data.get("avgPLTrade", 0.0),
        "total_volume": pnl_data.get("totalVolume", 0.0),
        "total_sol_spent": pnl_data.get("totalSolSpent", 0.0),
        "total_sol_received": pnl_data.get("totalSolReceived", 0.0),
        "median_pl_token": pnl_data.get("medianPLToken", 0.0),
        "token_win_rate": pnl_data.get("tokenWinRate", 0.0),
        "weighted_efficiency_score": pnl_data.get("weightedEfficiencyScore", 0.0),
        "data_from": pnl_data.get("dataFrom", "N/A"),
        "standard_deviation_pnl": pnl_data.get("standardDeviationPnl", 0.0),
        "average_pnl_per_day": pnl_data.get("averagePnlPerDayActiveApprox", 0.0)
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
    # Handle paginated response structure
    if isinstance(data, dict) and "data" in data:
        tokens = data.get("data", [])
    elif isinstance(data, list):
        tokens = data
    else:
        return []
    
    # Limit to top 3 tokens by totalAmountIn (or any other metric)
    if not tokens:
        return []
    
    sorted_tokens = sorted(tokens, key=lambda t: t.get("totalAmountIn", 0), reverse=True)[:3]
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
    print(f"Fetching data for wallet: {WALLET_ADDRESS}")
    print(f"API Base URL: {API_BASE_URL}")
    
    # Check if API key is provided
    if not API_KEY or API_KEY == "your-api-key-here":
        print("ERROR: Please set your API key in the .env file")
        print("Edit the .env file and replace 'your-api-key-here' with your actual API key")
        print("You can get an API key from your backend admin panel")
        return
    
    # Prepare query parameters for date range if specified
    params = {}
    if START_DATE and END_DATE:
        params["startDate"] = START_DATE
        params["endDate"] = END_DATE
        print(f"Fetching data for period: {START_DATE} to {END_DATE}")
    else:
        print("Fetching all-time data (no date range specified)")
    
    # Fetch data from API
    print("Fetching wallet summary...")
    summary = fetch(f"/wallets/{WALLET_ADDRESS}/summary", API_KEY, params)
    
    print("Fetching PNL overview...")
    pnl = fetch(f"/wallets/{WALLET_ADDRESS}/pnl-overview", API_KEY, params)
    
    print("Fetching behavior analysis...")
    behavior = fetch(f"/wallets/{WALLET_ADDRESS}/behavior-analysis", API_KEY, params)
    
    print("Fetching token performance...")
    tokens = fetch(f"/wallets/{WALLET_ADDRESS}/token-performance", API_KEY, params)

    # Check if we got valid responses
    if not summary:
        print("ERROR: Failed to fetch wallet summary")
        return
    
    if not pnl:
        print("ERROR: Failed to fetch PNL overview")
        return
    
    if not behavior:
        print("ERROR: Failed to fetch behavior analysis")
        return
    
    if not tokens:
        print("ERROR: Failed to fetch token performance")
        return

    # Sanitize and merge
    agent_input = {
        "wallet_address": WALLET_ADDRESS,
        "summary": sanitize_summary(summary),
        "pnl_overview": sanitize_pnl(pnl),
        "behavior": sanitize_behavior(behavior),
        "token_performance": sanitize_token_performance(tokens),
        "instruction": "Provide a comprehensive summary of this wallet's trading activity, performance, and any notable behavioral or risk patterns."
    }

    # Add date range info if specified
    if START_DATE and END_DATE:
        agent_input["date_range"] = {
            "start_date": START_DATE,
            "end_date": END_DATE
        }

    # Save to file
    with open(OUTPUT_FILE, "w") as f:
        json.dump(agent_input, f, indent=2)
    print(f"Agent input saved to {OUTPUT_FILE}")
    
    # Print some basic info to verify the data
    print(f"\nSummary:")
    print(f"  Status: {agent_input['summary']['status']}")
    print(f"  PNL: {agent_input['summary']['total_pnl']}")
    print(f"  Win Rate: {agent_input['summary']['win_rate']}%")
    print(f"  Days Active: {agent_input['summary']['days_active']}")
    print(f"  Behavior: {agent_input['summary']['behavior_classification']}")
    print(f"  Tokens: {len(agent_input['token_performance'])} tokens analyzed")
    
    if START_DATE and END_DATE:
        print(f"  Period: {START_DATE} to {END_DATE}")

if __name__ == "__main__":
    main() 