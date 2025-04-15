import subprocess
import os
import re

class Executor:
    def execute_plan(self, plan):
        try:
            # Split plan into lines and process each step
            lines = plan.split('\n')
            step_pattern = re.compile(r'^\d+\.\s+(.+)$')
            
            current_step = None
            current_content = []
            steps_to_execute = []
            
            # First, parse the plan into structured steps
            for line in lines:
                step_match = step_pattern.match(line.strip())
                if step_match:
                    # If we were collecting content for a previous step, save it
                    if current_step and current_step.startswith("Create a file"):
                        steps_to_execute.append((current_step, '\n'.join(current_content)))
                        current_content = []
                    
                    # Start a new step
                    current_step = step_match.group(1)
                    if not current_step.startswith("Create a file"):
                        steps_to_execute.append((current_step, None))
                        current_step = None
                elif current_step and current_step.startswith("Create a file"):
                    # Collecting content for file creation
                    current_content.append(line)
            
            # Don't forget the last step if it was file creation
            if current_step and current_step.startswith("Create a file"):
                steps_to_execute.append((current_step, '\n'.join(current_content)))
            
            # Now execute each step
            for step, content in steps_to_execute:
                if step.startswith("Create a file"):
                    # Extract filename
                    filename_match = re.search(r'Create a file ["\']?([^"\']+)["\']?', step)
                    if not filename_match:
                        print(f"Error: Could not parse filename from: {step}")
                        return False
                    
                    filename = filename_match.group(1)
                    
                    # Clean up content if we have any
                    if content:
                        # Remove code block markers
                        content = re.sub(r'^```python\s*', '', content)
                        content = re.sub(r'```\s*$', '', content)
                        content = content.strip()
                    else:
                        # Set default content if none was captured
                        content = ""
                    
                    # Write the file
                    with open(filename, "w") as f:
                        f.write(content)
                    print(f"Created file: {filename}")
                    print(f"Content written to file ({len(content)} characters)")
                
                elif step.startswith("Run the command:") or step.startswith("Run:"):
                    # Handle shell command
                    shell_cmd = step.replace("Run the command:", "").replace("Run:", "").strip()
                    print(f"Executing: {shell_cmd}")
                    result = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
                    print(f"Output: {result.stdout}")
                    if result.stderr:
                        print(f"Command error: {result.stderr}")
                        if result.returncode != 0:
                            print(f"Command failed with exit code: {result.returncode}")
                            return False
                else:
                    # Try to run as a direct command if not in recognized format
                    try:
                        print(f"Attempting to run as direct command: {step}")
                        result = subprocess.run(step, shell=True, capture_output=True, text=True)
                        print(f"Output: {result.stdout}")
                        if result.stderr:
                            print(f"Command error: {result.stderr}")
                    except Exception as cmd_error:
                        print(f"Failed to execute command: {cmd_error}")
                        return False
            return True
        except Exception as e:
            print(f"Execution failed: {str(e)}")
            return False