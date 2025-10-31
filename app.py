import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF

 
# LOAD ENV VARIABLES
 
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

 
# INITIALIZE GEMINI MODEL
 
model = genai.GenerativeModel("gemini-2.5-flash")


# HELPER FUNCTIONS

def generate_prompt(course_title, course_description):
    try:
        prompt = f"""
        Generate a detailed course outline for:
        Title: {course_title}
        Description: {course_description}
        Include 5-7 modules with subtopics.
        """
        response = model.generate_content(prompt)
        return response.text if hasattr(response, "text") else "No content generated."
    except Exception as e:
        return f"Error generating prompt: {str(e)}"

def generate_course_outline(prompt):
    try:
        outline_prompt = f"Convert the following into a structured JSON-style course outline:\n\n{prompt}"
        response = model.generate_content(outline_prompt)
        return response.text if hasattr(response, "text") else "No outline generated."
    except Exception as e:
        return f"Error generating course outline: {str(e)}"

def generate_full_course(course_outline):
    try:
        course_prompt = f"""
        Based on this outline, generate detailed, high-quality content for each module and subtopic.
        {course_outline}
        Format everything in markdown with clear headings and subheadings.
        """
        response = model.generate_content(course_prompt)
        return response.text if hasattr(response, "text") else "No course generated."
    except Exception as e:
        return f"Error generating course: {str(e)}"

def save_as_pdf(text, filename="Course_Content.pdf"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in text.split("\n"):
            pdf.multi_cell(0, 10, line)
        pdf.output(filename)
        return filename
    except Exception as e:
        st.error(f"Failed to generate PDF: {e}")
        return None

 
# STREAMLIT UI CONFIG
 
st.set_page_config(page_title="Course Creator ", layout="wide")
st.title("📘 Automated Course Content Generator")
st.markdown("Create detailed course outlines and content !")

 
# APP STATE
 
if "outline" not in st.session_state:
    st.session_state.outline = None
if "course" not in st.session_state:
    st.session_state.course = None

 
# LAYOUT SPLIT
 
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 Course Setup")
    course_title = st.text_input("Course Title", "")
    course_description = st.text_area("Course Description", "")

    if st.button("🚀 Generate Outline"):
        with st.spinner("Generating outline..."):
            prompt = generate_prompt(course_title, course_description)
            outline = generate_course_outline(prompt)
            st.session_state.outline = outline
            st.session_state.course = None

with col2:
    st.subheader("🧠 Output")
    if st.session_state.outline and not st.session_state.course:
        st.markdown("### 📚 Generated Course Outline")
        st.markdown(st.session_state.outline)

        st.write("Would you like to modify the outline or generate the full course?")
        colA, colB = st.columns(2)
        with colA:
            if st.button("✏️ Modify Outline"):
                new_outline = st.text_area("Edit your outline here:", st.session_state.outline, height=300)
                if st.button("✅ Save & Update"):
                    st.session_state.outline = new_outline
                    st.success("Outline updated successfully!")

        with colB:
            if st.button("🧾 Generate Full Course"):
                with st.spinner("Generating complete course..."):
                    course = generate_full_course(st.session_state.outline)
                    st.session_state.course = course

    elif st.session_state.course:
        st.markdown("### 🎓 Full Course Content")
        st.markdown(st.session_state.course)

        # Download PDF
        pdf_file = save_as_pdf(st.session_state.course)
        if pdf_file:
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="⬇️ Download Course as PDF",
                    data=f,
                    file_name=pdf_file,
                    mime="application/pdf",
                )

# Footer
st.markdown("---")
st.markdown("All Hail the Hitler")
