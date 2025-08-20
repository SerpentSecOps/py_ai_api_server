import os
import argparse
import fnmatch

def get_ignore_patterns(project_root):
    """
    Constructs a list of file and directory patterns to ignore.
    
    This function combines a default set of ignores with patterns found in a
    .gitignore file in the project root.
    """
    # A robust default list of common files and directories to ignore.
    ignore_patterns = [
        # Git
        '.git/',
        '.gitignore',
        '.gitattributes',
        
        # Python
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '*.egg-info/',
        'venv/',
        'pip-wheel-metadata/',
        
        # Environment
        '.env',
        
        # IDE/Editor
        '.vscode/',
        '.idea/',
        
        # Build artifacts
        'build/',
        'dist/',
        '*.egg',
        
        # Logs and temp files
        '*.log',
        
        # Databases
        '*.db',
        '*.sqlite',
        '*.sqlite3',
        '*.db-journal',
        
        # OS-specific
        '.DS_Store',
        'Thumbs.db'
    ]
    
    # Read patterns from .gitignore file, if it exists
    gitignore_path = os.path.join(project_root, '.gitignore')
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    ignore_patterns.append(line)
                    
    return ignore_patterns

def should_ignore(path, ignore_patterns):
    """
    Checks if a given path should be ignored based on a list of patterns.
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def bundle_project(project_root, output_file):
    """
    Parses all files in a project directory and rebuilds them in a single text file.
    """
    ignore_patterns = get_ignore_patterns(project_root)
    
    # Also ignore the output file and this script itself
    ignore_patterns.append(os.path.basename(output_file))
    ignore_patterns.append(os.path.basename(__file__))

    print(f"Starting to bundle project from: {project_root}")
    print(f"Output will be saved to: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8', errors='ignore') as outfile:
        for root, dirs, files in os.walk(project_root, topdown=True):
            
            # --- Directory Ignore Logic ---
            # Exclude specified directories from being traversed further
            original_dirs = dirs[:] # copy of dirs
            dirs[:] = [] # clear dirs
            for d in original_dirs:
                # To check a directory, we add a '/' at the end
                dir_path_for_check = os.path.join(os.path.relpath(root, project_root), d, '').replace('\\', '/')
                if not should_ignore(d, ignore_patterns) and not should_ignore(dir_path_for_check, ignore_patterns):
                    dirs.append(d)

            for filename in files:
                file_path = os.path.join(root, filename)
                relative_path = os.path.relpath(file_path, project_root).replace('\\', '/')

                if should_ignore(filename, ignore_patterns) or should_ignore(relative_path, ignore_patterns):
                    continue

                # Use a clear separator for easy parsing
                outfile.write(f"--- START FILE: {relative_path} ---\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as infile:
                        content = infile.read()
                        outfile.write(content)
                except Exception:
                    # If a file can't be read as text (e.g., it's a binary file), note it.
                    outfile.write("[SKIPPED] Could not read file as text (likely binary).")
                
                # Add a newline at the end of the content for separation
                outfile.write(f"\n--- END FILE: {relative_path} ---\n\n")
                print(f"  + Added: {relative_path}")

    print(f"\n✅ Project bundling complete. All files saved to {output_file}")

if __name__ == '__main__':
    # --- How to use this script ---
    # 1. Save this script as 'bundle.py' in your project's root directory.
    # 2. Open a terminal in that directory.
    # 3. Run the script: python bundle.py
    #    It will automatically use the default ignores and any found in a .gitignore file.
    #
    # It will create a file named 'project_bundle.txt' containing all your project files.
    
    parser = argparse.ArgumentParser(
        description="A script to bundle all project files into a single text file for AI analysis."
    )
    parser.add_argument(
        '--root', 
        type=str, 
        default='.', 
        help="The root directory of the project to bundle. Defaults to the current directory."
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='project_bundle.txt', 
        help="The name of the output file. Defaults to 'project_bundle.txt'."
    )
    
    args = parser.parse_args()
    
    # Get the absolute path for the project root
    project_directory = os.path.abspath(args.root)
    output_filename = os.path.join(project_directory, args.output)

    bundle_project(project_directory, output_filename)
