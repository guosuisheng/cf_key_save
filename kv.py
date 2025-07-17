#!/usr/bin/python3
import tkinter as tk
from tkinter import messagebox, scrolledtext, Toplevel, filedialog
import requests
import json
import os # For file operations

# --- API Endpoints and Authentication ---
BASE_URL=os.environ.get('KV_BASE_URL')
AUTH_TOKEN=os.environ.get('KV_AUTH_TOKEN')


LOCAL_SAVE_DIR = "~/source/saved_values" # Directory to save local files


# Ensure the local save directory exists
os.makedirs(LOCAL_SAVE_DIR, exist_ok=True)

# --- Function to fetch the list of keys ---
def fetch_remove_list():
    url = f"{BASE_URL}/list"
    headers = {"Content-Type": "application/json"}
    data = {"auth": AUTH_TOKEN}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        result = response.json()
        if result.get("success"):
            return result.get("keys", [])
        else:
            messagebox.showerror("API Error", f"Failed to fetch list: {result.get('error', 'Unknown error')}")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not connect to API: {e}")
        return []
    except json.JSONDecodeError:
        messagebox.showerror("API Error", "Invalid JSON response from server.")
        return []

# --- Function to get a value by key ---
def get_value_by_key(key):
    url = f"{BASE_URL}/get"
    headers = {"Content-Type": "application/json"}
    data = {"key": key, "auth": AUTH_TOKEN}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if "value" in result:
            return result["value"]
        else:
            messagebox.showerror("API Error", f"Failed to get value for key '{key}': {result.get('error', 'Unknown error')}")
            return None
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not connect to API: {e}")
        return None
    except json.JSONDecodeError:
        messagebox.showerror("API Error", "Invalid JSON response from server.")
        return None

# --- Function to send a new key-value pair to the service (used for new and updates) ---
def send_key_value(key, value):
    url = f"{BASE_URL}/receive" # This endpoint is used for both new and updates in your provided API
    headers = {"Content-Type": "application/json"}
    data = {"key": key, "value": value, "auth": AUTH_TOKEN}
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return True
        else:
            messagebox.showerror("API Error", f"Failed to save/update key-value: {result.get('error', 'Unknown error')}")
            return False
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Could not connect to API to save/update: {e}")
        return False
    except json.JSONDecodeError:
        messagebox.showerror("API Error", "Invalid JSON response from server when saving/updating.")
        return False

