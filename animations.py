import streamlit as st
import time

# ============= ANIMATION STYLES =============
ANIMATIONS_CSS = """
<style>
/* ===== PAGE FADE-IN ===== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInDown {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ===== SPINNER/LOADER ===== */
@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

@keyframes shimmer {
    0% {
        background-position: -1000px 0;
    }
    100% {
        background-position: 1000px 0;
    }
}

/* ===== CARD ANIMATIONS ===== */
@keyframes cardHover {
    from {
        transform: translateY(0);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    to {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(168, 213, 186, 0.2);
    }
}

@keyframes glow {
    0%, 100% {
        box-shadow: 0 4px 12px rgba(168, 213, 186, 0.1);
    }
    50% {
        box-shadow: 0 4px 20px rgba(168, 213, 186, 0.3);
    }
}

/* ===== BUTTON ANIMATIONS ===== */
@keyframes buttonClick {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(0.95);
    }
    100% {
        transform: scale(1);
    }
}

@keyframes buttonGlow {
    0%, 100% {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.18);
    }
    50% {
        box-shadow: 0 4px 12px rgba(168, 213, 186, 0.3);
    }
}

/* ===== APPLY ANIMATIONS TO ELEMENTS ===== */

/* Page container fade in */
[data-testid="stAppViewContainer"] {
    animation: fadeIn 0.6s ease-out;
}

/* Headers fade in down */
h1, h2 {
    animation: fadeInDown 0.7s ease-out !important;
}

h3, h4, h5, h6 {
    animation: fadeInUp 0.6s ease-out !important;
}

/* Text paragraphs fade in */
p {
    animation: fadeIn 0.8s ease-out !important;
}

/* Logo animation */
.logo img {
    animation: fadeInDown 0.8s ease-out, pulse 3s ease-in-out 1.5s infinite !important;
}

/* Form inputs */
[data-testid="stTextInput"], 
[data-testid="stTextArea"],
[data-testid="stPasswordInput"],
[data-testid="stSelectbox"],
[data-testid="stNumberInput"],
[data-testid="stMultiSelect"] {
    animation: fadeInUp 0.6s ease-out !important;
}

input, textarea, select {
    transition: all 0.3s ease !important;
    border: 1px solid rgba(168, 213, 186, 0.3) !important;
}

input:focus, textarea:focus, select:focus {
    border-color: #A8D5BA !important;
    box-shadow: 0 0 10px rgba(168, 213, 186, 0.2) !important;
}

/* Button enhancements */
button, .stButton > button, form button, .stButton > button[role="button"] {
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.6s ease-out !important;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
}

button:active, .stButton > button:active {
    animation: buttonClick 0.3s ease !important;
}

button:hover, .stButton > button:hover {
    animation: buttonGlow 2s ease-in-out infinite !important;
}

/* Expander animations */
[data-testid="stExpander"] {
    animation: fadeIn 0.5s ease-out !important;
}

/* Card/container animations */
.css-1r6slq1, .css-qbe2hs, [data-testid="stContainer"] {
    animation: fadeIn 0.6s ease-out !important;
}

/* Column animations */
.css-18ni7ap {
    animation: fadeInUp 0.6s ease-out !important;
}

/* Alert/message animations */
[data-testid="stAlert"] {
    animation: slideInLeft 0.5s ease-out !important;
}

/* Tab animations */
[data-testid="stTab"] {
    animation: fadeIn 0.4s ease-out !important;
}

/* Frame/metric cards */
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"] {
    animation: fadeInUp 0.5s ease-out !important;
}

/* Image animations */
img {
    animation: fadeIn 0.7s ease-out !important;
}

/* Smooth page transitions */
.page-transition {
    animation: fadeIn 0.4s ease-in-out;
}

/* Loading spinner overlay */
.spinner-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
}

.spinner-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #A8D5BA;
    animation: pulse 1.4s infinite;
}

.spinner-dot:nth-child(2) {
    animation-delay: 0.2s;
}

.spinner-dot:nth-child(3) {
    animation-delay: 0.4s;
}

/* Custom spinner */
.custom-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(168, 213, 186, 0.2);
    border-top-color: #A8D5BA;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

/* Success pulse */
@keyframes successPulse {
    0% {
        transform: scale(1);
    }
    50% {
        transform: scale(1.05);
    }
    100% {
        transform: scale(1);
    }
}

.success-animation {
    animation: successPulse 0.6s ease-out;
}

/* Smooth transitions for all input elements */
input::placeholder {
    transition: color 0.3s ease;
}

input:focus::placeholder {
    color: transparent;
}

</style>
"""

def inject_animations():
    """Inject animation CSS into the app"""
    st.markdown(ANIMATIONS_CSS, unsafe_allow_html=True)


def show_loading_spinner(message: str = "Processing...", duration: float = 3):
    """
    Show an animated loading spinner with message
    
    Args:
        message: Loading message to display
        duration: How long to show the spinner (in seconds)
    """
    placeholder = st.empty()
    
    spinner_html = f"""
    <div style='text-align: center; padding: 20px;'>
        <div class='spinner-dot' style='display: inline-block; margin: 0 2px;'></div>
        <div class='spinner-dot' style='display: inline-block; margin: 0 2px;'></div>
        <div class='spinner-dot' style='display: inline-block; margin: 0 2px;'></div>
        <p style='margin-top: 15px; color: #A8D5BA;'>{message}</p>
    </div>
    """
    
    placeholder.markdown(spinner_html, unsafe_allow_html=True)
    time.sleep(duration)
    placeholder.empty()


def show_success_animation(message: str = "Success!"):
    """Show an animated success message"""
    st.success(f"✅ {message}")


def show_loading_start(message: str = "Processing..."):
    """Show loading spinner (non-blocking)"""
    return st.spinner(message)


def fade_in_content(content_func, duration: float = 0.6):
    """
    Wrap content with fade-in animation
    
    Args:
        content_func: Function that renders the content
        duration: Animation duration
    """
    st.markdown("""
    <style>
    .fade-in-content {
        animation: fadeIn """ + str(duration) + """s ease-out;
    }
    </style>
    <div class='fade-in-content'>
    """, unsafe_allow_html=True)
    
    content_func()
    
    st.markdown("</div>", unsafe_allow_html=True)
