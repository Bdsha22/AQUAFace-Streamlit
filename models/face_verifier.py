# ============================================================================
# AQUAFace-Lite: Face Verification Backend
# ============================================================================

import numpy as np
import cv2
from PIL import Image
import io
from insightface.app import FaceAnalysis
import streamlit as st

class AQUAFaceVerifier:
    """
    Quality-Adaptive Face Verification System
    Combines ArcFace embeddings with image quality metrics
    """
    
    def __init__(self, gpu_id=0):
        """Initialize ArcFace model and quality metrics"""
        try:
            self.app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
            self.app.prepare(ctx_id=gpu_id, det_size=(640, 640))
            self.initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize GPU, falling back to CPU: {e}")
            self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
            self.app.prepare(ctx_id=-1, det_size=(640, 640))
            self.initialized = True
    
    def extract_embedding(self, img_bgr):
        """
        Extract 512-D embedding from face image
        
        Args:
            img_bgr: Image in BGR format (numpy array)
            
        Returns:
            embedding: 512-D normalized embedding, or None if no face detected
            face_detected: Boolean indicating if face was detected
        """
        try:
            faces = self.app.get(img_bgr)
            
            if len(faces) == 0:
                return None, False
            
            # Get largest face (by area)
            face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
            
            # Extract embedding and normalize
            embedding = face.embedding.astype(np.float32)
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding, True
        
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None, False
    
    def compute_image_quality(self, img_bgr):
        """
        Compute image quality metrics (sharpness + brightness)
        
        Args:
            img_bgr: Image in BGR format
            
        Returns:
            sharpness: Laplacian variance (0-1 normalized)
            brightness: Mean pixel intensity (0-1 normalized)
        """
        try:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Sharpness: Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness = min(1.0, laplacian_var / 1000.0)  # Normalize
            
            # Brightness: mean pixel intensity
            brightness_raw = gray.mean()
            brightness = brightness_raw / 255.0  # Normalize to 0-1
            
            return sharpness, brightness
        
        except Exception as e:
            print(f"Error computing quality: {e}")
            return 0.0, 0.5
    
    def verify(self, img_a_bgr, img_b_bgr, use_quality_weighting=True, threshold=0.75):
        """
        Verify if two faces belong to the same person
        
        Args:
            img_a_bgr: First image (BGR format)
            img_b_bgr: Second image (BGR format)
            use_quality_weighting: Whether to apply quality weighting
            threshold: Decision threshold (above = SAME person)
            
        Returns:
            dict with verification results and metrics
        """
        
        results = {
            "error": False,
            "error_message": "",
            "verdict": False,
            "confidence": 0.0,
            "baseline_similarity": 0.0,
            "quality_weighted_similarity": 0.0,
            "quality_a": {"overall": 0.0, "sharpness": 0.0, "brightness": 0.0, "face_detected": False},
            "quality_b": {"overall": 0.0, "sharpness": 0.0, "brightness": 0.0, "face_detected": False}
        }
        
        try:
            # Extract embeddings
            emb_a, face_a_detected = self.extract_embedding(img_a_bgr)
            emb_b, face_b_detected = self.extract_embedding(img_b_bgr)
            
            # Check if faces detected
            if emb_a is None or emb_b is None:
                results["error"] = True
                if not face_a_detected:
                    results["error_message"] = "❌ No face detected in Image A"
                elif not face_b_detected:
                    results["error_message"] = "❌ No face detected in Image B"
                else:
                    results["error_message"] = "❌ No faces detected in one or both images"
                return results
            
            # Compute quality metrics
            sharp_a, bright_a = self.compute_image_quality(img_a_bgr)
            sharp_b, bright_b = self.compute_image_quality(img_b_bgr)
            
            # Overall quality (sharpness × brightness)
            quality_a = sharp_a * bright_b
            quality_b = sharp_b * bright_b
            
            # Store quality metrics
            results["quality_a"] = {
                "overall": float(quality_a),
                "sharpness": float(sharp_a),
                "brightness": float(bright_a),
                "face_detected": True
            }
            results["quality_b"] = {
                "overall": float(quality_b),
                "sharpness": float(sharp_b),
                "brightness": float(bright_b),
                "face_detected": True
            }
            
            # Compute baseline similarity (cosine)
            baseline_sim = np.dot(emb_a, emb_b)
            results["baseline_similarity"] = float(baseline_sim)
            
            # Compute quality-weighted similarity
            if use_quality_weighting:
                q_min = min(quality_a, quality_b)  # Bottleneck principle
                quality_weighted_sim = baseline_sim * q_min
            else:
                quality_weighted_sim = baseline_sim
            
            results["quality_weighted_similarity"] = float(quality_weighted_sim)
            
            # Decision
            decision_score = quality_weighted_sim if use_quality_weighting else baseline_sim
            results["verdict"] = decision_score > threshold
            
            # Confidence (0-100%)
            if use_quality_weighting:
                confidence = (quality_weighted_sim / threshold) * 100 if quality_weighted_sim > 0 else 0
            else:
                confidence = (baseline_sim / threshold) * 100 if baseline_sim > 0 else 0
            
            confidence = min(100.0, max(0.0, confidence))  # Clamp to 0-100
            results["confidence"] = float(confidence)
            
            return results
        
        except Exception as e:
            results["error"] = True
            results["error_message"] = f"Error during verification: {str(e)}"
            return results
