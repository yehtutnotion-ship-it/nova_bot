import os
import json
import logging
import gspread
from telegram.ext import Updater, MessageHandler, Filters
from oauth2client.service_account import ServiceAccountCredentials

# === Load Google Credentials from environment ===
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Nova Edge Rental Hub Data").worksheet("Customer_contacts")

# === Bot token ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# === Message Parser ===
def parse_message(text):
    fields = {
        "Code": "", "Condo": "", "Price": "", "Location": "", "Room Type": "",
        "Size": "", "Floor": "", "Availability": "", "Contract": "", "Notes": ""
    }

    lines = text.strip().splitlines()
    for line in lines:
        if "Code" in line: fields["Code"] = line.split("-")[-1].strip()
        elif "Condo" in line: fields["Condo"] = line.split("-")[-1].strip()
        elif "Rent" in line: fields["Price"] = line.split("-")[-1].strip()
        elif "Location" in line: fields["Location"] = line.split("-")[-1].strip()
        elif "Room Type" in line: fields["Room Type"] = line.split("-")[-1].strip()
        elif "Size" in line: fields["Size"] = line.split("-")[-1].strip()
        elif "floor" in line.lower(): fields["Floor"] = line.split("-")[-1].strip()
        elif "Ready" in line or "Available" in line:
            fields["Availability"] = line.strip("✅").strip()
        elif "Contract" in line: fields["Contract"] = line.split("-")[-1].strip()
        else:
            fields["Notes"] += line.strip() + "\n"

    return fields

# === Telegram handler ===
def handle_message(update, context):
    text = update.message.text
    fields = parse_message(text)
    try:
        sheet.append_row([
            fields["Code"], fields["Condo"], fields["Price"], fields["Location"],
            fields["Room Type"], fields["Size"], fields["Floor"],
            fields["Availability"], fields["Contract"], fields["Notes"]
        ])
        update.message.reply_text("✅ Data added to Google Sheet.")
    except Exception as e:
        update.message.reply_text("❌ Failed to save. Check logs.")
        print("Error:", e)

def main():
    logging.basicConfig(level=logging.INFO)
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
