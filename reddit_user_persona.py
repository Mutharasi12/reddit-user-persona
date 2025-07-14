import praw
import openai
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Reddit client setup
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="personaScript by u/yourusername"
)

def get_reddit_username(url):
    import re
    match = re.search(r"reddit.com/user/([^/]+)", url)
    return match.group(1) if match else None

def scrape_user_data(username, limit=100):
    user = reddit.redditor(username)
    posts, comments = [], []

    print(f"Fetching data for u/{username}...")

    for submission in tqdm(user.submissions.new(limit=limit)):
        posts.append({
            "title": submission.title,
            "selftext": submission.selftext,
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}"
        })

    for comment in tqdm(user.comments.new(limit=limit)):
        comments.append({
            "body": comment.body,
            "permalink": f"https://reddit.com{comment.permalink}"
        })

    return posts, comments

def build_prompt(posts, comments):
    content = "Below are posts and comments by a Reddit user:\n\n"
    for p in posts:
        content += f"Post: {p['title']}\n{p['selftext']}\n(Source: {p['permalink']})\n\n"

    for c in comments:
        content += f"Comment: {c['body']}\n(Source: {c['permalink']})\n\n"

    content += (
        "\nBased on the above, build a detailed User Persona including:\n"
        "- Name (if inferred)\n"
        "- Age Range\n"
        "- Location (if possible)\n"
        "- Occupation or student status\n"
        "- Interests/hobbies\n"
        "- Political/ideological leanings\n"
        "- Personality traits\n"
        "- Writing style/tone\n"
        "- Any other unique identifiers\n\n"
        "For each point, **cite the exact post/comment with a link** that supports it.\n"
        "Format like a user persona document.\n"
    )
    return content

def generate_persona(posts, comments):
    prompt = build_prompt(posts, comments)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content

def save_to_file(username, content):
    filename = f"{username}_persona.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n✅ User persona saved to: {filename}")

def main():
    reddit_url = input("Enter Reddit user profile URL: ")
    username = get_reddit_username(reddit_url)
    if not username:
        print("Invalid Reddit URL.")
        return

    posts, comments = scrape_user_data(username)
    persona = generate_persona(posts, comments)
    save_to_file(username, persona)

if __name__ == "__main__":
    main()
