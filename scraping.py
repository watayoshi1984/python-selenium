# ==============================================================================
# セクション1: 環境構築（Google Colab環境で実行）
# ==============================================================================
import logging
import os
import sys

# 意図したフォーマットでログ出力する
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Colab環境であるかを判定
IS_COLAB = "google.colab" in sys.modules

try:
    if IS_COLAB:
        logging.info(">>> Google Colab環境を検出しました。環境構築を開始します。")
        # Chromeのインストール
        if not os.path.exists("/usr/bin/google-chrome-stable"):
            get_ipython().system('apt-get update -qq && apt-get install -y wget gnupg google-chrome-stable -qq')
        # 必要なPythonライブラリのインストール
        get_ipython().system('pip install selenium webdriver-manager pandas beautifulsoup4 lxml -q')
        logging.info(">>> 環境構築が正常に完了しました。")
    else:
        logging.info(">>> ローカル環境とみなし、環境構築をスキップします。")
except Exception as e:
    logging.error(f"--- 環境構築中にエラーが発生しました: {e} ---")
    raise SystemExit("環境構築に失敗したため、処理を中断します。")


# ==============================================================================
# セクション2: ライブラリのインポート
# ==============================================================================
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Colabでファイルをダウンロードするために必要
if IS_COLAB:
    from google.colab import files

# --- WebDriverのセットアップ ---
options = Options()
options.add_argument('--headless') # ブラウザを画面に表示しないモード
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
# ユーザーエージェントをPCに指定し、モバイルサイトへの意図しないリダイレクトを防ぐ

service = Service(ChromeDriverManager().install())
driver = None

# ==============================================================================
# セクション3: メイン処理
# ==============================================================================


