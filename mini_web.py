import web_dongtai
import re
from pymysql import connect
import logging
# 默认调用application函数,字典加函数引用
# 函数用来返回header
# 再返回body
URL_DICT = dict()


def route(url):
    def set_fun(fun):
        URL_DICT[url] = fun
        def call_fun(*args,**kwargs):
            return fun(*args,**kwargs)
        return call_fun
    return set_fun


@route('/index.html')
def index(ret):

    with open('./index.html','rb') as fr:
        content = fr.read()
        # return content
    # my_stock_info = 'hahahahh'
    logging.warning('kaishilianjieshujuku啦'.encode('utf8'))
    conn = connect(host = 'localhost',port = 3306,user='root',password='1234',database = 'stock_info',charset = 'utf8')
    curse = conn.cursor()
    curse.execute('select* from info;')
    infos = curse.fetchall()

    tempalte = """<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td> 
            <td>%s</td>
          
    </tr>
    """
    html_content = ""
    for temp in infos:
        html_content += tempalte % (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],temp[7])
    content = content.decode('gbk')
    content = re.sub(r'\{%content%\}',html_content,content)
    curse.close()
    conn.close()
    return content.encode('gbk')


@route('/center.html')
def center(ret):

    with open('./center.html', 'rb') as fr:
        return fr.read()


@route('/add/(\d+)\.html')
def add_focus(ret):

    stock_code = ret.group(1)
    # 判断是否有股票代码
    conn = connect(host='localhost', port=3306, user='root', password='1234', database='stock_info', charset='utf8')
    curse = conn.cursor()
    sql = 'select* from info where code=%s;'
    curse.execute(sql,(stock_code,))
    stock_info = curse.fetchone()
    if not stock_info:
        curse.close()
        conn.close()
        return "没有该公司！"
     # 判断是否已经添加关注
    sql ="""select* from info as i inner join focus as f on i.id = f.info_id where i.code = %s;"""
    curse.execute(sql,(stock_code,))
    if curse.fetchone():
        return "已经关注了"
    # 添加关注
    sql = """insert into focus (info_id) select id from info where code = %s"""
    curse.execute(sql, (stock_code,))
    conn.commit()
    curse.close()
    conn.close()
    return 'add %s success' % stock_code

@route('/del/(\d+)\.html')
def del_focus(ret):

    stock_code = ret.group(1)
    # 判断是否有股票代码
    conn = connect(host='localhost', port=3306, user='root', password='1234', database='stock_info', charset='utf8')
    curse = conn.cursor()
    sql = 'select* from info where code=%s;'
    curse.execute(sql,(stock_code,))
    stock_info = curse.fetchone()
    if not stock_info:
        curse.close()
        conn.close()
        return "没有该公司！"
     # 判断是否已经添加关注
    sql ="""select* from info as i inner join focus as f on i.id = f.info_id where i.code = %s;"""
    curse.execute(sql,(stock_code,))
    if not curse.fetchone():
        curse.close()
        conn.close()
        return "您还未关注！"
    # 取消关注
    # sql = """insert into focus (info_id) select id from info where code = %s"""
    sql = """ delete form focus where info_id =(select id from info where code = %s);"""
    curse.execute(sql, (stock_code,))
    conn.commit()
    curse.close()
    conn.close()
    return 'del %s success' % stock_code

def application(environ,set_response):

    set_response('200 ok', [('Context-file', 'text.file'),
                            ('Content-Type', 'text/html;charset=gbk')])
    file_name = environ['PATHINFO']
    # if file_name == '/index.py':
    #     return index()
    # elif file_name == '/center.py':
    #     return center()
    # else:
    #     return '没有找到文件！'
    # print(file_name)
    # try:
    #     del_fun = URL_DICT[file_name]
    #     # print(del_fun)
    # except:
    #     return 'error request!'.encode('gbk')
    # else:
    #     return del_fun()
    #支持正则表达式
    logging.basicConfig(level=logging.INFO,
                        filename = './log.txt',
                        filemode='a',
                        format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s:%(message)s'
                        )

    logging.info("fangwendeshi%s"%file_name)

    try:
        for url,func in URL_DICT.items():
            ret = re.match(url,file_name)
            if ret:
                return func(ret)
    except:
        return ("error request!").encode('gbk')
    else:
        return ("没有请求的函数%s"%file_name).encode('gbk')


