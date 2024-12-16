# %%

import concurrent.futures
import datetime
import json
import logging
import time

import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s ')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
fh = logging.FileHandler('log.log', encoding='utf-8')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

OPTIONAL_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getDataList.action'
SELECTED_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getXzkcList.action'
FOO_JS_URL = 'https://jxfw.gdut.edu.cn/xsxklist!xsmhxsxk.action'

USER_COURSE_URL = 'https://jxfw.gdut.edu.cn/xsgrkbcx!getDataList.action'
COURSE_DATECODE_URL = 'https://jxfw.gdut.edu.cn/xsgrkbcx!getXsgrbkList.action'

ADD_COURSE_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getAdd.action'
CANCEL_COURSE_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getCancel.action'

KEYWORD_TAKE_FOO = 'xsxklist!getAdd.action'

VERIFY = False

COURSE_LIST_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getDataList.action'

GET_DETAIL_URL = 'https://jxfw.gdut.edu.cn/xsxklist!getJxrlDataList.action'


class TakeCourseFailed(Exception):
    pass


def obj2Json(obj, filename='a.json'):
    import json
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=4, separators=(',', ':')))


def json2Obj(path):
    import json
    with open(path, encoding='utf-8') as f:
        return json.loads(f.read())


# %%

class CourseItem(object):
    def __init__(self, row: dict):
        self.data: dict = row
        self.row: str = str(row)
        self.kcrwdm: str = row.get('kcrwdm')  # 课程内部代码
        self.pkrs: str = row.get('pkrs')  # 课程容量
        self.jxbdm: str = row.get('jxbdm')  # 教学班代码
        self.kcptdm: str = row.get('kcptdm')  # 课程班级代码
        self.xmmc: str = row.get('xmmc')  # 项目名称
        self.kcdm: str = row.get('kcdm')  # 课程代码
        self.kcmc: str = row.get('kcmc')  # 课程名称
        self.rwdm: str = row.get('rwdm')  # 任务代码
        self.xbyqdm: str = row.get('xbyqdm')  # 校区代码
        self.rs1: str = row.get('rs1')  # 人数1
        self.rs2: str = row.get('rs2')  # 人数2
        self.wyfjdm: str = row.get('wyfjdm')
        self.kkxqdm: str = row.get('kkxqdm')
        self.zxs: str = row.get('zxs')
        self.xf: str = row.get('xf')
        self.kcflmc: str = row.get('kcflmc')
        self.teaxm: str = row.get('teaxm')
        self.jxbrs: str = row.get('jxbrs')  # 已选人数

    def print(self, simple: bool = True):
        if simple:
            print(f'课程名称：{self.kcmc} \t课程容量：{self.pkrs} \t课程已选人数：{self.jxbrs}')
        else:
            print(
                f'课程名称：{self.kcmc} 课程代码：{self.kcdm} 课程性质：{self.kcflmc} 课程学分：{self.xf} 课程教师：{self.teaxm} 课程容量：{self.pkrs} 课程已选人数：{self.jxbrs} 课程剩余容量：{self.rs1} 课程已选人数：{self.rs2} 课程周学时：{self.zxs} 课程开课学期：{self.kkxqdm} 课程任务代码：{self.rwdm} 课程班级代码：{self.kcptdm} 课程教学班代码：{self.jxbdm} 课程项目名称：{self.xmmc} 课程任务代码：{self.rwdm} 课程项目名称：{self.xmmc}\n')

    def get_detail(self, user: 'User'):
        r = user.post(GET_DETAIL_URL, data={'kcrwdm': self.kcrwdm})
        print("ttt" + r.text)
        row = json.loads(r.text)[0]
        self.data.update(row)

        self.dgksdm: str = row.get("dgksdm")
        self.xnxqmc: str = row.get("xnxqmc")
        self.jxbmc: str = row.get("jxbmc")
        self.jxhjmc: str = row.get("jxhjmc")
        self.zc: str = row.get("zc")
        self.kxh: str = row.get("kxh")
        self.xs: str = row.get("xs")
        self.pkrs: str = row.get("pkrs")
        self.teadms: str = row.get("teadms")
        self.pklbdm: str = row.get("pklbdm")
        self.teaxms: str = row.get("teaxms")
        self.zdgnqmc: str = row.get("zdgnqmc")
        self.zdjxcdmc: str = row.get("zdjxcdmc")
        self.flfzmc: str = row.get("flfzmc")
        self.lhkm: str = row.get("lhkm")
        self.sknrjj: str = row.get("sknrjj")
        self.kcrwdm: str = row.get("kcrwdm")
        self.xnxqdm: str = row.get("xnxqdm")
        self.kbdm: str = row.get("kbdm")
        self.jxbdm: str = row.get("jxbdm")
        self.zdjxcddm: str = row.get("zdjxcddm")
        self.zdgnqdm: str = row.get("zdgnqdm")
        self.kkbmdm: str = row.get("kkbmdm")
        self.kkjysdm: str = row.get("kkjysdm")
        self.xq: str = row.get("xq")
        self.jcdm2: str = row.get("jcdm2")
        self.istj: str = row.get("istj")


class CoueseList(object):
    def __init__(self, rows: list):
        self.rows = rows
        self.course_list = []
        for row in rows:
            self.course_list.append(CourseItem(row))

    def print(self):
        for course in self.course_list:
            course.print()


