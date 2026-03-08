import streamlit as st
import anthropic
import os

# Page configuration
st.set_page_config(
    page_title="Funny Birthday Card Generator",
    page_icon="🎂",
    layout="centered"
)

# Custom CSS for the birthday card
st.markdown("""
<style>
.birthday-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 40px;
    margin: 20px 0;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    text-align: center;
    color: white;
}
.card-title {
    font-size: 2.5em;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
.card-message {
    font-size: 1.3em;
    line-height: 1.6;
    margin: 20px 0;
}
.card-joke {
    font-size: 1.1em;
    font-style: italic;
    background: rgba(255,255,255,0.2);
    padding: 15px;
    border-radius: 10px;
    margin: 20px 0;
}
.card-footer {
    font-size: 1.5em;
    margin-top: 30px;
}
.confetti {
    font-size: 2em;
    letter-spacing: 10px;
}
</style>
""", unsafe_allow_html=True)

# App title
st.title("🎈 Funny Birthday Card Generator 🎈")
st.markdown("*Create hilarious AI-powered personalized birthday cards!*")
st.divider()

# Get API key from: 1) Streamlit secrets (cloud), 2) Environment variable, 3) Sidebar input
def get_api_key_from_secrets():
    """Try to get API key from Streamlit secrets (for cloud deployment)."""
    try:
        return st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        return ""

secrets_api_key = get_api_key_from_secrets()
env_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

with st.sidebar:
    st.header("Settings")
    if secrets_api_key:
        st.success("API key loaded from Streamlit secrets")
        api_key = secrets_api_key
    elif env_api_key:
        st.success("API key loaded from environment variable")
        api_key = env_api_key
    else:
        api_key = st.text_input("Anthropic API Key", type="password", help="Enter your Anthropic API key to generate cards")
        st.markdown("[Get an API key](https://console.anthropic.com/)")
    st.divider()
    st.markdown("**Powered by Claude AI**")

# Input form
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Person's Name", placeholder="Enter the birthday person's name")

with col2:
    age = st.number_input("Age", min_value=1, max_value=150, value=25)

hobby = st.text_input("Their Favorite Hobby", placeholder="e.g., gaming, cooking, sleeping...")


def generate_birthday_card(name: str, age: int, hobby: str, api_key: str) -> dict:
    """Use Claude to generate a funny birthday card."""

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Generate a funny and humorous birthday card for someone with these details:
- Name: {name}
- Age: {age}
- Favorite Hobby: {hobby}

Please provide exactly 3 parts in your response, separated by "---":

1. AGE JOKE: A funny joke about their age (be playful but not mean)
2. HOBBY JOKE: A humorous observation about their hobby
3. BIRTHDAY WISH: A funny but heartfelt birthday wish

Make it genuinely funny, witty, and personalized. Use wordplay, puns, or clever observations. Keep each part to 1-2 sentences.

Format your response exactly like this:
AGE_JOKE: [your age joke here]
---
HOBBY_JOKE: [your hobby joke here]
---
BIRTHDAY_WISH: [your birthday wish here]"""

    message = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text
    parts = response_text.split("---")

    result = {
        "age_joke": "",
        "hobby_joke": "",
        "birthday_wish": ""
    }

    for part in parts:
        part = part.strip()
        if part.startswith("AGE_JOKE:"):
            result["age_joke"] = part.replace("AGE_JOKE:", "").strip()
        elif part.startswith("HOBBY_JOKE:"):
            result["hobby_joke"] = part.replace("HOBBY_JOKE:", "").strip()
        elif part.startswith("BIRTHDAY_WISH:"):
            result["birthday_wish"] = part.replace("BIRTHDAY_WISH:", "").strip()

    return result


# Generate button
if st.button("🎂 Generate Birthday Card 🎂", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar to generate cards.")
    elif not name:
        st.warning("Please enter the person's name.")
    elif not hobby:
        st.warning("Please enter their hobby.")
    else:
        with st.spinner("✨ Claude is crafting your hilarious birthday card..."):
            try:
                card_content = generate_birthday_card(name, age, hobby, api_key)

                # Display the card
                st.markdown(f"""
                <div class="birthday-card">
                    <div class="confetti">🎉🎊🎈🎁🎂</div>
                    <div class="card-title">Happy {age}th Birthday, {name}!</div>
                    <div class="card-message">{card_content['age_joke']}</div>
                    <div class="card-joke">🎯 Hobby Alert: {card_content['hobby_joke']}</div>
                    <div class="card-message">{card_content['birthday_wish']}</div>
                    <div class="card-footer">🥳 Party On! 🥳</div>
                    <div class="confetti">🎂🎁🎈🎊🎉</div>
                </div>
                """, unsafe_allow_html=True)

                # Add balloons animation
                st.balloons()

                # Regenerate tip
                st.info("💡 Click the button again for a completely new AI-generated card!")

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key and try again.")
            except anthropic.RateLimitError:
                st.error("Rate limit exceeded. Please wait a moment and try again.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.divider()
st.markdown("*Made with ❤️ and Claude AI*")
