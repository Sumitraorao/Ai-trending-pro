"""Reinforcement Learning ready architecture"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import gymnasium as gym
from gymnasium import spaces

class TradeAction(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2

@dataclass
class TradeState:
    cash: float
    holdings: int
    portfolio_value: float
    current_price: float
    step: int
    done: bool

class TradingEnvironment(gym.Env):
    def __init__(self, data: pd.DataFrame, initial_balance: float = 100000.0):
        super().__init__()
        self.data = data.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.current_step = 0

        # Action space: 0=HOLD, 1=BUY, 2=SELL
        self.action_space = spaces.Discrete(3)

        # Observation space: [price, rsi, macd, sma20, sma50, cash, holdings, portfolio_value]
        self.observation_space = spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(8,), 
            dtype=np.float32
        )

        self.cash = initial_balance
        self.holdings = 0
        self.portfolio_value = initial_balance
        self.peak_value = initial_balance
        self.max_drawdown = 0
        self.trade_history = []
        self.daily_loss = 0
        self.daily_start_value = initial_balance

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        self.cash = self.initial_balance
        self.holdings = 0
        self.portfolio_value = self.initial_balance
        self.peak_value = self.initial_balance
        self.max_drawdown = 0
        self.trade_history = []
        self.daily_loss = 0
        self.daily_start_value = self.initial_balance

        return self._get_observation(), {}

    def _get_observation(self):
        row = self.data.iloc[self.current_step]
        return np.array([
            row['Close'] / 1000.0,  # Normalize price
            row.get('RSI', 50) / 100.0,
            row.get('MACD', 0) / 10.0,
            row.get('SMA_20', row['Close']) / row['Close'] - 1,
            row.get('SMA_50', row['Close']) / row['Close'] - 1,
            self.cash / self.initial_balance,
            self.holdings / 100.0,
            self.portfolio_value / self.initial_balance
        ], dtype=np.float32)

    def _calculate_portfolio_value(self):
        current_price = self.data.iloc[self.current_step]['Close']
        return self.cash + (self.holdings * current_price)

    def _calculate_reward(self, old_value: float, new_value: float, action: int) -> float:
        # Base reward: portfolio value change
        reward = (new_value - old_value) / old_value * 100

        # Penalize excessive trading
        if action != TradeAction.HOLD.value:
            reward -= 0.1

        # Penalize drawdown
        drawdown = (self.peak_value - new_value) / self.peak_value
        if drawdown > 0.05:  # More than 5% drawdown
            reward -= drawdown * 10

        # Penalize daily loss exceeding 2%
        daily_return = (new_value - self.daily_start_value) / self.daily_start_value
        if daily_return < -0.02:
            reward -= 5

        return reward

    def step(self, action: int):
        current_price = self.data.iloc[self.current_step]['Close']
        old_value = self._calculate_portfolio_value()

        # Execute action
        if action == TradeAction.BUY.value:
            max_shares = int(self.cash / current_price)
            if max_shares > 0:
                shares_to_buy = min(max_shares, 10)  # Limit to 10 shares per trade
                cost = shares_to_buy * current_price
                self.cash -= cost
                self.holdings += shares_to_buy
                self.trade_history.append({
                    'step': self.current_step,
                    'action': 'BUY',
                    'price': current_price,
                    'shares': shares_to_buy
                })

        elif action == TradeAction.SELL.value:
            if self.holdings > 0:
                shares_to_sell = min(self.holdings, 10)
                revenue = shares_to_sell * current_price
                self.cash += revenue
                self.holdings -= shares_to_sell
                self.trade_history.append({
                    'step': self.current_step,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': shares_to_sell
                })

        # Move to next step
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1

        new_value = self._calculate_portfolio_value()
        self.portfolio_value = new_value

        # Update peak and drawdown
        if new_value > self.peak_value:
            self.peak_value = new_value
        drawdown = (self.peak_value - new_value) / self.peak_value
        self.max_drawdown = max(self.max_drawdown, drawdown)

        reward = self._calculate_reward(old_value, new_value, action)

        # Check if we should stop (circuit breaker)
        if drawdown > 0.10:  # 10% max drawdown
            done = True
            reward -= 10

        observation = self._get_observation()
        info = {
            'portfolio_value': new_value,
            'cash': self.cash,
            'holdings': self.holdings,
            'max_drawdown': self.max_drawdown,
            'total_trades': len(self.trade_history)
        }

        return observation, reward, done, False, info

    def get_state(self) -> TradeState:
        return TradeState(
            cash=self.cash,
            holdings=self.holdings,
            portfolio_value=self.portfolio_value,
            current_price=self.data.iloc[self.current_step]['Close'],
            step=self.current_step,
            done=self.current_step >= len(self.data) - 1
        )

class RLAgent:
    """Placeholder for Stable Baselines3 integration"""
    def __init__(self, env: TradingEnvironment):
        self.env = env
        self.model = None

    def train(self, total_timesteps: int = 10000):
        """Train using Stable Baselines3 (requires installation)"""
        try:
            from stable_baselines3 import PPO
            from stable_baselines3.common.vec_env import DummyVecEnv

            vec_env = DummyVecEnv([lambda: self.env])
            self.model = PPO(
                "MlpPolicy",
                vec_env,
                verbose=1,
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2
            )
            self.model.learn(total_timesteps=total_timesteps)
            return {"status": "success", "message": f"Trained for {total_timesteps} steps"}
        except ImportError:
            return {"status": "error", "message": "stable-baselines3 not installed. Install with: pip install stable-baselines3"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def predict(self, observation: np.ndarray) -> Tuple[int, Optional[dict]]:
        if self.model is None:
            return 0, None  # HOLD if no model
        action, _states = self.model.predict(observation, deterministic=True)
        return int(action), None

    def save(self, path: str):
        if self.model:
            self.model.save(path)

    def load(self, path: str):
        try:
            from stable_baselines3 import PPO
            self.model = PPO.load(path)
            return True
        except:
            return False
