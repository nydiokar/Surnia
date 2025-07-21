# ReAct Agent Execution Plan for Dashboard Analysis

## 1. **Goal & Context**
Build a modular, LLM-powered agent that can ingest dashboard data (PNL, behavior, token performance, similarity, etc.), reason over it, and produce structured, actionable summaries or insights for the user. The agent should be easy to prototype, test, and extend.

---

## 2. **Step-by-Step Plan**

### **Step 1: Inventory & Normalize Data Structures**
- [x] **List all relevant DTOs/types** from `api.ts`:
  - `WalletSummaryData`
  - `PnlOverviewResponse` / `PnlOverviewResponseData`
  - `TokenPerformanceDataDto`
  - `BehaviorAnalysisResponseDto`
  - `RiskMetrics`, `TradingFrequency`, `AdvancedStatsResult`
  - 'Similarity analysis'
  - (Add others as needed)
- [x] **For each type, decide:**
  - Which fields are essential for the agent’s reasoning?
  - Are any fields redundant, too granular, or not useful for LLM analysis?
  - Should we merge types into a single agent input, or keep them as sections?
- [x] **Create a sample merged input schema** (Pydantic model) as a placeholder.

#### **Draft: Agent Input Schema (Pydantic)**
```python
from typing import List, Optional
from pydantic import BaseModel

class TokenPreferenceToken(BaseModel):
    mint: str
    count: int
    total_value: float
    first_seen: int
    last_seen: int

class TradingFrequency(BaseModel):
    trades_per_day: Optional[float]
    trades_per_week: Optional[float]
    trades_per_month: Optional[float]

class RiskMetrics(BaseModel):
    average_transaction_value_sol: Optional[float]
    largest_transaction_value_sol: Optional[float]

class TokenPerformanceSection(BaseModel):
    token_address: str
    name: Optional[str]
    symbol: Optional[str]
    total_amount_in: float
    total_amount_out: float
    net_amount_change: float
    total_sol_spent: float
    total_sol_received: float
    net_sol_profit_loss: float
    current_ui_balance: Optional[float]
    current_holdings_value_usd: Optional[float]
    realized_pnl_sol: Optional[float]
    unrealized_pnl_usd: Optional[float]
    price_usd: Optional[str]
    # Exclude URLs, images, and rarely used fields for LLM clarity

class WalletSummarySection(BaseModel):
    status: Optional[str]
    is_favorite: bool
    total_pnl: float
    win_rate: float
    total_volume: float
    days_active: int
    last_active_timestamp: int
    behavior_classification: Optional[str]
    classification: Optional[str]

class PnlOverviewSection(BaseModel):
    realized_pnl: float
    swap_win_rate: Optional[float]
    win_loss_count: Optional[str]
    avg_pl_trade: Optional[float]
    total_volume: Optional[float]
    total_sol_spent: float
    total_sol_received: float
    median_pl_token: Optional[float]
    token_win_rate: Optional[float]
    weighted_efficiency_score: Optional[float]

class BehaviorSection(BaseModel):
    trading_style: Optional[str]
    confidence_score: Optional[float]
    buy_sell_ratio: Optional[float]
    flipper_score: Optional[float]
    unique_tokens_traded: Optional[int]
    total_trade_count: Optional[int]
    trading_frequency: Optional[TradingFrequency]
    token_preferences: Optional[dict]  # mostTradedTokens, mostHeld (top 3 each)
    risk_metrics: Optional[RiskMetrics]
    percent_of_value_in_current_holdings: Optional[float]

class SimilarityPair(BaseModel):
    wallet_a: str
    wallet_b: str
    binary_score: float
    capital_score: float
    shared_tokens: List[dict]  # Only include top 3 pairs

class SimilaritySection(BaseModel):
    pairwise_similarities: List[SimilarityPair]
    unique_tokens_per_wallet: dict

class AgentInput(BaseModel):
    wallet_address: str
    summary: WalletSummarySection
    pnl_overview: PnlOverviewSection
    behavior: BehaviorSection
    token_performance: List[TokenPerformanceSection]  # Top N tokens (e.g., 5)
    similarity: Optional[SimilaritySection] = None
    instruction: Optional[str] = None  # e.g., "Summarize", "Compare wallets", etc.
```
**Notes:**
- Only include the most relevant/aggregate fields for LLM reasoning.
- Limit arrays (e.g., token_performance) to top N items for clarity.
- Exclude raw, redundant, or rarely used fields unless needed for a specific analysis.
- Add/adjust fields as new requirements emerge.

---

### **Step 2: Define Agent Input/Output Schema**
- [x] **Agent Input:** See above.
- [ ] **Agent Output:**
  - [ ] Start with plain text/markdown summary.
  - [ ] Plan for structured output (JSON with fields like `summary`, `tags`, `warnings`, etc) for future dashboard/API use.
  - [ ] _// TODO: Insert output schema draft_

### **Step 3: Prototype in Jupyter Notebook**
- [ ] Set up a notebook for rapid experimentation:
  - [ ] Load sample input data (from API or static JSON).
  - [ ] Allow easy editing of the prompt/instruction.
  - [ ] Send input + instruction to OpenAI (or other LLM).
  - [ ] Display and parse the output.
  - [ ] _// TODO: Insert notebook scaffolding_

### **Step 4: Iterative Prompt & Output Design**
- [ ] Experiment with different prompt templates and output formats.
- [ ] Validate that the LLM can:
  - [ ] Summarize wallet activity
  - [ ] Compare wallets
  - [ ] Highlight risks/opportunities
  - [ ] (Add more as needed)
- [ ] Adjust input schema and prompt as needed for best results.

### **Step 5: Tooling & Extensibility**
- [ ] Implement simple "tools" as Python functions (e.g., for calculations, lookups, etc).
- [ ] Plan for future tools (e.g., categorization, tagging, advanced analytics).
- [ ] _// TODO: List initial tools and their signatures_

### **Step 6: Integration & API Exposure**
- [ ] Once agent logic is stable, expose it via a function or API endpoint for frontend/dashboard use.
- [ ] Plan for saving agent outputs (e.g., to DB, for history or further analysis).
- [ ] _// TODO: Integration checklist_

### **Step 7: Memory & Context (Optional/Future)**
- [ ] Consider adding memory (e.g., embeddings, historical outputs) if needed for advanced use cases.
- [ ] _// TODO: Memory design placeholder_

---

## 3. **Type Reference & Role in Agent**
- **WalletSummaryData**: High-level wallet stats for quick overview/classification.
- **PnlOverviewResponseData**: Core PNL metrics, win rates, volume, etc.
- **TokenPerformanceDataDto**: Per-token trading and PNL details.
- **BehaviorAnalysisResponseDto**: Behavioral metrics, trading style, risk, frequency.
- **RiskMetrics, TradingFrequency, AdvancedStatsResult**: Sub-objects for deeper analysis.
- _// Add more as needed_

---

## 4. **Placeholders & TODOs**
- [x] Insert sample input schema after data inventory.
- [ ] Insert output schema after prototyping.
- [ ] Add comments/questions for any unclear fields or requirements.
- [ ] Update plan as new requirements or data types emerge.

---

## 5. **Comments & Guidance**
- Keep each step minimal and testable.
- Use comments in the plan to flag where decisions or more info are needed.
- Avoid over-engineering: only add complexity when justified by use case.
- Iterate quickly in notebook before formalizing architecture.

---

// End of plan. Update this file as you progress and clarify requirements. 