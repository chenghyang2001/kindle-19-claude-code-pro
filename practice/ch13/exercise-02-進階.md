# 練習 02 — 進階：CRUD API 實作

## 情境說明
你要為 Freelancer Dashboard 的「客戶管理」功能實作完整的 CRUD API。

## 任務

### 任務 1：API 端點設計
設計客戶管理的 RESTful API：

| Method | 路徑 | 功能 | 需要認證 |
|--------|------|------|---------|
| GET | /api/clients | 取得所有客戶 | 是 |
| POST | /api/clients | 建立新客戶 | 是 |
| GET | /api/clients/[id] | 取得單一客戶 | 是 |
| PUT | /api/clients/[id] | 更新客戶資料 | 是 |
| DELETE | /api/clients/[id] | 刪除客戶 | 是 |

對每個端點設計：
- Request body 格式（含 Zod 驗證 schema）
- 成功回應格式
- 可能的錯誤回應（400 / 401 / 404 / 500）

### 任務 2：實作最複雜的端點 + 測試
選 `POST /api/clients` 實作完整邏輯：
1. 認證中介軟體（確認使用者已登入）
2. Zod 驗證 Request body
3. 資料庫寫入（Drizzle ORM）
4. 成功回傳 201 + 新建立的客戶資料
5. 錯誤回傳對應的 4xx / 500

同時寫整合測試：
- 測試：認證 token 無效 → 401
- 測試：缺少必填欄位 → 400
- 測試：成功建立 → 201 + 回傳資料

## 延伸思考
思考：如果兩個使用者同時編輯同一個客戶資料，可能發生什麼問題？你會怎麼在 API 層面防範？

## 完成後
將 API 設計 + 程式碼 + 測試存入 `answer/ex02-answer.md`
