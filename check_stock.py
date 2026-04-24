import subprocess
import sys
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 確保 chromium 已安裝
subprocess.run(
    [sys.executable, "-m", "playwright", "install", "chromium"],
    check=True
)

from playwright.sync_api import sync_playwright

PRODUCT_PAGE = "https://www.popmart.com/sg/products/11942/Angry-Molly-Crocs-%22Angry-Cheese%22-Co-branded-Figurine"
PRODUCT_NAME = 'Angry Molly × Crocs "Angry Cheese" Co-branded Figurine'


def check_stock() -> tuple[bool, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/147.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = context.new_page()
        page.goto(PRODUCT_PAGE, wait_until="networkidle", timeout=30000)
        page.wait_for_selector("button", timeout=15000)

        buttons = page.locator("button").all_text_contents()
        print(f"  找到按鈕：{buttons}")

        for btn in buttons:
            text = btn.strip().upper()
            if "ADD TO CART" in text or "BUY NOW" in text:
                browser.close()
                return True, f"按鈕文字：'{btn.strip()}'"
            if "SOLD OUT" in text:
                browser.close()
                return False, f"按鈕文字：'{btn.strip()}'"

        browser.close()
        return False, f"未找到明確按鈕：{buttons}"


def send_email(reason: str):
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("NOTIFY_EMAIL", sender)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ 有貨了！快去搶！— {PRODUCT_NAME}"
    msg["From"] = sender
    msg["To"] = recipient

    body = f"""
<h2>&#x1F389; Pop Mart 有貨通知</h2>
<p><strong>商品：</strong>{PRODUCT_NAME}</p>
<p><strong>狀態：</strong>&#x1F7E2; 有貨！</p>
<p><strong>偵測依據：</strong>{reason}</p>
<p><strong>時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<hr>
<p><a href="{PRODUCT_PAGE}" style="font-size:18px; font-weight:bold;">&#x1F449; 立即前往購買</a></p>
"""
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print(f"✉️ 通知信已寄出至 {recipient}")


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 檢查庫存中...")
    try:
        in_stock, reason = check_stock()
        print(f"結果：{'🟢 有貨' if in_stock else '🔴 售罄'}（{reason}）")
        if in_stock:
            send_email(reason)
            print("✅ 通知信已發送！")
        else:
            print("ℹ️  仍售罄，等待下次偵測。")
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        raise


if __name__ == "__main__":
    main()
