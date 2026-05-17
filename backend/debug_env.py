import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

print(f"Current working directory: {os.getcwd()}")

found = find_dotenv()
print(f"find_dotenv() result: {found}")

# Explicit check for .env in parent of backend
current_file = Path(__file__).resolve()
# Assuming this script is run from backend/ or backend/scripts/
print(f"Script location: {current_file}")

# Try to locate .env relative to this script
# If we place this in backend/debug_env.py
project_root = current_file.parent.parent
env_path = project_root / ".env"
print(f"Checking for .env at: {env_path}")
print(f"Exists? {env_path.exists()}")

load_dotenv(found)
print(f"ETH_PRIVATE_KEY from find_dotenv: {os.getenv('ETH_PRIVATE_KEY')}")

load_dotenv(env_path)
print(f"ETH_PRIVATE_KEY from explicit path: {os.getenv('ETH_PRIVATE_KEY')}")
