import os
import subprocess
import sys
import webbrowser
from repositories.launcher_repository import LauncherRepository
from models.launcher_item import LauncherItem
from models.workspace import Workspace

class LauncherService:
    def __init__(self):
        self.repository = LauncherRepository()

    # --- Workspace Methods ---
    def add_workspace(self, name):
        return self.repository.add_workspace(name)

    def get_all_workspaces(self):
        workspaces_data = self.repository.get_all_workspaces()
        return [Workspace(id, name) for id, name in workspaces_data]

    def delete_workspace(self, workspace_id):
        self.repository.delete_workspace(workspace_id)

    # --- Item Methods ---
    def add_item(self, name, path, item_type, workspace_id):
        self.repository.add_item(name, path, item_type, workspace_id)

    def get_items_by_workspace(self, workspace_id):
        items_data = self.repository.get_items_by_workspace(workspace_id)
        return [LauncherItem(id, name, path, item_type) for id, name, path, item_type in items_data]

    def delete_item(self, item_id):
        self.repository.delete_item(item_id)

    def launch_item(self, path, item_type):
        try:
            if item_type == 'url':
                webbrowser.open(path)
            elif sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", path], check=True)
        except Exception as e:
            print(f"Error launching {path}: {e}")

    def launch_workspace(self, workspace_id):
        items = self.get_items_by_workspace(workspace_id)
        for item in items:
            self.launch_item(item.path, item.item_type)
