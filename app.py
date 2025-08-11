import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
import json

# Configure the page
st.set_page_config(
    page_title="Account Task Management",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for data persistence
if 'accounts' not in st.session_state:
    st.session_state.accounts = [
        {
            'id': 'VID4A',
            'name': 'VID4A',
            'stage': 'Customer',
            'phase': 'Journey',
            'tech_stack': ['Python', 'Streamlit']
        },
        {
            'id': 'REDIS',
            'name': 'REDIS',
            'stage': 'Prospect',
            'phase': 'Discovery',
            'tech_stack': ['Redis', 'Docker']
        },
        {
            'id': 'FINONEX',
            'name': 'FINONEX',
            'stage': 'Lead',
            'phase': 'Qualification',
            'tech_stack': ['React', 'Node.js']
        }
    ]

if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {
            'id': str(uuid.uuid4()),
            'account_id': 'VID4A',
            'title': 'Customer check-in task',
            'description': 'Need to check-in with customer, not scheduled',
            'priority_level': 'check-in',
            'estimated_hours': 2,
            'deadline': datetime.now() + timedelta(days=7),
            'status': 'pending',
            'created_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'account_id': 'REDIS',
            'title': 'Project implementation',
            'description': 'Project in 2 months, scheduled',
            'priority_level': 'task with deadline',
            'estimated_hours': 80,
            'deadline': datetime.now() + timedelta(days=60),
            'status': 'in_progress',
            'created_at': datetime.now()
        }
    ]

def calculate_priority_score(task: Dict) -> int:
    """Calculate priority score based on deadline proximity and effort"""
    days_until_deadline = (task['deadline'] - datetime.now()).days
    effort_hours = task['estimated_hours']
    
    # Higher score = higher priority
    if days_until_deadline <= 0:
        return 1000  # Overdue - highest priority
    elif days_until_deadline <= 3:
        return 900 - effort_hours  # Urgent
    elif days_until_deadline <= 7:
        return 800 - effort_hours  # High priority
    elif days_until_deadline <= 30:
        return 600 - effort_hours  # Medium priority
    else:
        return 400 - effort_hours  # Low priority

def get_priority_label(score: int) -> str:
    """Convert priority score to human readable label"""
    if score >= 900:
        return "🔴 Critical"
    elif score >= 800:
        return "🟠 Urgent"
    elif score >= 600:
        return "🟡 High"
    elif score >= 400:
        return "🔵 Medium"
    else:
        return "⚪ Low"