# --- Tkinter GUI Application ---
class KeyValueApp:
    def __init__(self, master):
        self.master = master
        master.title("Key-Value Viewer")
        master.geometry("800x600")

        # --- Frames ---
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.list_frame = tk.LabelFrame(self.main_frame, text="Keys")
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.value_frame = tk.LabelFrame(self.main_frame, text="Value")
        self.value_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- Key Listbox ---
        self.key_listbox = tk.Listbox(self.list_frame, selectmode=tk.SINGLE)
        self.key_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.key_listbox.bind("<<ListboxSelect>>", self.on_key_select)
        self.key_listbox.bind("<Double-Button-1>", self.on_key_double_click)  # Add double-click binding

        # Add a scrollbar to the listbox
        self.list_scrollbar = tk.Scrollbar(self.key_listbox, orient="vertical", command=self.key_listbox.yview)
        self.key_listbox.config(yscrollcommand=self.list_scrollbar.set)
        self.list_scrollbar.pack(side="right", fill="y")

        # --- Value Text Area ---
        self.value_text = scrolledtext.ScrolledText(self.value_frame, wrap=tk.WORD, state=tk.NORMAL, width=60, height=20)
        self.value_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Right-click context menu for value_text ---
        self.context_menu = tk.Menu(self.value_text, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.value_text.bind("<Button-3>", self.show_context_menu) # Bind right-click

        # --- Buttons ---
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.refresh_button = tk.Button(self.button_frame, text="Refresh Keys", command=self.load_keys)
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        self.new_button = tk.Button(self.button_frame, text="New Key-Value", command=self.open_new_window)
        self.new_button.pack(side=tk.LEFT, padx=5)

        self.update_button = tk.Button(self.button_frame, text="Update Selected Value", command=self.update_selected_value)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.copy_value_button = tk.Button(self.button_frame, text="Copy Value", command=self.copy_current_value)
        self.copy_value_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(self.button_frame, text="Clear Value", command=self.clear_value_text)
        self.clear_button.pack(side=tk.RIGHT, padx=5)

        # --- Initial Load ---
        self.load_keys()

    def load_keys(self):
        self.key_listbox.delete(0, tk.END)  # Clear existing keys
        self.clear_value_text()
        keys = fetch_remove_list()
        if keys:
            for key in keys:
                self.key_listbox.insert(tk.END, key)
        else:
            self.key_listbox.insert(tk.END, "No keys found or error fetching.")

    def on_key_select(self, event):
        selected_indices = self.key_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_key = self.key_listbox.get(index)
            self.display_value(selected_key)

    def on_key_double_click(self, event):
        """Handle double-click on a key to copy its value to clipboard"""
        selected_indices = self.key_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            selected_key = self.key_listbox.get(index)
            
            # Get the value for the selected key
            value = get_value_by_key(selected_key)
            if value is not None:
                # Copy to clipboard
                self.master.clipboard_clear()
                self.master.clipboard_append(value)
                messagebox.showinfo("Copied", f"Value for key '{selected_key}' copied to clipboard!")
            else:
                messagebox.showerror("Error", f"Could not retrieve value for key '{selected_key}'")

    def display_value(self, key):
        self.clear_value_text()
        value = get_value_by_key(key)
        if value is not None:
            #self.value_text.insert(tk.END, f"Key: {key}\n\nValue:\n{value}")
            self.value_text.insert(tk.END, value)
            self.master.title(f"Key-Value Viewer - {key}")  # Update title with selected key
        else:
            self.value_text.insert(tk.END, f"Could not retrieve value for key: {key}")

    def clear_value_text(self):
        self.value_text.delete(1.0, tk.END)  # Clear all text
        self.master.title(f"Key-Value Viewer")  # Update title with selected key

    def copy_current_value(self):
        """Copy the currently displayed value to clipboard"""
        current_value = self.value_text.get("1.0", tk.END).strip()
        if current_value:
            self.master.clipboard_clear()
            self.master.clipboard_append(current_value)
            messagebox.showinfo("Copied", "Current value copied to clipboard!")
        else:
            messagebox.showwarning("No Value", "No value to copy. Please select a key first.")

    def open_new_window(self):
        new_window = Toplevel(self.master)
        new_window.title("New Key-Value Pair")
        new_window.geometry("400x300")
        new_window.transient(self.master) # Make it a transient window
        new_window.grab_set() # Make it modal

        # Key Input
        key_label = tk.Label(new_window, text="Key:")
        key_label.pack(pady=(10, 0))
        self.new_key_entry = tk.Entry(new_window, width=50)
        self.new_key_entry.pack(pady=5)

        # Value Input
        value_label = tk.Label(new_window, text="Value:")
        value_label.pack(pady=(10, 0))
        self.new_value_text = scrolledtext.ScrolledText(new_window, wrap=tk.WORD, width=40, height=8)
        self.new_value_text.pack(pady=5)

        # Save Button
        save_button = tk.Button(new_window, text="Save", command=lambda: self.save_new_key_value(new_window))
        save_button.pack(pady=10)

        new_window.protocol("WM_DELETE_WINDOW", lambda: self.on_new_window_close(new_window)) # Handle close button

    def save_new_key_value(self, window):
        key = self.new_key_entry.get().strip()
        value = self.new_value_text.get("1.0", tk.END).strip() # Get all text from scrolledtext

        if not key:
            messagebox.showwarning("Input Error", "Key cannot be empty.")
            return
        if not value:
            messagebox.showwarning("Input Error", "Value cannot be empty.")
            return

        # 1. Save to local file
        try:
            filename = os.path.join(LOCAL_SAVE_DIR, f"{key}.txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(value)
            messagebox.showinfo("Local Save", f"Key-value saved locally as '{filename}'")
        except IOError as e:
            messagebox.showerror("Local Save Error", f"Failed to save locally: {e}")
            return # Stop if local save fails

        # 2. Send to remote service
        if send_key_value(key, value):
            messagebox.showinfo("Remote Save", "Key-value sent to remote service successfully!")
            self.load_keys() # Refresh the main list to show the new key
            window.destroy() # Close the pop-up window
        else:
            # Error message is already shown by send_key_value
            pass # Keep the window open if remote save fails

    def on_new_window_close(self, window):
        window.grab_release() # Release the grab
        window.destroy()

    def update_selected_value(self):
        selected_indices = self.key_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Key Selected", "Please select a key from the list to update.")
            return

        index = selected_indices[0]
        selected_key = self.key_listbox.get(index)
        new_value = self.value_text.get("1.0", tk.END).strip()

        if not new_value:
            messagebox.showwarning("No Value", "The value field is empty. Please enter a value to update.")
            return

        # Confirm with the user before updating
        confirm = messagebox.askyesno(
            "Confirm Update",
            f"Are you sure you want to update the value for key '{selected_key}'?\n\nNew Value (first 50 chars):\n{new_value[:50]}{'...' if len(new_value) > 50 else ''}"
        )
        if not confirm:
            return

        if send_key_value(selected_key, new_value):
            messagebox.showinfo("Update Success", f"Value for key '{selected_key}' updated successfully on remote service!")
            self.display_value(selected_key) # Re-fetch and display
        else:
            pass # Error already shown by send_key_value

    # --- New methods for context menu ---
    def show_context_menu(self, event):
        # Display the context menu at the mouse pointer's position
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            # make sure to release the grab (Tk 8.0a1)
            self.context_menu.grab_release()

    def copy_selected_text(self):
        try:
            selected_text = self.value_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.master.clipboard_clear() # Clear existing clipboard content
            self.master.clipboard_append(selected_text) # Append the selected text
        except tk.TclError:
            # No text selected, or selection is empty
            messagebox.showinfo("Copy", "No text selected to copy.")


# --- Main application execution ---
if __name__ == "__main__":
    root = tk.Tk()
    app = KeyValueApp(root)
    root.mainloop()
