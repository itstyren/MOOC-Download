# MOOC-Download 中国大学慕爬虫
项目为基于python3实现的爬虫，用于爬取指定课程资源的视频及可下载文档。


实现过程说明可以查看[我的博客](https://cyrusrenty.github.io//2018/12/03/moocspider/)

![](https://i.imgur.com/kpmVsqf.jpg)

# 特点
* 视频可选择清晰度，存储为下载链接，可使用第三方软件下载。
* 下载视频提供`Rename.bat`用于批量修改视频名称
* 所有文档按章节规范命名

# 使用方法
## 安装
```
pip install -r requirements.txt
```

## 使用
```
python main.py
```

# 注意事项
* 课程id为进入课程页面后，位于地址栏l中的，例如地址为：`https://www.icourse163.org/course/WHUT-1001861003?tid=1002066005` ，则课程id为：WHUT-1001861003
* 运行后会出现文档结构如下
```
MOOC_DOWNLOAD
  -- PDFs                     存放所有下载的pdf文档
       -- something1.pdf
       -- something2.pdf
  -- main.py                  主程序
  -- Links.txt                视频下载链接
  -- Rename.bat               视频下载完成后重命名程序（置于视频根目录下）
  -- TOC.txt                  爬取慕课的整体结构
  -- sth else
 ```

# TO DO LIST
* 下载文档按课程归类并指定存储路径
* 输入错误判定
* 加入直接搜索慕课功能

# 致谢
本程序思路来源于[Adam的程序](https://github.com/Dayunxi/getMOOCmedia)，感谢！