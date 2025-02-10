import requests
import json


def send_test_webhook(webhook_url):
    data = {
        "content": "🔔 Test message - Webhook is working!",
        "username": "Test Bot"
    }

    response = requests.post(webhook_url, json=data)

    if response.status_code == 204:
        print("Test message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")


# Use your webhook URL here
webhook_url = "https://discord.com/api/webhooks/1334878015078793310/qENtDsst4aV31baSn9BJ8cf4mEhk75QTpC_rRF5HZ5V5Q_gKzHivFcs9IS5rTHNUVjLL"
send_test_webhook(webhook_url)