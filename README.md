This implements the Ruby on Rails Tutorial using Python, Flask, Google App Engine and Cloud Datastore.

## 使い方

ローカルで起動するにはアプリのトップディレクトリで環境変数 FLASK_APP を sampleapp に設定して起動して下さい。

例：
```bash
$ rm -rf venv # 必要に応じて行う。
$ python -m venv venv
$ . venv/bin/activate
(env) $ pip install -r requirements.txt
(env) $ FLASK_APP=sampleapp flask run --port=5001 # port指定はオプション
# (Ctrl-C で終了後必要に応じて以下を行いvenvから抜ける)
(env) $ deactivate
```

但しユーザー登録等データベースにアクセスする必要がある処理はローカルでは動きません。

起動画面と、ソースコードを参照する程度でお使い下さい。