try:
    # 1. WebDriverのインスタンスを生成
    driver = webdriver.Chrome(service=service, options=options)
    logging.info("WebDriverのセットアップが完了しました。")

    # 待機時間設定 (最大30秒)
    wait = WebDriverWait(driver, 30)

    # 2. https://www.python.org/ にアクセスする
    driver.get("https://www.python.org/")
    logging.info(f"'{driver.title}' にアクセスしました。")

    # 3. ニュースをクリックする
    logging.info("「News」リンクをクリックします...")
    # 要素がクリックされるのを防ぐオーバーレイなどを回避するため、JavaScriptでクリック
    news_link_locator = (By.XPATH, '//*[@id="news"]/a')
    news_link_element = wait.until(EC.presence_of_element_located(news_link_locator))
    driver.execute_script("arguments[0].click();", news_link_element)

    # 4. https://www.python.org/blogs/ にページ遷移したことを確認
    wait.until(EC.url_contains('/blogs/'))
    logging.info(f"ニュース一覧ページ ({driver.current_url}) に遷移しました。")

    # 5. "more" をクリックする
    logging.info("「more」リンクをクリックします...")
    more_link_locator = (By.XPATH, '//*[@id="content"]/div/section/div/div[1]/div/p/a')
    more_link_element = wait.until(EC.element_to_be_clickable(more_link_locator))
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_link_element) # 要素を画面中央に表示
    time.sleep(1) # スクロール待機
    more_link_element.click()

    # 6. https://blog.python.org/ または https://pythoninsider.blogspot.com/ に遷移するのを待つ
    wait.until(
        lambda d: 'blog.python.org' in d.current_url or 'pythoninsider.blogspot.com' in d.current_url
    )
    logging.info(f"ブログサイト ({driver.current_url}) に正常に遷移しました。")

    # サイトの種類（PC版かモバイル版か）を判定
    is_mobile_site = 'pythoninsider.blogspot.com' in driver.current_url
    if is_mobile_site:
        logging.info(">>> モバイル版ブログサイトのスクレイピングを開始します。")
    else:
        logging.info(">>> PC版ブログサイトのスクレイピングを開始します。")

    # 7. ブログの記事タイトルおよび投稿日を取得する
    news_data = []
    MAX_PAGES = 10 # 最大10ページまで取得

    for i in range(MAX_PAGES):
        logging.info(f"--- ページ {i + 1} のデータを取得します ---")

        # 記事コンテナが表示されるまで待機
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".blog-posts")))

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')

        page_articles_found = 0

        # PCサイトとモバイルサイトで構造が異なるため、処理を分岐
        if is_mobile_site:
            # --- モバイルサイトのスクレイピングロジック ---
            # 日付ごとにグループ化されているコンテナを取得
            post_containers = soup.select(".blog-posts > div.date-posts")
            for container in post_containers:
                date_tag = container.select_one("div.date-header span")
                date = date_tag.get_text(strip=True) if date_tag else "日付不明"

                # コンテナ内の記事をすべて取得
                articles = container.select("div.mobile-post-outer")
                for article in articles:
                    title_tag = article.select_one("a > h3.post-title")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        # 重複がないかチェックしてリストに追加
                        if title and not any(d['タイトル'] == title for d in news_data):
                            logging.info(f"  >> 発見: [投稿日: {date}] [タイトル: {title}]")
                            news_data.append({'投稿日': date, 'タイトル': title})
                            page_articles_found += 1
        else:
            # --- PCサイトのスクレイピングロジック ---
            # 日付ごとにグループ化されているコンテナを取得
            post_containers = soup.select(".blog-posts > div.date-outer")
            for container in post_containers:
                date_tag = container.select_one("h2.date-header span")
                date = date_tag.get_text(strip=True) if date_tag else "日付不明"

                # コンテナ内の記事をすべて取得
                articles = container.select("div.post-outer")
                for article in articles:
                    title_tag = article.select_one("h3.post-title a")
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                        # 重複がないかチェックしてリストに追加
                        if title and not any(d['タイトル'] == title for d in news_data):
                            logging.info(f"  >> 発見: [投稿日: {date}] [タイトル: {title}]")
                            news_data.append({'投稿日': date, 'タイトル': title})
                            page_articles_found += 1

        logging.info(f"このページから新たに {page_articles_found} 件の記事を取得しました。")

        # 新しい記事が1件もなければ、最終ページとみなしてループを抜ける
        if page_articles_found == 0 and i > 0:
            logging.info("新たな記事がなかったため、最終ページと判断し、処理を終了します。")
            break

        # 次のページへ遷移 (最後のページでなければ)
        if i < MAX_PAGES - 1:
            try:
                # サイトによって「次のページ」ボタンのセレクタが違う
                if is_mobile_site:
                    next_button_locator = (By.ID, "blog-pager-older-link")
                else:
                    next_button_locator = (By.CSS_SELECTOR, "a.older-posts")

                # ボタンをクリックして次ページへ
                older_posts_button = driver.find_element(*next_button_locator)
                older_posts_button.click()
                logging.info(f"次のページ({i + 2}ページ目)へ遷移します...")
                time.sleep(2) # ページ遷移と読み込みのための待機
            except Exception:
                logging.info("「Older Posts」ボタンが見つかりませんでした。ここで取得を終了します。")
                break

    logging.info(f"合計 {len(news_data)} 件のニュースを取得しました。")

    # 8. CSVファイルに投稿日、記事タイトルをCSVファイルに出力し、ダウンロードする
    if news_data:
        df = pd.DataFrame(news_data, columns=['投稿日', 'タイトル'])
        csv_filename = 'python_blog_news.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        logging.info(f"取得したデータを'{csv_filename}'に保存しました。")

        # Google Colab環境の場合、ファイルをダウンロード
        if IS_COLAB:
            files.download(csv_filename)
            logging.info("ファイルのダウンロードが開始されました。")
    else:
        logging.warning("取得できたニュースがなかったため、CSVファイルは作成されませんでした。")

except Exception as e:
    logging.error(f"処理中に予期せぬエラーが発生しました: {e}", exc_info=True)
    if driver:
        # エラー発生時のスクリーンショットを保存
        error_filename = 'error_screenshot.png'
        driver.save_screenshot(error_filename)
        logging.info(f"エラー発生時のスクリーンショットを '{error_filename}' として保存しました。")
        if IS_COLAB:
            files.download(error_filename)
finally:
    if driver:
        driver.quit()
        logging.info("WebDriverを終了しました。")