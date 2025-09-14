from collections import deque
from typing import List, Dict
import numpy as np

class EMA:
    def __init__(self, alpha: float = 0.5, num_classes: int = 13):
        self.alpha = alpha
        self.ema = np.zeros(num_classes)
        self.initialized = False

    def update(self, probs: List[float]) -> List[float]:
        probs_arr = np.asarray(probs, dtype=float)
        if not self.initialized:
            self.ema = probs_arr
            self.initialized = True
        else:
            self.ema = self.alpha * probs_arr + (1 - self.alpha) * self.ema
        return self.ema.tolist()

class MajorityVote:
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.queue = deque(maxlen=window_size)

    def update(self, label: int) -> int:
        self.queue.append(label)
        return max(set(self.queue), key=self.queue.count)
