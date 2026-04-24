import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

URL = "https://www.popmart.com/sg/products/11942/Angry-Molly-Crocs-%22Angry-Cheese%22-Co-branded-Figurine"
PRODUCT_NAME = 'Angry Molly × Crocs "Angry Cheese" Co-branded Figurine'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

IN_STOCK_KEYWORDS = ["add to cart", "add to bag", "buy now", "加入購物車"]
OUT_OF_STOCK_KEYWORDS = ["sold out", "out of stock", "notify me", "售罄", "已售罄"]


def check_stock():
    resp = requests.get(URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    html = resp.text.lower()

    for kw in IN_STOCK_KEYWORDS:
        if kw in html:
            return True, f"找到關鍵字：'{kw}'"
    for kw in OUT_OF_STOCK_KEYWORDS:
        if kw in html:
            return False, f"找到售罄關鍵字：'{kw}'"
    return False, "未找到明確庫存狀態"


def send_email(reason):
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
<p><strong>時間：</strong>{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
<hr>
<p><a href="{URL}" style="font-size:18px; font-weight:bold;">👉 立即前往購買</a></p>
"""
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
    print(f"✉️ 通知信已寄出至 {recipient}")


def main():
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}] 檢查庫存中...")
    try:
        in_stock, reason = check_stock()
        print(f"結果：{'🟢 有貨' if in_stock else '🔴 售罄'}（{reason}）")
        if in_stock:
            send_email(reason)
    except Exception as e:
        print(f"❌ 錯誤：{e}")


if __name__ == "__main__":
    main()