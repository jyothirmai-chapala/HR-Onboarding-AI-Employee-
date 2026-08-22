from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import re
import json
import uuid


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="HR Onboarding AI Employee",
    description="AI-powered HR onboarding assistant",
    version="1.0.0"
)


# ==================================================
# CORS
# ==================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

KNOWLEDGE_BASE_DIR = BASE_DIR.parent / "knowledge_base"

FAQ_FILE = KNOWLEDGE_BASE_DIR / "hr_faq.txt"

TASK_FILE = BASE_DIR / "tasks.json"


# ==================================================
# CONVERSATION MEMORY
# ==================================================

# Stores the most recently displayed task list.
# This allows multi-turn conversations such as:
#
# User: Show me my tasks
# AI: Here are your tasks...
#
# User: Complete the second one
# AI: Sure. I marked "Prepare resume" as completed.

last_shown_tasks = []


# ==================================================
# KNOWLEDGE BASE
# ==================================================

def load_knowledge_base():
    """Load the HR FAQ document."""

    if not FAQ_FILE.exists():
        return ""

    return FAQ_FILE.read_text(
        encoding="utf-8"
    )


knowledge_base = load_knowledge_base()


# ==================================================
# TASK MANAGEMENT
# ==================================================

def load_tasks():
    """Load tasks from the JSON file."""

    if not TASK_FILE.exists():
        return {
            "tasks": []
        }

    with open(
        TASK_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_tasks(data):
    """Save tasks to the JSON file."""

    with open(
        TASK_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def create_task(title):
    """Create and store a new onboarding task."""

    data = load_tasks()

    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "status": "pending"
    }

    data["tasks"].append(task)

    save_tasks(data)

    return task


def get_tasks():
    """Return all onboarding tasks."""

    data = load_tasks()

    return data["tasks"]


def complete_task(task_id):
    """Mark a task as completed."""

    data = load_tasks()

    for task in data["tasks"]:

        if task["id"] == task_id:

            task["status"] = "completed"

            save_tasks(data)

            return task

    return None


# ==================================================
# QUESTION / ANSWER PROCESSING
# ==================================================

def find_answer(question: str):
    """
    Find the most relevant FAQ answer using
    simple keyword matching.
    """

    if not knowledge_base:

        return {
            "answer": (
                "The HR knowledge base is currently unavailable."
            ),
            "source": None
        }


    # ----------------------------------------------
    # Split FAQ into individual numbered sections
    # ----------------------------------------------

    sections = re.split(
        r"\n(?=\d+\.\s)",
        knowledge_base
    )


    # ----------------------------------------------
    # Extract words from user's question
    # ----------------------------------------------

    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{3,}\b",
            question.lower()
        )
    )


    best_section = None
    best_score = 0


    # ----------------------------------------------
    # Compare question with each FAQ section
    # ----------------------------------------------

    for section in sections:

        section_words = set(
            re.findall(
                r"\b[a-zA-Z]{3,}\b",
                section.lower()
            )
        )

        common_words = question_words.intersection(
            section_words
        )

        score = len(common_words)

        if score > best_score:

            best_score = score
            best_section = section


    # ----------------------------------------------
    # No relevant answer found
    # ----------------------------------------------

    if (
        best_section is None
        or best_score < 2
    ):

        return {
            "answer": (
                "I could not find this information in the HR "
                "knowledge base. Please contact HR or your "
                "assigned onboarding coordinator."
            ),
            "source": None
        }


    # ----------------------------------------------
    # Separate question and answer
    # ----------------------------------------------

    lines = best_section.strip().split("\n")

    faq_question = lines[0]

    answer = " ".join(
        lines[1:]
    ).strip()


    return {
        "answer": answer,
        "source": faq_question
    }


# ==================================================
# API MODELS
# ==================================================

class ChatRequest(BaseModel):
    message: str


class TaskRequest(BaseModel):
    title: str


# ==================================================
# TASK REQUEST DETECTION
# ==================================================

def is_task_request(message: str):
    """
    Check whether the user wants to create a task.
    """

    task_keywords = [
        "create task",
        "add task",
        "new task",
        "create a task",
        "add a task"
    ]

    message = message.lower().strip()

    return any(
        keyword in message
        for keyword in task_keywords
    )


