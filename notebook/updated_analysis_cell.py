# Updated Professional Wallet Analysis Cell
# Use this to replace your current notebook cells

import json
import os
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client (modern API)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def load_analysis_prompt():
    """Load the professional analysis prompt template"""
    prompt_path = Path('../wallet_analysis_prompt_v1.txt')
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()

def format_wallet_data(agent_input):
    """Format wallet data for optimal LLM processing"""
    # Create a clean, structured representation
    formatted_data = f"""
WALLET ADDRESS: {agent_input['wallet_address']}

SUMMARY METRICS:
- Total PNL: {agent_input['summary']['total_pnl']:.2f} SOL
- Win Rate: {agent_input['summary']['win_rate']:.1f}%
- Days Active: {agent_input['summary']['days_active']}
- Trading Classification: {agent_input['summary']['behavior_classification']}
- Status: {agent_input['summary']['classification']}

PERFORMANCE OVERVIEW:
- Realized PNL: {agent_input['pnl_overview']['realized_pnl']:.2f} SOL
- Win/Loss Record: {agent_input['pnl_overview']['win_loss_count']}
- Average P&L per Trade: {agent_input['pnl_overview']['avg_pl_trade']:.2f} SOL
- Median P&L per Token: {agent_input['pnl_overview']['median_pl_token']:.2f} SOL
- Total Volume: {agent_input['pnl_overview']['total_volume']:.2f} SOL
- Efficiency Score: {agent_input['pnl_overview']['weighted_efficiency_score']:.2f}
- Volatility (Std Dev): {agent_input['pnl_overview']['standard_deviation_pnl']:.2f}
- Data Period: {agent_input['pnl_overview']['data_from']}

BEHAVIORAL ANALYSIS:
- Trading Style: {agent_input['behavior']['trading_style']}
- Confidence Score: {agent_input['behavior']['confidence_score']:.3f}
- Buy/Sell Ratio: {agent_input['behavior']['buy_sell_ratio']:.2f}
- Flipper Score: {agent_input['behavior']['flipper_score']:.3f}
- Unique Tokens Traded: {agent_input['behavior']['unique_tokens_traded']}
- Total Trades: {agent_input['behavior']['total_trade_count']}
- Trading Frequency: {agent_input['behavior']['trading_frequency']['tradesPerDay']:.1f} trades/day
- Current Holdings %: {agent_input['behavior']['percent_of_value_in_current_holdings']:.1f}%
- Average Transaction: {agent_input['behavior']['risk_metrics']['averageTransactionValueSol']:.2f} SOL
- Largest Transaction: {agent_input['behavior']['risk_metrics']['largestTransactionValueSol']:.2f} SOL

TOP TOKEN POSITIONS:"""
    
    # Add token performance data
    for i, token in enumerate(agent_input['token_performance'][:3], 1):
        formatted_data += f"""

{i}. {token['name']} ({token['symbol']})
   - Address: {token['token_address']}
   - Net SOL P&L: {token['net_sol_profit_loss']:.2f} SOL
   - Current Holdings: {token['current_ui_balance']:,.0f} tokens
   - Current USD Value: ${token['current_holdings_value_usd']:,.2f}
   - Realized PNL: {token['realized_pnl_sol']:.2f} SOL
   - Unrealized PNL: ${token['unrealized_pnl_usd']:,.2f}
   - Token Price: ${token['price_usd']}"""

    # Add most traded tokens
    formatted_data += "\n\nMOST TRADED TOKENS:"
    for i, token in enumerate(agent_input['behavior']['token_preferences']['mostTradedTokens'][:5], 1):
        formatted_data += f"""
{i}. Token: {token['mint'][:8]}... (Trades: {token['count']}, Value: {token['totalValue']:.2f} SOL)"""
    
    return formatted_data

def analyze_wallet(agent_input):
    """Run professional wallet analysis using the structured prompt"""
    
    # Load prompt template
    prompt_template = load_analysis_prompt()
    
    # Format wallet data
    formatted_data = format_wallet_data(agent_input)
    
    # Fill in the template
    final_prompt = prompt_template.format(
        wallet_data=formatted_data,
        instruction=agent_input.get('instruction', 'Provide comprehensive wallet analysis')
    )
    
    # Call OpenAI with modern API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4 Omni for best analysis
            messages=[
                {
                    "role": "system", 
                    "content": "You are a senior crypto portfolio analyst with deep expertise in Solana DeFi, meme coin trading, and quantitative analysis. You provide professional, data-driven insights for institutional and professional traders."
                },
                {
                    "role": "user", 
                    "content": final_prompt
                }
            ],
            max_tokens=1500,
            temperature=0.3,  # Lower temperature for more consistent, factual analysis
            top_p=0.9
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error in analysis: {str(e)}"

# EXECUTION CELL
# Load your wallet data
with open('../agent_input_gake.json', 'r') as f:
    wallet_data = json.load(f)

# Run the analysis
print("🚀 PROFESSIONAL WALLET ANALYSIS")
print("=" * 50)

analysis_result = analyze_wallet(wallet_data)
print(analysis_result)

# Optional: Save results
output_path = f"analysis_output_{wallet_data['wallet_address'][:8]}.md"
with open(output_path, 'w') as f:
    f.write(f"# Wallet Analysis: {wallet_data['wallet_address']}\n\n")
    f.write(analysis_result)

print(f"\n💾 Analysis saved to: {output_path}")