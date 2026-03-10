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

## Resource Usage

### scripts/download_ipo_files.py

This is the main entry point for the automation. To run the full downloader:

```bash
python3 scripts/download_ipo_files.py
```

It uses Playwright for browser automation and directly saves PDFs to the local filesystem.

## Sample Triggers

- "下载本周的新上市公司资料"
- "获取 HKEX 的招股说明书和展示文件"
- "检查港股新上市公司的公告"
