
# WebKICのAnkiデッキのリポジトリ

## デッキの作成プログラム

アメリカ・カナダ大学連合日本研究センターのKanji In Contextのオンライン教科書（WebKIC）の学生開発者向けのリポジトリです。

`get_cards.py`というPython（３バージョン）ファイルを使ってAnkiデッキに変換するCSVファイルが作成できます。

※センターのコンテンツが含まれているので、Ankiのデッキは投稿されていない。このプログラムを使うのにWebKICのアカウントが必要です。起動するとアカウントのログインの情報を記入してください。（この情報は保存されていません。）

### インストール方法

`pip install -r requirements.txt`

`webdriver-manager`のモジュールで必要なSeleniumドライバーが自動的にダウンロードされますが、Firefoxも必要です。もし他のウェブブラウザを使う場合、`Gecko`という部分を更新する必要があります。[Selenium](https://selenium-python.readthedocs.io/api.html)と[webdriver-manager](https://pypi.org/project/webdriver-manager/)のドキュメント（英語版）をご覧くだいさい。

SVGファイルを最適化するのに（`--optimize`のフラグを使う場合）NodeJSとSVGOパッケージが必要です。

### プログラムの構造

ウェブスクレイピングを使ってWebKICのフラッシュカード機能から単語をダウンロードします。

### CLIパラメータ

`site` WebKICのサイトへのリンク

`output` フラッシュカードのコンテンツの保存先

`anki` SVGファイルの保存先

`-l, --lesson` KICの１課からどの課までダウンロードするか

`-o, --overwrite-svg` SVGファイルを上書きする

`-t, --timeout` 読み込みをタイムアウトするまでの時間

`-x, --extra` 基本語だけではなく全ての単語をダウンロードする

`--optimize` NodeJSのSVGOパッケージを使ってSVGファイルを最適化する

`--no-headless` ウェブブラウザのウィンドウを表示する

`--no-backup` ダウンロードしたカードのコンテンツをバックアップしない

## 他のファイル

`ノート.apkg`というファイルはAnkiデッキのサンプルです。カードのスタイル情報と例のノートだけです。

`color_code.js`というファイルはAnkiデッキで使わているJSのソースコードです。フラッシュカードのSVGファイルを文字ごとに彩ります。
