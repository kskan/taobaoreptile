from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import csv
import os,sys

def app_path():
    """Returns the base application path."""
    if hasattr(sys, 'frozen'):
        # Handles PyInstaller
        return os.path.dirname(sys.executable)  # 使用pyinstaller打包后的exe目录
    return os.path.dirname(__file__)

def createcsv():
    global tabel
    path = app_path()+"/taobao.csv"
    with open(path, 'w') as f:
        csv_write = csv.writer(f)
        csv_head = ["bigimg","title","price","longimg"]
        csv_write.writerow(csv_head)

def write_csv(data_row):
    path = app_path()+"/taobao.csv"
    with open(path,'a+') as f:
        csv_write = csv.writer(f)
        csv_write.writerow(data_row)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

if __name__ == '__main__':
    # 登陆密码和账号
    print("——————————————欢迎使用商品爬虫————————————————")
    print("1.本系统适用于现在用户在商品于兽次元商品同步问题，代码完全开源，但是请勿对其他友商进行攻击或者窃取，本系统一概不负责")
    print("2.使用本系统确保您的机子有Chrome85版本，且现在已经登陆淘宝账号（稍后爬虫需要使用）")
    print("3.请前往您自己的商品，所有分类(xxxxx.taobao.com/search.htm),（爬虫数据）")
    print("4.爬虫中会出现chrome来回切换，请勿手动关闭，爬虫完毕会自动关闭")
    print("5.爬虫完毕，后期就会出现csv文件，请从兽次元后台继续操作")
    print("——————————————点击回车继续————————————————")
    input()
    print('请输入(淘宝)账号：')
    username = input()
    print('请输入（淘宝）密码：')
    passworld = input()
    print('请输入您的店铺搜索页面：')
    url = input()
    #启动浏览器
    driver = webdriver.Chrome(executable_path=app_path()+"/chromedriver.exe")
    driver.maximize_window()
    driver.get(
        'https://login.taobao.com/member/login.jhtml?redirectURL=http%3A%2F%2Ftrade.taobao.com%2Ftrade%2Fitemlist%2Flist_sold_items.htm%3Fspm%3Da313o.201708ban.category.d28.64f0197aAFB4S5%26mytmenu%3Dymbb')
    js1 = '''Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) '''
    js2 = '''window.navigator.chrome = { runtime: {},  }; '''
    js3 = '''Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); '''
    js4 = '''Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); '''
    driver.execute_script(js1)
    driver.execute_script(js2)
    driver.execute_script(js3)
    driver.execute_script(js4)
    js = """
        document.getElementById('fm-login-id').value='{0}';
        document.getElementById('fm-login-password').value='{1}';
        document.getElementsByClassName('fm-submit')[0].click()
    """.format(username, passworld)
    driver.execute_script(js)
    try:
        element = driver.find_element_by_id('nc_1__scale_text')
        ActionChains(driver).drag_and_drop_by_offset(element, 400, 0).perform()
        time.sleep(2)
        driver.execute_script(js)
    except:
        print('无滑块')
        pass
    driver.get(url)
    # 检查页数
    pagesize = 1
    createcsv()
    # 正在查找页数
    print("正在查找页数")
    pagelist = driver.find_elements_by_class_name("J_SearchAsync")
    for page in pagelist:
        if is_number(page.text) and pagesize<int(page.text) :
            pagesize = int(page.text)
    for index in range(1,pagesize+1):
        print("现在页数："+str(index))
        if index is not 1:
            driver.get(url+"?pageNo="+str(index))
        item = driver.find_elements_by_class_name("item")
        dict = {}
        for  data in item:
            datatext=data.get_attribute("innerHTML")
            p= re.compile(r"\"\/\/item.taobao.com\/item\.htm\?id=(.*?)\"")
            numbers= p.findall(datatext)
            def check(numbers):
                for one in numbers:
                    p1 = re.compile(r"([&][^&]+)$")
                    one = p1.sub("", one)
                    return one
            dict[check(numbers)]=None;
        for a in dict:
            csvlist = []
            print("正在获取："+a)
            driver.get("https://item.taobao.com/item.htm?id="+a)
            #获取大图
            image = driver.find_element_by_id("J_ImgBooth")
            bigsrc = image.get_attribute("src")
            title = driver.find_element_by_class_name("tb-main-title")
            titlename = title.get_attribute("data-title")
            price = driver.find_element_by_class_name("tb-rmb-num").get_attribute("innerHTML")
            csvlist.append(bigsrc)
            csvlist.append(titlename)
            csvlist.append(price)
            longimglist = driver.find_element_by_id("J_DivItemDesc")
            longimglist = longimglist.find_elements_by_tag_name("img")
            for longimg in longimglist:
                csvlist.append(longimg.get_attribute("src"))
            write_csv(csvlist)
    driver.close()
    print("数据爬虫完毕")


