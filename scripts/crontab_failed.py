from logging_ops import notify_bot
import sys


msg = f'A crontab command had failed due to unexpected reasons.'
notify_bot(msg)


def main():
    if len(sys.argv) < 2:
        notify_bot("Usage: crontab_failed.py <error_message>")
        sys.exit(1)

    error_message = sys.argv[2]

    notify_bot(f"The crontab had failed with message: {error_message}")

if __name__ == "__main__":
    main()
