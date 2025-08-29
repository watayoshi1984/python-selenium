# Python Selenium スクレイピングプロジェクト

このプロジェクトは、Python と Selenium を使用して Web サイトからデータをスクレイピングするサンプルコードです。Google Colab とローカル環境の両方に対応しています。

## ファイル構成

- [scraping.py](scraping.py): メインのスクレイピングスクリプト（Google Colab用）
- [setup.py](setup.py): Google Colab用のライブラリインストールスクリプト
- [local-setup.py](local-setup.py): ローカル環境用のライブラリインストールスクリプト
- [local-requirements.txt](local-requirements.txt): ローカル環境で必要なPythonライブラリ一覧
- [local-main.py](local-main.py): ローカル環境用のメインスクレイピングスクリプト

## Google Colab での実行方法

1. Google Colab で新しいノートブックを作成します。
2. [scraping.py](scraping.py) の内容を新しいセルに貼り付けます。
3. スクリプトが自動的に必要なライブラリをインストールし、スクレイピングを開始します。
4. 実行が完了すると、`python_blog_news.csv` というCSVファイルが自動的にダウンロードされます。

## ローカル環境での実行方法

### 必要条件

- Python 3.6 以上
- Chrome ブラウザ

### セットアップ

1. このリポジトリをクローンまたはダウンロードします。
2. プロジェクトディレクトリに移動します。
3. 以下のコマンドを実行して、必要なライブラリをインストールします。

   ```bash
   python local-setup.py
   ```

   または、直接pipを使用する場合:

   ```bash
   pip install -r local-requirements.txt
   ```

### 実行方法

以下のコマンドでスクレイピングを開始します。

```bash
python local-main.py
```

実行が完了すると、`python_blog_news.csv` がプロジェクトディレクトリ内に生成されます。

## メンテナンス方法

- 使用するWebサイトの構造が変更された場合、セレクタの更新が必要になることがあります。[scraping.py](scraping.py) および [local-main.py](local-main.py) 内のセレクタを確認・更新してください。
- 新しい依存関係を追加する場合は、[local-requirements.txt](local-requirements.txt) ファイルを更新してください。

## 改善方法

- 現在のスクリプトはPython公式ブログのニュースを取得するように設計されています。他のサイトに対応するには、URLやセレクタを変更する必要があります。
- スクレイピングのパフォーマンスを向上させるために、非同期処理や並列処理の導入を検討できます。
- データの保存形式をCSV以外（例: JSON, データベース）にも対応させることで、利便性を高めることができます。