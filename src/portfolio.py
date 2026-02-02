"""Portfolio management module."""

import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json
from pathlib import Path


class Portfolio:
    """Manage portfolio holdings and performance tracking."""
    
    def __init__(self, data_file: str = "portfolio.json", logger: Optional[logging.Logger] = None):
        """
        Initialize Portfolio.
        
        Args:
            data_file: Path to portfolio data file
            logger: Optional logger instance
        """
        self.data_file = Path(data_file)
        self.logger = logger or logging.getLogger(__name__)
        self.holdings = self._load_portfolio()
    
    def _load_portfolio(self) -> List[Dict[str, Any]]:
        """
        Load portfolio from file.
        
        Returns:
            List of holdings
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading portfolio: {e}")
            return []
    
    def _save_portfolio(self) -> bool:
        """
        Save portfolio to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.holdings, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving portfolio: {e}")
            return False
    
    def add_holding(self, ticker: str, shares: float, purchase_price: float, 
                   purchase_date: Optional[str] = None, notes: str = "") -> bool:
        """
        Add a new holding to the portfolio.
        
        Args:
            ticker: Stock ticker symbol
            shares: Number of shares
            purchase_price: Price per share at purchase
            purchase_date: Date of purchase (ISO format)
            notes: Optional notes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if shares <= 0 or purchase_price <= 0:
                self.logger.error("Shares and purchase price must be positive")
                return False
            
            holding = {
                "ticker": ticker.upper(),
                "shares": shares,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date or datetime.now().isoformat(),
                "notes": notes,
                "id": len(self.holdings)  # Simple ID based on list length
            }
            
            self.holdings.append(holding)
            return self._save_portfolio()
        
        except Exception as e:
            self.logger.error(f"Error adding holding: {e}")
            return False
    
    def remove_holding(self, holding_id: int) -> bool:
        """
        Remove a holding from the portfolio.
        
        Args:
            holding_id: ID of the holding to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.holdings = [h for h in self.holdings if h.get("id") != holding_id]
            # Reassign IDs
            for i, holding in enumerate(self.holdings):
                holding["id"] = i
            return self._save_portfolio()
        
        except Exception as e:
            self.logger.error(f"Error removing holding: {e}")
            return False
    
    def get_holdings(self) -> List[Dict[str, Any]]:
        """
        Get all portfolio holdings.
        
        Returns:
            List of holdings
        """
        return self.holdings.copy()
    
    def calculate_portfolio_value(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate current portfolio value and performance.
        
        Args:
            current_prices: Dictionary mapping ticker to current price
            
        Returns:
            Dictionary with portfolio metrics
        """
        try:
            if not self.holdings:
                return {
                    "total_value": 0,
                    "total_cost": 0,
                    "total_gain_loss": 0,
                    "total_gain_loss_pct": 0,
                    "holdings_count": 0
                }
            
            total_value = 0
            total_cost = 0
            
            for holding in self.holdings:
                ticker = holding["ticker"]
                shares = holding["shares"]
                purchase_price = holding["purchase_price"]
                
                current_price = current_prices.get(ticker, purchase_price)
                
                holding_value = shares * current_price
                holding_cost = shares * purchase_price
                
                total_value += holding_value
                total_cost += holding_cost
            
            total_gain_loss = total_value - total_cost
            total_gain_loss_pct = (total_gain_loss / total_cost) if total_cost > 0 else 0
            
            return {
                "total_value": total_value,
                "total_cost": total_cost,
                "total_gain_loss": total_gain_loss,
                "total_gain_loss_pct": total_gain_loss_pct,
                "holdings_count": len(self.holdings)
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating portfolio value: {e}")
            return {
                "total_value": 0,
                "total_cost": 0,
                "total_gain_loss": 0,
                "total_gain_loss_pct": 0,
                "holdings_count": 0
            }
    
    def get_holdings_with_current_data(self, current_prices: Dict[str, float]) -> pd.DataFrame:
        """
        Get holdings as DataFrame with current prices and calculations.
        
        Args:
            current_prices: Dictionary mapping ticker to current price
            
        Returns:
            DataFrame with holding details
        """
        try:
            if not self.holdings:
                return pd.DataFrame()
            
            holdings_data = []
            
            for holding in self.holdings:
                ticker = holding["ticker"]
                shares = holding["shares"]
                purchase_price = holding["purchase_price"]
                purchase_date = holding.get("purchase_date", "")
                notes = holding.get("notes", "")
                holding_id = holding.get("id", 0)
                
                current_price = current_prices.get(ticker, purchase_price)
                
                current_value = shares * current_price
                cost_basis = shares * purchase_price
                gain_loss = current_value - cost_basis
                gain_loss_pct = (gain_loss / cost_basis) if cost_basis > 0 else 0
                
                holdings_data.append({
                    "ID": holding_id,
                    "Ticker": ticker,
                    "Shares": shares,
                    "Purchase Price": purchase_price,
                    "Current Price": current_price,
                    "Cost Basis": cost_basis,
                    "Current Value": current_value,
                    "Gain/Loss": gain_loss,
                    "Gain/Loss %": gain_loss_pct * 100,
                    "Purchase Date": purchase_date,
                    "Notes": notes
                })
            
            return pd.DataFrame(holdings_data)
        
        except Exception as e:
            self.logger.error(f"Error getting holdings with current data: {e}")
            return pd.DataFrame()
    
    def get_allocation(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate portfolio allocation by ticker.
        
        Args:
            current_prices: Dictionary mapping ticker to current price
            
        Returns:
            Dictionary mapping ticker to allocation percentage
        """
        try:
            if not self.holdings:
                return {}
            
            portfolio_value = self.calculate_portfolio_value(current_prices)["total_value"]
            
            if portfolio_value == 0:
                return {}
            
            allocation = {}
            
            for holding in self.holdings:
                ticker = holding["ticker"]
                shares = holding["shares"]
                current_price = current_prices.get(ticker, holding["purchase_price"])
                
                holding_value = shares * current_price
                allocation_pct = (holding_value / portfolio_value) * 100
                
                if ticker in allocation:
                    allocation[ticker] += allocation_pct
                else:
                    allocation[ticker] = allocation_pct
            
            return allocation
        
        except Exception as e:
            self.logger.error(f"Error calculating allocation: {e}")
            return {}


class Watchlist:
    """Manage stock watchlist."""
    
    def __init__(self, data_file: str = "watchlist.json", logger: Optional[logging.Logger] = None):
        """
        Initialize Watchlist.
        
        Args:
            data_file: Path to watchlist data file
            logger: Optional logger instance
        """
        self.data_file = Path(data_file)
        self.logger = logger or logging.getLogger(__name__)
        self.tickers = self._load_watchlist()
    
    def _load_watchlist(self) -> List[str]:
        """
        Load watchlist from file.
        
        Returns:
            List of ticker symbols
        """
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            self.logger.error(f"Error loading watchlist: {e}")
            return []
    
    def _save_watchlist(self) -> bool:
        """
        Save watchlist to file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.tickers, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving watchlist: {e}")
            return False
    
    def add_ticker(self, ticker: str) -> bool:
        """
        Add ticker to watchlist.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ticker = ticker.upper()
            if ticker not in self.tickers:
                self.tickers.append(ticker)
                return self._save_watchlist()
            return True
        except Exception as e:
            self.logger.error(f"Error adding ticker to watchlist: {e}")
            return False
    
    def remove_ticker(self, ticker: str) -> bool:
        """
        Remove ticker from watchlist.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ticker = ticker.upper()
            if ticker in self.tickers:
                self.tickers.remove(ticker)
                return self._save_watchlist()
            return True
        except Exception as e:
            self.logger.error(f"Error removing ticker from watchlist: {e}")
            return False
    
    def get_tickers(self) -> List[str]:
        """
        Get all tickers in watchlist.
        
        Returns:
            List of ticker symbols
        """
        return self.tickers.copy()
    
    def clear(self) -> bool:
        """
        Clear all tickers from watchlist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.tickers = []
            return self._save_watchlist()
        except Exception as e:
            self.logger.error(f"Error clearing watchlist: {e}")
            return False
