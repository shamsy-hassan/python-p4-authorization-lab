#!/usr/bin/env python3

from random import randint, choice as rc
from faker import Faker

from app import app
from models import db, Article, User

fake = Faker()

with app.app_context():
    print("Deleting all records...")
    Article.query.delete()
    User.query.delete()

    print("Creating users...")
    users = []
    usernames = set()

    for _ in range(25):
        username = fake.first_name()
        while username in usernames:
            username = fake.first_name()
        usernames.add(username)

        users.append(User(username=username))

    db.session.add_all(users)

    print("Creating articles...")
    articles = []

    # Ensure the first article is member-only for test compatibility
    first_article = Article(
        author=fake.name(),
        title="First Member-Only Article",
        content=fake.paragraph(nb_sentences=8),
        preview="Private content preview...",
        minutes_to_read=randint(1, 20),
        is_member_only=True
    )
    articles.append(first_article)

    # Create 99 additional articles with random member-only status
    for _ in range(99):
        content = fake.paragraph(nb_sentences=8)
        preview = content[:25] + '...'

        article = Article(
            author=fake.name(),
            title=fake.sentence(),
            content=content,
            preview=preview,
            minutes_to_read=randint(1, 20),
            is_member_only=rc([True, False, False])  # ~33% chance of True
        )
        articles.append(article)

    db.session.add_all(articles)
    db.session.commit()

    print("✅ Seeding complete.")
