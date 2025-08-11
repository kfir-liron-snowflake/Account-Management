import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Optional
import json

# Last updated: December 19, 2024 at 3:45 PM

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
        },
        {
            'id': str(uuid.uuid4()),
            'account_id': 'VID4A',
            'title': 'Documentation update',
            'description': 'Update project documentation',
            'estimated_hours': 5,
            'deadline': datetime.now() + timedelta(days=5),
            'status': 'pending',
            'created_at': datetime.now()
        },
        {
            'id': str(uuid.uuid4()),
            'account_id': 'FINONEX',
            'title': 'Initial setup',
            'description': 'Set up development environment',
            'estimated_hours': 12,
            'deadline': datetime.now() + timedelta(days=2),
            'status': 'pending',
            'created_at': datetime.now()
        }
    ]

# Initialize modal states
if 'show_task_modal' not in st.session_state:
    st.session_state.show_task_modal = False
if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None
if 'show_account_modal' not in st.session_state:
    st.session_state.show_account_modal = False
if 'edit_account_id' not in st.session_state:
    st.session_state.edit_account_id = None

def calculate_priority_score(task: Dict) -> int:
    """Calculate priority score based on deadline proximity and effort"""
    days_until_deadline = (task['deadline'] - datetime.now()).days
    effort_hours = task['estimated_hours']
    
    # Higher score = higher priority
    if days_until_deadline <= 0:
        return 1000 + effort_hours  # Overdue - highest priority
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
        return "🔴"
    elif score >= 800:
        return "🟠"
    elif score >= 600:
        return "🟡"
    elif score >= 400:
        return "🔵"
    else:
        return "⚪"

def get_priority_color(score: int) -> str:
    """Get background color for priority"""
    if score >= 900:
        return "#ffebee"  # Light red
    elif score >= 800:
        return "#fff3e0"  # Light orange
    elif score >= 600:
        return "#fffde7"  # Light yellow
    elif score >= 400:
        return "#e3f2fd"  # Light blue
    else:
        return "#f5f5f5"  # Light gray

def render_task_card(task: Dict, account_name: str):
    """Render a single task as a card"""
    priority_score = calculate_priority_score(task)
    priority_icon = get_priority_label(priority_score)
    priority_color = get_priority_color(priority_score)
    
    days_left = (task['deadline'] - datetime.now()).days
    
    # Task card styling
    card_style = f"""
    <div style="
        background-color: {priority_color};
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        margin: 8px;
        height: 140px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 18px;">{priority_icon}</span>
            <span style="font-size: 12px; color: #666;">{days_left}d</span>
        </div>
        <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; line-height: 1.2;">
            {task['title'][:30]}{'...' if len(task['title']) > 30 else ''}
        </div>
        <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
            {account_name}
        </div>
        <div style="font-size: 11px; color: #888; margin-bottom: 4px;">
            {task['estimated_hours']}h • {task['status'].replace('_', ' ').title()}
        </div>
        <div style="font-size: 10px; color: #aaa;">
            {task['description'][:40]}{'...' if len(task['description']) > 40 else ''}
        </div>
    </div>
    """
    
    return card_style

@st.dialog("Edit Task")
def task_edit_modal():
    """Modal for editing tasks"""
    if st.session_state.edit_task_id:
        task = next((t for t in st.session_state.tasks if t['id'] == st.session_state.edit_task_id), None)
        if task:
            with st.form("edit_task_modal_form"):
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
                    if st.form_submit_button("Update Task", use_container_width=True):
                        task_index = next(i for i, t in enumerate(st.session_state.tasks) if t['id'] == task['id'])
                        st.session_state.tasks[task_index].update({
                            'title': new_title,
                            'account_id': new_account,
                            'description': new_description,
                            'estimated_hours': new_hours,
                            'deadline': datetime.combine(new_deadline, datetime.min.time()),
                            'status': new_status
                        })
                        st.session_state.show_task_modal = False
                        st.session_state.edit_task_id = None
                        st.success("Task updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Delete Task", use_container_width=True):
                        st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                        st.session_state.show_task_modal = False
                        st.session_state.edit_task_id = None
                        st.success("Task deleted!")
                        st.rerun()
                with col3:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_task_modal = False
                        st.session_state.edit_task_id = None
                        st.rerun()

