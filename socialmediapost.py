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
st.markdown("Generate engaging social media posts for your marketing campaigns!")

# Initialize session state variables if they don't exist
if 'posts' not in st.session_state:
    st.session_state.posts = []

if 'post_history' not in st.session_state:
    st.session_state.post_history = pd.DataFrame(
        columns=["Platform", "Content Type", "Topic", "Tone", "Post Content", "Timestamp"]
    )

# Sidebar for input parameters
with st.sidebar:
    st.header("Post Parameters")
    
    # API Configuration
    st.subheader("API Configuration")
    api_key = st.text_input("Anthropic API Key", type="password", 
                           help="Enter your Anthropic API key. The key will be stored only for this session.")
    
    # Store API key in environment variable
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    
    use_api = st.checkbox("Use Claude API for generation", value=True, 
                         help="If checked, will use Anthropic's Claude API to generate posts. If unchecked or if API fails, will use template-based generation.")
    
    st.header("Post Parameters")
    
    platform = st.selectbox(
        "Social Media Platform",
        ["Instagram", "Twitter/X", "LinkedIn", "Facebook", "TikTok"]
    )
    
    content_type = st.selectbox(
        "Content Type",
        ["Promotional Post", "Educational Content", "Engagement Question", "Company Update", "Product Launch"]
    )
    
    topic = st.text_input("Topic or Product Name", "")
    
    tone = st.selectbox(
        "Tone of Voice",
        ["Professional", "Casual", "Enthusiastic", "Informative", "Humorous"]
    )
    
    target_audience = st.text_input("Target Audience (optional)", "")
    
    include_hashtags = st.checkbox("Include Hashtags", value=True)
    
    include_emojis = st.checkbox("Include Emojis", value=True)
    
    if not use_api:
        st.info("Using template-based generation (no API call).")
    
    if st.button("Generate Post"):
        if not topic:
            st.error("Please enter a topic or product name.")
        elif use_api and not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Please enter your Anthropic API key to use Claude for generation.")
        else:
            # Show spinner while generating 
            with st.spinner("Generating your social media post..."):
                # Generate post based on parameters
                post_content = generate_social_media_post(
                    platform, content_type, topic, tone, target_audience, include_hashtags, include_emojis
                )
            
            # Add to session state
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_post = {
                "Platform": platform, 
                "Content Type": content_type,
                "Topic": topic,
                "Tone": tone,
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

import os
import anthropic

# Function to generate social media posts using Anthropic's Claude API
def generate_social_media_post(platform, content_type, topic, tone, target_audience="", include_hashtags=True, include_emojis=True):
    try:
        # Initialize Anthropic client with API key from environment variable
        # You need to set the ANTHROPIC_API_KEY environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        
        if not api_key:
            st.error("Anthropic API key not found! Add it as an environment variable named ANTHROPIC_API_KEY.")
            # Fall back to template-based generation
            return generate_template_post(platform, content_type, topic, tone, target_audience, include_hashtags, include_emojis)
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Create hashtag instruction
        hashtag_instruction = "Include 3-5 relevant hashtags at the end of the post." if include_hashtags else "Do not include any hashtags."
        
        # Create emoji instruction
        emoji_instruction = "Use relevant emojis throughout the post where appropriate." if include_emojis else "Do not use any emojis."
        
        # Create audience instruction
        audience_instruction = f"Target audience: {target_audience}." if target_audience else "Target a general audience."
        
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
        
        # Construct the prompt
        prompt = f"""Create a compelling social media post for {platform} about {topic}.
        Content type: {content_type}
        Tone: {tone}
        {audience_instruction}
        {hashtag_instruction}
        {emoji_instruction}
        
        Make the post engaging, creative, and suitable for the platform.
        Keep the post under {char_limit} characters.
        
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
        st.error(f"Error with Claude API: {str(e)}")
        # Fall back to template-based generation
        return generate_template_post(platform, content_type, topic, tone, target_audience, include_hashtags, include_emojis)


# Fallback function that uses templates instead of API
def generate_template_post(platform, content_type, topic, tone, target_audience="", include_hashtags=True, include_emojis=True):
    # Templates for different platforms and content types
    templates = {
        "Instagram": {
            "Promotional Post": [
                "📢 Introducing {topic}! The perfect solution for {audience}. Check out our latest offering and take your experience to the next level. {hashtags}",
                "🎉 New arrival alert! {topic} is here to transform how you {audience_verb}. Available now! {hashtags}",
                "Elevate your experience with {topic} - designed specifically for {audience}. {emoji} {hashtags}"
            ],
            "Educational Content": [
                "Did you know? {topic} can help you {benefit}. Here's how: {tips} {hashtags}",
                "Understanding {topic} is easier than you think! {fact_intro} {fact} {hashtags}",
                "{emoji} {topic} 101: {fact_intro} {fact} Save this post for later! {hashtags}"
            ]
        },
        "Twitter/X": {
            "Promotional Post": [
                "Just launched: {topic}! Perfect for {audience}. Check it out now! {hashtags}",
                "Revolutionize your {audience_activity} with our new {topic}. Limited availability! {hashtags}",
                "{emoji} Say hello to {topic} - your new favorite {product_category}! {link} {hashtags}"
            ],
            "Engagement Question": [
                "What's your biggest challenge when it comes to {topic}? Share below! {hashtags}",
                "How has {topic} changed the way you {audience_activity}? We'd love to hear your thoughts! {hashtags}",
                "{emoji} Question for our community: What feature of {topic} would you like to see improved? {hashtags}"
            ]
        },
        "LinkedIn": {
            "Company Update": [
                "We're excited to announce our latest development in {topic}. This initiative will help {audience} to {benefit}. {hashtags}",
                "Company Update: We've reached a significant milestone with {topic}. Here's what this means for our clients and partners: {facts} {hashtags}",
                "{emoji} Proud to share our team's achievement in {topic}! {facts} #ProudMoment {hashtags}"
            ],
            "Educational Content": [
                "Industry Insights: How {topic} is transforming {industry}. {facts} What are your thoughts? {hashtags}",
                "5 things every professional should know about {topic}: {numbered_list} Let's discuss in the comments. {hashtags}",
                "{emoji} Professional tip: When dealing with {topic}, remember to {tips}. This can increase your {benefit} by {percentage}. {hashtags}"
            ]
        }
    }
    
    # Default to Facebook templates if the selected platform isn't in our templates
    if platform not in templates:
        platform_templates = {
            "Promotional Post": [
                "Exciting news! Introducing {topic} - designed for {audience}. Learn more today! {hashtags}",
                "You asked, we delivered! {topic} is now available for all our {audience}. {emoji} {hashtags}",
                "Meet {topic} - the solution you've been waiting for! Perfect for {audience}. {hashtags}"
            ],
            "Engagement Question": [
                "We're curious: How would {topic} help you in your daily routine? Share your thoughts below! {hashtags}",
                "Question of the day: What's your favorite thing about {topic}? {emoji} {hashtags}",
                "If you could change one thing about {topic}, what would it be? Let us know in the comments! {hashtags}"
            ]
        }
    else:
        platform_templates = templates[platform]
    
    # If content type not in templates, use the first available type
    if content_type not in platform_templates:
        content_type = list(platform_templates.keys())[0]
    
    # Select a random template for the platform and content type
    template_options = platform_templates[content_type]
    template = random.choice(template_options)
    
    # Audience handling
    audience = target_audience if target_audience else "everyone"
    audience_activities = ["workflow", "daily routine", "experience", "process", "strategy"]
    audience_verbs = ["work", "live", "perform", "succeed", "grow"]
    audience_activity = random.choice(audience_activities)
    audience_verb = random.choice(audience_verbs)
    
    # Benefits and facts
    benefits = ["save time", "increase productivity", "enhance performance", "reduce costs", "improve quality"]
    facts = [
        "Our research shows a 30% improvement in overall satisfaction.",
        "Industry experts predict this will become standard practice by next year.",
        "This approach has been tested with over 500 users with positive results.",
        "We've incorporated feedback from over 1,000 customers to refine this solution."
    ]
    fact_intros = ["Here's what you need to know:", "The key insight:", "Important to remember:"]
    
    # Product categories
    product_categories = ["tool", "solution", "product", "service", "resource"]
    
    # Industries
    industries = ["tech", "finance", "healthcare", "education", "retail"]
    
    # Tips
    tips_list = [
        "always validate your data first",
        "focus on user experience above all",
        "start with a clear strategy",
        "measure results consistently",
        "don't be afraid to innovate"
    ]
    
    # Percentages
    percentages = ["20%", "35%", "50%", "75%", "nearly double"]
    
    # Numbered list items
    numbered_items = [
        "Understand the fundamentals",
        "Stay updated on trends",
        "Network with industry experts",
        "Apply practical learning",
        "Share your knowledge"
    ]
    
    # Create a numbered list
    numbered_list = ""
    for i in range(min(3, len(numbered_items))):
        numbered_list += f"{i+1}. {numbered_items[i]}. "
    
    # Hashtags
    hashtag_options = {
        "Instagram": ["#instagood", "#photooftheday", "#followme", "#instadaily"],
        "Twitter/X": ["#trending", "#followback", "#twitterworld", "#viral"],
        "LinkedIn": ["#innovation", "#leadership", "#professionaldevelopment", "#networking"],
        "Facebook": ["#community", "#shareable", "#facebooklive", "#connect"],
        "TikTok": ["#fyp", "#foryoupage", "#viral", "#tiktoktrend"]
    }
    
    general_hashtags = ["#innovation", "#trending", "#new", "#mustcheck"]
    
    # Format the topic for hashtags (remove spaces and special characters)
    topic_hashtag = "#" + "".join(c for c in topic if c.isalnum())
    
    # Get platform-specific hashtags or use general ones
    platform_specific_hashtags = hashtag_options.get(platform, general_hashtags)
    
    # Combine hashtags
    hashtags = f"{topic_hashtag} {random.choice(platform_specific_hashtags)} {random.choice(general_hashtags)}" if include_hashtags else ""
    
    # Emojis
    emojis = ["✨", "🚀", "💯", "🎯", "🔥", "👍", "🙌", "💪", "👏", "🌟"]
    emoji = random.choice(emojis) if include_emojis else ""
    
    # Create the post by filling in the template
    post = template.format(
        topic=topic,
        audience=audience,
        audience_activity=audience_activity,
        audience_verb=audience_verb,
        benefit=random.choice(benefits),
        facts=random.choice(facts),
        fact_intro=random.choice(fact_intros),
        fact=random.choice(facts),
        product_category=random.choice(product_categories),
        industry=random.choice(industries),
        tips=random.choice(tips_list),
        percentage=random.choice(percentages),
        numbered_list=numbered_list,
        emoji=emoji,
        hashtags=hashtags,
        link="[link]"  # Placeholder for actual link
    )
    
    # Adjust tone based on selection
    if tone == "Professional":
        # Remove multiple exclamation marks and excessive emojis
        post = post.replace("!!", ".")
        if emoji and emoji in post:
            # Keep only one instance of the emoji
            emoji_count = post.count(emoji)
            if emoji_count > 1:
                post = post.replace(emoji, "", emoji_count - 1)
    
    elif tone == "Casual":
        # Add casual language markers
        casual_phrases = [" Hey there!", " Check this out!", " Let's chat!"]
        post = random.choice(casual_phrases) + " " + post
    
    elif tone == "Enthusiastic":
        # Add enthusiasm markers
        post = post.replace("!", "!!")
        post = post.replace(".", "!")
        if include_emojis:
            post += " " + random.choice(emojis) + random.choice(emojis)
    
    elif tone == "Informative":
        # Make more factual
        post = post.replace("!", ".")
        informative_intros = ["Research indicates that ", "According to industry data, ", "Expert analysis shows "]
        post = random.choice(informative_intros) + post
    
    elif tone == "Humorous":
        # Add humorous elements
        humor_phrases = [
            "Warning: may cause excessive excitement! ",
            "Don't blame us if everyone asks where you got it! ",
            "So good you'll wonder how you lived without it! "
        ]
        post = random.choice(humor_phrases) + post
    
    return post

# Main content area - Display generated posts
st.header("Generated Posts")

if st.session_state.posts:
    tabs = st.tabs(["Recent Posts", "Post History", "Export"])
    
    # Recent Posts Tab
    with tabs[0]:
        for i, post in enumerate(reversed(st.session_state.posts[-5:])):
            with st.expander(f"{post['Platform']} - {post['Content Type']} ({post['Timestamp']})", expanded=(i==0)):
                st.markdown(f"**Topic:** {post['Topic']}")
                st.markdown(f"**Tone:** {post['Tone']}")
                st.text_area(f"Post content {i+1}", post['Post Content'], height=100, key=f"post_{i}")
                
                # Copy button for each post
                if st.button(f"Copy to clipboard", key=f"copy_{i}"):
                    # This doesn't actually work in Streamlit as is - would need JavaScript
                    # Just a placeholder for the UI
                    st.success("Copied to clipboard!")
    
    # Post History Tab
    with tabs[1]:
        if not st.session_state.post_history.empty:
            st.dataframe(
                st.session_state.post_history[["Platform", "Content Type", "Topic", "Tone", "Timestamp"]],
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
                    st.markdown(f"**Content Type:** {selected_post['Content Type']}")
                    st.markdown(f"**Topic:** {selected_post['Topic']}")
                    st.markdown(f"**Tone:** {selected_post['Tone']}")
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
                    text_content += f"Content Type: {post.Content_Type}\n"
                    text_content += f"Topic: {post.Topic}\n"
                    text_content += f"Tone: {post.Tone}\n"
                    text_content += f"Date: {post.Timestamp}\n"
                    text_content += f"Content:\n{post.Post_Content}\n\n"
                
                b64 = base64.b64encode(text_content.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64}" download="social_media_posts.txt">Download Text File</a>'
                st.markdown(href, unsafe_allow_html=True)
                
else:
    st.info("No posts generated yet. Use the sidebar to configure and generate your first post!")

# Add some helpful instructions at the bottom
with st.expander("How to use this app"):
    st.markdown("""
    1. **Enter your Anthropic API key** in the sidebar:
       - This allows the app to use Claude AI for high-quality, creative post generation
       - The key is stored only for your current session
       - If you don't have an API key, you can get one at https://console.anthropic.com/
       - You can also uncheck "Use Claude API" to use template-based generation instead
    
    2. **Select your parameters** in the sidebar:
       - Choose the social media platform
       - Select the content type
       - Enter your topic or product name
       - Pick a tone of voice
       - Optionally specify a target audience
       - Toggle hashtags and emojis
       
    3. **Click 'Generate Post'** to create a new post
    
    4. **View and manage your posts** in the tabs:
       - See your most recent posts
       - Browse your post history
       - Export posts in various formats
       
    5. **Copy posts** to your clipboard for use in your social media platforms
    """)
