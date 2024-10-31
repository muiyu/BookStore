# BookStore
本仓库用于记录本小组对于“当代数据管理系统”课程项目的开发流程，并对开发代码进行归档。

原实验指南文件为 `Instruction.md` 。

## DB Schema
本项目采用 MongoDB ，其中数据的基本结构如下：
```
bookstore
    |-- user
        |-- user_id
        |-- password
        |-- balance
        |-- token                       用于保持会话，该值由 terminal 和 user_id 计算而来
        |-- terminal                    用于保持会话，该值同当前时间戳有关
        |-- collection: [book_id]
        |-- store_collection: [store_id]
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
    |-- new_order                       记录未付款订单，付款完成或取消会从库中移除记录，等待付款时间为5分钟，超时会自动取消订单
        |-- order_id
        |-- user_id
        |-- store_id
    |-- new_order_detail                记录未付款订单详情，付款完成或取消会从库中移除记录
        |-- order_id
        |-- book_id
        |-- count
        |-- price
    |-- user_store
        |-- user_id
        |-- store_id
    |-- books
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
```

## Dev Log
|日期        |进度             |详细描述             |
|------------|-----------------|--------------------|
|10/11|仓库初始化                 |无                    |
|10/15|重写数据库连接方式          |更改 SQLite API 为 MongoDB API                   |
|10/19|重构 be.model 结构         |将数据库连接部分从 be.store 中移出，独立为 be.database；修改 be.db_conn|
|10/23|重构 be 端                 |be 端对于 MongoDB 的适配完成，并添加了新功能                   |
|10/24|重构 fe 端                 |fe 端对于新 be 端的适配完成                   |
|10/25|初步测试通过                |小数据集上通过功能测试、压力测试、覆盖率测试             |
|10/27|新特性功能测试通过          |对新功能添加了测试代码，在小数据集测试通过             |
|10/28|拓展功能测试                |对拓展功能添加了测试代码，部分测试通过             |
|10/29|BUG修复                    |修复代码以通过测试；增加数据库索引；增加导入数据至 MongoDB 的脚本            |
|10/31|项目完成                   |所有测试通过，调整项目结构，发布最终版本，撰写实验报告            |

## Basic Feature
- 用户权限接口，如注册、登录、登出、注销
- 买家用户接口，如充值、下单、付款
- 卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存

以上基本功能相关测试均全部通过。

## Advanced Feature
- 订单操作补全接口
    - 支持卖家发货
    - 支持买家收货
- 图书搜索接口
    - 支持基于书籍书名，标签，目录，内容进行搜索
    - 支持全站搜索
    - 支持指定店铺搜索
- 订单状态接口
    - 支持查看订单历史与订单状态
    - 支持订单取消
    - 支持超时未付款系统自动取消订单

## New Feature
- 用户收藏夹接口
    - 支持用户收藏夹
    - 支持店铺收藏夹

## 待办
- [x] 提高新功能测试代码覆盖率
- [x] 导入书店数据至 MongoDB 数据库
- [x] 使用导入的完整书籍数据集进行测试
- [x] 提高拓展功能测试代码覆盖率
- [x] 增加索引
