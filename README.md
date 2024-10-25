# BookStore
本项目用于记录本小组对于“当代数据管理系统”课程项目的开发流程，并对开发代码进行归档。

## DB Schema
本项目采用 MongoDB ，其中数据的基本结构如下：
```
bookstore
    |-- user
        |-- user_id
        |-- password
        |-- balance
        |-- token               用于保持会话，该值由 terminal 和 user_id 计算而来
        |-- terminal            用于保持会话，该值同当前时间戳有关
        |-- collection: [book_id]
    |-- store
        |-- store_id
        |-- book_id
        |-- stock_level
        |-- book_info
            |-- tags
            |-- pictures
            |-- id
            |-- title
            |-- author
            |-- publisher
            |-- original_title
            |-- translator
            |-- pub_year
            |-- pages
            |-- price
            |-- binding
            |-- isbn
            |-- author_intro
            |-- book_intro
            |-- content
    |-- order_history
        |-- order_id
        |-- user_id
        |-- store_id
        |-- status: ["pending"/"cancelled"/"paid"/"shipped"/"received"]
    |-- order_history_detail
        |-- order_id
        |-- book_id
        |-- count
        |-- price
    |-- new_order               记录未付款订单，付款完成或取消会从库中移除记录，等待付款时间为5分钟，超时会自动取消订单
        |-- order_id
        |-- user_id
        |-- store_id
    |-- new_order_detail        记录未付款订单详情，付款完成或取消会从库中移除记录
        |-- order_id
        |-- book_id
        |-- count
        |-- price
    |-- user_store
        |-- user_id
        |-- store_id
```

## Dev Log

|日期        |进度             |详细描述             |
|------------|-----------------|--------------------|
|10/11|仓库初始化                 |无                    |
|10/15|重写数据库连接方式          |更改 SQLite API 为 MongoDB API                   |
|10/19|重构 be.model 结构         |将数据库连接部分从 be.store 中移出，独立为 be.database；修改 be.db_conn|
|10/23|重构 be 端                 |be 端对于 MongoDB 的适配完成，并添加了新功能                   |
|10/24|重构 fe 端                 |fe 端对于新 be 端的适配完成                   |
|10/25|初步测试通过               |小数据集上通过基本功能测试，`test_login` 未通过             |

## New Feature
- 支持通过书名、内容、标签搜索书籍，允许在算选定店铺中搜索
- 支持取消订单
- 支持查看历史订单
- 支持书籍收藏
