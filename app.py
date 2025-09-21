# homepage.py
import streamlit as st
import sqlite3
import hashlib
import time
from datetime import datetime
import secrets
import subprocess
import sys
import os

# Page configuration
st.set_page_config(
    page_title="Movie-Thruster - AI-Powered Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional color scheme constants
COLORS = {
    'primary': '#1f2937',      # Dark gray-blue
    'secondary': '#3b82f6',    # Professional blue  
    'accent': '#10b981',       # Emerald green
    'success': '#059669',      # Dark emerald
    'warning': '#f59e0b',      # Amber
    'error': '#ef4444',        # Red
    'text': '#374151',         # Gray
    'light': '#f9fafb',        # Light gray
    'white': '#ffffff'
}

# Enhanced database functions with better security
def init_user_db():
    """Initialize user database with enhanced schema"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password TEXT NOT NULL,
                created_date TEXT DEFAULT (datetime('now')),
                last_login TEXT,
                preferences TEXT DEFAULT '{}',
                is_active BOOLEAN DEFAULT 1,
                profile_data TEXT DEFAULT '{}')''')
    conn.commit()
    conn.close()

def hash_password(password):
    """Enhanced password hashing with salt"""
    salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt

def verify_password(password, hashed_password):
    """Verify password against hash"""
    try:
        password_hash, salt = hashed_password.split(':')
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == password_hash
    except:
        # Fallback for old simple hash method
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password

def register_user(username, email, password):
    """Enhanced user registration with validation"""
    # Input validation
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not email or '@' not in email or '.' not in email:
        return False, "Please enter a valid email address"
        
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        hashed_pw = hash_password(password)
        c.execute("INSERT INTO users (username, email, password, preferences, profile_data) VALUES (?, ?, ?, ?, ?)",
                 (username, email, hashed_pw, '{}', '{}'))
        conn.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if 'username' in str(e):
            return False, "Username already exists"
        elif 'email' in str(e):
            return False, "Email already registered"
        else:
            return False, "Registration failed"
    finally:
        conn.close()

def authenticate_user(username, password):
    """Enhanced user authentication"""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, password, email FROM users WHERE username = ? AND is_active = 1", (username,))
    result = c.fetchone()
    
    if result:
        user_id, stored_password, email = result
        if verify_password(password, stored_password):
            # Update last login
            c.execute("UPDATE users SET last_login = datetime('now') WHERE id = ?", (user_id,))
            conn.commit()
            conn.close()
            return True, {"id": user_id, "username": username, "email": email}
    
    conn.close()
    return False, None

def is_logged_in():
    """Check if user is logged in"""
    return ('logged_in' in st.session_state and 
            st.session_state.logged_in and 
            'user_data' in st.session_state)

def redirect_to_main_app():
    """Redirect to main application (app.py)"""
    user_data = st.session_state.get('user_data', {})
    username = user_data.get('username', 'User')
    
    # Show welcome message with loading animation
    st.markdown(f"""
    <div style='text-align: center; padding: 4rem 2rem;'>
        <div style='background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 3rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);'>
            <h1 style='margin: 0 0 1rem 0; font-size: 2.5rem;'>🎉 Welcome back, {username}!</h1>
            <p style='margin: 0; font-size: 1.2rem; opacity: 0.9;'>Preparing your personalized movie experience...</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Loading progress with status
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    loading_steps = [
        "🎬 Loading movie database...",
        "🤖 Initializing AI recommendations...", 
        "📊 Preparing your dashboard...",
        "🚀 Launching Movie-Thruster..."
    ]
    
    for i, step in enumerate(loading_steps):
        status_text.markdown(f"<div style='text-align: center; font-size: 1.1rem; color: #374151;'>{step}</div>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) * 25)
        time.sleep(0.8)
    
    # Final success message
    status_text.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <div style='background: #10b981; color: white; padding: 1rem 2rem; border-radius: 10px; display: inline-block;'>
            ✅ Ready to discover amazing movies!
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(1)
    
    # Method 1: Using st.switch_page (Recommended for Streamlit 1.31+)
    try:
        if os.path.exists("pages/homepage.py"):
            st.switch_page("pages/homepage.py")
        else:
            st.error("Main application (homepage.py) not found!")
            show_fallback_options()
    except AttributeError:
        # Fallback for older Streamlit versions
        st.info("🔄 Redirecting to main application...")
        st.markdown("""
        <script>
        window.location.href = window.location.origin + '/homepage.py';
        </script>
        """, unsafe_allow_html=True)
        show_manual_redirect()

def show_manual_redirect():
    """Show manual redirect options if automatic redirect fails"""
    st.markdown("---")
    st.markdown("### 🎯 Manual Navigation")
    st.info("If automatic redirect doesn't work, please use one of the options below:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Launch App", use_container_width=True, type="primary"):
            st.markdown("""
            <script>
            window.open('app.py', '_blank');
            </script>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Reload Page", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()

def show_fallback_options():
    """Show fallback options when main app is not accessible"""
    st.warning("⚠️ Main application not found. Please check the following:")
    
    st.markdown("""
    **Possible solutions:**
    1. Make sure `app.py` is in the same directory as `homepage.py`
    2. Run the app using: `streamlit run app.py` instead
    3. Check if all required component files are present
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Try Again", use_container_width=True, type="primary"):
            st.rerun()
    
    with col2:
        if st.button("🚪 Logout & Return", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.success("Logged out successfully!")
            time.sleep(1)
            st.rerun()

def show_hero_section():
    """Professional hero section using native Streamlit components"""
    # Create hero container with proper spacing
    st.markdown("---")
    
    # Main hero content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; margin-bottom: 1rem; color: #FF4D00;'>🎬 Movie-Thruster</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3 style='color: #6b7280; font-weight: 400; line-height: 1.6;'>
                Discover Your Next Favorite Movie with AI-Powered Recommendations
            </h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Hero stats in columns
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.metric(
            label="Happy Users",
            value="50K+",
            delta="Growing Daily"
        )
    
    with stat_col2:
        st.metric(
            label="Movies Recommended", 
            value="500K+",
            delta="AI Powered"
        )
        
    with stat_col3:
        st.metric(
            label="Satisfaction Rate",
            value="99.2%",
            delta="Verified Reviews"
        )
        
    with stat_col4:
        st.metric(
            label="Countries Served",
            value="150+",
            delta="Global Reach"
        )
    
    st.markdown("---")

def show_features_section():
    """Professional features section"""
    st.markdown("## ✨ Why Choose Movie-Thruster?")
    st.markdown("### Experience the future of movie discovery with our advanced features")
    
    # Features in organized rows
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("#### 🤖 AI-Powered Intelligence")
            st.markdown("""
            Our advanced machine learning algorithms analyze your viewing patterns, 
            preferences, and behavioral data to suggest movies you'll absolutely love. 
            The more you use it, the smarter it gets.
            """)
            
        st.markdown("")  # Spacing
        
        with st.container():
            st.markdown("#### 📊 Deep Movie Insights")
            st.markdown("""
            Access comprehensive movie data including detailed reviews, professional ratings, 
            cast & crew information, box office statistics, and exclusive behind-the-scenes content.
            """)
            
        st.markdown("")  # Spacing
            
        with st.container():
            st.markdown("#### 🌍 Global Cinema Database")
            st.markdown("""
            Explore movies from around the world with our extensive international database 
            covering Hollywood, Bollywood, European cinema, K-dramas, and independent films.
            """)
    
    with col2:
        with st.container():
            st.markdown("#### 🎭 Mood-Based Discovery")
            st.markdown("""
            Find the perfect movie for any emotion or situation. Whether you're seeking adventure, 
            romance, comedy, or need something thought-provoking, our mood engine has you covered.
            """)
            
        st.markdown("")  # Spacing
        
        with st.container():
            st.markdown("#### 🎯 Smart Watchlist Management")
            st.markdown("""
            Curate your perfect movie queue with intelligent recommendations, priority sorting, 
            availability notifications, and seamless integration across all your devices.
            """)
            
        st.markdown("")  # Spacing
            
        with st.container():
            st.markdown("#### 🔒 Privacy-First Approach")
            st.markdown("""
            Your viewing habits and personal data remain completely private and secure. 
            We don't sell your information or share it with third parties. Your data, your choice.
            """)

def show_how_it_works():
    """Professional how it works section"""
    st.markdown("---")
    st.markdown("## 🚀 How Movie-Thruster Works")
    st.markdown("### Get personalized movie recommendations in four simple steps")
    
    # Steps in columns
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='background: linear-gradient(135deg, #3b82f6, #1d4ed8); color: white; 
                        border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 1.5rem; font-weight: bold; margin: 0 auto 1rem;'>1</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Create Your Account**")
        st.markdown("Sign up in under 30 seconds with just your email and preferred username.")
        
    with step2:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='background: linear-gradient(135deg, #10b981, #059669); color: white; 
                        border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 1.5rem; font-weight: bold; margin: 0 auto 1rem;'>2</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Set Your Preferences**")
        st.markdown("Tell us your favorite genres, actors, directors, and current mood preferences.")
        
    with step3:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='background: linear-gradient(135deg, #f59e0b, #d97706); color: white; 
                        border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 1.5rem; font-weight: bold; margin: 0 auto 1rem;'>3</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Get AI Recommendations**")
        st.markdown("Receive personalized movie suggestions tailored specifically to your taste.")
        
    with step4:
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <div style='background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: white; 
                        border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; 
                        font-size: 1.5rem; font-weight: bold; margin: 0 auto 1rem;'>4</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("**Watch & Enjoy**")
        st.markdown("Discover amazing movies and share your favorites with friends and family.")

def show_testimonials():
    """Professional testimonials section"""
    st.markdown("---")
    st.markdown("## 💬 What Our Users Say")
    st.markdown("### Real experiences from movie enthusiasts worldwide")
    
    # Testimonials in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("⭐⭐⭐⭐⭐")
            st.markdown("""
            > "Movie-Thruster completely transformed how I discover movies. 
            > The AI recommendations are incredibly accurate and I've found 
            > so many hidden gems I never would have discovered otherwise!"
            """)
            st.markdown("**— Sarah Chen, Film Enthusiast**")
            
    with col2:
        with st.container():
            st.markdown("⭐⭐⭐⭐⭐")
            st.markdown("""
            > "The mood-based recommendations are absolutely perfect! 
            > Whether I want something uplifting after a tough day or 
            > need a good thriller for the weekend, it always knows exactly what I need."
            """)
            st.markdown("**— Marcus Johnson, Teacher**")
            
    with col3:
        with st.container():
            st.markdown("⭐⭐⭐⭐⭐")
            st.markdown("""
            > "As a film student, I love the deep insights and international 
            > cinema recommendations. It's expanded my cinematic horizons 
            > tremendously and helped with my research projects."
            """)
            st.markdown("**— Elena Rodriguez, Film Student**")

def show_login_form():
    """Professional login form"""
    st.markdown("### 🔐 Welcome Back")
    st.markdown("Sign in to access your personalized movie recommendations")
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter your username",
            help="The username you used when creating your account"
        )
        
        password = st.text_input(
            "Password", 
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            login_button = st.form_submit_button(
                "🚀 Sign In", 
                use_container_width=True,
                type="primary"
            )
        with col2:
            remember_me = st.checkbox("Remember me")
        
        if login_button:
            if not username or not password:
                st.error("⚠️ Please fill in all fields")
            else:
                with st.spinner("Authenticating..."):
                    success, user_data = authenticate_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user_data
                        st.success("🎉 Login successful! Redirecting to Movie-Thruster...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please check your username and password.")

def show_registration_form():
    """Professional registration form"""
    st.markdown("### 🌟 Create Your Account")
    st.markdown("Join thousands of movie enthusiasts and start discovering amazing films")
    
    with st.form("registration_form", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            help="3+ characters, letters and numbers only"
        )
        
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="We'll use this for account recovery and important updates"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Create a strong password",
            help="Minimum 8 characters with letters and numbers"
        )
        
        confirm_password = st.text_input(
            "Confirm Password",
            type="password", 
            placeholder="Repeat your password",
            help="Must match the password above"
        )
        
        # Terms and conditions
        terms_accepted = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            help="You must accept our terms to create an account"
        )
        
        # Newsletter subscription
        newsletter = st.checkbox(
            "Subscribe to our newsletter for movie recommendations and updates",
            value=True
        )
        
        register_button = st.form_submit_button(
            "✨ Create Account", 
            use_container_width=True,
            type="primary"
        )
        
        if register_button:
            if not all([username, email, password, confirm_password]):
                st.error("⚠️ Please fill in all required fields")
            elif password != confirm_password:
                st.error("❌ Passwords don't match")
            elif not terms_accepted:
                st.error("❌ Please accept the Terms of Service to continue")
            else:
                with st.spinner("Creating your account..."):
                    success, message = register_user(username, email, password)
                    if success:
                        st.success(f"✅ {message}")
                        st.info("You can now sign in with your credentials!")
                        st.balloons()  # Celebration effect
                    else:
                        st.error(f"❌ {message}")

def main():
    """Enhanced main function with proper redirection"""
    # Initialize database
    init_user_db()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    # Check if user is logged in
    if is_logged_in():
        # Redirect to main app (app.py)
        redirect_to_main_app()
    else:
        # Show homepage
        show_hero_section()
        show_features_section()
        show_how_it_works()
        show_testimonials()
        
        # Authentication section
        st.markdown("---")
        st.markdown("## 🎯 Get Started Today")
        st.markdown("### Join thousands of movie enthusiasts and transform your viewing experience")
        
        # Authentication forms in columns
        auth_col1, auth_col2 = st.columns(2, gap="large")
        
        with auth_col1:
            with st.container():
                show_login_form()
        
        with auth_col2:
            with st.container():
                show_registration_form()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #6b7280; padding: 2rem;'>
            <p>© 2025 Movie-Thruster. All rights reserved.</p>
            <p>🎬 Discover • 🤖 AI-Powered • 🔒 Secure • 🌍 Global</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
