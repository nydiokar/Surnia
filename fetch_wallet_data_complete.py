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
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "agent_input_complete.json")
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
        "classification": data.get("classification", "normal"),
        "current_sol_balance": data.get("currentSolBalance"),
        "current_usdc_balance": data.get("currentUsdcBalance"),
        "balances_fetched_at": data.get("balancesFetchedAt")
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

def sanitize_behavior_complete(data: Dict) -> Dict:
    """COMPLETE behavior data extraction - includes ALL missing fields"""
    return {
        # Basic classification (already extracted)
        "trading_style": data.get("tradingStyle"),
        "confidence_score": data.get("confidenceScore"),
        
        # MISSING CRITICAL FIELDS - Now included
        "buy_sell_ratio": data.get("buySellRatio"),
        "buy_sell_symmetry": data.get("buySellSymmetry"),  # ⭐ KEY MISSING FIELD
        "sequence_consistency": data.get("sequenceConsistency"),  # ⭐ KEY MISSING FIELD
        "flipper_score": data.get("flipperScore"),
        
        # Timing analysis (MISSING)
        "average_flip_duration_hours": data.get("averageFlipDurationHours"),  # ⭐ KEY
        "median_hold_time": data.get("medianHoldTime"),  # ⭐ KEY
        "percent_trades_under_1hour": data.get("percentTradesUnder1Hour"),  # ⭐ KEY
        "percent_trades_under_4hours": data.get("percentTradesUnder4Hours"),  # ⭐ KEY
        
        # Trading time distribution (CRITICAL MISSING)
        "trading_time_distribution": {
            "ultra_fast": data.get("tradingTimeDistribution", {}).get("ultraFast", 0),  # ⭐ KEY
            "very_fast": data.get("tradingTimeDistribution", {}).get("veryFast", 0),    # ⭐ KEY  
            "fast": data.get("tradingTimeDistribution", {}).get("fast", 0),             # ⭐ KEY
            "moderate": data.get("tradingTimeDistribution", {}).get("moderate", 0),
            "day_trader": data.get("tradingTimeDistribution", {}).get("dayTrader", 0),
            "swing": data.get("tradingTimeDistribution", {}).get("swing", 0),
            "position": data.get("tradingTimeDistribution", {}).get("position", 0)
        },
        
        # Token and trade analysis (MISSING)
        "unique_tokens_traded": data.get("uniqueTokensTraded"),
        "tokens_with_both_buy_and_sell": data.get("tokensWithBothBuyAndSell"),  # MISSING
        "tokens_with_only_buys": data.get("tokensWithOnlyBuys"),  # MISSING
        "tokens_with_only_sells": data.get("tokensWithOnlySells"),  # MISSING
        "total_trade_count": data.get("totalTradeCount"),
        "total_buy_count": data.get("totalBuyCount"),  # MISSING
        "total_sell_count": data.get("totalSellCount"),  # MISSING
        "complete_pairs_count": data.get("completePairsCount"),  # MISSING
        "average_trades_per_token": data.get("averageTradesPerToken"),  # MISSING
        
        # Advanced behavioral metrics (MISSING)
        "reentry_rate": data.get("reentryRate"),  # MISSING
        "percentage_of_unpaired_tokens": data.get("percentageOfUnpairedTokens"),  # MISSING
        
        # Session analysis (MISSING)
        "session_count": data.get("sessionCount"),  # MISSING
        "avg_trades_per_session": data.get("avgTradesPerSession"),  # MISSING
        "average_session_start_hour": data.get("averageSessionStartHour"),  # MISSING
        "average_session_duration_minutes": data.get("averageSessionDurationMinutes"),  # MISSING
        
        # Current holdings analysis (MISSING) 
        "average_current_holding_duration_hours": data.get("averageCurrentHoldingDurationHours"),  # MISSING
        "median_current_holding_duration_hours": data.get("medianCurrentHoldingDurationHours"),  # MISSING
        "weighted_average_holding_duration_hours": data.get("weightedAverageHoldingDurationHours"),  # MISSING
        "percent_of_value_in_current_holdings": data.get("percentOfValueInCurrentHoldings"),
        
        # Active trading periods (MISSING)
        "active_trading_periods": {
            "hourly_trade_counts": data.get("activeTradingPeriods", {}).get("hourlyTradeCounts", {}),
            "identified_windows": data.get("activeTradingPeriods", {}).get("identifiedWindows", []),
            "activity_focus_score": data.get("activeTradingPeriods", {}).get("activityFocusScore", 0)
        },
        
        # Existing fields (already extracted)
        "trading_frequency": data.get("tradingFrequency"),
        "token_preferences": data.get("tokenPreferences"),
        "risk_metrics": data.get("riskMetrics"),
        
        # Timestamps (MISSING)
        "first_transaction_timestamp": data.get("firstTransactionTimestamp"),  # MISSING
        "last_transaction_timestamp": data.get("lastTransactionTimestamp")     # MISSING
    }

