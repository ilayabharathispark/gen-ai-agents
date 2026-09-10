import streamlit as st

from langgraph.types import Command

from agent import graph


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Story Email Agent",
    page_icon="📖",
    layout="centered"
)


# ============================================================
# TITLE
# ============================================================

st.title("📖 Story Email Agent")

st.write(
    "Generate a story with an LLM and send it through Gmail "
    "after Human-in-the-Loop approval."
)


# ============================================================
# THREAD ID
# ============================================================

# This identifies this LangGraph execution.
#
# IMPORTANT:
# The same thread_id MUST be used when resuming
# the interrupted graph.

THREAD_ID = "story-001"


config = {
    "configurable": {
        "thread_id": THREAD_ID
    }
}


# ============================================================
# STREAMLIT SESSION STATE
# ============================================================

if "started" not in st.session_state:

    st.session_state.started = False


if "completed" not in st.session_state:

    st.session_state.completed = False


if "result" not in st.session_state:

    st.session_state.result = None


# ============================================================
# STEP 1 - USER STORY REQUEST
# ============================================================

if not st.session_state.started:

    st.subheader("1️⃣ Tell me what story you want")

    user_query = st.text_area(
        "Story request",

        placeholder=(
            "Example:\n"
            "Write a funny short story about a software "
            "engineer who accidentally travels back to "
            "the dinosaur era."
        ),

        height=150
    )


    # ========================================================
    # EMAIL DETAILS
    # ========================================================

    st.subheader("2️⃣ Email details")

    recipient = st.text_input(
        "Friend's email",

        placeholder="friend@gmail.com"
    )


    subject = st.text_input(
        "Email subject",

        value="A Story For You"
    )


    # ========================================================
    # GENERATE STORY
    # ========================================================

    if st.button(
        "✨ Generate Story",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not user_query:

            st.error(
                "Please describe the story you want."
            )

        elif not recipient:

            st.error(
                "Please enter your friend's email."
            )

        else:

            # ------------------------------------------------
            # START LANGGRAPH
            # ------------------------------------------------

            with st.spinner(
                "Writing your story..."
            ):

                result = graph.invoke(
                    {
                        "user_query": user_query,

                        "recipient": recipient,

                        "subject": subject
                    },

                    config=config
                )


            # ------------------------------------------------
            # SAVE RESULT
            # ------------------------------------------------

            st.session_state.result = result

            st.session_state.started = True

            st.rerun()


# ============================================================
# STEP 3 - HITL
# ============================================================

if st.session_state.started:

    result = st.session_state.result


    # --------------------------------------------------------
    # GET INTERRUPT
    # --------------------------------------------------------

    interrupts = result.get(
        "__interrupt__"
    )


    if interrupts:

        # ----------------------------------------------------
        # GET DATA FROM interrupt()
        # ----------------------------------------------------

        interrupt_data = interrupts[0].value


        st.divider()

        st.subheader(
            "3️⃣ 🛑 Human Approval Required"
        )


        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        st.warning(
            interrupt_data["message"]
        )


        # ----------------------------------------------------
        # EMAIL INFORMATION
        # ----------------------------------------------------

        st.markdown("### 📧 Email Details")


        st.write(
            f"**To:** {interrupt_data['recipient']}"
        )


        st.write(
            f"**Subject:** {interrupt_data['subject']}"
        )


        # ----------------------------------------------------
        # STORY
        # ----------------------------------------------------

        st.markdown("### 📖 Generated Story")


        st.text_area(
            "Review the story before sending",

            value=interrupt_data["story"],

            height=350,

            disabled=True
        )


        st.divider()


        # ----------------------------------------------------
        # APPROVAL QUESTION
        # ----------------------------------------------------

        st.subheader(
            "Do you want to send this email?"
        )


        col1, col2 = st.columns(2)


        # ====================================================
        # APPROVE
        # ====================================================

        with col1:

            if st.button(
                "✅ Approve & Send",

                type="primary",

                use_container_width=True
            ):

                # --------------------------------------------
                # RESUME LANGGRAPH
                # --------------------------------------------

                with st.spinner(
                    "Sending email..."
                ):

                    result = graph.invoke(

                        Command(
                            resume=True
                        ),

                        config=config
                    )


                st.session_state.result = result

                st.session_state.completed = True

                st.rerun()


        # ====================================================
        # REJECT
        # ====================================================

        with col2:

            if st.button(
                "❌ Reject",

                use_container_width=True
            ):

                # --------------------------------------------
                # RESUME LANGGRAPH
                # --------------------------------------------

                result = graph.invoke(

                    Command(
                        resume=False
                    ),

                    config=config
                )


                st.session_state.result = result

                st.session_state.completed = True

                st.rerun()


# ============================================================
# STEP 4 - COMPLETED
# ============================================================

if st.session_state.completed:

    st.divider()


    st.success(
        "🎉 Workflow completed."
    )


    st.write(
        "The Human-in-the-Loop decision has been processed."
    )


    # --------------------------------------------------------
    # NEW STORY
    # --------------------------------------------------------

    if st.button(
        "🔄 Create Another Story",

        use_container_width=True
    ):

        st.session_state.started = False

        st.session_state.completed = False

        st.session_state.result = None

        st.rerun()