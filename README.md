# Customer Messaging System

## Overview

The Customer Messaging System is designed to send personalized messages to customers via email or WhatsApp. Based on customer data, the system selects the appropriate message from a pre-defined library and delivers it through the chosen communication channel. The system supports custom messages based on customer categories and lead status.

## Features

- **Personalized Messages:** Sends messages tailored to the customer's category and lead status.
- **Multiple Communication Channels:** Allows users to choose between sending messages via email or WhatsApp.
- **Dynamic Content:** Generates dynamic content, including customer-specific information.
- **Logging and Error Handling:** Tracks successes, failures, and skipped customers.

## Requirements

- Python 3.x
- Libraries:
  - `json` (for loading message data)
  - `smtplib` (for email sending)
  - `requests` (for WhatsApp API, if needed)

## Setup Instructions

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <project_directory>
