import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
from pathlib import Path
import re

class RegexReplacerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Regex Replacer")
        self.root.geometry("650x700") # Adjusted for better visibility of all elements

        # --- Variables ---
        self.target_dir_path = tk.StringVar(value="No target directory selected")
        self.output_dir_path = tk.StringVar(value="Using default output directory (see below)")
        self.search_regex_var = tk.StringVar(value="Input search regex")
        self.replace_regex_var = tk.StringVar(value="Input replace regex")
        self.regex_list = []
        self.viable_file_extensions = {
        '.txt', '.md', '.json', '.csv', '.xml', '.html', '.htm',
        '.py', '.js', '.css', '.yaml', '.yml', '.ini', '.log',
        '.rtf', '.tex', '.java', '.c', '.cpp', '.h', '.hpp',
        '.sh', '.ps1', '.bat', '.sql', '.config', '.conf', '.properties'
        }
        self.default_output_base_dir = Path(os.path.expanduser("~")) / "regex_replacer_outputs"


        # --- Main Frame ---
        main_frame = ttk.Frame(root, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- 1. Target Directory Section ---
        target_dir_frame = ttk.LabelFrame(main_frame, text="Choose target directory for replacements", padding="10 10 10 10")
        target_dir_frame.pack(fill=tk.X, pady=5)

        choose_target_dir_button = ttk.Button(target_dir_frame, text="Choose directory", command=self.select_target_directory)
        choose_target_dir_button.pack(pady=5)

        target_path_frame = ttk.Frame(target_dir_frame)
        target_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(target_path_frame, text="Path:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(target_path_frame, textvariable=self.target_dir_path, relief="sunken", padding=2, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)


        # --- 2. Regex Input Section ---
        regex_input_frame = ttk.Frame(main_frame, padding="10 0 10 0")
        regex_input_frame.pack(fill=tk.X, pady=5)

        # Search Regex
        search_frame = ttk.Frame(regex_input_frame)
        search_frame.pack(fill=tk.X, pady=2)
        ttk.Label(search_frame, text="Search regex:").pack(side=tk.LEFT, anchor=tk.W, padx=(0,10))
        self.search_regex_entry = ttk.Entry(search_frame, textvariable=self.search_regex_var, width=40)
        self.search_regex_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,10))
        self.search_regex_entry.bind("<FocusIn>", lambda e: self.on_entry_click(e, self.search_regex_var, "Input search regex"))
        self.search_regex_entry.bind("<FocusOut>", lambda e: self.on_focusout(e, self.search_regex_var, "Input search regex"))


        # Replace Regex
        replace_frame = ttk.Frame(regex_input_frame)
        replace_frame.pack(fill=tk.X, pady=2)
        ttk.Label(replace_frame, text="Replace regex:").pack(side=tk.LEFT, anchor=tk.W, padx=(0,5)) # Adjusted padding
        self.replace_regex_entry = ttk.Entry(replace_frame, textvariable=self.replace_regex_var, width=40)
        self.replace_regex_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.replace_regex_entry.bind("<FocusIn>", lambda e: self.on_entry_click(e, self.replace_regex_var, "Input replace regex"))
        self.replace_regex_entry.bind("<FocusOut>", lambda e: self.on_focusout(e, self.replace_regex_var, "Input replace regex"))

        add_button = ttk.Button(regex_input_frame, text="Add", command=self.add_regex_pair, width=15)
        add_button.pack(pady=10)


        # --- 3. Regex List Section ---
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.regex_listbox = tk.Listbox(list_frame, height=8, selectmode=tk.SINGLE)
        self.regex_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.regex_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.regex_listbox.config(yscrollcommand=scrollbar.set)


        # --- 4. List Control Buttons ---
        list_control_frame = ttk.Frame(main_frame)
        list_control_frame.pack(fill=tk.X, pady=5)

        delete_selection_button = ttk.Button(list_control_frame, text="Delete selection", command=self.delete_selected_regex)
        delete_selection_button.pack(side=tk.LEFT, padx=(0, 10), expand=True)

        delete_all_button = ttk.Button(list_control_frame, text="Delete all", command=self.delete_all_regex)
        delete_all_button.pack(side=tk.LEFT, expand=True)


        # --- 5. Output Directory Section ---
        output_dir_frame = ttk.LabelFrame(main_frame, text="Output Directory Options", padding="10 10 10 10")
        output_dir_frame.pack(fill=tk.X, pady=10)

        # REASON: MAKE THE DEFAULT PATH LABEL DYNAMIC AND REFLECT THE ACTUAL DEFAULT PATH
        self.default_output_label_text = tk.StringVar(value=f"The default output path will be inside: {self.default_output_base_dir}")
        ttk.Label(output_dir_frame, textvariable=self.default_output_label_text).pack(anchor=tk.W, pady=(0,2)) # CORRECTED: USE TEXTVARIABLE
        ttk.Label(output_dir_frame, text="OR Choose another output directory (will also create a run-specific subfolder)").pack(anchor=tk.W, pady=(0,5))

        choose_output_dir_button = ttk.Button(output_dir_frame, text="Choose output directory", command=self.select_output_directory)
        choose_output_dir_button.pack(pady=5)

        output_path_frame = ttk.Frame(output_dir_frame)
        output_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_path_frame, text="Path:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(output_path_frame, textvariable=self.output_dir_path, relief="sunken", padding=2, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)


        # --- 6. Execute Button ---
        execute_button = ttk.Button(main_frame, text="Execute", command=self.execute_replacement, width=20)
        execute_button.pack(pady=15)

        # --- Set initial placeholder colors ---
        self.set_placeholder_color(self.search_regex_entry, self.search_regex_var, "Input search regex")
        self.set_placeholder_color(self.replace_regex_entry, self.replace_regex_var, "Input replace regex")



    def on_entry_click(self, event, text_variable, placeholder_text):
        """Clears the placeholder text when entry is clicked."""
        if text_variable.get() == placeholder_text:
           text_variable.set("")
           event.widget.config(foreground='black') # Or your default text color

    def on_focusout(self, event, text_variable, placeholder_text):
        """Restores placeholder text if entry is empty."""
        if not text_variable.get().strip(): # CORRECTED: STRIP WHITESPACE TO CHECK IF TRULY EMPTY
            text_variable.set(placeholder_text)
            event.widget.config(foreground='grey')

    def set_placeholder_color(self, entry_widget, text_variable, placeholder_text):
        """Sets initial placeholder color if text matches placeholder."""
        if text_variable.get() == placeholder_text:
            entry_widget.config(foreground='grey')
        else:
            entry_widget.config(foreground='black')

    def select_target_directory(self):
        """Opens a dialog to select the target directory."""
        directory = filedialog.askdirectory()
        if directory: # If a directory is chosen
            self.target_dir_path.set(directory)
        else: # If dialog is cancelled, keep or reset placeholder
            # CORRECTED: ONLY RESET IF IT WAS PREVIOUSLY THE PLACEHOLDER OR EMPTY
            current_val = self.target_dir_path.get()
            if not current_val or current_val == "No target directory selected":
                 self.target_dir_path.set("No target directory selected")
            # messagebox.showwarning("Input Missing", "Choose default") # REMOVED: NOT NECESSARY TO SHOW WARNING ON CANCEL

    def select_output_directory(self):
        """Opens a dialog to select the output directory."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_path.set(directory)
        else:
            current_val = self.output_dir_path.get()
            if not current_val or current_val == "Using default output directory (see below)" or not Path(current_val).is_dir():
                 self.output_dir_path.set("Using default output directory (see below)")

    def add_regex_pair(self):
        """Adds the current search and replace regex to the listbox."""
        search_val = self.search_regex_var.get()
        replace_val = self.replace_regex_var.get()

        # CORRECTED: ALSO CHECK IF SEARCH_VAL IS JUST WHITESPACE
        if search_val and search_val.strip() and search_val != "Input search regex":
            # If replace_val is placeholder, consider it empty for the list
            display_replace_val = replace_val if replace_val != "Input replace regex" else ""
            self.regex_listbox.insert(tk.END, f"S: '{search_val}' -> R: '{display_replace_val}'") # IMPROVED DISPLAY
            self.regex_list.append((search_val, display_replace_val))
            # Clear entries after adding and reset placeholders
            self.search_regex_var.set("Input search regex")
            self.replace_regex_var.set("Input replace regex")
            self.set_placeholder_color(self.search_regex_entry, self.search_regex_var, "Input search regex")
            self.set_placeholder_color(self.replace_regex_entry, self.replace_regex_var, "Input replace regex")
            self.search_regex_entry.focus_set() # Move focus back to search entry
        else:
            messagebox.showwarning("Input Missing", "Search regex cannot be empty or the placeholder text.")

    def delete_selected_regex(self):
        """Deletes the selected regex pair from the listbox."""
        try:
            selected_indices = self.regex_listbox.curselection()
            if not selected_indices:
                messagebox.showinfo("No Selection", "Please select an item to delete.")
                return
            selected_index = selected_indices[0]
            self.regex_listbox.delete(selected_index)
            del self.regex_list[selected_index]
        except IndexError:
            # This should ideally not be reached if the check above is done, but good for safety.
            messagebox.showinfo("Error", "Could not delete the selected item. It might no longer exist.")

    def delete_all_regex(self):
        """Deletes all regex pairs from the listbox."""
        if self.regex_list: # CORRECTED: ONLY ASK IF THERE'S SOMETHING TO DELETE
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all regex pairs?"):
                self.regex_listbox.delete(0, tk.END)
                self.regex_list.clear()
        else:
            messagebox.showinfo("Nothing to Delete", "The regex list is already empty.")

    def execute_replacement(self):
        regex_list:list[tuple] = self.regex_list
        target_dir_str = self.target_dir_path.get()
        output_dir_str_from_var = self.output_dir_path.get()

        if not regex_list:
            messagebox.showinfo("No Regex", "No regex pairs to execute. Please add some.")
            return

        if not target_dir_str or target_dir_str == "No target directory selected":
            messagebox.showerror("Select Target Directory", "Target Directory is not selected.")
            return

        target_dir_path = Path(target_dir_str)
        if not target_dir_path.is_dir():
            messagebox.showerror("Target Directory Error", f"Target Directory '{target_dir_str}' doesn't exist or is not a directory.")
            return 

        # Determine and create the base output directory
        if output_dir_str_from_var == "Using default output directory (see below)" or not output_dir_str_from_var:
            chosen_output_base_dir = self.default_output_base_dir
        else:
            chosen_output_base_dir = Path(output_dir_str_from_var)

        try:
            chosen_output_base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Output Directory Error", f"Could not create base output directory '{chosen_output_base_dir}': {e}")
            return

        # Create a run-specific subfolder
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        run_specific_folder_name = f"run_{timestamp_str}"
        final_run_output_path = chosen_output_base_dir / run_specific_folder_name

        try:
            final_run_output_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            messagebox.showerror("Output Directory Error", f"Could not create run-specific output directory '{final_run_output_path}': {e}")
            return

        files_to_process = [entry for entry in target_dir_path.iterdir() if entry.is_file()]
        processed_files_count = 0
        modified_files_count = 0

        if not files_to_process:
            messagebox.showinfo("No Files", f"No files found in the target directory: {target_dir_path}")
            return

        for file_path_obj in files_to_process:
            if file_path_obj.suffix.lower() in self.viable_file_extensions: # CORRECTED: USE .lower() FOR CASE-INSENSITIVE EXTENSION CHECK
                processed_files_count += 1
                try:
                    with open(file_path_obj, 'r', encoding='utf-8', errors='replace') as f:
                        original_data = f.read()
                    
                    current_data = original_data
                    for search_regex, replace_regex in regex_list: # CORRECTED: UNPACK TUPLE DIRECTLY
                        try:
                            current_data = re.sub(search_regex, replace_regex, current_data)
                        except re.error as e:
                            # Log or inform user about specific regex error but continue with other regexes/files
                            print(f"Regex error for '{search_regex}' on file '{file_path_obj.name}': {e}")
                            messagebox.showwarning("Regex Error", f"Error applying regex: '{search_regex}' on file '{file_path_obj.name}'.\nError: {e}\nSkipping this regex for this file.")
                            continue # Skip this specific regex for this file

                    if current_data != original_data:
                        modified_files_count +=1
                        output_file_path = final_run_output_path / file_path_obj.name
                        try:
                            with open(output_file_path, "w", encoding='utf-8') as ff:
                                ff.write(current_data)
                        except OSError as e:
                            messagebox.showerror("File Write Error", f"Could not write processed file '{output_file_path}': {e}")
                    else:
                        # Optionally, copy files that were processed but not changed, or just skip
                        # For now, we only write if modified. If you want to copy all processed files:
                        # output_file_path = final_run_output_path / file_path_obj.name
                        # shutil.copy2(file_path_obj, output_file_path) # Requires 'import shutil'
                        pass


                except FileNotFoundError:
                    messagebox.showerror("File Error", f"File not found during processing: {file_path_obj.name}")
                except Exception as e: # Catch other potential read errors
                    messagebox.showerror("File Read Error", f"Could not read file '{file_path_obj.name}': {e}")

        summary_message = f"Execution Complete!\n\n"
        summary_message += f"Processed {processed_files_count} viable files.\n"
        summary_message += f"{modified_files_count} files were modified and saved to:\n{final_run_output_path}"
        messagebox.showinfo("Execution Summary", summary_message)


if __name__ == '__main__':
    root = tk.Tk()
    app = RegexReplacerApp(root)
    root.mainloop()