def is_list_task_request(message: str):
    """
    Check whether the user wants to see their tasks.
    """

    task_keywords = [
        "show my tasks",
        "list my tasks",
        "get my tasks",
        "what are my tasks",
        "show tasks",
        "list tasks",
        "get tasks",
        "view my tasks",
        "check my tasks"
    ]

    message = message.lower().strip()

    return any(
        keyword in message
        for keyword in task_keywords
    )


# ==================================================
# EXTRACT TASK TITLE
# ==================================================

def extract_task_title(message: str):
    """
    Extract the actual task title from a task
    creation request.
    """

    title = message.lower().strip()

    keywords = [
        "create a task",
        "create task",
        "add a task",
        "add task",
        "new task"
    ]

    for keyword in keywords:

        if keyword in title:

            title = title.replace(
                keyword,
                "",
                1
            ).strip()

            break


    # Remove common connecting words

    title = re.sub(
        r"^(to|for)\s+",
        "",
        title
    ).strip()


    return title


# ==================================================
# COMPLETE TASK DETECTION
# ==================================================

def is_complete_task_request(message: str):
    """
    Check whether the user wants to complete a task.
    """

    keywords = [
        "complete task",
        "complete the task",
        "mark task as completed",
        "mark the task as completed",
        "finish task",
        "finish the task",
        "complete",
        "finish"
    ]

    message = message.lower().strip()

    return any(
        keyword in message
        for keyword in keywords
    )


# ==================================================
# EXTRACT TASK TITLE FOR COMPLETION
# ==================================================

def extract_complete_task_title(message: str):
    """
    Extract the task title from a completion request.
    """

    title = message.lower().strip()

    keywords = [
        "complete the task",
        "complete task",
        "mark the task as completed",
        "mark task as completed",
        "finish the task",
        "finish task",
        "complete",
        "finish"
    ]

    for keyword in keywords:

        if keyword in title:

            title = title.replace(
                keyword,
                "",
                1
            ).strip()

            break

    return title


# ==================================================
# FIND TASK BY TITLE
# ==================================================

def find_task_by_title(title: str):
    """
    Find a task by its exact title.
    """

    tasks = get_tasks()

    title = title.lower().strip()

    for task in tasks:

        if task["title"].lower().strip() == title:

            return task

    return None


# ==================================================
# FIND TASK NUMBER
# ==================================================

def get_task_number_from_message(message: str):
    """
    Detect whether the user refers to a task
    using a position or number.

    Examples:

    "complete the first one" -> 1
    "complete the second one" -> 2
    "complete task 3" -> 3
    "finish number 2" -> 2
    """

    message = message.lower().strip()


    # ----------------------------------------------
    # Number words
    # ----------------------------------------------

    number_words = {

        "first": 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eighth": 8,
        "ninth": 9,
        "tenth": 10

    }


    for word, number in number_words.items():

        if word in message:

            return number


    # ----------------------------------------------
    # Numeric task number
    # ----------------------------------------------

    match = re.search(
        r"\b(?:task\s*)?(\d+)(?:st|nd|rd|th)?\b",
        message
    )


    if match:

        return int(
            match.group(1)
        )


    return None


# ==================================================
# ROOT ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": (
            "HR Onboarding AI Employee "
            "Backend is running!"
        )
    }


# ==================================================
# CHAT ENDPOINT
# ==================================================

