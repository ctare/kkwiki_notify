# pukiwikiの変更を監視して通知を送るツール

## 実行
`python wiki.py`


## 準備
* tokens.py
    - SLACK_BOT にslack botのapi tokenを入れる
    - WIKI にwikiの承認情報を入れる
        + 適当なwikiのページにアクセスする
        + リクエストヘッダー内のAuthorizationの値

wiki内データを取るだけならWIKIだけ埋める