@st.dialog("Edit Account")
def account_edit_modal():
    """Modal for editing accounts"""
    if st.session_state.edit_account_id:
        account = next((acc for acc in st.session_state.accounts if acc['id'] == st.session_state.edit_account_id), None)
        if account:
            with st.form("edit_account_modal_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Account Name", value=account['name'])
                    new_stage = st.selectbox("Stage", ["Lead", "Prospect", "Customer", "Partner"], 
                                           index=["Lead", "Prospect", "Customer", "Partner"].index(account['stage']))
                with col2:
                    new_phase = st.selectbox("Phase", ["Discovery", "Qualification", "Journey", "Implementation", "Support"],
                                           index=["Discovery", "Qualification", "Journey", "Implementation", "Support"].index(account['phase']))
                
                new_tech_stack = st.multiselect("Tech Stack", 
                    ["Python", "Streamlit", "React", "Node.js", "Redis", "Docker", "PostgreSQL", "MongoDB", "AWS", "Azure"],
                    default=account['tech_stack'])
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Account", use_container_width=True):
                        account_index = next(i for i, acc in enumerate(st.session_state.accounts) if acc['id'] == account['id'])
                        st.session_state.accounts[account_index].update({
                            'name': new_name,
                            'stage': new_stage,
                            'phase': new_phase,
                            'tech_stack': new_tech_stack
                        })
                        st.session_state.show_account_modal = False
                        st.session_state.edit_account_id = None
                        st.success("Account updated!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_account_modal = False
                        st.session_state.edit_account_id = None
                        st.rerun()

def render_tasks_section():
    """Render the tasks management section with card layout"""
    st.header("📋 TASKS")
    
    # Sort tasks by priority
    sorted_tasks = sorted(st.session_state.tasks, 
                         key=lambda x: calculate_priority_score(x), 
                         reverse=True)
    
    # Display tasks in a grid layout (5 per row)
    if sorted_tasks:
        rows = [sorted_tasks[i:i+5] for i in range(0, len(sorted_tasks), 5)]
        
        for row in rows:
            cols = st.columns(5)
            for i, task in enumerate(row):
                with cols[i]:
                    # Find associated account
                    account = next((acc for acc in st.session_state.accounts if acc['id'] == task['account_id']), None)
                    account_name = account['name'] if account else 'Unknown'
                    
                    # Render task card
                    card_html = render_task_card(task, account_name)
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    # Edit button for each task
                    if st.button("✏️ Edit", key=f"edit_task_{task['id']}", use_container_width=True):
                        st.session_state.edit_task_id = task['id']
                        st.session_state.show_task_modal = True
                        st.rerun()
            
            # Fill empty columns if needed
            for i in range(len(row), 5):
                with cols[i]:
                    st.empty()
    
    # Add new task button
    if st.button("➕ ADD TASK", key="add_task_btn", use_container_width=True):
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

def render_accounts_section():
    """Render the accounts management section"""
    st.header("📊 ACCOUNTS")
    
    # Display existing accounts in a more compact format
    for account in st.session_state.accounts:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 1.5, 1.5, 2, 1])
            with col1:
                st.write(f"**{account['name']}**")
            with col2:
                st.write(f"{account['stage']}")
            with col3:
                st.write(f"{account['phase']}")
            with col4:
                st.write(f"{', '.join(account['tech_stack'])}")
            with col5:
                if st.button("✏️", key=f"edit_account_{account['id']}", help="Edit Account"):
                    st.session_state.edit_account_id = account['id']
                    st.session_state.show_account_modal = True
                    st.rerun()
            st.divider()
    
    # Add new account button
    if st.button("➕ ADD ACCOUNT", key="add_account_btn"):
        st.session_state.show_add_account = True
    
    # Add account form
    if st.session_state.get('show_add_account', False):
        with st.form("add_account_form"):
            st.subheader("Add New Account")
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Account Name")
                new_stage = st.selectbox("Stage", ["Lead", "Prospect", "Customer", "Partner"])
            with col2:
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

def main():
    """Main application"""
    st.title("📋 Account Task Management")
    
    # Sidebar for filters and stats
    with st.sidebar:
        st.header("📊 Dashboard")
        
        # Calculate comprehensive stats
        total_accounts = len(st.session_state.accounts)
        total_tasks = len(st.session_state.tasks)
        pending_tasks = len([t for t in st.session_state.tasks if t['status'] == 'pending'])
        in_progress_tasks = len([t for t in st.session_state.tasks if t['status'] == 'in_progress'])
        completed_tasks = len([t for t in st.session_state.tasks if t['status'] == 'completed'])
        overdue_tasks = len([t for t in st.session_state.tasks if (t['deadline'] - datetime.now()).days < 0])
        
        # Calculate total hours
        total_hours_all = sum(t['estimated_hours'] for t in st.session_state.tasks)
        total_hours_pending = sum(t['estimated_hours'] for t in st.session_state.tasks if t['status'] == 'pending')
        total_hours_in_progress = sum(t['estimated_hours'] for t in st.session_state.tasks if t['status'] == 'in_progress')
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Accounts", total_accounts)
            st.metric("Pending", pending_tasks)
            st.metric("In Progress", in_progress_tasks)
        with col2:
            st.metric("Total Tasks", total_tasks)
            st.metric("Completed", completed_tasks)
            st.metric("Overdue", overdue_tasks, delta=None if overdue_tasks == 0 else "!")
        
        st.divider()
        
        # Hours metrics
        st.subheader("⏱️ Hours Summary")
        st.metric("Total Hours", f"{total_hours_all}h")
        st.metric("Pending Hours", f"{total_hours_pending}h")
        st.metric("Active Hours", f"{total_hours_in_progress}h")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        account_filter = st.multiselect("Filter by Account", 
                                      options=[acc['id'] for acc in st.session_state.accounts])
        status_filter = st.multiselect("Filter by Status", 
                                     options=["pending", "in_progress", "completed", "on_hold"])
        
        # Apply filters (this would be used in the main display logic)
        if account_filter or status_filter:
            filtered_tasks = st.session_state.tasks
            if account_filter:
                filtered_tasks = [t for t in filtered_tasks if t['account_id'] in account_filter]
            if status_filter:
                filtered_tasks = [t for t in filtered_tasks if t['status'] in status_filter]
            st.session_state.filtered_tasks = filtered_tasks
        else:
            st.session_state.filtered_tasks = st.session_state.tasks
    
    # Main content - Tasks on top (larger section), Accounts on bottom
    
    # Tasks section (takes up more space)
    with st.container():
        render_tasks_section()
    
    st.divider()
    
    # Accounts section (smaller, at bottom)
    with st.container():
        render_accounts_section()
    
    # Handle modals
    if st.session_state.show_task_modal:
        task_edit_modal()
    
    if st.session_state.show_account_modal:
        account_edit_modal()

if __name__ == "__main__":
    main()