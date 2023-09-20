import subprocess
import sys

def execute_command(command):
    """Execute the given command and print the output."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print the output and error (if any)
    if result.stdout:
        print(result.stdout.decode())
    if result.stderr:
        print(result.stderr.decode())

def open():
    """Run the 'open' series of commands."""
    # Pull Batch
    execute_command("python utils/process.py -o batch.csv --batch 30")
    
    # Add WIP Flag to Batch
    execute_command("python utils/keap.py -csv batch.csv --action 3")
    
    # Generate Shipping Labels
    execute_command("python utils/labels.py -csv batch.csv -avery 5260")
    
    # Run Mail Merge
    execute_command("python mailmerge.py -odt template.odt -csv batch.csv -f output -print")

def close():
    """Run the 'close' series of commands."""
    # Mark Sent
    execute_command("python utils/keap.py -csv batch.csv --action 2")

    # Remove WIP Flag
    execute_command("python utils/keap.py -csv batch.csv --action 1")

    # Delete Cache
    execute_command("python utils/keap.py -csv batch.csv --action 5")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py -open/-close")
        sys.exit(1)

    action = sys.argv[1]

    if action == '-open':
        open()
    elif action == '-close':
        close()
    else:
        print(f"Unknown action: {action}")
        print("Usage: python orchestrator.py -open/-close")
