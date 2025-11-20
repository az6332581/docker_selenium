import os
import time
import smtplib
import traceback
from datetime import datetime
from email.message import EmailMessage
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import schedule
import shutil

# ========== 信件設定 ==========
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "az6332581@gmail.com"
SENDER_PASSWORD = "totwfjkphmoxzmix"  # ⚠️ Gmail 建議使用「應用程式密碼」
RECEIVER_EMAILS = [
    "yu6332581@gmail.com",
    "lijh@frontierteches.com",
    "dcs0813@gmail.com"
]


def clean_old_folders(days=7):
    """刪除超過指定天數的截圖資料夾與日誌"""
    base_dir = os.getcwd()
    now = time.time()
    removed = []

    # 清理日期資料夾（例如：2025-11-11）
    for name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, name)
        if os.path.isdir(folder_path):
            try:
                folder_date = datetime.strptime(name, "%Y-%m-%d")
                age_days = (datetime.now() - folder_date).days
                if age_days > days:
                    shutil.rmtree(folder_path)
                    removed.append(folder_path)
            except ValueError:
                continue  # 跳過非日期格式的資料夾

    # 清理 logs 資料夾
    log_folder = os.path.join(base_dir, "logs")
    if os.path.exists(log_folder):
        for file in os.listdir(log_folder):
            file_path = os.path.join(log_folder, file)
            if os.path.isfile(file_path):
                mtime = os.path.getmtime(file_path)
                if now - mtime > days * 86400:  # 秒數換算天數
                    os.remove(file_path)
                    removed.append(file_path)

    if removed:
        log_message(f"🧹 已清理以下超過 {days} 天的檔案/資料夾：\n" + "\n".join(removed))
    else:
        log_message("🧹 沒有需要清理的舊檔案。")




def send_email(subject, body, attachments=None):
    """寄出郵件，可附加檔案"""
    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = subject
    msg.set_content(body)

    if attachments:
        for filepath in attachments:
            if os.path.exists(filepath):
                with open(filepath, "rb") as f:
                    msg.add_attachment(
                        f.read(),
                        maintype="application",
                        subtype="octet-stream",
                        filename=os.path.basename(filepath),
                    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"📧 已寄出郵件：{subject}")
    except Exception as e:
        print(f"⚠️ 郵件寄送失敗：{e}")


def log_message(message: str):
    """寫入日誌"""
    log_folder = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

    print(message)
    return log_file


def run_selenium_job():
    today = datetime.now().strftime("%Y-%m-%d")
    folder = os.path.join(os.getcwd(), today)
    os.makedirs(folder, exist_ok=True)
    log_file = None
    attachments = []
    status = "✅ 成功"
    message_body = ""

    try:
        log_message("=== 開始執行 Selenium 截圖任務 ===")

        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--force-device-scale-factor=0.67")
        # options.add_argument("--headless")  # 無頭模式可開啟
        driver = webdriver.Chrome(options=options)

        driver.get("https://www.mooddeer.net/")
        time.sleep(3)

        ''' 登入 '''
        login_link = driver.find_element(By.LINK_TEXT, "登入")
        login_link.click()
        time.sleep(3)

        account_input = driver.find_element(By.XPATH, "//input[@type='text']")
        account_input.send_keys("mood1020")

        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys("mood1020")

        login_button = driver.find_element(By.CSS_SELECTOR, "button.login-btn")
        login_button.click()
        time.sleep(5)

        timestamp = datetime.now().strftime("%H%M")
        driver.save_screenshot(os.path.join(folder, f"首頁_{timestamp}.png"))

        ''' 課程 '''
        menu = driver.find_element(By.XPATH, "//div[contains(text(), '課程訊息')]")
        actions = ActionChains(driver)
        actions.move_to_element(menu).perform()
        time.sleep(3)

        course_signup = driver.find_element(By.XPATH, "//li//a[contains(text(), '課程報名')]")
        course_signup.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"課程_{timestamp}.png"))

        course_signup = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div/div[3]/div/ul/li[1]")
        course_signup.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"課程詳細_{timestamp}.png"))

        ''' 回放 '''
        menu = driver.find_element(By.XPATH, "//div[contains(text(), '課程訊息')]")
        actions.move_to_element(menu).perform()
        time.sleep(4)

        course_replay = driver.find_element(By.XPATH, "//li//a[contains(text(), '課程回放')]")
        course_replay.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"回放_{timestamp}.png"))

        course_replay = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/ul/li[1]")
        course_replay.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"回放詳細_{timestamp}.png"))

        ''' 預錄 '''
        menu = driver.find_element(By.XPATH, "//div[contains(text(), '課程訊息')]")
        actions.move_to_element(menu).perform()
        time.sleep(4)

        prerecorded = driver.find_element(By.XPATH, "//li//a[contains(text(), '預錄課程')]")
        prerecorded.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"預錄_{timestamp}.png"))

        prerecorded = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/ul/li[1]")
        prerecorded.click()
        time.sleep(3)
        driver.save_screenshot(os.path.join(folder, f"預錄詳細_{timestamp}.png"))

        driver.quit()
        log_file = log_message(f"✅ 任務完成，圖片已存於：{folder}")
        message_body = f"任務執行成功，請查看附檔。\n\n圖片資料夾：{folder}"

    except Exception as e:
        status = "❌ 失敗"
        error_msg = traceback.format_exc()
        log_file = log_message(f"❌ 發生錯誤：{e}\n{error_msg}")
        message_body = f"任務執行失敗，詳細錯誤如下：\n\n{e}\n\n請查看日誌附件。"

    finally:
        # 收集附件：log + 所有截圖
        if log_file:
            attachments.append(log_file)
        for file in os.listdir(folder):
            if file.endswith(".png"):
                attachments.append(os.path.join(folder, file))
    
        # 寄信（一定會執行）
        send_email(
            subject=f"{status} Selenium 截圖報告 {today}",
            body=message_body,
            attachments=attachments,
        )
        log_message(f"📨 任務完成後已寄出郵件（狀態：{status}）")
        # 清理超過 7 天的資料夾與日誌
        clean_old_folders(days=7)




log_message("🕛 自動截圖排程啟動中，每天 00:55 會執行 Selenium 測試。 test1")


run_selenium_job()


# === 每天執行時間（測試時可改成幾分鐘後） ===
schedule.every().day.at("00:05").do(run_selenium_job)

while True:
    schedule.run_pending()
    time.sleep(60)
