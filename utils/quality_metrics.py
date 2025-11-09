# ============================================================================
# Quality Metrics Computation
# ============================================================================

import numpy as np
import cv2

def compute_quality_metrics(img_bgr):
    """
    Compute comprehensive quality metrics for a face image
    
    Args:
        img_bgr: Image in BGR format
        
    Returns:
        dict with quality metrics
    """
    
    try:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness = min(1.0, laplacian_var / 1000.0)
        
        # 2. Brightness (mean pixel intensity)
        brightness_raw = gray.mean()
        brightness = brightness_raw / 255.0
        
        # 3. Contrast (standard deviation)
        contrast = gray.std() / 255.0
        
        # 4. Image quality score (combined)
        quality_score = (sharpness * 0.5) + (brightness * 0.3) + (contrast * 0.2)
        quality_score = min(1.0, max(0.0, quality_score))
        
        return {
            "sharpness": sharpness,
            "brightness": brightness,
            "contrast": contrast,
            "overall_quality": quality_score
        }
    
    except Exception as e:
        print(f"Error computing quality metrics: {e}")
        return {
            "sharpness": 0.0,
            "brightness": 0.5,
            "contrast": 0.0,
            "overall_quality": 0.0
        }

def quality_report(quality_a, quality_b):
    """Generate quality comparison report"""
    
    report = {
        "image_a": quality_a,
        "image_b": quality_b,
        "recommendation": ""
    }
    
    # Generate recommendation
    avg_quality = (quality_a.get("overall_quality", 0) + quality_b.get("overall_quality", 0)) / 2
    
    if avg_quality >= 0.8:
        report["recommendation"] = "🟢 Excellent quality images. Verification highly reliable."
    elif avg_quality >= 0.6:
        report["recommendation"] = "🟡 Good quality images. Verification reliable."
    elif avg_quality >= 0.4:
        report["recommendation"] = "🟠 Fair quality images. Results may be less reliable."
    else:
        report["recommendation"] = "🔴 Poor quality images. Consider re-uploading clearer images."
    
    return report
