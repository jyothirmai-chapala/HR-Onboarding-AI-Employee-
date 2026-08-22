# HR Onboarding AI Employee

A conversational HR onboarding assistant built with React and FastAPI. The application helps new employees get answers to HR onboarding questions using a provided HR knowledge base and manage simple onboarding tasks conversationally.

## Problem Statement

Build a conversational agent that helps a new hire with onboarding questions such as:

- HR policies
- Benefits
- IT setup
- Required documents
- Onboarding procedures

The application should also create, store, track, and complete onboarding tasks.

## Features

### 1. HR Question Answering

The assistant answers HR onboarding questions using information from the provided HR FAQ and policy documents.

Example:

> User: What are the working hours?

The system searches the HR knowledge base and returns the relevant answer along with the source FAQ question.

### 2. Create Onboarding Tasks

Users can create tasks through natural language.

Example:

> Create a task to upload passport copy

The task is created with:

- Unique task ID
- Task title
- Pending status

### 3. View Tasks

Users can ask:

> Show me my tasks

The assistant displays the current onboarding tasks and their status.

### 4. Complete Tasks

Tasks can be completed in two ways:

- Conversationally through the chat
- Using the `Mark Complete` button in the task panel

Example:

> Complete the fourth one

The assistant identifies the referenced task and marks it as completed.

### 5. Multi-Turn Conversation

The application supports multi-turn task conversations.

Example:

```text
User: Show me my tasks

Assistant: Here are your tasks...

User: Complete the fourth one

Assistant: Sure. I marked "Apply for internship" as completed.

User: What tasks are still pending?

Assistant: Here are your remaining pending tasks...
