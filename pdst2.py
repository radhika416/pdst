import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk

class ListNode:
    def __init__(self, name=None, contact=None):
        self.name = name
        self.contact = contact
        self.next = None

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.deleted_stack = []
        self.sorted_contacts = []

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

    def delete(self, word):
        def _delete_helper(node, word, depth):
            if depth == len(word):
                if not node.is_end_of_word:
                    return False
                node.is_end_of_word = False
                return len(node.children) == 0
            
            char = word[depth]
            if char not in node.children:
                return False
            
            should_delete_current_node = _delete_helper(node.children[char], word, depth + 1)
            
            if should_delete_current_node:
                del node.children[char]
                return len(node.children) == 0
            return False
        
        if self.search(word):
            self.deleted_stack.append(word)
            _delete_helper(self.root, word, 0)

    def undo(self):
        if self.deleted_stack:
            word_to_undo = self.deleted_stack.pop()
            self.insert(word_to_undo)

    def sort_contacts(self):
        self.sorted_contacts = []
        self._traverse_and_collect(self.root, '')

    def _traverse_and_collect(self, node, prefix):
        if node.is_end_of_word:
            self.sorted_contacts.append(prefix)
        for char, child_node in sorted(node.children.items()):  # Sort alphabetically
            self._traverse_and_collect(child_node, prefix + char)

    def get_sorted_contacts(self):
        return self.sorted_contacts

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Manager")
        self.geometry("400x300")

        # Initialize the Trie
        self.trie = Trie()
        self.contacts_by_number = {}
        self.emergency_contact = None

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Create labels and buttons
        self.label = tk.Label(self, text="Contact Manager", font=("Arial", 18))
        self.label.pack(pady=10)

        self.menu = tk.Menu(self)
        self.menu.add_command(label="Create contact", command=self.create_contact)
        self.menu.add_command(label="Update contact", command=self.update_contact)
        self.menu.add_command(label="Delete contact", command=self.delete_contact)
        self.menu.add_command(label="Sort by name", command=self.sort_contacts)
        self.menu.add_command(label="Search by name", command=self.search_by_name)
        self.menu.add_command(label="Search by number", command=self.search_by_number)
        self.menu.add_command(label="Undo", command=self.undo)
        self.menu.add_command(label="Emergency Contact", command=self.show_emergency_contact)
        self.menu.add_command(label="Exit", command=self.quit)
        self.config(menu=self.menu)

        # Contacts Treeview
        self.contacts_tree = ttk.Treeview(self, columns=("Name", "Contact"), show="headings")
        self.contacts_tree.heading("Name", text="Name")
        self.contacts_tree.heading("Contact", text="Contact")
        self.contacts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_contact(self):
        name = simpledialog.askstring("Create Contact", "Enter name:")
        contact = simpledialog.askstring("Create Contact", "Enter contact:")
        
        # Validate contact number
        if contact and contact.isdigit() and len(contact) == 10:
            if name:
                if contact not in self.contacts_by_number.values():
                    self.trie.insert(name)
                    self.contacts_by_number[name] = contact
                    self.update_contacts_tree()
                else:
                    messagebox.showwarning("Duplicate Contact", "Contact number already exists.")
        else:
            messagebox.showwarning("Invalid Contact", "Contact number must contain only digits and have a length of 10.")

    def update_contact(self):
        name_to_update = simpledialog.askstring("Update Contact", "Enter name to update:")
        if name_to_update:
            new_contact = simpledialog.askstring("Update Contact", "Enter new contact:")
            if new_contact and new_contact.isdigit() and len(new_contact) == 10:
                if name_to_update in self.contacts_by_number:
                    self.contacts_by_number[name_to_update] = new_contact
                    self.update_contacts_tree()
                else:
                    messagebox.showwarning("Contact not found", "Contact not found for updating.")
            else:
                messagebox.showwarning("Invalid Contact", "Contact number must contain only digits and have a length of 10.")

    def delete_contact(self):
        name_to_delete = simpledialog.askstring("Delete Contact", "Enter name to delete:")
        if name_to_delete:
            if name_to_delete in self.contacts_by_number:
                self.trie.delete(name_to_delete)
                messagebox.showinfo("Delete Contact", f"Contact '{name_to_delete}' deleted successfully.")
                # Update the tree after deleting the contact
                self.update_contacts_tree()
            else:
                messagebox.showwarning("Contact not found", "Contact not found for deletion.")

    def sort_contacts(self):
        self.contacts_tree.delete(*self.contacts_tree.get_children())  # Clear the tree
        self.trie.sort_contacts()
        sorted_contacts = self.trie.get_sorted_contacts()
        for name in sorted_contacts:
            contact = self.contacts_by_number.get(name, "")
            self.contacts_tree.insert("", "end", values=(name, contact))

    def search_by_name(self):
        name_to_search = simpledialog.askstring("Search by Name", "Enter name to search:")
        if name_to_search:
            if name_to_search in self.contacts_by_number:
                contact_number = self.contacts_by_number[name_to_search]
                messagebox.showinfo("Search Result", f"Contact found: {name_to_search} ({contact_number})")
                self.emergency_contact = (name_to_search, contact_number)
            else:
                messagebox.showinfo("Search Result", f"No contact found for {name_to_search}.")
                self.emergency_contact = None

    def search_by_number(self):
        contact_to_search = simpledialog.askstring("Search by Number", "Enter contact to search:")
        if contact_to_search:
            name = next((name for name, contact in self.contacts_by_number.items() if contact == contact_to_search), None)
            if name:
                messagebox.showinfo("Search Result", f"Contact found: {name}")
            else:
                messagebox.showinfo("Search Result", f"No contact found for contact number {contact_to_search}.")

    def undo(self):
        self.trie.undo()
        messagebox.showinfo("Undo", "Undo successful.")

    def show_emergency_contact(self):
        if self.emergency_contact:
            name, contact = self.emergency_contact
            if contact:
                messagebox.showinfo("Emergency Contact", f"Emergency contact: {name} ({contact})")
            else:
                messagebox.showinfo("Emergency Contact", f"Emergency contact: {name} (No contact number available).")
        else:
            messagebox.showinfo("Emergency Contact", "No emergency contact available.")

    def update_contacts_tree(self):
        self.contacts_tree.delete(*self.contacts_tree.get_children())
        for name, contact in sorted(self.contacts_by_number.items()):
            self.contacts_tree.insert("", "end", values=(name, contact))

if __name__ == "__main__":
    app = Application()
    app.mainloop()
