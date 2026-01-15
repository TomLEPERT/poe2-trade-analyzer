import streamlit as st

def sparkline(values, color):
    st.line_chart(
        values,
        height=50,
        use_container_width=True
    )