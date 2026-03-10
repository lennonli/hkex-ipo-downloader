---
name: hkex-ipo-downloader
description: This skill automates the tracking of new listings on the HKEX Main Board and downloading relevant IPO documents. It should be used when the user wants to fetch "Display Documents" (展示文件) and "Prospectuses" (發售以供認購) for newly listed companies.
---

# HKEX IPO Downloader

## Overview

This skill provides a fully automated workflow to monitor the HKEX "New Listing Information" page, cross-reference with local storage to avoid duplicates, and download all PDF documents into organized folders.

## Workflow

To use this skill, follow these steps:

1. **New Listing Discovery**: The skill scrapes `https://www2.hkexnews.hk/New-Listings/New-Listing-Information/Main-Board?sc_lang=zh-HK` to identify the latest companies.
2. **Local Consistency Check**: It checks `/Users/licheng/Documents/港股IPO自动文档/` for folders named `YYYYMMDD+Company Name`.
3. **Document Search**: For each new listing, it searches the HKEX Announcement portal using the stock code.
4. **Download Categories**:
    - **Prospectuses (發售以供認購)**: Downloaded and named `[Company Name]招股说明书.pdf`.
    - **Display Documents (展示文件)**: All associated PDFs are downloaded with their original Chinese titles.
5. **PDF Extraction**: The skill handles both direct PDF links and "(多檔案)" index pages (`_c.htm`) by crawling them recursively.

6. **Scheduling**:
    - **Download**: Runs every Saturday at 20:00 (8 PM).
    - **Report**: Sends a weekly summary email every Monday at 10:00 AM.

## Resource Usage

### scripts/download_ipo_files.py
The main downloader.

### scripts/send_email_report.py
Generates and sends the weekly email report. **Required**: Configure `SENDER_EMAIL` and `SENDER_PASSWORD` (App Password) inside the script before use.

### scripts/setup_schedule.sh
Automates the creation of macOS `launchd` tasks for both scripts.

## Scheduling Setup

1. Open `scripts/send_email_report.py` and enter your email and App Password.
2. Run the setup script:
   ```bash
   bash scripts/setup_schedule.sh
   ```

## Sample Triggers

- "下载本周的新上市公司资料"
- "获取 HKEX 的招股说明书和展示文件"
- "检查港股新上市公司的公告"