class User:
    '''用户对象'''

    def __init__(self, cookies: dict):
        self._cookies = cookies
        self._headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://jxfw.gdut.edu.cn',
            'Pragma': 'no-cache',
            'Referer': 'https://jxfw.gdut.edu.cn/xsxklist!xsmhxsxk.action',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

    def post(self, url: str, data: dict) -> requests.models.Response:
        '''发送post请求，携带用户的cookies和headers'''
        logger.info(f'发送post请求 url={url} data={data}')
        r = requests.post(url=url, cookies=self._cookies, headers=self._headers, data=data,
                          )
        logger.info(f'请求结果：{r.text}')
        return r

    def get_course_list(self) -> CoueseList:
        '''获取可选课程列表'''

        data = {
            'page': '1',
            'rows': '360',
            'sort': 'kcrwdm',
            'order': 'asc',
        }
        logger.info(f'获取可选课程列表 data={data}')
        r = self.post(COURSE_LIST_URL, data=data)
        if '使用统一认证中心登录' in r.text:
            logger.warning('登录失效')
            raise '登录失效，请重新登录'
        courses = CoueseList(json.loads(r.text)['rows'])
        logger.info(f'查询到课程数量：{len(courses.course_list)}')
        return courses

    def \
            take_course(self, course: CourseItem) -> requests.models.Response:
        '''选课'''
        data = {
            # 'jxbdm': course.jxbdm,
            # 'jxbrs': course.jxbrs,
            # 'kcdm': course.kcdm,
            # 'kcflmc': course.kcflmc,
            'kcmc': course.kcmc,
            # 'kcptdm': course.kcptdm,
            'kcrwdm': course.kcrwdm,
            # 'kkxqdm': course.kkxqdm,
            # 'pkrs': course.pkrs,
            # 'rs1': course.rs1,
            # 'rs2': course.rs2,
            # 'rwdm': course.rwdm,
            # 'teaxm': course.teaxm,
            # 'wyfjdm': course.wyfjdm,
            # 'xbyqdm': course.xbyqdm,
            # 'xf': course.xf,
            # 'xmmc': course.xmmc,
            # 'zxs': course.zxs
        }
        logger.info(f'开始选课，课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        r = self.post(ADD_COURSE_URL, data=data)
        if r.text == '1':
            logger.info(f'选课成功，课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        elif r.text == '您已经选了该门课程':
            logger.info(
                f'课程已选择：{r.text} 课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        elif '超出选课要求门数' in r.text:
            logger.info(
                f'超出限选数量 （{r.text}）课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        else:
            msg = f'选课失败，错误原因：{r.text} 课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}'
            logger.info(msg)
            raise TakeCourseFailed(msg)
        return r

    def cancel_course(self, course: CourseItem) -> requests.models.Response:
        '''退课'''
        data = {
            'jxbdm': course.jxbdm,
            'kcrwdm': course.kcrwdm,
            'kcmc': course.kcmc,
        }
        logger.info(
            f'开始退课，课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        r = self.post(CANCEL_COURSE_URL, data=data)
        if r.text == '1':
            logger.info(
                f'退课成功，课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}')
        else:
            msg = f'退课失败，错误原因：{r.text} 课程名称：{course.kcmc} 课程代码：{course.kcdm} 课程内部代码：{course.kcrwdm}'
            logger.info(msg)
            raise TakeCourseFailed(msg)
        return r


# %%

cookies = json.load(open('cookies.json', 'r'))

user = User(cookies=cookies)


# courses = user.get_course_list()

# %%
# r = user.take_course(courses.course_list[0])
# r = user.take_course(target_course)


def worker(user: User, course: CourseItem) -> requests.models.Response:
    while True:
        try:
            result = user.take_course(course)
            if result:  # 如果函数成功退出，返回结果
                return result
        except Exception as e:
            time.sleep(0.2)


def fast_take_course():
    target_courses = [CourseItem({'kcrwdm': '1316674'})]
    target_courses[0].get_detail(user)
    target_courses[0].print()
    start_time = "2024-12-17 12:00:00"
    start_time_stamp = time.mktime(
        time.strptime(start_time, "%Y-%m-%d %H:%M:%S"))

    # 等待到选课开始前几秒
    while time.time() < start_time_stamp - 1:
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logger.warning(f"当前时间：{current_time}，等待选课开始，还有 {start_time_stamp - int(time.time())} 秒")
        time.sleep(1)

    # 开始多线程选课
    MAX_THREADS = 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS * len(target_courses)) as executor:
        futures = []  # 任务列表
        for target_course in target_courses:  # 为每个课程创建多个线程
            futures.extend(executor.submit(worker, user, target_course)
                           for _ in range(MAX_THREADS))
        for f in concurrent.futures.as_completed(futures):  # 遍历任务列表，等待任务完成
            print(f.result())


def test():
    target_course = CourseItem({'kcrwdm': '1316674'})
    target_course.get_detail(user)

    datas = []
    courses = user.get_course_list()
    for i, course in enumerate(courses.course_list):
        logger.info(f'正在获取课程详情：{i}/{len(courses.course_list)}')
        course.get_detail(user)
        datas.append(course.data)
        time.sleep(0.1)
        obj2Json(datas)


if __name__ == '__main__':
    fast_take_course()
    # test()
