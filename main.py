import requests
# from bs4 import BeautifulSoup
import re
import os

HEADER = {'User-Agent': 'Mozilla/5.0'}
SOURCE_INFO_URL = 'http://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
SOURCE_RESOURCE_URL = 'http://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'


class Course(object):
    '''
    存储课程相关信息

    '''

    def __init__(self, *args, **kwargs):
        self.course_page_url = 'http://www.icourse163.org/learn/'

    def set_course(self, course):
        self.course = course

    def get_course_info(self):
        '''
        获取课程基本信息
        获取课程id用于发送post请求
        '''
        course_page_url = self.course_page_url + self.course
        course_page = requests.get(course_page_url, headers=HEADER)
        id_pattern_compile = re.compile(r'id:(\d+),')
        # 获取课程名称
        basicinfo_pattern_compile = re.compile(
            r'<meta name="description" content=".*?,(.*?),(.*?),.*?/>')
        basic_set = re.search(basicinfo_pattern_compile, course_page.text)
        self.course_title = basic_set.group(1)
        self.course_collage = basic_set.group(2)
        self.course_id = re.search(id_pattern_compile,
                                   course_page.text).group(1)


def get_course_all_source(course_id):
    '''
    通过解析的course_id获取当前所有可下载的资源信息
    '''
    # 选择下载视频的清晰度
    video_level = select_video_level()
    # c0-param0：代表课程id
    # batchId：可以为任意时间戳
    # 其他字段为固定不变字段
    post_data = {
        'callCount': '1',
        'scriptSessionId': '${scriptSessionId}190',
        'c0-scriptName': 'CourseBean',
        'c0-methodName': 'getMocTermDto',
        'c0-id': '0',
        'c0-param0': 'number:' + course_id,
        'c0-param1': 'number:1',
        'c0-param2': 'boolean:true',
        'batchId': '1492167717772'
    }

    source_info = requests.post(
        SOURCE_INFO_URL, data=post_data, headers=HEADER)
    # 对文档内容进行解码，以便查看中文
    source_info_transcoding = source_info.text.encode('utf-8').decode(
        'unicode_escape')
    # 这里的id是一级目录id
    chapter_pattern_compile = re.compile(
        r'homeworks=.*?;.+id=(\d+).*?name="(.*?)";')
    # 查找所有一级级目录id和name
    chapter_set = re.findall(chapter_pattern_compile, source_info_transcoding)
    with open('TOC.txt', 'w', encoding='utf-8') as file:
        # 遍历所有一级目录id和name并写入目录
        for index, single_chaper in enumerate(chapter_set):
            file.write('%s    \n' % (single_chaper[1]))
            # 这里id为二级目录id
            lesson_pattern_compile = re.compile(
                r'chapterId=' + single_chaper[0] +
                r'.*?contentType=1.*?id=(\d+).+name="(.*?)".*?test')
            # 查找所有二级目录id和name
            lesson_set = re.findall(lesson_pattern_compile,
                                    source_info_transcoding)
            # 遍历所有二级目录id和name并写入目录
            for sub_index, single_lesson in enumerate(lesson_set):
                file.write('　%s    \n' % (single_lesson[1]))
                # 查找二级目录下视频，并返回 [contentid,contenttype,id,name]
                video_pattern_compile = re.compile(
                    r'contentId=(\d+).+contentType=(1).*?id=(\d+).*?lessonId='
                    + single_lesson[0] + r'.*?name="(.+)"')
                video_set = re.findall(video_pattern_compile,
                                       source_info_transcoding)
                # 查找二级目录下文档，并返回 [contentid,contenttype,id,name]
                pdf_pattern_compile = re.compile(
                    r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                    single_lesson[0] + r'.+name="(.+)"')
                pdf_set = re.findall(pdf_pattern_compile,
                                     source_info_transcoding)
                name_pattern_compile = re.compile(
                    r'^[第一二三四五六七八九十\d]+[\s\d\._章课节讲]*[\.\s、]\s*\d*')
                # 遍历二级目录下视频集合，写入目录并下载
                count_num = 0
                for video_index, single_video in enumerate(video_set):
                    rename = re.sub(name_pattern_compile, '', single_video[3])
                    file.write('　　[视频] %s \n' % (rename))
                    get_content(
                        single_video, '%d.%d.%d [视频] %s' %
                        (index + 1, sub_index + 1, video_index + 1, rename),
                        video_level)
                    count_num += 1
                # 遍历二级目录下pdf集合，写入目录并下载
                for pdf_index, single_pdf in enumerate(pdf_set):
                    rename = re.sub(name_pattern_compile, '', single_pdf[3])
                    file.write('　　[文档] %s \n' % (rename))
                    get_content(
                        single_pdf, '%d.%d.%d [文档] %s' %
                        (index + 1, sub_index + 1, pdf_index + 1 + count_num,
                         rename))


