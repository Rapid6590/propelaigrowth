# propelaigrowth.com

Propel AI 啟進智能決策 官網。靜態站，GitHub Pages 代管（main 分支根目錄）。

- 內容改版：改 `tools/build.py` 與來源（入口頁 hub 來源、data/*.json），重跑後把輸出放回根目錄。
- `CNAME` 指 propelaigrowth.com；`.nojekyll` 關掉 Jekyll。
- 文章：`data/articles.json`；客戶案例與推薦語：`data/clients.json`（空則頁面不產生）。
- AEO：`tools/aeo_patch.py <根目錄>` 產生 `/faq/`、課程頁「你可能想問」、JSON-LD、`robots.txt`、`llms.txt`；`build.py` 結尾會自動跑。問答原文以 `/quiz/` 的七題為準。
- 常見卡點 /q/：`tools/pain_pages.py <根目錄>` 從 `tools/data/pain_pages.json` 產生每個痛點句一頁（Article＋FAQPage）與索引；新增一題只要加一筆 JSON 再跑。
- 主選單與首頁痛點卡：`tools/nav_patch.py <根目錄>`——選單第一項「常見卡點」→ /q/，首頁三張痛點卡連到對應 /q/ 頁，「講師把關」一律改「講師帶你一起判斷」；`build.py` 結尾會自動跑，可重跑。
- 文章頁：`tools/articles.py <根目錄>`——資料在 `tools/data/articles.json`（LinkedIn 貼文發出後把該則 `draft` 改 false 再跑），產生 `/articles/<slug>/` 與索引、BlogPosting JSON-LD、sitemap；圖放 `assets/articles/`，正文段落內 `\n` 為換行，`image_after` 指定第二張以後的圖插在第幾段之後；每篇結尾「接著看」連回 /q/ 與小測驗。順序：pain_pages → nav_patch → articles → wayfinding。
- 算算看 /calc/：`tools/calc_page.py <根目錄>`——「每一關多一點，最後差多少？」三條示範鏈（賣給消費者／賣給企業客戶／讓民眾辦得成），數字可改、全在瀏覽器裡算、不收資料；示範數字與改法在檔頭 `CHAINS`，全站統一免責句在 `DISCLAIMER`（別處要用照抄）；首頁第 02 段加一個入口。
- 主選單＝四步（v0.2，2026-11-18）：`tools/wayfinding_patch.py <根目錄>`——主選單就是 ① 找到卡住的事 ② 看懂為什麼 ③ 選一個開始 ④ 聊一聊（不再有另一條路徑條、也不再用名詞選單）；所在那步亮橘，下面一排列出這一步裡的頁面；第二層頁面（各題、課前說明、各篇文章）才放麵包屑；產生 `/courses/`（第三步入口，課程卡取自首頁）與 `/map/`（兩頁皆 noindex）。**主選單、展開列、/map/ 都從檔頭同一份 `STEPS` 產生——新增一頁只改那裡。** `/quiz/`、`/picker/` 是獨立工具頁，不放主選單；`/en/` 不動。一定最後跑（其他腳本借關於頁當外框，跑完要由它把選單狀態修正）。順序：pain_pages → nav_patch → articles → calc_page → wayfinding。`nav_patch.py` 的選單改寫已由本腳本取代，只剩首頁痛點卡與用語替換有作用。

- 選題器題目順序（v0.1，2026-11-18）：`tools/picker_order_patch.py <根目錄>`——講義題號照模組路線圖的順序編，這支把 `/picker/` 裡四個模組（工具沒人照做、產品沒在用、價格、購物車／民眾）的題目排成同一個順序。只動順序，不動文字與網址；可重跑。選題器來源檔不在 repo，所以用補丁做；來源檔哪天改了順序，這支會自己變成不動。順序：… → calc_page → picker_order_patch → wayfinding。

- 董事與高階主管場（v0.1，2026-11-18）：`tools/big_decisions_page.py <根目錄>`——產生 `/big-decisions/`「大決定之前，該問的都問了嗎？」（決策品質線；同一個網站底下的一頁），首頁課程段與 `/courses/` 底下各加一條入口，選單項目在 `wayfinding_patch.py` 的 `STEPS`。頁面上不放研究數字、不寫保證結果與免責。順序：… → calc_page → picker_order_patch → big_decisions_page → wayfinding。

- AI 頁（v0.1，2026-11-19）：`tools/ai_page.py <根目錄>`——產生 `/ai/`「AI 做得出東西；東西不會自己變成行為」（我們跟 AI 的關係；第二步「看懂為什麼」底下，選單上叫「AI 時代」），首頁第 02 段加一個入口，選單項目在 `wayfinding_patch.py` 的 `STEPS`。頁上的數字都對過原始報告；措辭規矩寫在檔頭（不寫導入失敗率、67% 對 32% 是相對重要性不是因果、AIF 兩個數字的分母是受訪企業）。順序：… → big_decisions_page → ai_page → wayfinding。

- 英文站（v0.1，2026-11-19）：`tools/en_patch.py <根目錄>`——英文五頁的主選單換成四步（① What's stuck ② See why ③ Pick a start ④ Talk to us；第 1、3 步連到英文首頁的段落，不展開），產生英文版算算看 `/en/calc/`（算式直接取自 `calc_page.py` 的 JS，介面字串逐句對照；示範數字跟中文版逐關核對，不一致會停下來），英文首頁第 02 段加入口，中文 `/calc/` 的 EN 指到英文算算看。選單在檔頭 `STEPS`，英文免責句在 `DISCLAIMER_EN`。**順序放最後**：… → wayfinding → en_patch。
