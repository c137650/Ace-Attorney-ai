"""
辩题加载器
"""

import json
import os
from typing import Optional
from dataclasses import dataclass

from game_state import Topic


def load_topics(topics_dir: str = None) -> list:
    """加载所有辩题"""
    if topics_dir is None:
        topics_dir = os.path.join(os.path.dirname(__file__), "topics")

    topics_file = os.path.join(topics_dir, "topics.json")

    if not os.path.exists(topics_file):
        return []

    with open(topics_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Topic(**t) for t in data]


def get_random_topic(topics_dir: str = None) -> Optional[Topic]:
    """随机获取一个辩题"""
    import random
    topics = load_topics(topics_dir)
    if not topics:
        return None
    return random.choice(topics)


def get_topic_by_id(topic_id: str, topics_dir: str = None) -> Optional[Topic]:
    """根据ID获取辩题"""
    topics = load_topics(topics_dir)
    for topic in topics:
        if topic.id == topic_id:
            return topic
    return None


def create_topic_from_dict(topic_dict: dict) -> Topic:
    """从字典创建Topic对象"""
    return Topic(
        id=topic_dict.get("id", "custom"),
        title=topic_dict.get("title", ""),
        description=topic_dict.get("description", ""),
        stance_a=topic_dict.get("stance_a", ""),
        stance_b=topic_dict.get("stance_b", "")
    )
