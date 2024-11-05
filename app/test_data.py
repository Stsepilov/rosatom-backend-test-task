from sqlmodel import Session
from .database import create_db_and_tables, engine
from .crud import create_user, create_message


def create_test_data():
    create_db_and_tables()

    with Session(engine) as session:
        user1 = create_user(session, username="testuser", password="password1", moderator=False)
        user2 = create_user(session, username="moderator", password="modpassword", moderator=True)
        user3 = create_user(session, username="anotheruser", password="password2", moderator=False)

        message1 = create_message(session, content="Hello from testuser", sender_id=user1.id, channel_id=1)
        message2 = create_message(session, content="Moderator's message", sender_id=user2.id, channel_id=1)
        message3 = create_message(session, content="Another user's message", sender_id=user3.id, channel_id=1)

        session.commit()

    print("Тестовые данные успешно созданы.")


if __name__ == "__main__":
    create_test_data()
