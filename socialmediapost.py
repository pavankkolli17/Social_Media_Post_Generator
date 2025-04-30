import streamlit as st
import json
import base64
from datetime import datetime

# Embedded API key - already configured in the app
API_KEY = "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"

# Check anthropic library version
import pkg_resources
try:
    anthropic_version = pkg_resources.get_distribution("anthropic").version
    st.sidebar.markdown(f"Using Anthropic SDK version: {anthropic_version}")
except:
    st.sidebar.markdown("Could not determine Anthropic SDK version")

# First try importing the specific client we need
try:
    from anthropic import Anthropic
    # For newer versions (0.6.0+)
    def get_client():
        return Anthropic(api_key=API_KEY)
    st.sidebar.markdown("Using new Anthropic client")
except ImportError:
    try:
        # For older versions
        from anthropic import Client
        def get_client():
            return Client(api_key=API_KEY)
        st.sidebar.markdown("Using legacy Anthropic client")
    except ImportError:
        st.error("Could not import Anthropic client. Please check your installation.")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .css-1v0mbdj.e115fcil1 {
        border-radius: 10px;
        padding: 1rem;
    }
    .generated-post {
        background-color: #f6f6f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 5px solid #4CAF50;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .event-textarea {
        min-height: 100px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("📱 Social Media Post Generator")
st.markdown("Generate perfect social media posts with AI assistance!")

# Sidebar with instructions
with st.sidebar:
    st.header("How to use")
    st.markdown("1. Select a social media platform")
    st.markdown("2. Enter event details (what, when, where, etc.)")
    st.markdown("3. Generate your post")
    st.markdown("4. Download the result or copy to clipboard")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app uses Anthropic's Claude AI to create platform-specific social media posts based on your input.")
    st.markdown("API key is pre-configured for your convenience.")

# Function to create a downloadable link
def get_download_link(text, filename, link_text):
    b64 = base64.b64encode(text.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

# Platform selection
platform_options = [
    "Select a platform", "Instagram", "Twitter", "LinkedIn", 
    "Facebook", "TikTok", "Pinterest", "Reddit"
]
platform = st.selectbox("Select Social Media Platform:", platform_options)

# Event details input - now with text area for more detailed information
st.subheader("Event Details")
event_details = st.text_area(
    "Describe your event (what, when, where, who, etc.):",
    placeholder="Example: Annual tech conference happening next weekend at the Convention Center featuring industry experts and networking opportunities",
    help="Provide as much detail as possible about your event for a better generated post",
    height=120
)

# Platform-specific guidance
platform_info = {
    "Instagram": {
        "style": "Visual-focused with short to medium captions, heavy use of emojis and hashtags",
        "length": "Up to 2200 characters, ideally 150-300 for captions",
        "best_for": "Visual storytelling, lifestyle content, product showcases"
    },
    "Twitter": {
        "style": "Concise and snappy content, conversational tone",
        "length": "280 characters maximum",
        "best_for": "Real-time updates, trending topics, quick announcements"
    },
    "LinkedIn": {
        "style": "Professional tone, industry insights, minimal emojis",
        "length": "Up to 3000 characters, ideally 1200-1500 for optimal engagement",
        "best_for": "Professional updates, industry news, career milestones"
    },
    "Facebook": {
        "style": "Conversational and engaging, mix of formal and casual",
        "length": "Up to 63,206 characters, ideally 40-80 characters for best engagement",
        "best_for": "Community building, events, longer stories"
    },
    "TikTok": {
        "style": "Ultra-casual, trendy language, hashtag focused",
        "length": "Up to 2200 characters, but should be brief and catchy",
        "best_for": "Trendy, entertaining content that supports video"
    },
    "Pinterest": {
        "style": "Inspirational, descriptive but concise",
        "length": "Up to 500 characters, focus on keywords",
        "best_for": "DIY, recipes, fashion, home decor, inspiration"
    },
    "Reddit": {
        "style": "Authentic, community-focused, can be more detailed",
        "length": "Up to 40,000 characters, but should be appropriate for the subreddit",
        "best_for": "Discussion starters, niche community engagement"
    }
}

# Display platform info if selected
if platform != "Select a platform" and platform in platform_info:
    with st.expander(f"{platform} Post Guidelines"):
        info = platform_info[platform]
        st.markdown(f"**Style:** {info['style']}")
        st.markdown(f"**Optimal Length:** {info['length']}")
        st.markdown(f"**Best For:** {info['best_for']}")

# Additional options in expander
with st.expander("Additional Options (Optional)"):
    target_audience = st.text_input("Target Audience:", 
                                    placeholder="Example: Young professionals, parents, tech enthusiasts")
    post_tone = st.select_slider("Post Tone:", 
                                options=["Very Casual", "Casual", "Neutral", "Professional", "Very Professional"],
                                value="Neutral")
    include_cta = st.checkbox("Include Call-to-Action", value=True)

# Generate button
generate_clicked = st.button("Generate Post", type="primary", disabled=(platform == "Select a platform" or not event_details))

# Initialize session state for storing generated content
if 'generated_post' not in st.session_state:
    st.session_state.generated_post = None
if 'hashtags' not in st.session_state:
    st.session_state.hashtags = None

# Generate post when button is clicked
if generate_clicked:
    if platform == "Select a platform":
        st.error("Please select a social media platform")
    elif not event_details:
        st.error("Please enter event details")
    else:
        with st.spinner("Generating your perfect post..."):
            try:
                # Get client based on available API
                client = get_client()
                
                # Prepare additional options for the prompt
                additional_instructions = []
                if target_audience:
                    additional_instructions.append(f"Target audience: {target_audience}")
                if post_tone != "Neutral":
                    additional_instructions.append(f"Tone should be {post_tone.lower()}")
                if include_cta:
                    additional_instructions.append("Include a compelling call-to-action")
                
                additional_prompt = "\n".join(additional_instructions)
                
                # Prepare the prompt
                prompt = f"""
                Create an engaging social media post for {platform} about the following event:
                
                EVENT DETAILS:
                {event_details}
                
                The post should follow the platform's best practices:
                - Style: {platform_info[platform]['style']}
                - Length: {platform_info[platform]['length']}
                - Best Use: {platform_info[platform]['best_for']}
                
                {additional_prompt}
                
                Format your response as JSON with the following structure:
                {{
                    "post_text": "The main text of the post",
                    "hashtags": "Relevant hashtags separated by spaces"
                }}
                
                Make the post compelling, authentic, and optimized for engagement on {platform}.
                """
                
                # Generate content based on available API
                is_newer_api = hasattr(client, 'messages')
                
                if is_newer_api:
                    # For newer Anthropic SDK
                    response = client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=1000,
                        temperature=0.7,
                        system="You are an expert social media copywriter who creates engaging platform-specific content.",
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    content = response.content[0].text
                else:
                    # For older Anthropic SDK
                    response = client.completion(
                        prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                        model="claude-3-opus-20240229",
                        max_tokens_to_sample=1000,
                        temperature=0.7,
                    )
                    content = response.completion
                
                # Extract and parse the JSON response
                try:
                    # Extract JSON block if needed
                    if "```json" in content:
                        json_content = content.split("```json")[1].split("```")[0].strip()
                    elif "```" in content:
                        json_content = content.split("```")[1].strip()
                    else:
                        json_content = content.strip()
                        
                    result = json.loads(json_content)
                    
                    # Store in session state
                    st.session_state.generated_post = result.get("post_text", "")
                    st.session_state.hashtags = result.get("hashtags", "")
                    
                except Exception as e:
                    st.error(f"Error parsing response: {str(e)}")
                    st.code(content)  # Show raw response for debugging
            
            except Exception as e:
                st.error(f"Error generating content: {str(e)}")
                import traceback
                st.code(traceback.format_exc())  # Show detailed error for debugging

# Display generated content
if st.session_state.generated_post:
    st.subheader("Your Generated Post:")
    
    with st.container():
        st.markdown(f'<div class="generated-post">{st.session_state.generated_post}</div>', unsafe_allow_html=True)
        
        if st.session_state.hashtags:
            st.markdown("**Suggested Hashtags:**")
            st.markdown(f"`{st.session_state.hashtags}`")
    
    # Combine post and hashtags for download
    full_post = f"{st.session_state.generated_post}\n\n{st.session_state.hashtags}"
    
    # Create a filename based on platform and first few words of event details
    event_summary = "_".join(event_details.split()[:3]).lower()
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{platform.lower()}_{event_summary}_{current_time}.txt"
    
    # Create two columns for the buttons
    col1, col2 = st.columns(2)
    
    with col1:
        # Download button
        st.markdown(get_download_link(full_post, filename, "📥 Download Post"), unsafe_allow_html=True)
    
    with col2:
        # Copy button (using JavaScript)
        st.markdown("""
            <div style="display: flex; justify-content: center;">
                <button 
                    onclick="
                        navigator.clipboard.writeText(document.querySelector('.generated-post').innerText + '\\n\\n' + document.querySelector('code').innerText);
                        this.innerHTML = '✓ Copied!';
                        setTimeout(() => this.innerHTML = '📋 Copy to Clipboard', 2000);
                    "
                    style="
                        background-color: #4CAF50;
                        border: none;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 5px;
                    "
                >
                    📋 Copy to Clipboard
                </button>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Anthropic Claude")
