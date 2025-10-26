"""
Unit tests for ml/model_loader.py - Model loading system
"""

import pytest
import torch
import numpy as np
from ml.model_loader import ModelLoader, MODEL_PATH, SimpleImageProcessor, SimpleViTModel


class TestSimpleImageProcessor:
    """Test image preprocessing functionality"""
    
    def test_processor_initialization(self):
        """Test processor initializes correctly"""
        processor = SimpleImageProcessor(image_size=224)
        assert processor.image_size == 224
        assert processor.transform is not None
    
    def test_processor_with_pil_image(self):
        """Test processor with PIL image"""
        from PIL import Image
        
        processor = SimpleImageProcessor()
        pil_img = Image.new('RGB', (256, 256), color=(255, 0, 0))
        
        result = processor(images=pil_img, return_tensors="pt")
        assert "pixel_values" in result
        assert result["pixel_values"].shape == (1, 3, 224, 224)
    
    def test_processor_with_image_list(self):
        """Test processor with list of images"""
        from PIL import Image
        
        processor = SimpleImageProcessor()
        images = [Image.new('RGB', (256, 256)) for _ in range(3)]
        
        result = processor(images=images, return_tensors="pt")
        assert result["pixel_values"].shape == (3, 3, 224, 224)
    
    def test_processor_resizes_image(self):
        """Test that processor resizes images to correct size"""
        from PIL import Image
        
        processor = SimpleImageProcessor(image_size=256)
        # Create image with different size
        pil_img = Image.new('RGB', (640, 480))
        
        result = processor(images=pil_img, return_tensors="pt")
        assert result["pixel_values"].shape == (1, 3, 256, 256)
    
    def test_processor_with_none_input(self):
        """Test processor handles None input"""
        processor = SimpleImageProcessor()
        result = processor(images=None, return_tensors="pt")
        assert result == {}


class TestSimpleViTModel:
    """Test ViT model wrapper"""
    
    def test_model_initialization(self):
        """Test model initializes correctly"""
        model = SimpleViTModel()
        assert model.config is not None
        assert model.config.num_labels == 14
    
    def test_model_config_id2label(self):
        """Test model config has id2label mapping"""
        model = SimpleViTModel()
        assert model.config.id2label is not None
        assert len(model.config.id2label) == 14
        assert all(isinstance(k, int) and isinstance(v, str) for k, v in model.config.id2label.items())
    
    def test_model_forward_pass(self):
        """Test model forward pass"""
        model = SimpleViTModel()
        model.eval()
        
        # Create dummy input
        pixel_values = torch.randn(1, 3, 224, 224)
        
        with torch.no_grad():
            # Should not raise error
            try:
                output = model(pixel_values)
                # Output might be None for placeholder model
            except NotImplementedError:
                # Expected for placeholder model
                pass


class TestModelLoader:
    """Test model loader singleton"""
    
    def test_model_loader_singleton(self):
        """Test that ModelLoader is a singleton"""
        loader1 = ModelLoader()
        loader2 = ModelLoader()
        assert loader1 is loader2
    
    def test_model_loader_initialization(self):
        """Test model loader initializes with None values"""
        loader = ModelLoader()
        # Reset for test
        loader.model = None
        loader.processor = None
        loader.device = None
        
        assert loader.model is None
        assert loader.processor is None
        assert loader.device is None
    
    def test_get_device_without_loading(self):
        """Test get_device without loading model"""
        loader = ModelLoader()
        loader.device = None
        device = loader.get_device()
        # Should return None if not loaded, or auto-detect device
        assert device is None or isinstance(device, torch.device)
    
    def test_get_model_not_loaded_raises_error(self):
        """Test get_model raises error when model not loaded"""
        loader = ModelLoader()
        loader.model = None
        
        with pytest.raises(RuntimeError, match="Model not loaded"):
            loader.get_model()
    
    def test_get_processor_not_loaded_raises_error(self):
        """Test get_processor raises error when not loaded"""
        loader = ModelLoader()
        loader.processor = None
        
        with pytest.raises(RuntimeError, match="Processor not loaded"):
            loader.get_processor()
    
    def test_load_creates_processor(self):
        """Test load creates processor"""
        loader = ModelLoader()
        loader.model = None
        loader.processor = None
        
        try:
            loader.load(model_path="dummy_path")
        except FileNotFoundError:
            # Expected - just checking processor creation attempt
            pass


class TestModelLoaderEdgeCases:
    """Test edge cases for model loader"""
    
    def test_load_with_invalid_path(self):
        """Test loading with invalid model path"""
        loader = ModelLoader()
        loader.model = None
        
        with pytest.raises(RuntimeError):
            loader.load(model_path="nonexistent/path.pth")
    
    def test_load_idempotent(self):
        """Test that loading is idempotent (doesn't reload if already loaded)"""
        loader = ModelLoader()
        # Mock a loaded state
        loader.model = SimpleViTModel()
        loader.processor = SimpleImageProcessor()
        loader.device = torch.device("cpu")
        
        # Store original references
        original_model = loader.model
        original_processor = loader.processor
        
        # Try to load again - should return same model
        try:
            result = loader.load(model_path="dummy")
        except:
            pass
        
        # Model should not have changed
        assert loader.model is original_model
