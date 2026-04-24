import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

URL = "https://www.popmart.com/sg/products/11942/Angry-Molly-Crocs-%22Angry-Cheese%22-Co-branded-Figurine"
PRODUCT_NAME = 'Angry Molly × Crocs "Angry Cheese" Co-branded Figurine'

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

IN_STOCK_KEYWORDS = ["add to cart", "add to bag", "buy now", "加入購物車"]
OUT_OF_STOCK_KEYWORDS = ["sold out", "out of stock", "notify me", "售罄", "已售罄"]


def check_stock() -> tuple[bool, str]:
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text.lower()

        for kw in IN_STOCK_KEYWORDS:
            if kw.lower() in html:
                return True, f"找到關鍵字：'{kw}'"

        for kw in OUT_OF_STOCK_KEYWORDS:
            if kw.lower() in html:
                return False, f"找到售罄關鍵字：'{kw}'"

        return False, "未找到明確庫存狀態關鍵字，預設為售罄"

    except requests.RequestException as e:
        raise RuntimeError(f"網路請求失敗：{e}")


def send_email(in_stock: bool, reason: str):
    sender = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient = os.environ.get("NOTIFY_EMAIL", sender)

    subject = f"✅ 有貨了！{PRODUCT_NAME}" if in_stock else f"❌ 仍售罄 — {PRODUCT_NAME}"

    body = f"""
<h2>Pop Mart 庫存通知</h2>
<p><strong>商品：</strong>{PRODUCT_NAME}</p>
<p><strong>狀態：</strong>{'🟢 有貨！快去搶購！' if in_stock else '🔴 目前仍售罄'}</p>
<p><strong>偵測依據：</strong>{reason}</p>
<p><strong>時間：</strong>{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
<hr>
<p><a href="{URL}">👉 點此前往商品頁面</a></p>
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())

    print(f"✉️  通知信已寄出至 {recipient}")


def main():
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}] 開始檢查庫存...")
    print(f"商品：{PRODUCT_NAME}")
    print(f"網址：{URL}")

    in_stock, reason = check_stock()

    status = "🟢 有貨" if in_stock else "🔴 售罄"
    print(f"結果：{status}（{reason}）")

    # 只在有貨時寄信（避免每次都收到售罄通知）
    if in_stock:
        send_email(in_stock, reason)
        print("✅ 有貨通知已發送！")
    else:
        print("ℹ️  仍售罄，不發送通知。")

    # 輸出結果供 GitHub Actions 使用
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"in_stock={'true' if in_stock else 'false'}\n")


if __name__ == "__main__":
    main()
