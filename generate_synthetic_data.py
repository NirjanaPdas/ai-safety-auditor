from pathlib import Path
import argparse
import random
import pandas as pd
import datetime as dt


def generate_users(n=20, start_date="2024-01-01"):
    user_ids = [f"u{i+1}" for i in range(n)]
    ages = [random.choice([13, 14, 15, 16, 17, 18, 21, 25, 30]) for _ in range(n)]
    account_types = [random.choice(["standard", "creator", "business"]) for _ in range(n)]
    created_at = pd.date_range(start_date, periods=n).tolist()

    return pd.DataFrame(
        {
            "user_id": user_ids,
            "age": ages,
            "account_type": account_types,
            "created_at": created_at,
        }
    )


def sample_post_text(user_age):
    risky_self_harm = [
        "I feel like nothing matters anymore.",
        "Sometimes I just want to disappear.",
        "I have not eaten properly in days.",
    ]
    risky_bully = [
        "You are so ugly lol.",
        "Nobody likes you, just leave.",
        "You are a loser, everyone knows it.",
    ]
    risky_grooming = [
        "Don't tell your parents we talk here.",
        "Keep our chats secret okay?",
        "You can trust me, I’m older and I know better.",
    ]
    risky_substance = [
        "Got so drunk last night lol.",
        "Trying pills for the first time haha.",
        "Smoking every day now, feels great.",
    ]
    safe = [
        "Exam went well today.",
        "Had a great day with friends!",
        "Practicing for my football match.",
        "Studying hard for JEE.",
        "Watching movies with family.",
    ]

    bucket = random.random()
    if user_age < 18:
        if bucket < 0.15:
            return random.choice(risky_self_harm)
        elif bucket < 0.3:
            return random.choice(risky_bully)
        elif bucket < 0.4:
            return random.choice(risky_grooming)
        else:
            return random.choice(safe)
    else:
        if bucket < 0.15:
            return random.choice(risky_substance)
        elif bucket < 0.3:
            return random.choice(risky_grooming)
        elif bucket < 0.4:
            return random.choice(risky_bully)
        else:
            return random.choice(safe)


def generate_posts(users_df, posts_per_user=5, start_ts="2024-03-01"):
    rows = []
    post_id = 1
    base = pd.Timestamp(start_ts)
    for _, row in users_df.iterrows():
        for _ in range(posts_per_user):
            rows.append(
                {
                    "post_id": f"p{post_id}",
                    "user_id": row["user_id"],
                    "text": sample_post_text(row["age"]),
                    "timestamp": base + pd.Timedelta(days=random.randint(0, 60)),
                }
            )
            post_id += 1
    return pd.DataFrame(rows)


def generate_interactions(users_df, n_interactions=60, start_ts="2024-03-01"):
    rows = []
    user_ids = users_df["user_id"].tolist()
    ages = dict(zip(users_df["user_id"], users_df["age"]))

    def sample_dm_text(older, younger):
        risky = [
            "Don't tell anyone we talk here.",
            "I can send you pics but keep it secret.",
            "We should meet alone sometime.",
        ]
        neutral = [
            "Hey, how are your exams going?",
            "Let's play BGMI later.",
            "Did you finish the homework?",
        ]
        return random.choice(risky if random.random() < 0.4 else neutral)

    base = pd.Timestamp(start_ts)
    for i in range(n_interactions):
        u1, u2 = random.sample(user_ids, 2)
        a1, a2 = ages[u1], ages[u2]
        older, younger = (u1, u2) if a1 > a2 else (u2, u1)

        rows.append(
            {
                "interaction_id": f"i{i+1}",
                "from_user": older,
                "to_user": younger,
                "type": "dm",
                "text": sample_dm_text(older, younger),
                "timestamp": base + pd.Timedelta(days=random.randint(0, 60)),
            }
        )

    return pd.DataFrame(rows)


def save_data(data_dir: Path, prefix: str, users, posts, interactions):
    data_dir.mkdir(parents=True, exist_ok=True)
    users.to_csv(data_dir / f"{prefix}_users.csv", index=False)
    posts.to_csv(data_dir / f"{prefix}_posts.csv", index=False)
    interactions.to_csv(data_dir / f"{prefix}_interactions.csv", index=False)


def parse_args():
    p = argparse.ArgumentParser(description="Generate synthetic data for SafeScroll demo.")
    p.add_argument("--users", type=int, default=20, help="Number of users")
    p.add_argument("--posts-per-user", type=int, default=5, help="Posts per user")
    p.add_argument("--interactions", type=int, default=60, help="Number of interactions (DMs)")
    p.add_argument("--seed", type=int, default=None, help="Random seed (optional)")
    p.add_argument("--out-dir", type=str, default="data", help="Output directory")
    p.add_argument("--prefix", type=str, default="safescroll", help="Output filename prefix")
    return p.parse_args()


def main():
    args = parse_args()

    if args.seed is not None:
        random.seed(args.seed)
        pd.np.random.seed(args.seed)  # type: ignore[attr-defined]

    data_dir = Path(args.out_dir)
    users = generate_users(args.users)
    posts = generate_posts(users, posts_per_user=args.posts_per_user)
    interactions = generate_interactions(users, n_interactions=args.interactions)

    save_data(data_dir, args.prefix, users, posts, interactions)

    print(
        f"Synthetic data written to {data_dir}/{args.prefix}_users.csv, "
        f"{data_dir}/{args.prefix}_posts.csv, {data_dir}/{args.prefix}_interactions.csv"
    )


if __name__ == "__main__":
    main()
