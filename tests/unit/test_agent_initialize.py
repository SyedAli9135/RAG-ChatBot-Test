import pytest_check as check

from app.agent.chat_agent import get_agent, get_db
from app.knowledge.store import get_knowledge


def test_agent_initialization():
    """
    Agent initializes correctly.
    """
    agent1 = get_agent()
    agent2 = get_agent()

    check.equal(id(agent1), id(agent2), "Singleton pattern is broken!")

    check.is_not_none(agent1.agent, "Agno agent is missing!")


def test_database_initialization():
    """
    Database instance created
    """
    db1 = get_db()
    db2 = get_db()

    check.equal(id(db1), id(db2), "Database singleton broken!")


def test_knowledge_initialization():
    """
    Knowledge base initialized
    """
    kb1 = get_knowledge()
    kb2 = get_knowledge()

    check.equal(id(kb1), id(kb2), "Knowledge singleton broken!")

    check.is_not_none(kb1.vector_db, "Vector DB missing!")
    check.is_not_none(kb1.contents_db, "Contents DB missing!")
