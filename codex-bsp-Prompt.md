# codex用

## 概要

この公式ではサポートされていないmicro python環境を作るリポジトリです。

## ファイル構成

``` text
add-BSP-microPython
│
├─ micropython/(サブモジュールで参照する)
│  ├─ py/
│  ├─ extmod/
│  └─ ports/
│
├─ boards/
│  ├─ nrf52/(native nrfのみ)
│  │  ├─ isp1507_ax/
│  │  ├─ isp1807/
│  │  ├─ HY0020/
│  │  └─ ...
│  │
│  └─ nrf91/(zephyrのみ)
│     ├─ nrf9160/
│     ├─ nrf9151/
│     └─ ...
│
├─ scripts/
│  └─ build.py(ローカルビルド用のスクリプト)
│
└─ .github/
   └─ workflows/
      └─ build.yml(公式のCIを使用したgithub上でのビルド)
```