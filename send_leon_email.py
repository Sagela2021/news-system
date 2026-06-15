name: Leon每日学术情报

on:
  schedule:
    - cron: '0 5 * * *'
  workflow_dispatch:

jobs:
  send-email:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 安装依赖
        run: pip install requests

      - name: 发送今日学术邮件
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          RESEND_API_KEY: ${{ secrets.RESEND_API_KEY }}
          RECEIVER_EMAIL: ${{ secrets.RECEIVER_EMAIL }}
        run: python send_leon_email.py
