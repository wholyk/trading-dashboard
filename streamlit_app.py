"""
TradingView Chart Analyzer - Streamlit Dashboard

This application provides a user interface for analyzing TradingView screenshots
to detect liquidity sweeps and Break of Structure (BOS) patterns.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from chart_analyzer import ChartAnalyzer


# Page configuration
st.set_page_config(
    page_title="TradingView Chart Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ChartAnalyzer()

# Title and description
st.title("📊 TradingView Chart Analyzer")
st.markdown("""
This tool analyzes TradingView screenshots to detect:
- **Liquidity Sweeps**: Price movements that quickly reverse after breaking key levels
- **Break of Structure (BOS)**: Clear breaks of previous market structure

Upload a TradingView screenshot to get started.
""")

# Sidebar
with st.sidebar:
    st.header("Settings")
    st.markdown("### About")
    st.info("""
    **Liquidity Sweep Detection**
    - Identifies wick patterns
    - Detects spike formations
    - Analyzes reversal structures
    
    **BOS Detection**
    - Identifies support/resistance breaks
    - Analyzes directional momentum
    - Detects structure changes
    """)
    
    if st.button("Clear Analysis Log"):
        st.session_state.analyzer.clear_log()
        st.success("Log cleared!")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Upload Screenshot")
    uploaded_file = st.file_uploader(
        "Choose a TradingView screenshot",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a screenshot from TradingView"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Screenshot", use_container_width=True)
        
        # Analyze button
        if st.button("🔍 Analyze Chart", type="primary"):
            with st.spinner("Analyzing chart..."):
                # Read image data
                image_data = uploaded_file.getvalue()
                
                # Perform analysis
                results = st.session_state.analyzer.analyze_screenshot(
                    image_data,
                    filename=uploaded_file.name
                )
                
                # Store results in session state
                st.session_state.latest_results = results
                st.success("Analysis complete!")

with col2:
    st.header("Analysis Results")
    
    if 'latest_results' in st.session_state:
        results = st.session_state.latest_results
        
        # Display confidence scores
        st.subheader("Confidence Scores")
        
        # Overall confidence
        overall_conf = results['overall_confidence']
        st.metric(
            "Overall Confidence",
            f"{overall_conf:.1%}",
            help="Combined confidence of both patterns"
        )
        
        # Individual confidences
        col_a, col_b = st.columns(2)
        
        with col_a:
            liq_conf = results['liquidity_sweep']['confidence']
            st.metric(
                "Liquidity Sweep",
                f"{liq_conf:.1%}",
                help="Confidence of liquidity sweep detection"
            )
        
        with col_b:
            bos_conf = results['break_of_structure']['confidence']
            st.metric(
                "Break of Structure",
                f"{bos_conf:.1%}",
                help="Confidence of BOS detection"
            )
        
        # Progress bars for visualization
        st.subheader("Pattern Detection")
        
        st.write("**Liquidity Sweep Indicators:**")
        st.progress(liq_conf, text=f"Confidence: {liq_conf:.1%}")
        
        st.write("**Break of Structure Indicators:**")
        st.progress(bos_conf, text=f"Confidence: {bos_conf:.1%}")
        
        # Detailed metrics in expander
        with st.expander("📊 Detailed Metrics"):
            st.markdown("### Liquidity Sweep Metrics")
            liq_metrics = results['liquidity_sweep']['metrics']
            st.write(f"- **Wick Count**: {liq_metrics['wick_count']}")
            st.write(f"- **Significant Wicks**: {liq_metrics['significant_wicks']}")
            st.write(f"- **Edge Density**: {liq_metrics['edge_density']:.4f}")
            
            st.markdown("### Break of Structure Metrics")
            bos_metrics = results['break_of_structure']['metrics']
            st.write(f"- **Horizontal Lines**: {bos_metrics['horizontal_lines']}")
            st.write(f"- **Average Gradient**: {bos_metrics['avg_gradient']:.2f}")
            st.write(f"- **Green Presence**: {bos_metrics['green_presence']:.4f}")
            st.write(f"- **Red Presence**: {bos_metrics['red_presence']:.4f}")
            st.write(f"- **Color Contrast**: {bos_metrics['color_contrast']:.4f}")
        
        # Image information
        with st.expander("🔍 Image Information"):
            st.write(f"**Filename**: {results['filename']}")
            st.write(f"**Image Hash**: `{results['image_hash']}`")
            st.write(f"**Timestamp**: {results['timestamp']}")
            st.write(f"**Image Size**: {results['image_size'][0]} × {results['image_size'][1]} pixels")
    else:
        st.info("👆 Upload a screenshot and click 'Analyze Chart' to see results")

# Analysis log section
st.header("📝 Analysis Log")

log = st.session_state.analyzer.get_analysis_log()

if log:
    # Convert log to DataFrame
    df = pd.DataFrame(log)
    
    # Display as table
    st.dataframe(
        df,
        column_config={
            "timestamp": "Timestamp",
            "image_hash": st.column_config.TextColumn(
                "Image Hash",
                help="SHA-256 hash of the screenshot",
                width="medium"
            ),
            "filename": "Filename",
            "liquidity_sweep_confidence": st.column_config.ProgressColumn(
                "Liquidity Sweep",
                format="%.1f%%",
                min_value=0,
                max_value=1
            ),
            "bos_confidence": st.column_config.ProgressColumn(
                "BOS",
                format="%.1f%%",
                min_value=0,
                max_value=1
            ),
            "overall_confidence": st.column_config.ProgressColumn(
                "Overall",
                format="%.1f%%",
                min_value=0,
                max_value=1
            )
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Download log as CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Log as CSV",
        data=csv,
        file_name=f"chart_analysis_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("No analyses yet. Upload and analyze screenshots to build the log.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>TradingView Chart Analyzer | Pattern Detection with Computer Vision</small>
</div>
""", unsafe_allow_html=True)
