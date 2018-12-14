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
* 如果爬取的链接，用第三方无法下载，将链接复制到游览器会404的话（极少数课程出现这种情况）。可以尝试吧下载链接开头`http://v.stu.126.net/mooc-video/`部分替换为`http://jdvodrvfb210d.vod.126.net/jdvodrvfb210d/`，这个应该是慕课存储资源的路径问题。同时由于这个链接下载的文件命名也和Rename中的不同，需要将156行写入Rename.bat部分代码更换为下面
```python
with open('Rename.bat', 'a', encoding='utf-8') as file:
     video_down_url=re.sub(r'/','_',video_down_url)
     file.write('rename "' + re.search(r'http:.*video_(.*.mp4)', video_down_url).group(1) + '" "' + name +'.mp4"' + '\n')
```
* 部分链接如果无法下载失败（如果全部无法下载看上一条），这个不影响应该是爬虫爬到了已经被老师删除的资源，正常下载就是该课程所有的资源。


# TO DO LIST
* 下载文档按课程归类并指定存储路径
* 输入错误判定
* 加入直接搜索慕课功能

# 致谢
本程序思路来源于[Adam的程序](https://github.com/Dayunxi/getMOOCmedia)，感谢！