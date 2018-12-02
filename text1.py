''' 中国大学 MOOC 定向爬虫 '''
import os
import re
import requests


def userinput():
    ''' 解析用户输入 '''
    # course = re.search(r'(\w+-\d+)', input("在此处输入 URL：")).group(1)
    course = ''
    course_page_url = 'http://www.icourse163.org/learn/' + course
    course_page = requests.get(course_page_url, headers=HEADER)
    course_id_number = re.search(r'id:(\d+),', course_page.text).group(1)
    return course_id_number


def parseinfo(course):
    ''' 解析课程所包含的内容 '''
    # 欲发送的数据信息
    postdata = {
        'callCount': '1',
        'scriptSessionId': '${scriptSessionId}190',
        'c0-scriptName': 'CourseBean',
        'c0-methodName': 'getMocTermDto',
        'c0-id': '0',
        'c0-param0': 'number:' + course,
        'c0-param1': 'number:1',
        'c0-param2': 'boolean:true',
        'batchId': '1492167717772'
    }
    rplsort = re.compile(r'^[第一二三四五六七八九十\d]+[\s\d\._章课节讲]*[\.\s、]\s*\d*')
    # 对文档内容进行解码，以便查看中文
    info = requests.post(INFO, headers=HEADER, data=postdata).text.encode(
        'utf-8').decode('unicode_escape')
    # 查找第 N 周的信息，并返回 [id,name]
    chaps = re.findall(r'homeworks=\w+;.+id=(\d+).+name="(.+)";', info)
    for chapcnt, chap in enumerate(chaps):
        print(chap[1])
        TOCFILE.write('%s {%d}\n' % (chap[1], chapcnt + 1))
        # 查找更小的结构，并返回 [id,name]
        secs = re.findall(r'chapterId=' + chaps[chapcnt][0]
                          + r'.+contentType=1.+id=(\d+).+name="(.+)".+test', info)
        for seccnt, sec in enumerate(secs):
            print('  ' + sec[1])
            TOCFILE.write('  %s {%d.%d}\n' % (sec[1], chapcnt + 1, seccnt + 1))
            # 查找视频，并返回 [contentid,contenttype,id,name]
            lessons = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId='
                                 + secs[seccnt][0] + r'.+name="(.+)"', info)
            # 查找文档，并返回 [contentid,contenttype,id,name]
            pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId='
                              + secs[seccnt][0] + r'.+name="(.+)"', info)
            for lsncnt, lsn in enumerate(lessons):
                TOCFILE.write('    %s {%d.%d.%d}\n' %
                              (lsn[3], chapcnt + 1, seccnt + 1, lsncnt + 1))
                print('    ' + lsn[3])
                name = rplsort.sub('', lsn[3])
                getcontent(lessons[lsncnt], '%d.%d.%d %s' %
                           (chapcnt + 1, seccnt + 1, lsncnt + 1, name))
            for pdfcnt, pdf in enumerate(pdfs):
                TOCFILE.write('    %s {%d.%d.%d}*\n' %
                              (pdf[3], chapcnt + 1, seccnt + 1, pdfcnt + 1))
                print('    【PDF】' + pdf[3])
                name = rplsort.sub('', pdf[3])
                getcontent(pdfs[pdfcnt], '%d.%d.%d %s' %
                           (chapcnt + 1, seccnt + 1, pdfcnt + 1, name))


def getcontent(lesson, name):
    ''' 获取每个资源的详细信息 '''
    filename = FILENAME_SAVE.sub(' ', name)
    if os.path.exists('PDFs\\' + filename + '.pdf'):
        print("------->文件已经存在！")
        return
    postdata = {
        'callCount': '1',
        'scriptSessionId': '${scriptSessionId}190',
        'httpSessionId': '5531d06316b34b9486a6891710115ebc',
        'c0-scriptName': 'CourseBean',
        'c0-methodName': 'getLessonUnitLearnVo',
        'c0-id': '0',
        'c0-param0': 'number:' + lesson[0],
        'c0-param1': 'number:' + lesson[1],
        'c0-param2': 'number:0',
        'c0-param3': 'number:' + lesson[2],
        'batchId': '1492168138043'
    }
    resource = requests.post(RESOURCE, headers=HEADER, data=postdata).text
    if lesson[1] == '1':
        # mp4url = re.search(r'mp4ShdUrl="(.*?)"', resource).group(1)
        mp4url = re.search(r'mp4ShdUrl="(.*\.mp4).*?"', resource).group(1)
        print('------->' + name + '.mp4')
        FILES.writelines('rename "' + re.search(r'(\w+_shd.mp4)', mp4url).group(1)
                         + '" "' + filename + '.mp4"' + '\n')
        DOWNLOAD.writelines(mp4url + '\n')
    else:
        pdfurl = re.search(r'textOrigUrl:"(.*?)"', resource).group(1)
        print('------->' + name + '.pdf')
        pdf = requests.get(pdfurl, headers=HEADER)
        if not os.path.isdir('PDFs'):
            os.mkdir(r'PDFs')
        with open('PDFs\\' + filename + '.pdf', 'wb') as file:
            file.write(pdf.content)


HEADER = {'User-Agent': 'Mozilla/5.0'}
INFO = 'http://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
RESOURCE = 'http://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'
FILENAME_SAVE = re.compile(r'[\\/:\*\?"<>\|]')

if __name__ == '__main__':
    FILES = open('Rename.bat', 'w', encoding='utf-8')
    FILES.writelines('chcp 65001\n')
    DOWNLOAD = open('Links.txt', 'w', encoding='utf-8')
    TOCFILE = open('TOC.txt', 'w', encoding='utf-8')
    COURSE_ID = userinput()
    parseinfo(COURSE_ID)
    FILES.close()
    DOWNLOAD.close()
    TOCFILE.close()