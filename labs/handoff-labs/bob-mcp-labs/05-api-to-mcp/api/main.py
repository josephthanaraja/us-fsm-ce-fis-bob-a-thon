# api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="FinServ Portfolio API",
    description="A simple financial services API for the MCP lab",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class Holding(BaseModel):
    ticker: str
    name: str
    shares: float
    current_price_usd: float
    market_value_usd: float
    weight_pct: float


class PortfolioResponse(BaseModel):
    client_id: str
    holdings: list[Holding]
    total_market_value_usd: float


class AccountSummary(BaseModel):
    client_id: str
    client_name: str
    account_type: str
    total_portfolio_value_usd: float
    cash_balance_usd: float
    ytd_return_pct: float


# ---------------------------------------------------------------------------
# Hardcoded data store
# ---------------------------------------------------------------------------

PORTFOLIOS: dict[str, PortfolioResponse] = {
    "C001": PortfolioResponse(
        client_id="C001",
        total_market_value_usd=248_500.00,
        holdings=[
            Holding(ticker="AAPL", name="Apple Inc.", shares=120, current_price_usd=189.25, market_value_usd=22_710.00, weight_pct=9.14),
            Holding(ticker="MSFT", name="Microsoft Corp.", shares=85, current_price_usd=415.80, market_value_usd=35_343.00, weight_pct=14.22),
            Holding(ticker="JPM",  name="JPMorgan Chase", shares=200, current_price_usd=198.40, market_value_usd=39_680.00, weight_pct=15.97),
            Holding(ticker="BRK.B", name="Berkshire Hathaway B", shares=150, current_price_usd=368.00, market_value_usd=55_200.00, weight_pct=22.21),
            Holding(ticker="VTI",  name="Vanguard Total Market ETF", shares=400, current_price_usd=238.92, market_value_usd=95_568.00, weight_pct=38.46),
        ],
    ),
    "C002": PortfolioResponse(
        client_id="C002",
        total_market_value_usd=92_300.00,
        holdings=[
            Holding(ticker="VTI",  name="Vanguard Total Market ETF", shares=150, current_price_usd=238.92, market_value_usd=35_838.00, weight_pct=38.83),
            Holding(ticker="VXUS", name="Vanguard Total Intl ETF", shares=200, current_price_usd=58.45,  market_value_usd=11_690.00, weight_pct=12.67),
            Holding(ticker="BND",  name="Vanguard Total Bond ETF",  shares=300, current_price_usd=72.80,  market_value_usd=21_840.00, weight_pct=23.66),
            Holding(ticker="GLD",  name="SPDR Gold Shares",         shares=100, current_price_usd=229.32, market_value_usd=22_932.00, weight_pct=24.84),
        ],
    ),
}

ACCOUNTS: dict[str, AccountSummary] = {
    "C001": AccountSummary(
        client_id="C001",
        client_name="Margaret Holloway",
        account_type="Taxable Brokerage",
        total_portfolio_value_usd=248_500.00,
        cash_balance_usd=12_340.00,
        ytd_return_pct=11.4,
    ),
    "C002": AccountSummary(
        client_id="C002",
        client_name="David Tran",
        account_type="Traditional IRA",
        total_portfolio_value_usd=92_300.00,
        cash_balance_usd=3_200.00,
        ytd_return_pct=7.8,
    ),
}

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    """Confirms the API is running."""
    return {"status": "ok"}


@app.get("/portfolio/{client_id}", response_model=PortfolioResponse)
def get_portfolio(client_id: str):
    """
    Returns investment holdings for the given client.
    Raises 404 if the client ID is not found.
    """
    portfolio = PORTFOLIOS.get(client_id.upper())
    if not portfolio:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
    return portfolio


@app.get("/account/{client_id}/summary", response_model=AccountSummary)
def get_account_summary(client_id: str):
    """
    Returns account-level summary for the given client.
    Raises 404 if the client ID is not found.
    """
    account = ACCOUNTS.get(client_id.upper())
    if not account:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
    return account

# Made with Bob
