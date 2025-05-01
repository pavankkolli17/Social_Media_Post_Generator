import streamlit as st
import pandas as pd
import datetime
import random
import io
import base64
import os
import anthropic

# Set page configuration FIRST before any other Streamlit commands
st.set_page_config(
    page_title="Social Media Post Generator",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("Social Media Post Generator")
st.markdown("Generate engaging social media posts inspired by your topic phrase!")

# Initialize session state variables if they don't exist
if 'posts' not in st.session_state:
    st.session_state.posts = []

if 'post_history' not in st.session_state:
    st.session_state.post_history = pd.DataFrame(
        columns=["Platform", "Topic Phrase", "Post Content", "Timestamp"]
    )

# Function to generate social media posts using Anthropic's Claude API
def generate_social_media_post(platform, topic_phrase, use_api=True):
    try:
        if not use_api:
            raise Exception("Template generation selected")
            
        # Initialize Anthropic client with API key from environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise Exception("API key not found")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Character limits by platform
        char_limits = {
            "Twitter/X": 280,
            "Instagram": 2200,
            "LinkedIn": 3000,
            "Facebook": 5000,
            "TikTok": 2200
        }
        
        # Use default if platform not in list
        char_limit = char_limits.get(platform, 1000)
        
        # Select random content types and tones for variety
        content_types = ["promotional", "educational", "question", "announcement", "tips", "inspirational"]
        tones = ["professional", "casual", "enthusiastic", "informative", "humorous"]
        
        selected_content = random.choice(content_types)
        selected_tone = random.choice(tones)
        
        # Construct the prompt
        prompt = f"""Create a compelling social media post for {platform} inspired by this topic phrase: "{topic_phrase}".

        The post should be in a {selected_tone} tone and work as a {selected_content} type of content.
        
        Include appropriate hashtags and emojis where they enhance the message.
        Keep the post under {char_limit} characters and make it engaging for the platform.
        
        Format the response as just the post itself without any explanations or introductions.
        """
        
        # Call Claude API
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Using the fastest model for quick response
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Get the generated post
        post = response.content[0].text.strip()
        
        return post
        
    except Exception as e:
        st.warning(f"Using template-based generation: {str(e)}")
        # Fall back to template-based generation
        return generate_template_post(platform, topic_phrase)


# Fallback function that uses templates instead of API
def generate_template_post(platform, topic_phrase):
    # Templates for different platforms
    templates = {
        "Instagram": [
            "✨ {topic_phrase} ✨\n\nHas anyone else been thinking about this lately? I'd love to hear your thoughts!\n\n#inspiration #thoughts #community #shareyourideas",
            "Today's reflection: {topic_phrase}\n\nTaking a moment to appreciate the little things that make a big difference. Double tap if you agree!\n\n#mindfulness #dailyinspo #reflection",
            "NEW POST ALERT 🚨\n\n{topic_phrase}\n\nSaving this for later? Hit that bookmark button!\n\n#trending #mustread #followforfollowback"
        ],
        "Twitter/X": [
            "{topic_phrase}\n\nThoughts? 👇 #JustSaying",
            "Just pondering: {topic_phrase}\n\nAnyone else feel this way? RT if you agree!",
            "Hot take: {topic_phrase} is more important than people realize. #ChangeMyMind"
        ],
        "LinkedIn": [
            "I've been reflecting on this lately:\n\n{topic_phrase}\n\nHow has your experience with this shaped your professional journey? I'd love to hear your insights.\n\n#ProfessionalDevelopment #CareerInsights #Leadership",
            "📊 Industry Insight 📊\n\n{topic_phrase}\n\nThis concept is transforming how we approach business challenges in 2025. What's your take on this trend?\n\n#BusinessStrategy #Innovation #FutureOfWork",
            "Today I want to start a conversation about:\n\n{topic_phrase}\n\nThis has been instrumental in our recent project success. How are you leveraging this in your organization?\n\n#BestPractices #ProfessionalGrowth"
        ],
        "Facebook": [
            "{topic_phrase}\n\nHas anyone else been thinking about this lately? I'd love to hear your thoughts in the comments below! 💭",
            "Random thought of the day: {topic_phrase}\n\nAnyone relate to this? Let me know! ❤️",
            "Can we talk about {topic_phrase} for a minute?\n\nI feel like this doesn't get enough attention these days. What do you think? 🤔"
        ],
        "TikTok": [
            "POV: When you realize {topic_phrase} 🤯 #fyp #viral #trending",
            "No one:\nAbsolutely no one:\nMe: {topic_phrase} 😂 #relatable #comedy #trending",
            "5 reasons why {topic_phrase} matters ⬆️ Follow for more life hacks! #learnontiktok #didyouknow"
        ]
    }
    
    # Default templates if platform is not in the list
    default_templates = [
        "Thinking about {topic_phrase} today. What are your thoughts?",
        "{topic_phrase} - this has been on my mind lately. Anyone else?",
        "Question of the day: {topic_phrase} - discuss below!"
    ]
    
    # Get platform templates or use default
    platform_templates = templates.get(platform, default_templates)
    
    # Select a random template
    template = random.choice(platform_templates)
    
    # Create the post by filling in the template
    post = template.format(topic_phrase=topic_phrase)
    
    return post

# Main layout with two columns
col1, col2 = st.columns([1, 2])

# Input column
with col1:
    st.header("Create Your Post")
    
    # API Configuration
    st.subheader("API Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", 
                           help="Enter your Anthropic API key. The key will be stored only for this session.")
    
    # Store API key in environment variable
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    use_api = st.checkbox("Use Claude AI for generation", value=True, 
                        help="If checked, will use Claude AI to generate posts. If unchecked or if API fails, will use template-based generation.")
    
    # Platform selection
    st.subheader("1. Select Platform")
    platform = st.selectbox(
        "Social Media Platform",
        ["Instagram", "Twitter/X", "LinkedIn", "Facebook", "TikTok"]
    )
    
    # Topic phrase input with character counter
    st.subheader("2. Enter Topic Phrase")
    topic_phrase = st.text_area("Topic Phrase (up to 10 words)", 
                              height=100, 
                              help="Enter a short phrase or topic to inspire your post (maximum 10 words).")
    
    # Word count display
    word_count = len(topic_phrase.split()) if topic_phrase else 0
    if word_count > 10:
        st.error(f"⚠️ {word_count}/10 words. Please limit your topic to 10 words.")
    else:
        st.success(f"✓ {word_count}/10 words")
    
    # Generate button
    generate_button = st.button("Generate Post", disabled=(word_count > 10))
    
    if generate_button:
        if not topic_phrase:
            st.error("Please enter a topic phrase.")
        elif word_count > 10:
            st.error("Topic phrase must be 10 words or less.")
        elif use_api and not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please enter your Anthropic API key to use Claude for generation.")
        else:
            # Show spinner while generating 
            with st.spinner("Generating your social media post..."):
                # Generate post based on parameters
                post_content = generate_social_media_post(platform, topic_phrase, use_api)
                
                # Add to session state
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_post = {
                    "Platform": platform, 
                    "Topic Phrase": topic_phrase,
                    "Post Content": post_content,
                    "Timestamp": timestamp
                }
                
                st.session_state.posts.append(new_post)
                
                # Update history dataframe
                st.session_state.post_history = pd.concat([
                    st.session_state.post_history, 
                    pd.DataFrame([new_post])
                ], ignore_index=True)
                
                st.success("Post generated successfully!")

# Preview and history column
with col2:
    if st.session_state.posts:
        tabs = st.tabs(["Current Post", "Post History", "Export"])
        
        # Current Post Tab
        with tabs[0]:
            latest_post = st.session_state.posts[-1]
            
            st.subheader(f"{latest_post['Platform']} Post")
            st.caption(f"Topic: {latest_post['Topic Phrase']}")
            
            # Platform-specific styling
            if latest_post['Platform'] == "Instagram":
                st.markdown("---")
                st.markdown("📱 **Instagram Preview**")
                st.markdown(f"**@user** • Follow")
                st.markdown(latest_post['Post Content'])
                st.markdown("❤️ Like   💬 Comment   🔄 Share   🔖 Save")
                st.markdown("---")
            elif latest_post['Platform'] == "Twitter/X":
                st.markdown("---")
                st.markdown("🔄 **X Preview**")
                st.markdown(f"**@user**")
                st.markdown(latest_post['Post Content'])
                st.markdown("💬 Reply   🔁 Repost   ❤️ Like   📊 Views")
                st.markdown("---")
            else:
                # Generic display for other platforms
                st.text_area("Post content", latest_post['Post Content'], height=200)
            
            # Copy button
            st.button("Copy to clipboard", key="copy_current", help="Copy post content to clipboard")
        
        # Post History Tab
        with tabs[1]:
            if not st.session_state.post_history.empty:
                st.dataframe(
                    st.session_state.post_history[["Platform", "Topic Phrase", "Timestamp"]],
                    use_container_width=True
                )
                
                # Filter and view specific posts
                st.subheader("View Specific Post")
                
                # Get post index to view
                if len(st.session_state.post_history) > 0:
                    post_index = st.number_input(
                        "Select post number", 
                        min_value=1, 
                        max_value=len(st.session_state.post_history),
                        value=len(st.session_state.post_history)
                    )
                    
                    if st.button("View Post"):
                        selected_post = st.session_state.post_history.iloc[post_index-1]
                        st.markdown(f"**Platform:** {selected_post['Platform']}")
                        st.markdown(f"**Topic:** {selected_post['Topic Phrase']}")
                        st.text_area("Post content", selected_post['Post Content'], height=150)
        
        # Export Tab
        with tabs[2]:
            st.subheader("Export Posts")
            
            export_format = st.radio("Export Format", ["CSV", "Excel", "Text"])
            
            if st.button("Generate Export"):
                if export_format == "CSV":
                    csv = st.session_state.post_history.to_csv(index=False)
                    b64 = base64.b64encode(csv.encode()).decode()
                    href = f'<a href="data:file/csv;base64,{b64}" download="social_media_posts.csv">Download CSV File</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                elif export_format == "Excel":
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        st.session_state.post_history.to_excel(writer, index=False, sheet_name='Posts')
                    b64 = base64.b64encode(output.getvalue()).decode()
                    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="social_media_posts.xlsx">Download Excel File</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                elif export_format == "Text":
                    text_content = ""
                    for i, post in enumerate(st.session_state.post_history.itertuples()):
                        text_content += f"--- Post {i+1} ---\n"
                        text_content += f"Platform: {post.Platform}\n"
                        text_content += f"Topic: {post.Topic_Phrase}\n"
                        text_content += f"Date: {post.Timestamp}\n"
                        text_content += f"Content:\n{post.Post_Content}\n\n"
                    
                    b64 = base64.b64encode(text_content.encode()).decode()
                    href = f'<a href="data:text/plain;base64,{b64}" download="social_media_posts.txt">Download Text File</a>'
                    st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("Enter a topic phrase and generate your first post!")

# Add helpful instructions at the bottom
with st.expander("How to use this app"):
    st.markdown("""
    ### Simple 3-Step Process:
    
    1. **Enter your Anthropic API key** (optional):
       - This allows the app to use Claude AI for high-quality, creative post generation
       - The key is stored only for your current session
       - If you don't have an API key, you can uncheck "Use Claude AI" to use template-based generation
    
    2. **Create your post**:
       - Select your social media platform
       - Enter a topic phrase (up to 10 words) that will inspire your post
       - Click "Generate Post"
    
    3. **Use your posts**:
       - View and copy your generated post
       - Check your post history
       - Export posts in various formats
    
    ### Tips for good topic phrases:
    - Be specific rather than general
    - Include key concepts or emotions you want highlighted
    - Think about what would interest your audience
    - Examples: "sustainable fashion trends for summer 2025" or "remote work productivity hacks that actually work"
    """)