def render_accounts_section():
    """Render the accounts management section"""
    st.header("📊 ACCOUNTS")
    
    # Display existing accounts
    for account in st.session_state.accounts:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
            with col1:
                st.write(f"**{account['name']}**")
            with col2:
                st.write(f"Stage: {account['stage']}")
            with col3:
                st.write(f"Phase: {account['phase']}")
            with col4:
                st.write(f"Tech: {', '.join(account['tech_stack'])}")
            st.divider()
    
    # Add new account button
    if st.button("➕ ADD ACCOUNT", key="add_account_btn"):
        st.session_state.show_add_account = True
    
    # Add account form
    if st.session_state.get('show_add_account', False):
        with st.form("add_account_form"):
            st.subheader("Add New Account")
            new_name = st.text_input("Account Name")
            new_stage = st.selectbox("Stage", ["Lead", "Prospect", "Customer", "Partner"])
            new_phase = st.selectbox("Phase", ["Discovery", "Qualification", "Journey", "Implementation", "Support"])
            new_tech_stack = st.multiselect("Tech Stack", 
                ["Python", "Streamlit", "React", "Node.js", "Redis", "Docker", "PostgreSQL", "MongoDB", "AWS", "Azure"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Account"):
                    if new_name:
                        new_account = {
                            'id': new_name.upper().replace(' ', '_'),
                            'name': new_name,
                            'stage': new_stage,
                            'phase': new_phase,
                            'tech_stack': new_tech_stack
                        }
                        st.session_state.accounts.append(new_account)
                        st.session_state.show_add_account = False
                        st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_account = False
                    st.rerun()

def render_tasks_section():
    """Render the tasks management section"""
    st.header("📋 TASKS")
    
    # Sort tasks by priority
    sorted_tasks = sorted(st.session_state.tasks, 
                         key=lambda x: calculate_priority_score(x), 
                         reverse=True)
    
    # Display tasks
    for i, task in enumerate(sorted_tasks):
        priority_score = calculate_priority_score(task)
        priority_label = get_priority_label(priority_score)
        
        # Find associated account
        account = next((acc for acc in st.session_state.accounts if acc['id'] == task['account_id']), None)
        account_name = account['name'] if account else 'Unknown'
        
        # Task container with priority color
        with st.container():
            # Task header
            col1, col2, col3 = st.columns([6, 2, 1])
            with col1:
                if st.button(f"📌 {task['title']} ({account_name})", 
                           key=f"task_{task['id']}", 
                           use_container_width=True):
                    # Toggle task expansion
                    task_key = f"expand_task_{task['id']}"
                    st.session_state[task_key] = not st.session_state.get(task_key, False)
                    st.rerun()
            with col2:
                st.write(f"{priority_label}")
            with col3:
                days_left = (task['deadline'] - datetime.now()).days
                st.write(f"{days_left}d")
            
            # Expandable task details
            if st.session_state.get(f"expand_task_{task['id']}", False):
                with st.expander("Task Details", expanded=True):
                    with st.form(f"edit_task_{task['id']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_title = st.text_input("Title", value=task['title'])
                            new_account = st.selectbox("Account", 
                                                     options=[acc['id'] for acc in st.session_state.accounts],
                                                     index=[acc['id'] for acc in st.session_state.accounts].index(task['account_id']))
                            new_status = st.selectbox("Status", 
                                                    ["pending", "in_progress", "completed", "on_hold"],
                                                    index=["pending", "in_progress", "completed", "on_hold"].index(task['status']))
                        with col2:
                            new_hours = st.number_input("Estimated Hours", value=task['estimated_hours'], min_value=1)
                            new_deadline = st.date_input("Deadline", value=task['deadline'].date())
                        
                        new_description = st.text_area("Description", value=task['description'])
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.form_submit_button("Update Task"):
                                # Update task
                                task_index = next(i for i, t in enumerate(st.session_state.tasks) if t['id'] == task['id'])
                                st.session_state.tasks[task_index].update({
                                    'title': new_title,
                                    'account_id': new_account,
                                    'description': new_description,
                                    'estimated_hours': new_hours,
                                    'deadline': datetime.combine(new_deadline, datetime.min.time()),
                                    'status': new_status
                                })
                                st.success("Task updated!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Delete Task", type="secondary"):
                                st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                                st.success("Task deleted!")
                                st.rerun()
                        with col3:
                            if st.form_submit_button("Close", type="secondary"):
                                st.session_state[f"expand_task_{task['id']}"] = False
                                st.rerun()
            
            st.divider()
    
    # Add new task button
    if st.button("➕ ADD TASK", key="add_task_btn"):
        st.session_state.show_add_task = True
    
    # Add task form
    if st.session_state.get('show_add_task', False):
        with st.form("add_task_form"):
            st.subheader("Add New Task")
            col1, col2 = st.columns(2)
            with col1:
                task_title = st.text_input("Task Title")
                task_account = st.selectbox("Account", options=[acc['id'] for acc in st.session_state.accounts])
                task_hours = st.number_input("Estimated Hours", value=1, min_value=1)
            with col2:
                task_deadline = st.date_input("Deadline", value=datetime.now().date() + timedelta(days=7))
                task_status = st.selectbox("Status", ["pending", "in_progress", "completed", "on_hold"])
            
            task_description = st.text_area("Description")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Add Task"):
                    if task_title:
                        new_task = {
                            'id': str(uuid.uuid4()),
                            'account_id': task_account,
                            'title': task_title,
                            'description': task_description,
                            'estimated_hours': task_hours,
                            'deadline': datetime.combine(task_deadline, datetime.min.time()),
                            'status': task_status,
                            'created_at': datetime.now()
                        }
                        st.session_state.tasks.append(new_task)
                        st.session_state.show_add_task = False
                        st.success("Task added!")
                        st.rerun()
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.show_add_task = False
                    st.rerun()

def main():
    """Main application"""
    st.title("📋 Account Task Management")
    
    # Sidebar for filters and stats
    with st.sidebar:
        st.header("📊 Dashboard")
        
        # Quick stats
        total_accounts = len(st.session_state.accounts)
        total_tasks = len(st.session_state.tasks)
        pending_tasks = len([t for t in st.session_state.tasks if t['status'] == 'pending'])
        overdue_tasks = len([t for t in st.session_state.tasks if (t['deadline'] - datetime.now()).days < 0])
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accounts", total_accounts)
            st.metric("Pending", pending_tasks)
        with col2:
            st.metric("Total Tasks", total_tasks)
            st.metric("Overdue", overdue_tasks, delta=None if overdue_tasks == 0 else "!")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        account_filter = st.multiselect("Filter by Account", 
                                      options=[acc['id'] for acc in st.session_state.accounts])
        status_filter = st.multiselect("Filter by Status", 
                                     options=["pending", "in_progress", "completed", "on_hold"])
        
        if account_filter or status_filter:
            filtered_tasks = st.session_state.tasks
            if account_filter:
                filtered_tasks = [t for t in filtered_tasks if t['account_id'] in account_filter]
            if status_filter:
                filtered_tasks = [t for t in filtered_tasks if t['status'] in status_filter]
            st.session_state.filtered_tasks = filtered_tasks
        else:
            st.session_state.filtered_tasks = st.session_state.tasks
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_accounts_section()
    
    with col2:
        render_tasks_section()

if __name__ == "__main__":
    main()