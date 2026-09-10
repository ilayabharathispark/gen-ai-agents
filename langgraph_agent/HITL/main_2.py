import uuid

import streamlit as st

from langgraph.types import Command

from agent import graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="LangGraph AI Assistant",
    page_icon="🤖",
    layout="centered",
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None


# ============================================================
# TITLE
# ============================================================

st.title("🤖 LangGraph AI Assistant")


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# ============================================================
# EMAIL APPROVAL / HITL
# ============================================================

if st.session_state.pending_interrupt:

    interrupt_data = st.session_state.pending_interrupt

    email_data = interrupt_data.value

    st.divider()

    st.subheader("📧 Email Approval Required")

    st.write(
        "The agent is requesting permission to send this email."
    )

    st.table(
        {
            "Field": [
                "To",
                "Subject",
                "Story",
            ],
            "Value": [
                email_data.get("recipient", ""),
                email_data.get("subject", ""),
                email_data.get("story", ""),
            ],
        }
    )

    col1, col2 = st.columns(2)

    # ========================================================
    # APPROVE
    # ========================================================

    with col1:

        if st.button(
            "✅ Approve & Send",
            use_container_width=True,
        ):

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            result = graph.invoke(
                Command(
                    resume={
                        "approved": True
                    }
                ),
                config=config,
            )

            st.session_state.pending_interrupt = None

            if result.get("result"):

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": result["result"],
                    }
                )

            st.rerun()

    # ========================================================
    # REJECT
    # ========================================================

    with col2:

        if st.button(
            "❌ Reject",
            use_container_width=True,
        ):

            config = {
                "configurable": {
                    "thread_id": st.session_state.thread_id
                }
            }

            result = graph.invoke(
                Command(
                    resume={
                        "approved": False
                    }
                ),
                config=config,
            )

            st.session_state.pending_interrupt = None

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Email was not sent.",
                }
            )

            st.rerun()


# ============================================================
# EMAIL DETAILS
# ============================================================

st.divider()

recipient = st.text_input(
    "Recipient Email",
    placeholder="friend@gmail.com",
)

subject = st.text_input(
    "Email Subject",
    value="Message from AI Assistant",
)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask me anything..."
)


# ============================================================
# RUN GRAPH
# ============================================================

if user_input:

    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.write(user_input)

    # --------------------------------------------------------
    # GRAPH INPUT
    # --------------------------------------------------------

    state = {
        "user_query": user_input,
        "recipient": recipient,
        "subject": subject,
    }

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id
        }
    }

    # --------------------------------------------------------
    # INVOKE GRAPH
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            result = graph.invoke(
                state,
                config=config,
            )

        # ----------------------------------------------------
        # HITL INTERRUPT
        # ----------------------------------------------------

        if result.get("__interrupt__"):

            interrupt_data = result["__interrupt__"][0]

            st.session_state.pending_interrupt = (
                interrupt_data
            )

            st.write(
                "I need your approval before sending the email."
            )

            st.rerun()

        # ----------------------------------------------------
        # NORMAL RESPONSE
        # ----------------------------------------------------

        elif result.get("result"):

            st.write(
                result["result"]
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result["result"],
                }
            )