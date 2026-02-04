后端目标
1. 使用 uv 进行python版本和包管理. 使用 python 3.12
2. 使用 fastapi + aioauth + sqlalchemy 构建oauth2 server
3. 暂时不需要使用 docker + docker-compose 进行部署
4. 使用 pytest 进行测试
5. 使用 alembic 进行数据库迁移
6. 使用 pydantic 进行数据验证
前端目标
使用 sveltekit + tailwindcss + typescript 构建前端
测试:
构建一个演示 client, 完成 client 跳转到授权页面, 用户授权后, client 跳转回 redirect_uri, 并携带 code, client 使用 code 换取 access_token, 并使用 access_token 访问受保护资源的完整演示流程

额外要求:
1. 数据库使用 sqlite, 方便本地开发
2. 注意代码规范、项目可维护性、可读性
3. 充分理解代码即文档的理论, 尽量减少不必要的注释, 充分利用 pydantic 和 fastapi 的自文档特性
