import pytest
from backend.utils import trade_safety

# Monkeypatch TradingHelper directly
class MockTradingHelper:
    @staticmethod
    def calculate_position_size(balance):
        return balance * 0.2

def test_normal_case(monkeypatch):
    monkeypatch.setattr("backend.victorq.neutralizer.TradingHelper", MockTradingHelper)
    balance = 100.0
    expected = min(100.0 * 0.2, 100.0 * trade_safety.MAX_POSITION_RATIO)
    result = trade_safety.get_safe_position_size(balance)
    assert result == round(expected, 6)

def test_size_below_min(monkeypatch):
    class TinyHelper:
        @staticmethod
        def calculate_position_size(balance): return 0.0
    monkeypatch.setattr("backend.victorq.neutralizer.TradingHelper", TinyHelper)
    result = trade_safety.get_safe_position_size(50.0)
    assert result == trade_safety.MIN_POSITION_SIZE

def test_oversized_quantity(monkeypatch):
    class GreedyHelper:
        @staticmethod
        def calculate_position_size(balance): return balance
    monkeypatch.setattr("backend.victorq.neutralizer.TradingHelper", GreedyHelper)
    result = trade_safety.get_safe_position_size(50.0)
    expected = round(50.0 * trade_safety.MAX_POSITION_RATIO, 6)
    assert result == expected

def test_exception_fallback(monkeypatch):
    class ErrorHelper:
        @staticmethod
        def calculate_position_size(balance): raise Exception("Failure")
    monkeypatch.setattr("backend.victorq.neutralizer.TradingHelper", ErrorHelper)
    result = trade_safety.get_safe_position_size(100.0)
    assert result == trade_safety.MIN_POSITION_SIZE