def sanitize_token_performance_complete(data: Any) -> Any:
    """COMPLETE token performance extraction - includes ALL missing fields"""
    # Handle paginated response structure
    if isinstance(data, dict) and "data" in data:
        tokens = data.get("data", [])
    elif isinstance(data, list):
        tokens = data
    else:
        return []
    
    # Limit to top 5 tokens by totalAmountIn for LLM analysis
    if not tokens:
        return []
    
    sorted_tokens = sorted(tokens, key=lambda t: t.get("totalAmountIn", 0), reverse=True)[:5]
    return [
        {
            # Basic info (already extracted)
            "token_address": t.get("tokenAddress"),
            "name": t.get("name"),
            "symbol": t.get("symbol"),
            
            # Trading volumes (already extracted)
            "total_amount_in": t.get("totalAmountIn", 0.0),
            "total_amount_out": t.get("totalAmountOut", 0.0),
            "net_amount_change": t.get("netAmountChange", 0.0),
            "total_sol_spent": t.get("totalSolSpent", 0.0),
            "total_sol_received": t.get("totalSolReceived", 0.0),
            "net_sol_profit_loss": t.get("netSolProfitLoss", 0.0),
            
            # MISSING: Trade frequency and timing
            "transfer_count_in": t.get("transferCountIn", 0),   # MISSING
            "transfer_count_out": t.get("transferCountOut", 0), # MISSING
            "first_transfer_timestamp": t.get("firstTransferTimestamp"),  # MISSING
            "last_transfer_timestamp": t.get("lastTransferTimestamp"),    # MISSING
            
            # MISSING: Separate realized vs unrealized PNL
            "realized_pnl_sol": t.get("realizedPnlSol"),        # MISSING - critical
            "unrealized_pnl_usd": t.get("unrealizedPnlUsd"),    # MISSING - critical
            "unrealized_pnl_sol": t.get("unrealizedPnlSol"),    # MISSING
            "total_pnl_sol": t.get("totalPnlSol"),              # MISSING
            "realized_pnl_percentage": t.get("realizedPnlPercentage"),    # MISSING
            "unrealized_pnl_percentage": t.get("unrealizedPnlPercentage"), # MISSING
            
            # Current holdings (already extracted)
            "current_ui_balance": t.get("currentUiBalance"),
            "current_holdings_value_usd": t.get("currentHoldingsValueUsd"),
            "current_holdings_value_sol": t.get("currentHoldingsValueSol"),  # MISSING 
            "price_usd": t.get("priceUsd"),
            
            # MISSING: Market data for context
            "market_cap_usd": t.get("marketCapUsd"),          # MISSING
            "liquidity_usd": t.get("liquidityUsd"),           # MISSING
            "volume_24h": t.get("volume24h"),                 # MISSING
            "fdv": t.get("fdv"),                              # MISSING
            "pair_created_at": t.get("pairCreatedAt"),        # MISSING
            
            # Meta information
            "image_url": t.get("imageUrl"),
            "website_url": t.get("websiteUrl"),
            "twitter_url": t.get("twitterUrl"),
            "telegram_url": t.get("telegramUrl"),
            "dexscreener_updated_at": t.get("dexscreenerUpdatedAt"),
            "balance_fetched_at": t.get("balanceFetchedAt")
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
    print(f"Fetching COMPLETE data for wallet: {WALLET_ADDRESS}")
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
    
    print("Fetching COMPLETE behavior analysis...")
    behavior = fetch(f"/wallets/{WALLET_ADDRESS}/behavior-analysis", API_KEY, params)
    
    print("Fetching COMPLETE token performance...")
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

    # Sanitize and merge with COMPLETE data extraction
    agent_input = {
        "wallet_address": WALLET_ADDRESS,
        "summary": sanitize_summary(summary),
        "pnl_overview": sanitize_pnl(pnl),
        "behavior": sanitize_behavior_complete(behavior),  # NOW COMPLETE
        "token_performance": sanitize_token_performance_complete(tokens),  # NOW COMPLETE
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
    print(f"COMPLETE agent input saved to {OUTPUT_FILE}")
    
    # Print summary of extracted data
    print(f"\n=== COMPLETE DATA EXTRACTION SUMMARY ===")
    print(f"Status: {agent_input['summary']['status']}")
    print(f"PNL: {agent_input['summary']['total_pnl']}")
    print(f"Win Rate: {agent_input['summary']['win_rate']}%")
    print(f"Days Active: {agent_input['summary']['days_active']}")
    print(f"Behavior: {agent_input['summary']['behavior_classification']}")
    print(f"Confidence: {agent_input['behavior']['confidence_score']:.1%}")
    
    # Key metrics now available
    print(f"\n=== NEWLY AVAILABLE BEHAVIORAL INSIGHTS ===")
    print(f"Buy/Sell Symmetry: {agent_input['behavior']['buy_sell_symmetry']:.1%}")
    print(f"Sequence Consistency: {agent_input['behavior']['sequence_consistency']:.1%}")
    print(f"Avg Flip Duration: {agent_input['behavior']['average_flip_duration_hours']:.1f}h")
    print(f"% Trades Under 1h: {agent_input['behavior']['percent_trades_under_1hour']:.1%}")
    print(f"Ultra-Fast Trading: {agent_input['behavior']['trading_time_distribution']['ultra_fast']:.1%}")
    print(f"Complete Pairs: {agent_input['behavior']['complete_pairs_count']}")
    print(f"Tokens w/ Both Buy+Sell: {agent_input['behavior']['tokens_with_both_buy_and_sell']}")
    
    print(f"\n=== TOKEN ANALYSIS ===")
    print(f"Tokens analyzed: {len(agent_input['token_performance'])}")
    for token in agent_input['token_performance'][:3]:
        print(f"  {token['symbol']}: Realized PNL: {token['realized_pnl_sol']:.2f} SOL, Unrealized: ${token['unrealized_pnl_usd']:,.0f}")
    
    if START_DATE and END_DATE:
        print(f"\nPeriod: {START_DATE} to {END_DATE}")

if __name__ == "__main__":
    main()