"""
Unit tests for ml/inference.py - Model inference
"""

import pytest
import numpy as np
import torch
from unittest.mock import Mock, patch, MagicMock
from PIL import Image


class TestBgrToPil:
    """Test BGR to PIL conversion"""
    
    @patch('ml.inference.cv2')
    def test_bgr_to_pil_conversion(self, mock_cv2):
        """Test BGR frame conversion to PIL image"""
        from ml.inference import bgr_to_pil
        
        # Create mock BGR frame
        bgr_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Mock cv2.cvtColor to return RGB
        mock_cv2.cvtColor.return_value = bgr_frame
        mock_cv2.COLOR_BGR2RGB = 4
        
        # Call function
        result = bgr_to_pil(bgr_frame)
        
        # Should be PIL Image
        assert isinstance(result, Image.Image)
        # Should have called cvtColor
        mock_cv2.cvtColor.assert_called_once()
    
    @patch('ml.inference.cv2')
    def test_bgr_to_pil_with_none_frame(self, mock_cv2):
        """Test BGR to PIL with None frame"""
        from ml.inference import bgr_to_pil
        
        mock_cv2.cvtColor.side_effect = Exception("Cannot process None")
        
        with pytest.raises(ValueError):
            bgr_to_pil(None)


class TestPredictFrame:
    """Test single frame prediction"""
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    @patch('ml.inference.device')
    @patch('ml.inference.bgr_to_pil')
    def test_predict_frame_success(self, mock_bgr_to_pil, mock_device, mock_processor, mock_model):
        """Test successful frame prediction"""
        from ml.inference import predict_frame
        
        # Setup mocks
        mock_device.return_value = torch.device("cpu")
        mock_bgr_to_pil.return_value = Image.new('RGB', (224, 224))
        
        # Mock processor output
        mock_processor.return_value = {
            "pixel_values": torch.randn(1, 3, 224, 224)
        }
        
        # Mock model output
        mock_logits = torch.randn(1, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = {i: f"class_{i}" for i in range(14)}
        
        # Create frame
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Make prediction
        result = predict_frame(frame, top_k=3)
        
        # Should return dict with predictions
        assert isinstance(result, dict)
        assert len(result) <= 3
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_predict_frame_with_empty_frame(self, mock_processor, mock_model):
        """Test prediction with empty frame"""
        from ml.inference import predict_frame
        
        frame = np.array([])
        
        with pytest.raises(RuntimeError):
            predict_frame(frame)
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_predict_frame_with_different_top_k(self, mock_processor, mock_model):
        """Test prediction with different top_k values"""
        from ml.inference import predict_frame
        
        mock_processor.return_value = {"pixel_values": torch.randn(1, 3, 224, 224)}
        mock_logits = torch.randn(1, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = {i: f"class_{i}" for i in range(14)}
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result1 = predict_frame(frame, top_k=1)
        result2 = predict_frame(frame, top_k=5)
        
        # top_k=1 should have 1 result, top_k=5 should have up to 5
        assert len(result1) <= 1
        assert len(result2) <= 5


class TestPredictBatch:
    """Test batch prediction"""
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    @patch('ml.inference.bgr_to_pil')
    def test_predict_batch_success(self, mock_bgr_to_pil, mock_processor, mock_model):
        """Test successful batch prediction"""
        from ml.inference import predict_batch
        
        # Setup mocks
        mock_bgr_to_pil.return_value = Image.new('RGB', (224, 224))
        mock_processor.return_value = {
            "pixel_values": torch.randn(5, 3, 224, 224)
        }
        
        # Mock model output for batch
        mock_logits = torch.randn(5, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = {i: f"class_{i}" for i in range(14)}
        
        # Create batch of frames
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(5)]
        
        # Make batch prediction
        results = predict_batch(frames, top_k=3)
        
        # Should return list of dicts
        assert isinstance(results, list)
        assert len(results) == 5
        assert all(isinstance(r, dict) for r in results)
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_predict_batch_empty_list(self, mock_processor, mock_model):
        """Test batch prediction with empty frame list"""
        from ml.inference import predict_batch
        
        results = predict_batch([], top_k=3)
        assert results == []
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_predict_batch_with_different_sizes(self, mock_processor, mock_model):
        """Test batch prediction with different batch sizes"""
        from ml.inference import predict_batch
        
        mock_processor.return_value = {
            "pixel_values": torch.randn(3, 3, 224, 224)
        }
        mock_logits = torch.randn(3, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = {i: f"class_{i}" for i in range(14)}
        
        frames = [np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8) for _ in range(3)]
        
        results = predict_batch(frames)
        assert len(results) == 3


class TestInferenceEdgeCases:
    """Test edge cases in inference"""
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_inference_with_missing_id2label(self, mock_processor, mock_model):
        """Test inference when id2label is missing"""
        from ml.inference import predict_frame
        
        mock_processor.return_value = {"pixel_values": torch.randn(1, 3, 224, 224)}
        mock_logits = torch.randn(1, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = None  # Missing id2label
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Should fall back to string IDs
        result = predict_frame(frame, top_k=3)
        assert isinstance(result, dict)
    
    @patch('ml.inference.model')
    @patch('ml.inference.processor')
    def test_inference_torch_device_movement(self, mock_processor, mock_model):
        """Test that tensors are moved to correct device"""
        from ml.inference import predict_frame
        
        device = torch.device("cpu")
        pixel_values = torch.randn(1, 3, 224, 224)
        mock_processor.return_value = {"pixel_values": pixel_values}
        mock_logits = torch.randn(1, 14)
        mock_model.return_value = Mock(logits=mock_logits)
        mock_model.config.id2label = {i: f"class_{i}" for i in range(14)}
        
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        result = predict_frame(frame)
        # Should not raise error
        assert isinstance(result, dict)
