# ============================================================================
# Visualization Module for Results
# ============================================================================

import plotly.graph_objects as go
import plotly.express as px
import numpy as np

def plot_comparison(results):
    """
    Create comparison chart between baseline and AQUAFace-Lite
    
    Args:
        results: Verification results dictionary
        
    Returns:
        plotly figure
    """
    
    fig = go.Figure()
    
    # Add baseline bar
    fig.add_trace(go.Bar(
        x=['Baseline ArcFace'],
        y=[results['baseline_similarity']],
        name='Baseline',
        marker_color='#1f77b4',
        text=[f"{results['baseline_similarity']:.4f}"],
        textposition='outside',
        hovertemplate='<b>Baseline ArcFace</b><br>Similarity: %{y:.4f}<extra></extra>'
    ))
    
    # Add AQUAFace-Lite bar
    fig.add_trace(go.Bar(
        x=['AQUAFace-Lite'],
        y=[results['quality_weighted_similarity']],
        name='AQUAFace-Lite',
        marker_color='#ff7f0e',
        text=[f"{results['quality_weighted_similarity']:.4f}"],
        textposition='outside',
        hovertemplate='<b>AQUAFace-Lite</b><br>Similarity: %{y:.4f}<extra></extra>'
    ))
    
    # Add threshold line
    fig.add_hline(
        y=results.get('threshold', 0.75),
        line_dash="dash",
        line_color="red",
        annotation_text="Decision Threshold",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="Similarity Score Comparison",
        yaxis_title="Similarity Score (0-1)",
        xaxis_title="Method",
        barmode='group',
        height=400,
        showlegend=True,
        hovermode='x unified',
        plot_bgcolor='rgba(240,240,240,0.5)',
        yaxis=dict(range=[0, 1.1])
    )
    
    return fig

def plot_quality_analysis(results):
    """
    Create quality analysis visualization
    
    Args:
        results: Verification results dictionary
        
    Returns:
        plotly figure
    """
    
    qa_a = results['quality_a']
    qa_b = results['quality_b']
    
    # Prepare data for radar chart
    categories = ['Sharpness', 'Brightness', 'Overall']
    
    fig = go.Figure()
    
    # Image A
    fig.add_trace(go.Scatterpolar(
        r=[qa_a['sharpness'], qa_a['brightness'], qa_a['overall']],
        theta=categories,
        fill='toself',
        name='Image A',
        line_color='#1f77b4',
        fillcolor='rgba(31, 119, 180, 0.3)'
    ))
    
    # Image B
    fig.add_trace(go.Scatterpolar(
        r=[qa_b['sharpness'], qa_b['brightness'], qa_b['overall']],
        theta=categories,
        fill='toself',
        name='Image B',
        line_color='#ff7f0e',
        fillcolor='rgba(255, 127, 14, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=True,
        title="Image Quality Comparison",
        height=500,
        hovermode='closest'
    )
    
    return fig

def plot_similarity_distribution(baseline_scores, quality_scores, issame_labels=None):
    """
    Plot distribution of similarity scores
    
    Args:
        baseline_scores: Array of baseline similarities
        quality_scores: Array of quality-weighted similarities
        issame_labels: Array of labels (True = same person)
        
    Returns:
        plotly figure
    """
    
    fig = go.Figure()
    
    if issame_labels is not None:
        # Plot by label
        fig.add_trace(go.Histogram(
            x=baseline_scores[issame_labels],
            name='Baseline (Same Person)',
            marker_color='#1f77b4',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=baseline_scores[~issame_labels],
            name='Baseline (Different Person)',
            marker_color='#d62728',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=quality_scores[issame_labels],
            name='AQUAFace (Same Person)',
            marker_color='#2ca02c',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=quality_scores[~issame_labels],
            name='AQUAFace (Different Person)',
            marker_color='#ff7f0e',
            opacity=0.7,
            nbinsx=20
        ))
    else:
        fig.add_trace(go.Histogram(
            x=baseline_scores,
            name='Baseline',
            marker_color='#1f77b4',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=quality_scores,
            name='AQUAFace-Lite',
            marker_color='#ff7f0e',
            opacity=0.7,
            nbinsx=20
        ))
    
    fig.update_layout(
        title="Similarity Score Distribution",
        xaxis_title="Similarity Score",
        yaxis_title="Frequency",
        barmode='overlay',
        height=450,
        hovermode='x unified',
        plot_bgcolor='rgba(240,240,240,0.5)'
    )
    
    return fig

def plot_roc_curves(fpr_baseline, tpr_baseline, fpr_quality, tpr_quality, auc_baseline, auc_quality):
    """
    Plot ROC curves for comparison
    
    Args:
        fpr_baseline, tpr_baseline: False/True positive rates for baseline
        fpr_quality, tpr_quality: False/True positive rates for AQUAFace
        auc_baseline, auc_quality: Area under curve for both methods
        
    Returns:
        plotly figure
    """
    
    fig = go.Figure()
    
    # Baseline ROC
    fig.add_trace(go.Scatter(
        x=fpr_baseline,
        y=tpr_baseline,
        mode='lines',
        name=f'Baseline (AUC={auc_baseline:.4f})',
        line=dict(color='#1f77b4', width=3),
        hovertemplate='FPR: %{x:.4f}<br>TPR: %{y:.4f}<extra></extra>'
    ))
    
    # AQUAFace ROC
    fig.add_trace(go.Scatter(
        x=fpr_quality,
        y=tpr_quality,
        mode='lines',
        name=f'AQUAFace-Lite (AUC={auc_quality:.4f})',
        line=dict(color='#ff7f0e', width=3),
        hovertemplate='FPR: %{x:.4f}<br>TPR: %{y:.4f}<extra></extra>'
    ))
    
    # Random classifier
    fig.add_trace(go.Scatter(
        x=[0, 1],
        y=[0, 1],
        mode='lines',
        name='Random Classifier',
        line=dict(color='#d3d3d3', width=2, dash='dash'),
        hovertemplate='FPR: %{x:.4f}<br>TPR: %{y:.4f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="ROC Curve Comparison",
        xaxis_title="False Positive Rate",
        yaxis_title="True Positive Rate",
        height=500,
        xaxis=dict(range=[-0.02, 1.02]),
        yaxis=dict(range=[-0.02, 1.02]),
        hovermode='closest',
        plot_bgcolor='rgba(240,240,240,0.5)'
    )
    
    return fig