def get_content(single_content, name, *args):
    '''
    如果是文档，则直接下载
    如果是视频，则保存链接供第三方下载
    '''
    # 检查文件命名，防止网站资源有特殊字符本地无法保存
    file_pattern_compile = re.compile(r'[\\/:\*\?"<>\|]')
    name = re.sub(file_pattern_compile, '', name)
    # 检查是否有重名的（即已经下载过的）
    if os.path.exists('PDFs\\' + name + '.pdf'):
        print(name + "------------->已下载")
        return
    post_data = {
        'callCount': '1',
        'scriptSessionId': '${scriptSessionId}190',
        'httpSessionId': '5531d06316b34b9486a6891710115ebc',
        'c0-scriptName': 'CourseBean',
        'c0-methodName': 'getLessonUnitLearnVo',
        'c0-id': '0',
        'c0-param0': 'number:' + single_content[0],  # 二级目录id
        'c0-param1': 'number:' + single_content[1],  # 判定文件还是视频
        'c0-param2': 'number:0',
        'c0-param3': 'number:' + single_content[2],  # 具体资源id
        'batchId': '1492168138043'
    }
    sources = requests.post(
        SOURCE_RESOURCE_URL, headers=HEADER, data=post_data).text
    # 如果是视频的话
    if single_content[1] == '1':
        try:
            if args[0] == 'a':
                download_pattern_compile = re.compile(
                    r'mp4SdUrl="(.*?\.mp4).*?"')
            elif args[0] == "b":
                download_pattern_compile = re.compile(
                    r'mp4HdUrl="(.*?\.mp4).*?"')
            else:
                download_pattern_compile = re.compile(
                    r'mp4ShdUrl="(.*?\.mp4).*?"')
            video_down_url = re.search(download_pattern_compile,
                                       sources).group(1)
        except AttributeError:
            print('－－－－－－－－－－－－－－－－－－－－－－－－')
            print(name + '没有该清晰度格式，降级处理')
            print('－－－－－－－－－－－－－－－－－－－－－－－－')
            download_pattern_compile = re.compile(r'mp4SdUrl="(.*?\.mp4).*?"')
            video_down_url = re.search(download_pattern_compile,
                                       sources).group(1)
        print('正在存储链接：' + name + '.mp4')
        with open('Links.txt', 'a', encoding='utf-8') as file:
            file.write('%s \n' % (video_down_url))
        with open('Rename.bat', 'a', encoding='utf-8') as file:
            video_down_url = re.sub(r'/', '_', video_down_url)
            file.write('rename "' + re.search(
                r'http:.*video_(.*.mp4)', video_down_url).group(1) + '" "' +
                       name + '.mp4"' + '\n')

    # 如果是文档的话
    else:
        pdf_download_url = re.search(r'textOrigUrl:"(.*?)"', sources).group(1)
        print('正在下载：' + name + '.pdf')
        pdf_file = requests.get(pdf_download_url, headers=HEADER)
        if not os.path.isdir('PDFs'):
            os.mkdir(r'PDFs')
        with open('PDFs\\' + name + '.pdf', 'wb') as file:
            file.write(pdf_file.content)


def select_video_level():
    '''
    选择视频质量
    '''
    print('\n')
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    print("|　请选择视频质量：　　　　　　　　　　　　　　|")
    print("|　　　　　　　　　　　　　　　　　　　　　　　|")
    print("|（ａ）标清　　　（ｂ）高清　　　（ｃ）超清　　|")
    print("|　　　　　　　　　　　　　　　　　　　　　　　|")
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    video_level = input('请选择（a或b或c）')
    level = {'a': "标清", 'b': '高清', 'c': "超清"}
    print('\n')
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    print('视频将下载为【' + level.get(video_level) + '】')
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    print('\n')
    return (video_level)


def check_select_course(course):
    '''
    提供用户监测输入的课程编号是否正确
    '''
    print("\n")
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    print('您选择的是：')
    print(course.course_title + '\n' + course.course_collage)
    print('－－－－－－－－－－－－－－－－－－－－－－－－')
    return input('请确认输入（y/n）：')


def main():
    course = Course()
    # 因为Links文件夹为追加模式打开，所以需要事先删除
    if os.path.exists('Links.txt'):
        os.remove('Links.txt')
    # 同样是追加模式，首先删除原来的，然后确定新的编码格式
    if os.path.exists("Rename.bat"):
        os.remove("Rename.bat")
        with open('Rename.bat', 'a', encoding='utf-8') as file:
            file.writelines('chcp 65001\n')
    while True:
        course.set_course(input("\n请输入课程id（例如SICNU-1002031014）"))
        course.get_course_info()
        if check_select_course(course) == 'y':
            break
    get_course_all_source(course.course_id)


if __name__ == '__main__':
    main()