from typing import Any

MINI_APPS: dict[str, dict[str, Any]] = {
    "problem-analysis": {
        "id": "problem-analysis",
        "title": "Problem Analysis",
        "description": "Structure the main problem and find a first small step.",
        "questions": [
            "What is the main problem?",
            "When did it start?",
            "What makes it difficult?",
            "What result would feel helpful?",
        ],
    },
    "anxiety-helper": {
        "id": "anxiety-helper",
        "title": "Anxiety Helper",
        "description": "Balance a worry with facts and choose one safe action.",
        "questions": [
            "What exactly are you worried about?",
            "What facts support this worry?",
            "What facts make it less certain?",
            "What is one safe small action today?",
        ],
    },
    "decision-assistant": {
        "id": "decision-assistant",
        "title": "Decision Assistant",
        "description": "Compare options, pros, cons, and the main risk.",
        "questions": [
            "What decision do you need to make?",
            "What options do you have?",
            "What are the pros and cons?",
            "What is the main risk?",
        ],
    },
    "goal-planner": {
        "id": "goal-planner",
        "title": "Goal Planner",
        "description": "Turn a goal into a short weekly action plan.",
        "questions": [
            "What goal do you want to reach?",
            "Why is it important?",
            "What deadline do you have?",
            "What are 3 small steps?",
        ],
    },
}
