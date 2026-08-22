import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [tasksLoading, setTasksLoading] = useState(false);

  // --------------------------------------------------
  // LOAD TASKS
  // --------------------------------------------------

  const loadTasks = async () => {
    try {
      setTasksLoading(true);

      const response = await fetch(`${API_URL}/tasks`);

      if (!response.ok) {
        throw new Error("Failed to load tasks");
      }

      const data = await response.json();

      setTasks(data.tasks);
    } catch (error) {
      console.error("Error loading tasks:", error);
    } finally {
      setTasksLoading(false);
    }
  };

  // --------------------------------------------------
  // LOAD TASKS WHEN PAGE OPENS
  // --------------------------------------------------

  useEffect(() => {
    loadTasks();
  }, []);

  // --------------------------------------------------
  // SEND CHAT MESSAGE
  // --------------------------------------------------

  const sendMessage = async () => {
    if (!message.trim() || loading) {
      return;
    }

    const userMessage = message.trim();

    // Show user message immediately
    setMessages((previousMessages) => [
      ...previousMessages,
      {
        role: "user",
        text: userMessage,
      },
    ]);

    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from server");
      }

      const data = await response.json();

      // Show assistant response
      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          text: data.answer,
          source: data.source,
          task: data.task,
          tasks: data.tasks,
        },
      ]);

      // Always refresh the task panel after chat.
      // This keeps the panel synchronized when:
      // - a task is created
      // - a task is completed
      // - tasks are listed
      // - task status changes conversationally
      await loadTasks();
    } catch (error) {
      console.error("Error sending message:", error);

      setMessages((previousMessages) => [
        ...previousMessages,
        {
          role: "assistant",
          text: "Sorry, I could not connect to the HR assistant.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // COMPLETE TASK FROM UI
  // --------------------------------------------------

  const completeTask = async (taskId) => {
    try {
      const response = await fetch(
        `${API_URL}/tasks/${taskId}/complete`,
        {
          method: "PUT",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to complete task");
      }

      const data = await response.json();

      console.log(data);

      // Refresh task list
      await loadTasks();
    } catch (error) {
      console.error("Error completing task:", error);
    }
  };

  // --------------------------------------------------
  // ENTER KEY
  // --------------------------------------------------

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="app">

      {/* HEADER */}

      <header className="header">

        <div>
          <h1>HR Onboarding AI Assistant</h1>

          <p>
            Ask questions about HR policies and onboarding.
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Online
        </div>

      </header>


      {/* MAIN CONTENT */}

      <main className="main-content">

        {/* CHAT SECTION */}

        <section className="chat-section">

          <div className="chat-container">

            {messages.length === 0 ? (

              <div className="welcome">

                <h2>Welcome 👋</h2>

                <p>
                  I can help you with HR onboarding questions,
                  tasks, policies, leave, documents, IT access,
                  and employee support.
                </p>

                <div className="suggestions">

                  <button
                    onClick={() =>
                      setMessage(
                        "What are the working hours?"
                      )
                    }
                  >
                    What are the working hours?
                  </button>

                  <button
                    onClick={() =>
                      setMessage(
                        "What documents are required for onboarding?"
                      )
                    }
                  >
                    What documents are required?
                  </button>

                  <button
                    onClick={() =>
                      setMessage(
                        "Show me my tasks"
                      )
                    }
                  >
                    Show my tasks
                  </button>

                </div>

              </div>

            ) : (

              <div className="messages">

                {messages.map((item, index) => (

                  <div
                    key={index}
                    className={`message ${
                      item.role === "user"
                        ? "user-message"
                        : "assistant-message"
                    }`}
                  >

                    <div className="message-label">
                      {item.role === "user"
                        ? "You"
                        : "HR Assistant"}
                    </div>

                    <div className="message-text">
                      {item.text}
                    </div>


                    {/* CHAT TASK */}

                    {item.task && (

                      <div className="task-card">

                        <div className="task-title">
                          {item.task.title}
                        </div>

                        <div className="task-status">
                          Status:{" "}
                          <strong>
                            {item.task.status}
                          </strong>
                        </div>

                      </div>

                    )}


                    {/* CHAT TASK LIST */}

                    {item.tasks &&
                      item.tasks.length > 0 && (

                        <div className="task-list">

                          {item.tasks.map((task) => (

                            <div
                              className="task-card"
                              key={task.id}
                            >

                              <div className="task-title">
                                {task.title}
                              </div>

                              <div className="task-status">
                                Status:{" "}
                                <strong>
                                  {task.status}
                                </strong>
                              </div>

                            </div>

                          ))}

                        </div>

                      )}


                    {/* SOURCE */}

                    {item.source && (

                      <div className="source">
                        Source: {item.source}
                      </div>

                    )}

                  </div>

                ))}


                {/* LOADING MESSAGE */}

                {loading && (

                  <div className="message assistant-message">

                    <div className="message-label">
                      HR Assistant
                    </div>

                    <div className="message-text">
                      Thinking...
                    </div>

                  </div>

                )}

              </div>

            )}

          </div>

        </section>


        {/* TASK PANEL */}

        <aside className="task-panel">

          <div className="task-panel-header">

            <div>
              <h2>My Tasks</h2>

              <p>
                Onboarding tasks
              </p>
            </div>

            <button
              className="refresh-button"
              onClick={loadTasks}
              disabled={tasksLoading}
              title="Refresh tasks"
            >
              ↻
            </button>

          </div>


          {/* TASK LOADING */}

          {tasksLoading ? (

            <div className="task-loading">
              Loading tasks...
            </div>

          ) : tasks.length === 0 ? (

            /* NO TASKS */

            <div className="empty-tasks">

              <div className="empty-icon">
                ✓
              </div>

              <p>
                No tasks yet.
              </p>

              <span>
                Create a task through the chat.
              </span>

            </div>

          ) : (

            /* TASK LIST */

            <div className="panel-task-list">

              {tasks.map((task) => (

                <div
                  className={`panel-task ${
                    task.status === "completed"
                      ? "completed-task"
                      : ""
                  }`}
                  key={task.id}
                >

                  <div className="task-check">

                    {task.status === "completed"
                      ? "✓"
                      : "○"}

                  </div>


                  <div className="panel-task-content">

                    <div className="panel-task-title">
                      {task.title}
                    </div>

                    <div
                      className={`status-badge ${
                        task.status === "completed"
                          ? "completed"
                          : "pending"
                      }`}
                    >
                      {task.status}
                    </div>


                    {/* MARK COMPLETE BUTTON */}

                    {task.status === "pending" && (

                      <button
                        className="complete-button"
                        onClick={() =>
                          completeTask(task.id)
                        }
                      >
                        Mark Complete
                      </button>

                    )}

                  </div>

                </div>

              ))}

            </div>

          )}

        </aside>

      </main>


      {/* INPUT AREA */}

      <div className="input-area">

        <input
          type="text"
          placeholder="Ask an HR question or manage your tasks..."
          value={message}
          onChange={(event) =>
            setMessage(event.target.value)
          }
          onKeyDown={handleKeyDown}
          disabled={loading}
        />

        <button
          onClick={sendMessage}
          disabled={loading || !message.trim()}
        >
          {loading ? "..." : "Send"}
        </button>

      </div>

    </div>
  );
}

export default App;