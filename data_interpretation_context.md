# Wallet Analysis Data Interpretation Context

## Purpose
This document provides critical context for interpreting wallet analysis data to avoid misclassification and ensure accurate LLM prompting.

---

## ⚠️ CRITICAL CLASSIFICATION UNDERSTANDING

### Trading Style Confidence Interpretation

**MOST IMPORTANT**: The `confidence_score` is the key to proper interpretation:

- **< 0.5 (50%)**: **LOW CONFIDENCE** - Classification is uncertain, treat skeptically
- **0.5-0.7 (50-70%)**: **MODERATE CONFIDENCE** - Classification likely but verify with other metrics
- **> 0.7 (70%+)**: **HIGH CONFIDENCE** - Classification is reliable

**Example from your data:**
```json
"trading_style": "Partial Flipper",
"confidence_score": 0.46368  // 46% = LOW CONFIDENCE!
```
**Interpretation**: System is UNSURE about "Partial Flipper" classification. Look at supporting metrics.

---

## 🔍 KEY BEHAVIORAL METRICS FOR ACCURATE CLASSIFICATION

### 1. **Buy/Sell Symmetry** (`buy_sell_symmetry`)
- **Range**: 0.0 - 1.0
- **Meaning**: How balanced buy/sell patterns are per token
- **0.7+**: Strong flipper behavior (balanced buy/sell per token)
- **< 0.5**: Imbalanced - either accumulator or distributor tendencies

### 2. **Sequence Consistency** (`sequence_consistency`) 
- **Range**: 0.0 - 1.0
- **Meaning**: How often buys are followed by sells (FIFO pairs)
- **0.7+**: Consistent flip patterns
- **< 0.5**: Inconsistent - many incomplete sequences

### 3. **Trading Time Distribution** (Critical for flipper vs holder distinction)
```json
"trading_time_distribution": {
  "ultra_fast": 0.15,    // < 30 minutes
  "very_fast": 0.25,     // 30-60 minutes  
  "fast": 0.30,          // 1-4 hours
  "moderate": 0.20,      // 4-8 hours
  "day_trader": 0.10,    // 8-24 hours
  "swing": 0.0,          // 1-7 days
  "position": 0.0        // > 7 days
}
```

**TRUE FLIPPER PATTERN**: `ultra_fast + very_fast > 0.6` (60%+ trades under 1 hour)
**HOLDER PATTERN**: `swing + position > 0.3` (30%+ trades over 1 day)

### 4. **Current Holdings Analysis**
- **`percent_of_value_in_current_holdings`**: 
  - **> 30%**: NOT a true flipper (significant position holding)
  - **< 10%**: True flipper behavior (minimal holdings retention)
  - **10-30%**: Partial flipper or strategic trader

---

## 🎯 CLASSIFICATION LOGIC CORRECTIONS

### The "Partial Flipper" Issue
The system defaults to "Partial Flipper" when `flipper_score > 0.4` but other conditions aren't met. This is often **MISLEADING**.

**Better Classification Logic**:
1. **Check confidence first** - if < 50%, classification is unreliable
2. **Verify with holdings retention** - if > 30% value held, NOT a flipper
3. **Confirm with time distribution** - if < 40% fast trades, NOT a flipper

### Alternative Classifications for High Holdings Retention

When `percent_of_value_in_current_holdings > 30%`:
- **Strategic Explorer**: High token diversity + significant holdings retention
- **Conviction Trader**: Selective positions + holds winners
- **Meme Specialist**: Focused on new token discovery + position sizing

---

## 🔢 TRADE FREQUENCY INTERPRETATION

### Volume vs Activity Intensity
```json
"unique_tokens_traded": 650,      // High diversity
"total_trade_count": 1474,        // High activity  
"days_active": 64,                // Short timeframe
```

**Analysis**: 
- **650 tokens / 64 days = 10.2 tokens/day** = Exploration behavior
- **1474 trades / 650 tokens = 2.3 trades/token** = Light touch per token
- **23 trades/day** = High activity but NOT bot-like for human meme trader

