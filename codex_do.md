## 2026-01-04

- **确保数据库持久化**：`backend/app/database.py` 现在会优先使用 `DATABASE_PATH`/`DATABASE_DIR` 或 `/app/data` 创建 SQLite 文件，避免多实例导致的数据丢失。
- **环境变量示例更新**：`backend/.env.example` 新增了 `DATABASE_PATH` 的配置说明，方便本地/线上显式指定数据库文件位置。
- **Render 部署配置**：`render.yaml` 增加 `DATABASE_PATH=/app/data/pal_budget.db`，并配合现有磁盘挂载保证线上实例共享一份数据库。

> 说明：按照此方式记录后续的修改，便于你追踪我在仓库中的每次变更。
