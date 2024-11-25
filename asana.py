import requests
from datetime import datetime, timedelta

ASANA_TOKEN = "2/1208779539612523/1208824174176866:99d6decca6ce6ef503bf0c5bca554e1a"
ASANA_PROJECT_ID = "1208824149247558"
ASANA_BASE_URL = "https://app.asana.com/api/1.0"

headers = {"Authorization": f"Bearer {ASANA_TOKEN}"}

# Function to calculate the due date based on priority
def calculate_due_date(priority):
    print(f"Calculating due date for priority: {priority}")
    priority = priority.strip().lower()  # Normalize to lowercase and strip any extra spaces
    if priority == 'low':
        return datetime.now() + timedelta(days=14)
    elif priority == 'mid':
        return datetime.now() + timedelta(days=7)
    elif priority == 'high':
        return datetime.now() + timedelta(days=2)
    else:
        print(f"Unknown priority '{priority}', defaulting to 14 days.")
        return datetime.now() + timedelta(days=14)

# Function to update task due date in Asana
def set_due_date(task_id, priority):
    try:
        due_date = calculate_due_date(priority).strftime('%Y-%m-%d')
        data = {"data": {"due_on": due_date}}
        response = requests.put(f"{ASANA_BASE_URL}/tasks/{task_id}", headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Due date for task {task_id} set to {due_date}")
        else:
            print(f"Failed to set due date for task {task_id}: {response.status_code}, {response.json()}")
    except Exception as e:
        print(f"Error while setting due date for task {task_id}: {str(e)}")

# Function to fetch tasks and apply due dates
def apply_deadlines():
    try:
        # Fetch all tasks from the project
        response = requests.get(f"{ASANA_BASE_URL}/projects/{ASANA_PROJECT_ID}/tasks", headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch tasks: {response.status_code}, {response.json()}")
            return
        
        tasks = response.json().get('data', [])
        if not tasks:
            print("No tasks found in the project.")
            return
        
        # Process each task
        for task in tasks:
            print(f"Processing task: {task['name']} (ID: {task['gid']})")
            
            # Fetch detailed task information to access custom fields
            task_details_response = requests.get(f"{ASANA_BASE_URL}/tasks/{task['gid']}", headers=headers)
            if task_details_response.status_code != 200:
                print(f"Failed to fetch details for task {task['gid']}: {task_details_response.status_code}")
                continue
            
            task_details = task_details_response.json().get('data', {})
            
            # Get the priority from custom fields
            custom_fields = task_details.get('custom_fields', [])
            priority = "low"  # Default to low if no priority is set
            for field in custom_fields:
                if field.get('name', '').strip().lower() == 'priority':
                    priority = field.get('display_value', 'low').strip().lower()
                    print(f"Found priority for task {task['gid']}: {priority}")  # Log priority value
                    break
            
            print(f"Priority for task {task['name']}: {priority}")
            
            # Set the due date based on priority
            set_due_date(task['gid'], priority)
    
    except Exception as e:
        print(f"Error in apply_deadlines: {str(e)}")

# Main function
if __name__ == "__main__":
    print("Starting the script...")
    apply_deadlines()
