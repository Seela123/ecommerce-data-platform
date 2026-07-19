import json
from pathlib import Path
from datetime import datetime, timezone

import requests


BASE_URL = "https://dummyjson.com/users"
LIMIT = 100


def fetch_all_users() -> list[dict]:
    all_users = []
    skip = 0

    while True:
        response = requests.get(
            BASE_URL,
            params={
                "limit": LIMIT,
                "skip": skip
            },
            timeout=30
        )

        response.raise_for_status()

        payload = response.json()
        users = payload.get("users", [])
        total = payload.get("total", 0)

        all_users.extend(users)

        print(f"Fetched {len(users)} users. Skip: {skip}")

        if not users or len(all_users) >= total:
            break

        skip += LIMIT

    return all_users


def save_users(users: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        "source": "dummyjson_users",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "total_users": len(users),
        "users": users
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4, ensure_ascii=False)


def main():
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "staging" / "users.json"

    try:
        print("Starting users extraction...")

        all_users = fetch_all_users()
        save_users(all_users, output_path)

        print("Users extraction completed successfully.")
        print(f"Saved users to: {output_path}")
        print(f"Total users extracted: {len(all_users)}")

    except requests.exceptions.RequestException as error:
        print(f"Users extraction failed: {error}")
        raise


if __name__ == "__main__":
    main()