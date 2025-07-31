#!/usr/bin/env python3
"""
Smart Wallet Analysis Execution Script
Uses the advanced prompt and complete wallet data for accurate analysis
"""

import json
import os
from openai import OpenAI
from pathlib import Path

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def load_smart_prompt():
    """Load the advanced analysis prompt"""
    prompt_path = Path('smart_wallet_analysis_prompt.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def format_wallet_data_for_analysis(agent_input):
    """Format the complete wallet data for optimal LLM analysis"""
    
    # Extract key metrics
    summary = agent_input['summary']
    pnl = agent_input['pnl_overview'] 
    behavior = agent_input['behavior']
    tokens = agent_input['token_performance']
    
    formatted_data = f"""
## WALLET ANALYSIS DATA

### WALLET IDENTIFICATION
- **Address**: {agent_input['wallet_address']}
- **Analysis Period**: {pnl['data_from']}
- **Current Status**: {summary['status']}

### FINANCIAL PERFORMANCE
- **Total Realized PNL**: {pnl['realized_pnl']:.2f} SOL
- **Win/Loss Record**: {pnl['win_loss_count']} ({pnl['swap_win_rate']:.1f}% win rate)
- **Total Volume Traded**: {pnl['total_volume']:,.2f} SOL
- **SOL Spent**: {pnl['total_sol_spent']:,.2f} | **SOL Received**: {pnl['total_sol_received']:,.2f}
- **Average P&L per Trade**: {pnl['avg_pl_trade']:.2f} SOL
- **Median P&L per Token**: {pnl['median_pl_token']:.2f} SOL
- **Efficiency Score**: {pnl['weighted_efficiency_score']:.2f}
- **Volatility (Std Dev)**: {pnl['standard_deviation_pnl']:.2f} SOL
- **Current SOL Balance**: {summary['current_sol_balance']:.2f} SOL

### BEHAVIORAL ANALYSIS
- **Automated Classification**: "{behavior['trading_style']}" (Confidence: {behavior['confidence_score']:.1%})
- **Buy/Sell Ratio**: {behavior['buy_sell_ratio']:.2f}:1
- **Buy/Sell Symmetry**: {behavior['buy_sell_symmetry']:.1%}
- **Flipper Score**: {behavior['flipper_score']:.3f}

#### Trading Speed Distribution:
- **Ultra-Fast (<30min)**: {behavior['trading_time_distribution']['ultra_fast']:.1%}
- **Very Fast (30-60min)**: {behavior['trading_time_distribution']['very_fast']:.1%}  
- **Fast (1-4 hours)**: {behavior['trading_time_distribution']['fast']:.1%}
- **Moderate (4-8 hours)**: {behavior['trading_time_distribution']['moderate']:.1%}
- **Day Trading (8-24h)**: {behavior['trading_time_distribution']['day_trader']:.1%}
- **Swing Trading (1-7 days)**: {behavior['trading_time_distribution']['swing']:.1%}
- **Position Holding (>7 days)**: {behavior['trading_time_distribution']['position']:.1%}

#### Key Metrics:
- **Unique Tokens Traded**: {behavior['unique_tokens_traded']}
- **Tokens with Both Buy+Sell**: {behavior['tokens_with_both_buy_and_sell']}
- **Tokens with Only Buys**: {behavior['tokens_with_only_buys']} 
- **Total Trade Count**: {behavior['total_trade_count']}
- **Complete Pairs**: {behavior['complete_pairs_count']}
- **Average Flip Duration**: {behavior['average_flip_duration_hours']:.1f} hours
- **Median Hold Time**: {behavior['median_hold_time']:.1f} hours
- **% Trades Under 1 Hour**: {behavior['percent_trades_under_1hour']:.1%}
- **% Value in Current Holdings**: {behavior['percent_of_value_in_current_holdings']:.1%}

#### Session Analysis:
- **Session Count**: {behavior['session_count']}
- **Avg Trades per Session**: {behavior['avg_trades_per_session']:.1f}
- **Trading Frequency**: {behavior['trading_frequency']['tradesPerDay']:.1f} trades/day
- **Average Session Start Hour**: {behavior['average_session_start_hour']:.1f} UTC
- **Primary Trading Window**: 12am-5am UTC ({behavior['active_trading_periods']['identified_windows'][0]['percentageOfTotalTrades']:.1f}% of activity)

#### Risk Metrics:
- **Average Transaction Size**: {behavior['risk_metrics']['averageTransactionValueSol']:.2f} SOL
- **Largest Single Transaction**: {behavior['risk_metrics']['largestTransactionValueSol']:.2f} SOL

### TOP TOKEN POSITIONS"""

    # Add detailed token analysis
    for i, token in enumerate(tokens, 1):
        market_cap_m = token['market_cap_usd'] / 1_000_000
        formatted_data += f"""

**{i}. {token['name']} ({token['symbol']})**
- **Market Cap**: ${market_cap_m:.1f}M | **Liquidity**: ${token['liquidity_usd']:,.0f}
- **Total Investment**: {token['total_sol_spent']:.0f} SOL → **Received**: {token['total_sol_received']:.0f} SOL
- **Realized PNL**: {token['realized_pnl_sol']:.2f} SOL ({token['realized_pnl_percentage']:.0f}%)
- **Current Holdings**: {token['current_ui_balance']:,.0f} tokens = ${token['current_holdings_value_usd']:,.0f}
- **Unrealized PNL**: ${token['unrealized_pnl_usd']:,.0f} ({token['unrealized_pnl_percentage']:.0f}%)
- **Trading Activity**: {token['transfer_count_in']} buys, {token['transfer_count_out']} sells
- **Position Period**: {(token['last_transfer_timestamp'] - token['first_transfer_timestamp']) // (24*3600)} days
- **Social Links**: {'Website' if token['website_url'] else 'None'} | {'Twitter' if token['twitter_url'] else 'None'} | {'Telegram' if token['telegram_url'] else 'None'}"""

    formatted_data += f"""

### MOST TRADED TOKENS (by frequency):"""
    
    for i, token_pref in enumerate(behavior['token_preferences']['mostTradedTokens'][:5], 1):
        formatted_data += f"""
{i}. **{token_pref['mint'][:8]}...** - {token_pref['count']} trades, {token_pref['totalValue']:.1f} SOL volume"""

    return formatted_data

def run_smart_analysis():
    """Execute the complete smart wallet analysis"""
    
    print("🧠 Loading Smart Analysis System...")
    
    # Load prompt and data
    smart_prompt = load_smart_prompt()
    
    with open('agent_input_gake.json', 'r') as f:
        wallet_data = json.load(f)
    
    formatted_data = format_wallet_data_for_analysis(wallet_data)
    
    # Combine prompt with data
    full_prompt = smart_prompt + "\n\n" + formatted_data
    
    print(f"📊 Analyzing wallet: {wallet_data['wallet_address'][:8]}...")
    print(f"💰 Total PNL: {wallet_data['pnl_overview']['realized_pnl']:.0f} SOL")
    print(f"🎯 Win Rate: {wallet_data['pnl_overview']['swap_win_rate']:.1f}%")
    print(f"🔄 Activity: {wallet_data['behavior']['unique_tokens_traded']} tokens, {wallet_data['behavior']['total_trade_count']} trades")
    
    try:
        # Call OpenAI with optimized parameters
        response = client.chat.completions.create(
            model="gpt-4o",  # GPT-4 Omni for best analysis
            messages=[
                {
                    "role": "system", 
                    "content": "You are a senior cryptocurrency portfolio analyst with deep expertise in Solana DeFi, meme coin trading strategies, and institutional-grade financial analysis. Provide professional, data-driven insights with institutional credibility."
                },
                {
                    "role": "user", 
                    "content": full_prompt
                }
            ],
            max_tokens=2000,
            temperature=0.2,  # Low temperature for consistent analysis
            top_p=0.9
        )
        
        analysis_result = response.choices[0].message.content
        
        # Display results
        print("\n" + "="*60)
        print("🚀 SMART WALLET ANALYSIS COMPLETE")
        print("="*60)
        print(analysis_result)
        
        # Save results
        output_file = f"smart_analysis_{wallet_data['wallet_address'][:8]}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Smart Wallet Analysis: {wallet_data['wallet_address']}\n\n")
            f.write(f"**Analysis Date**: {wallet_data['pnl_overview']['data_from']}\n\n")
            f.write(analysis_result)
        
        print(f"\n💾 Analysis saved to: {output_file}")
        
        return analysis_result
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return None

if __name__ == "__main__":
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Please set your OPENAI_API_KEY environment variable")
        exit(1)
    
    run_smart_analysis()