# propelaigrowth.com

Propel AI 啟進智能決策 官網。靜態站，GitHub Pages 代管（main 分支根目錄）。

- 內容改版：改 `tools/build.py` 與來源（入口頁 hub 來源、data/*.json），重跑後把輸出放回根目錄。
- `CNAME` 指 propelaigrowth.com；`.nojekyll` 關掉 Jekyll。
- 文章：`data/articles.json`；客戶案例與推薦語：`data/clients.json`（空則頁面不產生）。
- AEO：`tools/aeo_patch.py <根目錄>` 產生 `/faq/`、課程頁「你可能想問」、JSON-LD、`robots.txt`、`llms.txt`；`build.py` 結尾會自動跑。問答原文以 `/quiz/` 的七題為準。
- 常見卡點 /q/：`tools/pain_pages.py <根目錄>` 從 `tools/data/pain_pages.json` 產生每個痛點句一頁（Article＋FAQPage）與索引；新增一題只要加一筆 JSON 再跑。
- 主選單與首頁痛點卡：`tools/nav_patch.py <根目錄>`——選單第一項「常見卡點」→ /q/，首頁三張痛點卡連到對應 /q/ 頁，「講師把關」一律改「講師帶你一起判斷」；`build.py` 結尾會自動跑，可重跑。
- 四步路徑條、麵包屑、網站地圖：`tools/wayfinding_patch.py <根目錄>`——中文內頁 `<main>` 開頭加「首頁 › … › 本頁」麵包屑，/q/、怎麼看問題、四個課程頁（含課前說明）、常見問題、為什麼是我們、聯絡加四步路徑條（① 找到卡住的事 ② 看懂為什麼 ③ 選一個開始 ④ 聊一聊，所在步亮橘）；產生 `/map/`（noindex），頁尾加「網站地圖」；首頁與 /en/ 不動；`build.py` 結尾會自動跑，可重跑。
