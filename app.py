# ============================================================================
# AQUAFace-Lite: Quality-Adaptive Face Verification
# Streamlit Web Application
# ============================================================================

import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import plotly.graph_objects as go
import plotly.express as px
from models.face_verifier import AQUAFaceVerifier
from utils.quality_metrics import compute_quality_metrics
from utils.visualization import plot_comparison, plot_quality_analysis
import json
from datetime import datetime

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="AQUAFace-Lite | Face Verification",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1em;
    }
    .subheader-text {
        font-size: 1.1em;
        color: #666;
        text-align: center;
        margin-bottom: 2em;
    }
    .result-same {
        background-color: #d4edda;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        font-size: 1.3em;
        font-weight: bold;
        color: #155724;
    }
    .result-diff {
        background-color: #f8d7da;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #dc3545;
        font-size: 1.3em;
        font-weight: bold;
        color: #721c24;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .confidence-high {
        color: #28a745;
        font-weight: bold;
    }
    .confidence-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .confidence-low {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if "verifier" not in st.session_state:
    st.session_state.verifier = None

if "results" not in st.session_state:
    st.session_state.results = None

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">🎭 AQUAFace-Lite</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-text">Quality-Adaptive Face Verification System</div>', unsafe_allow_html=True)
st.markdown("""
<p style="text-align: center; color: #888; font-size: 0.95em;">
    Verify if two face images belong to the same person using AI-powered face recognition with quality weighting
</p>
""", unsafe_allow_html=True)

st.divider()

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Model Settings")
    use_quality_weighting = st.toggle(
        "Enable Quality Weighting",
        value=True,
        help="Weight similarity scores by image quality (sharpness & brightness)"
    )
    
    threshold = st.slider(
        "Similarity Threshold",
        min_value=0.0,
        max_value=1.0,
        value=0.75,
        step=0.05,
        help="Score above this threshold = SAME person"
    )
    
    st.divider()
    st.subheader("About")
    st.info("""
    **AQUAFace-Lite** improves upon standard ArcFace face verification by incorporating 
    image quality metrics (sharpness + brightness). This helps make more reliable decisions, 
    especially on lower-quality images.
    
    **Baseline:** Pure cosine similarity
    **AQUAFace-Lite:** Quality-weighted cosine similarity
    """)
    
    st.divider()
    st.subheader("Project Info")
    st.markdown("""
    - **Model:** InsightFace ArcFace
    - **Backbone:** ResNet50 (512-D embeddings)
    - **Quality Metrics:** Laplacian Sharpness + Brightness
    - **Deployment:** Streamlit Cloud
    """)

# ============================================================================
# MAIN APP
# ============================================================================

col1, col2 = st.columns(2, gap="large")

# ============================================================================
# IMAGE UPLOAD SECTION
# ============================================================================

with col1:
    st.subheader("📤 Upload Image A")
    img_a_file = st.file_uploader(
        "Choose first face image",
        type=["jpg", "jpeg", "png"],
        key="img_a",
        help="PNG or JPG, recommended: 112x112 or larger"
    )
    
    if img_a_file:
        img_a_pil = Image.open(img_a_file).convert('RGB')
        img_a_np = np.array(img_a_pil)[:, :, ::-1]  # RGB to BGR
        st.image(img_a_pil, use_column_width=True, caption="Image A Preview")
    else:
        st.info("Upload an image to get started")
        img_a_np = None

with col2:
    st.subheader("📤 Upload Image B")
    img_b_file = st.file_uploader(
        "Choose second face image",
        type=["jpg", "jpeg", "png"],
        key="img_b",
        help="PNG or JPG, recommended: 112x112 or larger"
    )
    
    if img_b_file:
        img_b_pil = Image.open(img_b_file).convert('RGB')
        img_b_np = np.array(img_b_pil)[:, :, ::-1]  # RGB to BGR
        st.image(img_b_pil, use_column_width=True, caption="Image B Preview")
    else:
        st.info("Upload an image to get started")
        img_b_np = None

# ============================================================================
# VERIFICATION BUTTON
# ============================================================================

st.divider()

col_verify = st.columns([1, 1, 1])
with col_verify[1]:
    verify_button = st.button(
        "🔍 Verify Faces",
        use_container_width=True,
        type="primary",
        disabled=(img_a_np is None or img_b_np is None)
    )

# ============================================================================
# PROCESSING AND RESULTS
# ============================================================================

if verify_button and img_a_np is not None and img_b_np is not None:
    try:
        with st.spinner("🔄 Processing... Detecting faces and extracting embeddings..."):
            
            # Initialize verifier
            if st.session_state.verifier is None:
                st.session_state.verifier = AQUAFaceVerifier()
            
            verifier = st.session_state.verifier
            
            # Verify faces
            results = verifier.verify(
                img_a_np,
                img_b_np,
                use_quality_weighting=use_quality_weighting,
                threshold=threshold
            )
            
            st.session_state.results = results
        
        st.divider()
        
        # ====================================================================
        # RESULTS DISPLAY
        # ====================================================================
        
        if results["error"]:
            st.error(f"❌ Error: {results['error_message']}")
        else:
            # Main Result
            st.subheader("📊 Verification Result")
            
            is_same = results["verdict"]
            confidence = results["confidence"]
            
            if is_same:
                st.markdown(
                    f'<div class="result-same">✅ SAME PERSON | Confidence: {confidence:.2f}%</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="result-diff">❌ DIFFERENT PERSON | Confidence: {abs(100 - confidence):.2f}%</div>',
                    unsafe_allow_html=True
                )
            
            st.divider()
            
            # Similarity Scores
            st.subheader("📈 Similarity Analysis")
            
            col_scores1, col_scores2, col_scores3 = st.columns(3)
            
            with col_scores1:
                st.metric(
                    "Baseline ArcFace",
                    f"{results['baseline_similarity']:.4f}",
                    help="Pure cosine similarity between embeddings"
                )
            
            with col_scores2:
                if use_quality_weighting:
                    st.metric(
                        "AQUAFace-Lite (Weighted)",
                        f"{results['quality_weighted_similarity']:.4f}",
                        help="Quality-adjusted similarity"
                    )
                else:
                    st.metric(
                        "Quality-Weighted",
                        "N/A",
                        help="Disabled in configuration"
                    )
            
            with col_scores3:
                st.metric(
                    "Decision Threshold",
                    f"{threshold:.4f}",
                    help="Scores above this → SAME person"
                )
            
            # Quality Analysis
            st.subheader("🎨 Quality Analysis")
            
            col_qa1, col_qa2 = st.columns(2)
            
            with col_qa1:
                st.markdown("#### Image A Quality")
                qa_a = results["quality_a"]
                
                col_qa_a1, col_qa_a2 = st.columns(2)
                with col_qa_a1:
                    st.metric("Overall Quality", f"{qa_a['overall']:.2f}", help="0-1 scale")
                with col_qa_a2:
                    if qa_a['overall'] >= 0.7:
                        st.metric("Rating", "🟢 High", help="Good quality image")
                    elif qa_a['overall'] >= 0.5:
                        st.metric("Rating", "🟡 Medium", help="Acceptable quality")
                    else:
                        st.metric("Rating", "🔴 Low", help="Poor quality image")
                
                with st.expander("📋 Details"):
                    st.write(f"**Sharpness:** {qa_a['sharpness']:.3f}")
                    st.write(f"**Brightness:** {qa_a['brightness']:.3f}")
                    st.write(f"**Face Detected:** {'Yes ✅' if qa_a['face_detected'] else 'No ❌'}")
            
            with col_qa2:
                st.markdown("#### Image B Quality")
                qa_b = results["quality_b"]
                
                col_qa_b1, col_qa_b2 = st.columns(2)
                with col_qa_b1:
                    st.metric("Overall Quality", f"{qa_b['overall']:.2f}", help="0-1 scale")
                with col_qa_b2:
                    if qa_b['overall'] >= 0.7:
                        st.metric("Rating", "🟢 High", help="Good quality image")
                    elif qa_b['overall'] >= 0.5:
                        st.metric("Rating", "🟡 Medium", help="Acceptable quality")
                    else:
                        st.metric("Rating", "🔴 Low", help="Poor quality image")
                
                with st.expander("📋 Details"):
                    st.write(f"**Sharpness:** {qa_b['sharpness']:.3f}")
                    st.write(f"**Brightness:** {qa_b['brightness']:.3f}")
                    st.write(f"**Face Detected:** {'Yes ✅' if qa_b['face_detected'] else 'No ❌'}")
            
            st.divider()
            
            # Visualizations
            st.subheader("📊 Visualizations")
            
            fig_comparison = plot_comparison(results)
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            fig_quality = plot_quality_analysis(results)
            st.plotly_chart(fig_quality, use_container_width=True)
            
            st.divider()
            
            # Export Results
            st.subheader("💾 Export Results")
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "verdict": "SAME" if is_same else "DIFFERENT",
                "confidence": float(confidence),
                "baseline_similarity": float(results["baseline_similarity"]),
                "quality_weighted_similarity": float(results["quality_weighted_similarity"]),
                "threshold": float(threshold),
                "quality_a": {
                    "overall": float(qa_a["overall"]),
                    "sharpness": float(qa_a["sharpness"]),
                    "brightness": float(qa_a["brightness"])
                },
                "quality_b": {
                    "overall": float(qa_b["overall"]),
                    "sharpness": float(qa_b["sharpness"]),
                    "brightness": float(qa_b["brightness"])
                }
            }
            
            json_str = json.dumps(export_data, indent=2)
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=json_str,
                    file_name=f"aquaface_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col_export2:
                st.download_button(
                    label="📋 Download Report (TXT)",
                    data=f"""AQUAFace-Lite Verification Report
================================

Result: {export_data['verdict']}
Confidence: {export_data['confidence']:.2f}%
Timestamp: {export_data['timestamp']}

Similarity Scores:
- Baseline ArcFace: {export_data['baseline_similarity']:.4f}
- AQUAFace-Lite: {export_data['quality_weighted_similarity']:.4f}
- Decision Threshold: {export_data['threshold']:.4f}

Image A Quality:
- Overall: {export_data['quality_a']['overall']:.2f}
- Sharpness: {export_data['quality_a']['sharpness']:.3f}
- Brightness: {export_data['quality_a']['brightness']:.3f}

Image B Quality:
- Overall: {export_data['quality_b']['overall']:.2f}
- Sharpness: {export_data['quality_b']['sharpness']:.3f}
- Brightness: {export_data['quality_b']['brightness']:.3f}
""",
                    file_name=f"aquaface_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    except Exception as e:
        st.error(f"❌ Error during verification: {str(e)}")
        st.write("Please ensure both images contain clear faces.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9em; margin-top: 3em;">
    <p><strong>AQUAFace-Lite</strong> | Quality-Adaptive Face Verification</p>
    <p>Built with InsightFace ArcFace • Streamlit Cloud Deployment</p>
    <p style="font-size: 0.85em;">© 2025 Research Project | Contact: Your Name</p>
</div>
""", unsafe_allow_html=True)
