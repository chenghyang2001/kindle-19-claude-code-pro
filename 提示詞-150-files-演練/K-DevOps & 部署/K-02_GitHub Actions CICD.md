# K-02　GitHub Actions CI/CD

> **類別**：K. DevOps & 部署

---

```
建立 GitHub Actions 工作流程：
觸發條件：push to main / PR to main
步驟：
1. 程式碼品質檢查（lint + type check）
2. 單元測試（含覆蓋率報告）
3. 整合測試
4. 建構 Docker 映像
5. 部署到 （Vercel / GCP / AWS）（只在 main branch）
要求：測試通過才部署，機密用 GitHub Secrets。
```