### Session Patterns (When Available)
```json
"session_count": 45,
"avg_trades_per_session": 32.8,
"average_session_start_hour": 14,
"average_session_duration_minutes": 180
```
**Human Pattern**: Distinct sessions, reasonable duration, consistent timing

---

## 💰 FINANCIAL PERFORMANCE INTERPRETATION

### PNL Breakdown Understanding
```json
"realized_pnl": 2156.76,          // From completed trades
"unrealized_pnl_usd": 131000,     // From current holdings
"percent_of_value_in_current_holdings": 33.25
```

**Key Insight**: High unrealized gains + significant holdings = **STRATEGIC HOLDER**, not flipper

### Win Rate vs PNL Relationship
```json
"win_rate": 27.4,                 // Low win rate
"total_pnl": 2156.76             // High total profit
```
**Pattern**: **High-risk, high-reward strategy** - few wins but large when successful

---

## 🤖 BOT DETECTION CONTEXT

### Human vs Bot Indicators

**BOT Indicators**:
- Trades > 100 tokens/day consistently
- Round number preferences (amounts ending in .00)
- Ultra-consistent timing (coefficient of variation < 0.1)
- Zero holdings retention
- Micro-transaction values (< 0.01 SOL avg)

**HUMAN Indicators (Your Wallet)**:
- Variable session patterns
- Significant holdings retention (33%)
- Large average transaction size (14+ SOL)
- Meme coin focus (exploration behavior)
- Irregular timing patterns

---

## 📊 PROMPT CONSTRUCTION GUIDELINES

### 1. **Context Setting**
Always provide context about:
- Classification confidence level
- FIFO-based holding time calculations  
- Difference between flipper vs strategic trader
- Meme coin trading environment specifics

### 2. **Data Hierarchy for Analysis**
1. **Confidence score** - primary reliability indicator
2. **Holdings retention %** - key behavior differentiator  
3. **Time distribution** - trading speed analysis
4. **Buy/sell symmetry** - pattern consistency
5. **Financial outcomes** - strategy effectiveness

### 3. **Avoid These Assumptions**
- ❌ "Partial Flipper" = flipping behavior (check confidence!)
- ❌ High trade count = bot behavior (context matters)
- ❌ Low win rate = poor performance (check total PNL)
- ❌ Many unique tokens = unfocused (could be systematic exploration)

### 4. **Contextual Explanations to Include**
```
"The 'Partial Flipper' classification has only 46% confidence, indicating uncertainty. 
The 33% value retention in current holdings suggests strategic position holding rather 
than true flipping behavior. This appears to be a selective meme coin explorer with 
conviction-based holding patterns."
```

---

## 🎯 RECOMMENDATIONS FOR YOUR SPECIFIC CASE

Based on your wallet data (`confidence_score: 0.46368`, `percent_of_value_in_current_holdings: 33.25`):

### True Classification: **"Strategic Meme Coin Explorer"**
- **High exploration activity**: 650 tokens tested over 64 days
- **Selective conviction holding**: 33% value retained in winners  
- **Large position sizing**: 14+ SOL average transactions
- **Profitable strategy**: 2156 SOL realized + $131K unrealized gains

### Prompt Framing:
```
"This wallet demonstrates sophisticated meme coin exploration and selective holding 
behavior, despite being misclassified as 'Partial Flipper' with low confidence (46%). 
The trader systematically explores new tokens (10+ per day) but holds winning positions 
(33% value retention), generating significant returns through a high-risk, high-reward 
strategy with 27% win rate but substantial total profits."
```

---

## 🔄 NEXT STEPS

1. **Use the complete data extraction script** to get all behavioral metrics
2. **Apply this interpretation framework** in prompt construction
3. **Focus on confidence-weighted analysis** rather than raw classifications
4. **Consider creating custom classification categories** for meme coin specialists

This approach will provide much more accurate and nuanced wallet analysis compared to taking raw API classifications at face value.