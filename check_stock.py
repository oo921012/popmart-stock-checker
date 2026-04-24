import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

PRODUCT_PAGE = "https://www.popmart.com/sg/products/11942/Angry-Molly-Crocs-%22Angry-Cheese%22-Co-branded-Figurine"
PRODUCT_NAME = 'Angry Molly × Crocs "Angry Cheese" Co-branded Figurine'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def check_stock() -> tuple[bool, str]:
    resp = requests.get(PRODUCT_PAGE, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text

    if "ADD TO CART" in html:
        return True, "找到關鍵字：'ADD TO CART'"
    if "SOLD OUT" in html:
        return False, "找到售罄關鍵字：'SOLD OUT'"

    print(f"[DEBUG] HTML 片段：{html[:2000]}")
    return False, "未找到明確庫存狀態"


def send_email(reason: str):
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("NOTIFY_EMAIL", sender)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"✅ 有貨了！快去搶！— {PRODUCT_NAME}"
    msg["From"] = sender
    msg["To"] = recipient

    body = f"""
<h2>🎉 Pop Mart 有貨通知</h2>
<p><strong>商品：</strong>{PRODUCT_NAME}</p>
<p><strong>狀態：</strong>🟢 有貨！</p>
<p><strong>偵測依據：</strong>{reason}</p>
<p><strong>時間：</strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
<hr>
<p><a href="{PRODUCT_PAGE}" style="font-size:18px; font-weight:bold;">👉 立即前往購買</a></p>
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


if __name__ == "__main__":
    main()
