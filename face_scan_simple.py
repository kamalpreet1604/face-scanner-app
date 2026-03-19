import streamlit as st
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AI Face Scanner & Beauty Consultant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    h1 { color: #2c3e50; font-size: 2.5em; }
    h2 { color: #34495e; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }
    .success-box { background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; }
    .error-box { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 8px; }
    .info-box { background: #d1ecf1; color: #0c5460; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input("Enter your Google Gemini API Key", type="password", help="Get free key from aistudio.google.com")
    
    if api_key:
        try:
            genai.configure(api_key=api_key)
            st.session_state.api_configured = True
            st.success("✅ API Key configured!")
        except:
            st.error("❌ Invalid API Key")
            st.session_state.api_configured = False
    
    st.markdown("---")
    st.markdown("### 📋 Settings")
    detail_level = st.radio("Analysis Detail", ["Quick", "Standard", "Detailed"])
    include_products = st.checkbox("Include Product Recommendations", value=True)
    
    st.markdown("---")
    st.markdown("### 📜 History")
    st.write(f"Total analyses: {len(st.session_state.analysis_history)}")
    if st.button("🗑️ Clear History"):
        st.session_state.analysis_history = []
        st.rerun()

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("✨ AI Face Scan: Skincare & Makeup Planner")

st.markdown("""
<div style='background: #667eea; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;'>
📸 <b>How to use:</b> Take a clear photo of your bare face. The AI will analyze your skin and provide personalized skincare and makeup recommendations!
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CAMERA INPUT
# ============================================================================

st.markdown("## 📸 Capture Your Face")

col1, col2 = st.columns([1, 1])

with col1:
    camera_image = st.camera_input("Take a clear photo of your face")

with col2:
    st.markdown("""
    ### 💡 Tips for Best Results:
    - Use natural daylight or good lighting
    - Face the camera directly
    - Fill most of the frame
    - Minimal or no makeup
    - Neutral expression
    """)

# ============================================================================
# ANALYSIS
# ============================================================================

if camera_image is not None:
    if not st.session_state.api_configured:
        st.error("❌ Please configure your API key in the sidebar first!")
    else:
        st.markdown("## 🤖 Analysis Results")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.success("✅ Face captured!")
            image = Image.open(camera_image)
            st.image(image, use_column_width=True)
        
        with col2:
            st.info("🔄 Processing...")
        
        image = Image.open(camera_image)
        
        # Validate image
        if image.size[0] < 100 or image.size[1] < 100:
            st.warning("⚠️ Image too small. Please retake with your face filling more of the frame.")
        else:
            with st.spinner("🔍 Analyzing your face..."):
                try:
                    # Build prompt based on detail level
                    if detail_level == "Quick":
                        detail_text = "Provide brief 2-3 sentence analysis for each section."
                    elif detail_level == "Detailed":
                        detail_text = "Provide comprehensive, detailed analysis with multiple options."
                    else:
                        detail_text = "Provide standard detailed analysis with recommendations."
                    
                    product_text = "Include specific product recommendations." if include_products else "Provide general product type recommendations."
                    
                    prompt = f"""
You are an expert dermatologist and celebrity makeup artist. Analyze this face and provide:

{detail_text}
{product_text}

1. 🔍 SKIN & FACE ANALYSIS
- Skin type (oily, dry, combination, normal, sensitive)
- Undertone (warm, cool, neutral)
- Visible concerns
- Face shape
- Eye shape

2. 🧴 PRE-MAKEUP SKINCARE ROUTINE
- Cleanser recommendation
- Toner/Essence
- Serum
- Moisturizer
- Sunscreen
- Primer

3. 💄 MAKEUP RECOMMENDATIONS
- Foundation (finish and undertone)
- Blush colors
- Bronzer
- Eye makeup style
- Lip colors

4. ⚠️ SKIN CONCERNS & SOLUTIONS
If visible: identify and provide tips

5. 🌟 PERSONALIZED TIPS
3-5 specific tips for this person

Be warm, encouraging, and specific!
"""
                    
                    # Use the model that works
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content([prompt, image])
                    
                    # Display results
                    st.markdown("### 💖 Your Personalized Routine")
                    st.markdown(response.text)
                    
                    # Store in history
                    st.session_state.analysis_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "analysis": response.text
                    })
                    
                    # Download button
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        analysis_text = f"AI FACE SCAN ANALYSIS\nGenerated: {datetime.now()}\nDetail Level: {detail_level}\n\n{response.text}"
                        st.download_button(
                            "📥 Download Analysis",
                            analysis_text,
                            file_name=f"face_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        )
                    with col2:
                        if st.button("🔄 New Analysis"):
                            st.rerun()
                    with col3:
                        st.info(f"Analysis #{len(st.session_state.analysis_history)}")
                    
                    st.success("✅ Analysis complete!")
                
                except Exception as e:
                    st.error(f"❌ Analysis Error: {str(e)}")
                    st.write("**Try:**")
                    st.write("- Verify your API key is correct")
                    st.write("- Check internet connection")
                    st.write("- Retake photo with better lighting")

# ============================================================================
# FAQ
# ============================================================================

with st.expander("❓ Frequently Asked Questions"):
    st.write("""
    **Q: Is my photo stored?**
    A: No, only analyzed by Google's API.
    
    **Q: How accurate is this?**
    A: AI provides educated recommendations. Consult dermatologist for medical concerns.
    
    **Q: Can I try different photos?**
    A: Yes! Click "New Analysis" to capture again.
    
    **Q: Why is analysis slow?**
    A: First analysis takes 20-30 seconds. Subsequent ones are faster.
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p><b>AI Face Scanner & Beauty Consultant v2.0</b></p>
    <p>Powered by Google Gemini | Created with Streamlit</p>
</div>
""", unsafe_allow_html=True)
