from logging_ops import notify_bot
import sys

def main():
    # Read full stderr message from stdin
    error_message = sys.stdin.read().strip()

    if not error_message:
        notify_bot("crontab_failed.py was called but no error message was passed.")
        sys.exit(1)

    notify_bot(f"The crontab had failed with message:\n{error_message}")

if __name__ == "__main__":
    main()
