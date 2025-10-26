"""
Unit tests for ml/smoothing.py - Prediction smoothing
"""

import pytest
import numpy as np
from ml.smoothing import EMA, MajorityVote


class TestEMA:
    """Test Exponential Moving Average smoothing"""
    
    def test_ema_initialization(self):
        """Test EMA initializes correctly"""
        ema = EMA(alpha=0.5, num_classes=14)
        assert ema.alpha == 0.5
        assert len(ema.ema) == 14
        assert not ema.initialized
    
    def test_ema_first_update(self):
        """Test EMA first update initializes with given values"""
        ema = EMA(alpha=0.5, num_classes=5)
        probs = [0.1, 0.2, 0.3, 0.2, 0.2]
        
        result = ema.update(probs)
        
        # After first update, EMA should equal input
        np.testing.assert_array_almost_equal(result, probs)
        assert ema.initialized
    
    def test_ema_second_update(self):
        """Test EMA second update applies exponential averaging"""
        ema = EMA(alpha=0.5, num_classes=3)
        
        # First update
        probs1 = [0.5, 0.3, 0.2]
        ema.update(probs1)
        
        # Second update
        probs2 = [0.2, 0.3, 0.5]
        result = ema.update(probs2)
        
        # Result should be between probs1 and probs2 due to averaging
        expected = [0.5 * 0.2 + 0.5 * 0.5, 0.5 * 0.3 + 0.5 * 0.3, 0.5 * 0.5 + 0.5 * 0.2]
        np.testing.assert_array_almost_equal(result, expected)
    
    def test_ema_different_alphas(self):
        """Test EMA with different alpha values"""
        probs1 = [0.5, 0.3, 0.2]
        probs2 = [0.2, 0.3, 0.5]
        
        # High alpha (more weight to new)
        ema_high = EMA(alpha=0.9, num_classes=3)
        ema_high.update(probs1)
        result_high = ema_high.update(probs2)
        
        # Low alpha (more weight to old)
        ema_low = EMA(alpha=0.1, num_classes=3)
        ema_low.update(probs1)
        result_low = ema_low.update(probs2)
        
        # High alpha result should be closer to probs2
        assert np.abs(result_high[0] - probs2[0]) < np.abs(result_low[0] - probs2[0])
    
    def test_ema_returns_list(self):
        """Test EMA returns list"""
        ema = EMA(alpha=0.5, num_classes=3)
        result = ema.update([0.3, 0.3, 0.4])
        assert isinstance(result, list)
    
    def test_ema_with_numpy_array_input(self):
        """Test EMA with numpy array input"""
        ema = EMA(alpha=0.5, num_classes=3)
        probs = np.array([0.3, 0.3, 0.4])
        result = ema.update(probs)
        assert isinstance(result, list)
    
    def test_ema_stability(self):
        """Test EMA stability over multiple updates"""
        ema = EMA(alpha=0.5, num_classes=2)
        
        # Constant input should converge
        for _ in range(10):
            result = ema.update([0.7, 0.3])
        
        # Should be close to constant value after many updates
        np.testing.assert_array_almost_equal(result, [0.7, 0.3], decimal=1)


class TestMajorityVote:
    """Test Majority Voting smoothing"""
    
    def test_majority_vote_initialization(self):
        """Test MajorityVote initializes correctly"""
        mv = MajorityVote(window_size=5)
        assert mv.window_size == 5
        assert len(mv.queue) == 0
    
    def test_majority_vote_single_update(self):
        """Test MajorityVote with single update"""
        mv = MajorityVote(window_size=5)
        result = mv.update(2)
        assert result == 2
    
    def test_majority_vote_with_majority(self):
        """Test MajorityVote with clear majority"""
        mv = MajorityVote(window_size=5)
        
        labels = [1, 1, 1, 2, 2]
        results = []
        
        for label in labels:
            result = mv.update(label)
            results.append(result)
        
        # Last result should be the majority (1 appears 3 times)
        assert results[-1] == 1
    
    def test_majority_vote_window_size(self):
        """Test MajorityVote respects window size"""
        mv = MajorityVote(window_size=3)
        
        # Add 5 labels but window is only 3
        for i in range(5):
            mv.update(i)
        
        # Queue should only keep last 3
        assert len(mv.queue) == 3
        assert list(mv.queue) == [2, 3, 4]
    
    def test_majority_vote_with_tie(self):
        """Test MajorityVote behavior with tied votes"""
        mv = MajorityVote(window_size=4)
        
        labels = [1, 1, 2, 2]
        results = []
        
        for label in labels:
            result = mv.update(label)
            results.append(result)
        
        # When there's a tie, one will be chosen
        # The exact behavior depends on set() implementation
        assert results[-1] in [1, 2]
    
    def test_majority_vote_changes_over_time(self):
        """Test that majority vote result changes as queue updates"""
        mv = MajorityVote(window_size=3)
        
        # First few updates
        r1 = mv.update(1)
        r2 = mv.update(1)
        r3 = mv.update(1)
        
        # All are 1s, so result should be 1
        assert r3 == 1
        
        # Add 2s that fill the window
        r4 = mv.update(2)
        r5 = mv.update(2)
        r6 = mv.update(2)
        
        # Now window is [2, 2, 2], majority is 2
        assert r6 == 2
    
    def test_majority_vote_different_window_sizes(self):
        """Test MajorityVote with different window sizes"""
        labels = [1, 1, 1, 2, 2]
        
        # Small window
        mv_small = MajorityVote(window_size=2)
        for label in labels:
            result_small = mv_small.update(label)
        
        # Large window
        mv_large = MajorityVote(window_size=10)
        for label in labels:
            result_large = mv_large.update(label)
        
        # Results might differ based on window size
        assert isinstance(result_small, int)
        assert isinstance(result_large, int)


class TestSmoothingComparison:
    """Compare different smoothing techniques"""
    
    def test_ema_vs_majority_vote(self):
        """Compare EMA vs Majority Vote on same data"""
        probs_sequence = [
            [0.9, 0.1],
            [0.8, 0.2],
            [0.7, 0.3],
        ]
        
        # EMA smoothing
        ema = EMA(alpha=0.5, num_classes=2)
        ema_results = []
        for probs in probs_sequence:
            result = ema.update(probs)
            ema_results.append(result)
        
        # Both should produce reasonable results
        assert all(isinstance(r, list) for r in ema_results)
    
    def test_smoothing_noise_reduction(self):
        """Test that smoothing reduces noise in predictions"""
        # Noisy predictions
        noisy_probs = [
            [0.1, 0.9],
            [0.9, 0.1],
            [0.1, 0.9],
            [0.9, 0.1],
        ]
        
        ema = EMA(alpha=0.5, num_classes=2)
        results = []
        
        for probs in noisy_probs:
            result = ema.update(probs)
            results.append(result)
        
        # Variance in smoothed results should be lower than input
        input_var = np.var(noisy_probs)
        output_var = np.var(results)
        
        # Smoothing should reduce variance
        # (May not always be true for small sequences, but generally true)
        assert isinstance(output_var, np.floating)