@app.post("/chat")
def chat(request: ChatRequest):

    global last_shown_tasks

    message = request.message.strip()


    # ==================================================
    # 1. CREATE TASK
    # ==================================================

    if is_task_request(message):

        title = extract_task_title(
            message
        )


        if not title:

            return {
                "question": message,
                "answer": (
                    "Please provide a task title."
                )
            }


        task = create_task(
            title
        )


        return {
            "question": message,
            "answer": (
                "Task created successfully."
            ),
            "task": task
        }


    # ==================================================
    # 2. LIST TASKS
    # ==================================================

    if is_list_task_request(message):

        tasks = get_tasks()


        # ----------------------------------------------
        # Remember the latest task list
        # ----------------------------------------------

        last_shown_tasks = tasks.copy()


        return {
            "question": message,
            "answer": "Here are your tasks.",
            "tasks": tasks
        }


    # ==================================================
    # 3. CHECK PENDING TASKS
    # ==================================================

    pending_request_keywords = [
    "pending tasks",
    "tasks are pending",
    "tasks still pending",
    "what tasks are pending",
    "what tasks are still pending",
    "which tasks are pending",
    "which tasks are still pending",
    "remaining tasks",
    "tasks remaining",
    "unfinished tasks",
    "what is left",
    "what's left",
    "what remains",
    "remaining"
]
    if any(
        keyword in message.lower()
        for keyword in pending_request_keywords
    ):

        tasks = get_tasks()

        pending_tasks = [
            task
            for task in tasks
            if task["status"] == "pending"
        ]


        if not pending_tasks:

            return {
                "question": message,
                "answer": (
                    "You have no pending tasks. "
                    "Great job!"
                )
            }


        return {
            "question": message,
            "answer": (
                f"You have {len(pending_tasks)} "
                f"pending task(s)."
            ),
            "tasks": pending_tasks
        }


    # ==================================================
    # 4. COMPLETE TASK
    # ==================================================

    if is_complete_task_request(message):


        # ----------------------------------------------
        # First try task number / position
        # ----------------------------------------------

        task_number = get_task_number_from_message(
            message
        )


        if task_number is not None:


            # ------------------------------------------
            # Use remembered task list
            # ------------------------------------------

            if last_shown_tasks:

                if (
                    1 <= task_number
                    <= len(last_shown_tasks)
                ):

                    selected_task = (
                        last_shown_tasks[
                            task_number - 1
                        ]
                    )


                    completed_task = complete_task(
                        selected_task["id"]
                    )


                    if completed_task:

                        # Update remembered task
                        # so subsequent turns are accurate

                        for task in last_shown_tasks:

                            if (
                                task["id"]
                                == completed_task["id"]
                            ):

                                task["status"] = (
                                    "completed"
                                )


                        return {
                            "question": message,
                            "answer": (
                                f'Sure. I marked '
                                f'"{completed_task["title"]}" '
                                f'as completed.'
                            ),
                            "task": completed_task
                        }


                return {
                    "question": message,
                    "answer": (
                        "I could not find that task "
                        "number in the task list."
                    )
                }


            # ------------------------------------------
            # No previous task list
            # ------------------------------------------

            tasks = get_tasks()


            if (
                1 <= task_number
                <= len(tasks)
            ):

                selected_task = tasks[
                    task_number - 1
                ]


                completed_task = complete_task(
                    selected_task["id"]
                )


                if completed_task:

                    return {
                        "question": message,
                        "answer": (
                            f'I marked '
                            f'"{completed_task["title"]}" '
                            f'as completed.'
                        ),
                        "task": completed_task
                    }


            return {
                "question": message,
                "answer": (
                    "I could not find that task number."
                )
            }


        # ----------------------------------------------
        # Otherwise try task title
        # ----------------------------------------------

        title = extract_complete_task_title(
            message
        )


        task = find_task_by_title(
            title
        )


        if task is None:

            return {
                "question": message,
                "answer": (
                    "I could not find that task. "
                    "Please provide the task name "
                    "or task number."
                )
            }


        completed_task = complete_task(
            task["id"]
        )


        return {
            "question": message,
            "answer": (
                f'I marked '
                f'"{completed_task["title"]}" '
                f'as completed.'
            ),
            "task": completed_task
        }


    # ==================================================
    # 5. HR KNOWLEDGE BASE
    # ==================================================

    result = find_answer(
        message
    )


    return {
        "question": message,
        "answer": result["answer"],
        "source": result["source"]
    }


# ==================================================
# DIRECT TASK CREATION ENDPOINT
# ==================================================

@app.post("/tasks")
def create_onboarding_task(
    request: TaskRequest
):

    task = create_task(
        request.title
    )


    return {
        "message": (
            "Task created successfully"
        ),
        "task": task
    }


# ==================================================
# GET ALL TASKS ENDPOINT
# ==================================================

@app.get("/tasks")
def list_onboarding_tasks():

    tasks = get_tasks()


    return {
        "tasks": tasks
    }


# ==================================================
# COMPLETE TASK BY ID ENDPOINT
# ==================================================

@app.put("/tasks/{task_id}/complete")
def mark_task_completed(
    task_id: str
):

    task = complete_task(
        task_id
    )


    if task is None:

        return {
            "message": "Task not found"
        }


    return {
        "message": (
            "Task marked as completed"
        ),
        "task": task
    }