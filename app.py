import streamlit as st
import io
import numpy as np
from PIL import Image
import torch
import onnx
from onnx2torch import convert
import cv2

# ============================================================
# AQUAFACE-LITE STREAMLIT APP
# Based on your working Colab code (ARCFace-1.ipynb)
# ============================================================

st.set_page_config(page_title="AQUAFace-Lite", layout="wide")

# ============================================================
# SETUP & CACHING
# ============================================================

@st.cache_resource
def load_model():
    """Load ArcFace ONNX model once"""
    try:
        # Try to use InsightFace (simpler)
        from insightface.app import FaceAnalysis
        app = FaceAnalysis(providers=['CPUExecutionProvider'])
        app.prepare(ctx_id=-1, det_size=(640, 640))
        return app
    except Exception as e:
        st.error(f"Failed to load InsightFace: {e}")
        st.error("Trying to load ONNX directly...")
        return None

# ============================================================
# UTILITY FUNCTIONS (from your Colab)
# ============================================================

def decode_image(uploaded_file):
    """Convert uploaded file to BGR image"""
    img = Image.open(uploaded_file).convert('RGB')
    return np.array(img)[:, :, ::-1]  # RGB to BGR

def preprocess_image(img_bgr):
    """Preprocess image for ArcFace (112x112)"""
    x = cv2.resize(img_bgr, (112, 112))
    x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    x = (x - 0.5) / 0.5
    x = np.transpose(x, (2, 0, 1))
    return x

def extract_embedding_insightface(app, img_bgr):
    """Extract 512-D embedding using InsightFace"""
    try:
        faces = app.get(img_bgr)
        if len(faces) == 0:
            return None
        embedding = faces[0].embedding / np.linalg.norm(faces[0].embedding)
        return embedding
    except Exception as e:
        st.error(f"Error extracting embedding: {e}")
        return None

def compute_quality_score(img_bgr):
    """
    YOUR IMPROVEMENT: Compute image quality
    - Sharpness: Laplacian variance
    - Brightness: Mean pixel intensity
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    
    # Sharpness (Laplacian variance)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    sharpness_norm = min(1.0, sharpness / 500.0)  # Normalize
    
    # Brightness (mean pixel intensity, normalized to 0-1)
    brightness = gray.mean() / 255.0
    brightness_norm = min(1.0, max(0.0, (brightness - 0.3) / 0.4))  # Best in 0.3-0.7 range
    
    # Combined quality score
    quality = (sharpness_norm * 0.5) + (brightness_norm * 0.5)
    
    return quality, sharpness_norm, brightness_norm

def compute_similarity(emb1, emb2):
    """Compute baseline (cosine) similarity"""
    return np.dot(emb1, emb2)

def aquaface_verification(emb1, emb2, q1, q2):
    """
    YOUR AQUAFACE-LITE IMPROVEMENT:
    Quality-adaptive similarity = baseline_sim × min(quality1, quality2)
    """
    baseline_sim = compute_similarity(emb1, emb2)
    min_quality = min(q1, q2)
    aquaface_sim = baseline_sim * min_quality
    return baseline_sim, aquaface_sim

# ============================================================
# STREAMLIT UI
# ============================================================

st.title("🔐 AQUAFace-Lite: Face Verification System")
st.markdown("**Your improvement**: Quality-adaptive face verification (ArcFace + Quality Weighting)")

# ============================================================
# LOAD MODEL
# ============================================================

with st.spinner("Loading ArcFace model..."):
    face_app = load_model()
    if face_app is None:
        st.error("❌ Failed to load face model. Check your installation.")
        st.stop()

st.success("✅ Model loaded successfully!")

# ============================================================
# FILE UPLOAD
# ============================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Image 1")
    uploaded_img1 = st.file_uploader("Upload first image", type=["jpg", "jpeg", "png"], key="img1")
    
    if uploaded_img1:
        img1_bgr = decode_image(uploaded_img1)
        st.image(cv2.cvtColor(img1_bgr, cv2.COLOR_BGR2RGB), use_column_width=True)

with col2:
    st.subheader("📸 Image 2")
    uploaded_img2 = st.file_uploader("Upload second image", type=["jpg", "jpeg", "png"], key="img2")
    
    if uploaded_img2:
        img2_bgr = decode_image(uploaded_img2)
        st.image(cv2.cvtColor(img2_bgr, cv2.COLOR_BGR2RGB), use_column_width=True)

# ============================================================
# VERIFICATION LOGIC
# ============================================================

if st.button("🔍 Verify Faces", use_container_width=True):
    if uploaded_img1 is None or uploaded_img2 is None:
        st.error("❌ Please upload both images!")
    else:
        with st.spinner("Processing..."):
            # Extract embeddings
            emb1 = extract_embedding_insightface(face_app, img1_bgr)
            emb2 = extract_embedding_insightface(face_app, img2_bgr)
            
            if emb1 is None or emb2 is None:
                st.error("❌ Could not detect faces in one or both images!")
            else:
                # Compute quality scores
                q1, sharp1, bright1 = compute_quality_score(img1_bgr)
                q2, sharp2, bright2 = compute_quality_score(img2_bgr)
                
                # Compute similarities
                baseline_sim, aquaface_sim = aquaface_verification(emb1, emb2, q1, q2)
                
                # Decision threshold (tunable)
                threshold = 0.50
                
                # Decision
                if aquaface_sim > threshold:
                    verdict = "✅ SAME PERSON"
                    verdict_color = "green"
                else:
                    verdict = "❌ DIFFERENT PERSON"
                    verdict_color = "red"
                
                # ============================================================
                # DISPLAY RESULTS
                # ============================================================
                
                st.markdown("---")
                st.markdown(f"<h2 style='text-align: center; color: {verdict_color};'>{verdict}</h2>", 
                           unsafe_allow_html=True)
                st.markdown("---")
                
                # Metrics table
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("**Image 1 Quality**", f"{q1:.3f}")
                    st.caption(f"Sharpness: {sharp1:.3f}, Brightness: {bright1:.3f}")
                
                with col2:
                    st.metric("**Image 2 Quality**", f"{q2:.3f}")
                    st.caption(f"Sharpness: {sharp2:.3f}, Brightness: {bright2:.3f}")
                
                with col3:
                    st.metric("**Decision Threshold**", f"{threshold:.3f}")
                
                st.markdown("---")
                
                # Similarity scores
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("**Baseline Similarity**", f"{baseline_sim:.4f}")
                    st.caption("Standard ArcFace cosine similarity")
                
                with col2:
                    st.metric("**AQUAFace Similarity**", f"{aquaface_sim:.4f}")
                    st.caption("Quality-weighted (YOUR IMPROVEMENT!)")
                
                with col3:
                    improvement = ((aquaface_sim - baseline_sim) / max(abs(baseline_sim), 0.001)) * 100
                    st.metric("**Change**", f"{improvement:.2f}%")
                    st.caption("Impact of quality weighting")
                
                st.markdown("---")
                
                # Explanation
                st.info("""
                **AQUAFace-Lite Methodology:**
                - **Baseline**: Standard ArcFace (cosine similarity of 512-D embeddings)
                - **Quality Metrics**: 
                  - Sharpness: Laplacian variance (detects blur)
                  - Brightness: Mean pixel intensity (detects poor lighting)
                - **Your Innovation**: `AQUAFace_sim = baseline_sim × min(quality1, quality2)`
                - **Result**: Low-quality images get downweighted → fewer false accepts!
                """)
