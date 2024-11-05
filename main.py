import requests
from datetime import datetime, timedelta
import random
import subprocess
import dotenv
import os

# Load environment variables from .env file
dotenv.load_dotenv()

# Constants
GITHUB_TOKEN = os.getenv("TOKEN")
USERNAME = "EukkMaru"
START_DATE = datetime(2023, 1, 1)
REPO_PATH = "C:\\Users\\Lenovo\\Desktop\\EukkMaru\\coding\\touch-grass"  # Path to your Git repository

def get_contribution_data(username, start_date, end_date):
    """Fetches contribution data between start_date and end_date using GitHub GraphQL API."""
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}"
    }
    
    contributions = []

    # Loop through the date range in one-year increments
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + timedelta(days=365), end_date)
        
        query = f"""
        {{
          user(login: "{username}") {{
            contributionsCollection(from: "{current_start.isoformat()}", to: "{current_end.isoformat()}") {{
              contributionCalendar {{
                weeks {{
                  contributionDays {{
                    date
                    contributionCount
                  }}
                }}
              }}
            }}
          }}
        }}
        """
        
        response = requests.post(url, json={'query': query}, headers=headers)
        data = response.json()
        
        if "errors" in data:
            raise Exception(data["errors"])
        
        contributions += data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        current_start = current_end + timedelta(days=1)

    return contributions

def find_empty_days(contribution_weeks):
    """Identifies days with zero contributions."""
    empty_days = []
    for week in contribution_weeks:
        for day in week["contributionDays"]:
            if day["contributionCount"] == 0:
                empty_days.append(day["date"])
    return empty_days

def create_commit(date):
    """Create a commit with a specific date in the repository."""
    dateStr = date.strftime("%a %b %d %H:%M:%S %Y +0000")
    with open("test.txt", "a") as f:
        f.write(f"Commit on {dateStr}\n")
    subprocess.run(["git", "add", "test.txt"], cwd=REPO_PATH)
    subprocess.run(["git", "commit", "-m", f"Commit on {dateStr}"], cwd=REPO_PATH)
    subprocess.run(["git", "commit", "--amend", "--no-edit", f'--date="{dateStr}"'], cwd=REPO_PATH)

def main():
    today = datetime.today()
    # Get contribution data from GitHub
    contribution_data = get_contribution_data(USERNAME, START_DATE, today)
    empty_days = find_empty_days(contribution_data)

    # Generate commits for empty days
    for day in empty_days:
        commit_date = datetime.fromisoformat(day)
        num_commits = random.randint(2, 15)
        for _ in range(num_commits):
            create_commit(commit_date)
        print(f"Created {num_commits} commits on {commit_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()

