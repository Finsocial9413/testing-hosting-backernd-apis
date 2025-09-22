import json
import os
import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path

class TaskManager:
    def __init__(self, temp_dir: str = "temp_tasks", cleanup_interval: int = 300):  # 5 minutes = 300 seconds
        self.temp_dir = Path(temp_dir)
        self.cleanup_interval = cleanup_interval
        self.temp_dir.mkdir(exist_ok=True)
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        print(f"TaskManager initialized with cleanup interval: {cleanup_interval} seconds")
    
    def _get_task_file(self, task_id: str) -> Path:
        """Get the file path for a task."""
        return self.temp_dir / f"task_{task_id}.json"
    
    def save_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Save task data to file."""
        task_data["created_at"] = time.time()
        task_data["updated_at"] = time.time()
        task_file = self._get_task_file(task_id)
        
        try:
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            print(f"Task {task_id} saved successfully")
        except Exception as e:
            print(f"Error saving task {task_id}: {e}")
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data from file."""
        task_file = self._get_task_file(task_id)
        
        if not task_file.exists():
            print(f"Task file not found: {task_id}")
            return None
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                task_data = json.load(f)
                return task_data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error reading task {task_id}: {e}")
            return None
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing task data."""
        task_data = self.get_task(task_id)
        if task_data is None:
            print(f"Cannot update task {task_id}: task not found")
            return False
        
        task_data.update(updates)
        task_data["updated_at"] = time.time()
        self.save_task(task_id, task_data)
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete task file."""
        task_file = self._get_task_file(task_id)
        try:
            task_file.unlink()
            print(f"Task {task_id} deleted successfully")
            return True
        except FileNotFoundError:
            print(f"Task file not found for deletion: {task_id}")
            return False
    
    def task_exists(self, task_id: str) -> bool:
        """Check if task exists."""
        return self._get_task_file(task_id).exists()
    
    def _cleanup_loop(self):
        """Background thread to cleanup old tasks."""
        while True:
            try:
                self._cleanup_old_tasks()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"Cleanup error: {e}")
    
    def _cleanup_old_tasks(self):
        """Remove task files older than cleanup_interval."""
        current_time = time.time()
        cleaned_count = 0
        
        for task_file in self.temp_dir.glob("task_*.json"):
            try:
                # Check file modification time
                if current_time - task_file.stat().st_mtime > self.cleanup_interval:
                    task_file.unlink()
                    cleaned_count += 1
                    print(f"Cleaned up old task file: {task_file.name}")
            except Exception as e:
                print(f"Error cleaning up {task_file}: {e}")
        
        if cleaned_count > 0:
            print(f"Cleanup completed: {cleaned_count} old task files removed")

# Global task manager instance
task_manager = TaskManager()