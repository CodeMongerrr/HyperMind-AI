import ccxt
import os
import time
from dotenv import load_dotenv
import logging
from typing import Dict, List, Optional, Union

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

class HyperliquidClient:
    def __init__(self, wallet_address: str = None, private_key: str = None):
        self.exchange = self._initialize_exchange(wallet_address, private_key)
        
    def _initialize_exchange(self, wallet_address: str = None, private_key: str = None) -> Optional[ccxt.hyperliquid]:
        try:
            exchange = ccxt.hyperliquid({
                'walletAddress': wallet_address or os.getenv('WALLET_ADDRESS', '0x8b3846CcfeCE6D84CcD0f1d1c0Ce73421B300DdC'),
                'privateKey': private_key or os.getenv('PRIVATE_KEY', '0x76798a7330a5f2989c67783e385bb780f894f854537242ed96f7382c7497c3d8'),
                'enableRateLimit': True,
                'api': {
                    'public': 'https://api.hyperliquid.xyz/info',
                    'private': 'https://api.hyperliquid.xyz/exchange'
                }
            })
            exchange.load_markets()
            logging.info("Exchange initialized successfully.")
            return exchange
        except Exception as e:
            logging.error(f"Failed to initialize exchange: {e}")
            return None

    def get_market_price(self, symbol: str) -> Optional[float]:
        try:
            markets = self.exchange.load_markets()
            if symbol in markets:
                price = float(markets[symbol]['info']['midPx'])
                logging.info(f"Current price for {symbol}: {price}")
                return price
            else:
                logging.error(f"Symbol {symbol} not found in markets.")
                return None
        except Exception as e:
            logging.error(f"Failed to fetch market price: {e}")
            return None

    def get_portfolio_balance(self) -> Dict:
        try:
            balance = self.exchange.fetch_balance()
            logging.info(f"Portfolio balance fetched: {balance}")
            return balance
        except Exception as e:
            logging.error(f"Failed to fetch portfolio balance: {e}")
            return {}

    def get_open_positions(self) -> List[Dict]:
        try:
            positions = self.exchange.fetch_positions()
            open_positions = [pos for pos in positions if pos['size'] != 0]
            logging.info(f"Open positions: {open_positions}")
            return open_positions
        except Exception as e:
            logging.error(f"Failed to fetch open positions: {e}")
            return []

    def place_market_order(self, symbol: str, side: str, amount: float) -> Union[Dict, bool]:
        try:
            price = self.get_market_price(symbol)
            if price is None:
                return False
            order = self.exchange.create_order(symbol, 'market', side, amount, price=price)
            logging.info(f"Market {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place market {side} order: {e}")
            return False

    def place_limit_order(self, symbol: str, side: str, amount: float, price: float) -> Union[Dict, bool]:
        try:
            order = self.exchange.create_order(symbol, 'limit', side, amount, price)
            logging.info(f"Limit {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place limit {side} order: {e}")
            return False

    def place_stop_market_order(self, symbol: str, side: str, amount: float, stop_price: float, reduce_only: bool = False) -> Union[Dict, bool]:
        try:
            price = self.get_market_price(symbol)
            if price is None:
                return False
            params = {'stopPrice': stop_price, 'type': 'stop_market'}
            if reduce_only:
                params['reduceOnly'] = True
            order = self.exchange.create_order(symbol, 'market', side, amount, params=params)
            logging.info(f"Stop-market {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place stop-market {side} order: {e}")
            return False

    def place_stop_limit_order(self, symbol: str, side: str, amount: float, price: float, stop_price: float, reduce_only: bool = False) -> Union[Dict, bool]:
        try:
            params = {'stopPrice': stop_price, 'type': 'stop_limit'}
            if reduce_only:
                params['reduceOnly'] = True
            order = self.exchange.create_order(symbol, 'limit', side, amount, price, params=params)
            logging.info(f"Stop-limit {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place stop-limit {side} order: {e}")
            return False

    def place_take_profit_order(self, symbol: str, side: str, amount: float, price: float) -> Union[Dict, bool]:
        try:
            order = self.exchange.create_order(
                symbol, 'limit', side, amount, price,
                params={'reduceOnly': True}
            )
            logging.info(f"Take-profit {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place take-profit {side} order: {e}")
            return False

    def place_trailing_stop_order(self, symbol: str, side: str, amount: float, callback_rate: float) -> Union[Dict, bool]:
        try:
            params = {
                'type': 'trailing_stop_market',
                'callbackRate': callback_rate,
                'reduceOnly': True
            }
            order = self.exchange.create_order(symbol, 'market', side, amount, params=params)
            logging.info(f"Trailing stop {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place trailing stop {side} order: {e}")
            return False

    def place_iceberg_order(self, symbol: str, side: str, amount: float, price: float, visible_size: float) -> Union[Dict, bool]:
        try:
            params = {
                'type': 'iceberg',
                'visibleSize': visible_size
            }
            order = self.exchange.create_order(symbol, 'limit', side, amount, price, params=params)
            logging.info(f"Iceberg {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place iceberg {side} order: {e}")
            return False

    def place_post_only_order(self, symbol: str, side: str, amount: float, price: float) -> Union[Dict, bool]:
        try:
            params = {'postOnly': True}
            order = self.exchange.create_order(symbol, 'limit', side, amount, price, params=params)
            logging.info(f"Post-only {side} order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to place post-only {side} order: {e}")
            return False

    def place_bracket_order(self, symbol: str, side: str, amount: float, price: float, stop_loss: float, take_profit: float) -> Dict:
        try:
            main_order = self.place_limit_order(symbol, side, amount, price)
            if not main_order:
                return {'success': False, 'error': 'Failed to place main order'}
            
            time.sleep(0.5)
            
            opposite_side = 'sell' if side == 'buy' else 'buy'
            sl_order = self.place_stop_market_order(symbol, opposite_side, amount, stop_loss, reduce_only=True)
            tp_order = self.place_take_profit_order(symbol, opposite_side, amount, take_profit)
            
            return {
                'success': True,
                'main_order': main_order,
                'stop_loss_order': sl_order,
                'take_profit_order': tp_order
            }
        except Exception as e:
            logging.error(f"Failed to place bracket order: {e}")
            return {'success': False, 'error': str(e)}

    def cancel_order(self, symbol: str, order_id: str) -> Union[Dict, bool]:
        try:
            response = self.exchange.cancel_order(order_id, symbol)
            logging.info(f"Order cancelled: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to cancel order: {e}")
            return False

    def cancel_all_orders(self, symbol: str = None) -> Union[Dict, bool]:
        try:
            if symbol:
                response = self.exchange.cancel_all_orders(symbol)
            else:
                response = self.exchange.cancel_all_orders()
            logging.info(f"All orders cancelled: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to cancel all orders: {e}")
            return False

    def modify_order(self, symbol: str, order_id: str, amount: float = None, price: float = None) -> Union[Dict, bool]:
        try:
            params = {}
            if amount:
                params['amount'] = amount
            if price:
                params['price'] = price
            response = self.exchange.edit_order(order_id, symbol, params=params)
            logging.info(f"Order modified: {response}")
            return response
        except Exception as e:
            logging.error(f"Failed to modify order: {e}")
            return False

    def get_open_orders(self, symbol: str = None) -> List[Dict]:
        try:
            if symbol:
                orders = self.exchange.fetch_open_orders(symbol)
            else:
                orders = self.exchange.fetch_open_orders()
            logging.info(f"Open orders: {orders}")
            return orders
        except Exception as e:
            logging.error(f"Failed to fetch open orders: {e}")
            return []

    def get_order_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        try:
            if symbol:
                orders = self.exchange.fetch_closed_orders(symbol, limit=limit)
            else:
                orders = self.exchange.fetch_closed_orders(limit=limit)
            logging.info(f"Order history: {orders}")
            return orders
        except Exception as e:
            logging.error(f"Failed to fetch order history: {e}")
            return []

    def get_trade_history(self, symbol: str = None, limit: int = 50) -> List[Dict]:
        try:
            if symbol:
                trades = self.exchange.fetch_my_trades(symbol, limit=limit)
            else:
                trades = self.exchange.fetch_my_trades(limit=limit)
            logging.info(f"Trade history: {trades}")
            return trades
        except Exception as e:
            logging.error(f"Failed to fetch trade history: {e}")
            return []

    def close_position(self, symbol: str, amount: float = None) -> Union[Dict, bool]:
        try:
            positions = self.get_open_positions()
            position = next((pos for pos in positions if pos['symbol'] == symbol), None)
            
            if not position:
                logging.warning(f"No open position found for {symbol}")
                return False
            
            close_amount = amount or abs(position['size'])
            side = 'sell' if position['side'] == 'long' else 'buy'
            
            order = self.place_market_order(symbol, side, close_amount)
            logging.info(f"Position closed: {order}")
            return order
        except Exception as e:
            logging.error(f"Failed to close position: {e}")
            return False

    def close_all_positions(self) -> Dict:
        try:
            positions = self.get_open_positions()
            results = {}
            
            for position in positions:
                symbol = position['symbol']
                result = self.close_position(symbol)
                results[symbol] = result
                time.sleep(0.1)
            
            return results
        except Exception as e:
            logging.error(f"Failed to close all positions: {e}")
            return {}

    def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        try:
            order_book = self.exchange.fetch_order_book(symbol, limit)
            logging.info(f"Order book for {symbol}: {order_book}")
            return order_book
        except Exception as e:
            logging.error(f"Failed to fetch order book: {e}")
            return {}

    def get_ticker(self, symbol: str) -> Dict:
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logging.info(f"Ticker for {symbol}: {ticker}")
            return ticker
        except Exception as e:
            logging.error(f"Failed to fetch ticker: {e}")
            return {}

    def get_funding_rate(self, symbol: str) -> Optional[float]:
        try:
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            logging.info(f"Funding rate for {symbol}: {funding_rate}")
            return funding_rate['fundingRate']
        except Exception as e:
            logging.error(f"Failed to fetch funding rate: {e}")
            return None