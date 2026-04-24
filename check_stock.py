import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

PRODUCT_ID = "11942"
API_URL = f"https://prod-intl-api.popmart.com/shop/v1/shop/productDetails?spuId={PRODUCT_ID}&s=0b3b75d83e789be6c06c6274a75eba02"
PRODUCT_PAGE = f"https://www.popmart.com/sg/products/{PRODUCT_ID}/Angry-Molly-Crocs-%22Angry-Cheese%22-Co-branded-Figurine"
PRODUCT_NAME = 'Angry Molly × Crocs "Angry Cheese" Co-branded Figurine'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Origin": "https://www.popmart.com",
    "Referer": "https://www.popmart.com/sg/",
    "Country": "SG",
    "Clientkey": "rmdsjsk7gwylcix",
}


def check_stock() -> tuple[bool, str]:
    ts = int(datetime.now(timezone.utc).timestamp())
    url = f"{API_URL}&t={ts}"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    skus = data.get("data", {}).get("skus", [])
    if not skus:
        return False, "API 回傳無 SKU 資料"

    for sku in skus:
        stock = sku.get("stock", {})
        online_stock = stock.get("onlineStock", 0)
        sku_title = sku.get("title", sku.get("id", "?"))
        print(f"  SKU [{sku_title}] onlineStock = {online_stock}")
        if online_stock > 0:
            return True, f"SKU '{sku_title}' 庫存 = {online_stock}"

    return False, "所有 SKU onlineStock = 0"


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


if __name__ == "__main__":
    main()
