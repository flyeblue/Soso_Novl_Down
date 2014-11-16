# -*- coding: utf-8 -*-
"""
#=============================================================================
# Author: flying - 231138521@qq.com
#
# QQ : 231138521
#
# Last modified:	2014-11-16 08:12
#
# Filename:		soso_novel.py
#
# Description:
#
#=============================================================================
"""

import os
import urllib
import re
import requests
from bs4 import BeautifulSoup


class novel_serch(object):
    """
    通过soku.com网站搜索下载
    """
    home_url = "http://k.sogou.com/"
    headers = {"User-Agent":
               "Mozilla/5.0 (Windows NT 5.1; rv:33.0) "
               "Gecko/20100101 Firefox/33.0"}
    main_session = requests.Session()
    last_url = ""
    serch_key = ""
    serch_gets = list()
    show_last = 0
    serch_get_pre_page = ""
    serch_get_next_page = ""
    get_novel_name = ""
    get_novel_about = ""
    get_novel_mulu = list()
    isDebug = False

    def __init__(self, serchkey=""):
        self.serch_key = serchkey

    def internet_get(self, url, params=""):
        """
        读取指定网站并整理html
        """
        if url[0] == "/":
            url = self.home_url+url[1:]
        self.headers["content-encoding"] = "utf8"
        # print(url)
        if self.last_url:
            self.headers["Referer"] = urllib.parse.quote(self.last_url)
        # print(self.headers)
        if params:
            _getct = self.main_session.get(url,
                                           headers=self.headers,
                                           params=params)
        else:
            _getct = self.main_session.get(url, headers=self.headers)
        _getct.encoding = "utf8"
        _get_text = _getct.text.replace("&nbsp;", " ")
        _get_text = _get_text.replace("\xa0", " ")
        if self.isDebug:
            if os.path.exists("log.txt"):
                ff = "log2.txt"
            else:
                ff = "log.txt"
            print(_getct.url)
            with open(ff, "w", encoding="utf8", errors="ignore") as h_file:
                h_file.write(_get_text)
        self.last_url = url
        _get_bs = BeautifulSoup(_get_text)
        return _get_bs

    def serch(self, serch_k=""):
        """
        通过k.soku.com网站搜索小说
        """
        if not serch_k:
            serch_k = self.serch_key
        else:
            self.serch_key = serch_k
        _serch_value = dict()
        # 读取网友初始化参数
        _serch_bs = self.internet_get(self.home_url)
        _action, _serch_value = self.home_except(_serch_bs)
        _serch_value["keyword"] = serch_k
        # print(_serch_value)
        # 开始搜索
        _serch_bs = self.internet_get(_action,
                                      params=_serch_value)
        self.serch_except(_serch_bs)

    def home_except(self, home_bs):
        """
        分析搜索参数，以字典形式返回
        """
        _serchkey = dict()
        for _form in home_bs.findAll("form"):
            _ac = _form["action"]
            if _ac[:1] == "/":
                _ac = self.home_url + _ac[1:]
            else:
                _ac = self.home_url + _ac
            for _input in _form.findAll("input"):
                try:
                    _serchkey[_input["name"]] = _input["value"]
                except KeyError:
                    pass
        return _ac, _serchkey

    def serch_except(self, serch_bs):
        """
        结果页分析
        """
        for _serch_ in serch_bs.findAll("div", {"class": "con"}):
            for _li in _serch_.findAll("li"):
                _book_info = _li.find("a",
                                      {"href": re.compile("list.+")})
                if _book_info:
                    _book_temp = {"name": _book_info.text.strip()}
                    _book_temp["href"] = _book_info["href"]
                    # print("*******%s*********" % _book_info.text.strip())
                    _book_about = _li.find("p", {"class": "r_cont"})
                    if _book_about:
                        _book_temp["about"] = _book_about.text.strip()
                    else:
                        _book_temp["about"] = "无简介"
                        # print(_book_about.text.strip())
                    """
                    _book_last_page = _li.find("a",
                                               {"href": re.compile("detail.*")})
                    if _book_last_page:
                        print(_book_last_page.text.strip())
                    _book_last_time = _li.find("span",
                                               {"class": "green"})
                    if _book_last_time:
                        print(_book_last_time.text.strip())
                    _book_wangzhan = _li.find("span",
                                              {"class": "grey"})
                    if _book_wangzhan:
                        print(_book_wangzhan.text.strip())
                    _book_wangzh_all = _li.find("a",
                                                {"class": "grey",
                                                 "href": re.compile("souce.*")})
                    if _book_wangzh_all:
                        print(_book_wangzh_all.text.strip())
                    """
                    self.serch_gets.append(_book_temp)
        for _page_bs in serch_bs.findAll("div", {"id": "page"}):
            """
            for _page_num in _page_bs.findAll("span"):
                if _page_num:
                    print("这是第%5s页" % _page_num.text)
                else:
                    pass
            """
            for _a in _page_bs.findAll("a"):
                try:
                    if "pager_nextPage" in _a["class"]:
                        self.serch_get_next_page = _a["href"]
                        # print("下一页链接为：%s" % self.serch_get_next_page)
                    if "pager_prevPage" in _a["class"]:
                        self.serch_get_pre_page = _a["href"]
                        # print("上一页链接为：%s" % self.serch_get_pre_page)
                except KeyError:
                    pass

    def serch_show(self, show_number=5):
        """
        依据给定数字返回搜索结果，如果要求的数字大于已经获取的结果数则自动请求
        下一页。
        self.show_last 上次请求的最后编号
        show_number 设置返回的结果个数，默认5
        """
        _maxnum = self.show_last+show_number
        _last = self.show_last
        if not self.serch_gets:
            print("获取搜索结果异常")
            return
        """
        print("现有%s，本次获取第%s到%s。" %
              (len(self.serch_gets), _last, _maxnum))
        """
        if _maxnum > len(self.serch_gets):
            while self.serch_get_next_page:
                # print("读取下一页")
                _temp = self.internet_get(self.serch_get_next_page)
                self.serch_except(_temp)
                if len(self.serch_gets) > _maxnum:
                    break
        self.show_last = self.show_last+show_number
        if _last > len(self.serch_gets):
            return []
        return self.serch_gets[_last:_maxnum]

    def downbook(self, book):
        """
        """
        # print("下载%s" % bookurl)
        _bookdir = book["name"].replace(" ", "")
        if not os.path.exists(_bookdir):
            os.mkdir(_bookdir)
        print("开始分析目录页")
        _down_mulu_bs = self.internet_get(book["href"])
        self.mulu_except(_down_mulu_bs)
        self.page_down(book["name"])
        self.bookzip(_bookdir, "%s/%s.txt" % (_bookdir, _bookdir))

    def page_down(self, bname):
        """
        """
        _len = len(self.get_novel_mulu)
        _len_s = len(str(_len))
        print("开始下载%s...." % bname)
        for _ll in range(_len):
            _temp_name = "%s/%s.txt" % (bname, str(_ll).rjust(_len_s, "0"))
            _temp_name = _temp_name.replace(" ", "")
            print("下载(%s/%s)%s..." %
                  ((_ll+1), _len, self.get_novel_mulu[_ll]["章节名"]))
            _temp_ct = self.internet_get(self.get_novel_mulu[_ll]["href"])
            _temp_txt = self.page_except(_temp_ct)
            if _temp_txt:
                _temp_txt = "%s\n%s" % (self.get_novel_mulu[_ll]["章节名"],
                                        _temp_txt)
                with open(_temp_name, "w", encoding="utf8", errors="ignore"
                          ) as h_file:
                    h_file.write(_temp_txt)
            """
            """

    def page_except(self, page_bs):
        """
        """
        _temp2_txt = ""
        _ct = page_bs.find("div", {"id": "tc_content"})
        _br = _ct.findAll("br")
        [b.insert(0, "\n") for b in _br]
        _temp1 = _ct.text
        for _a in page_bs.findAll("a"):
            if "下一页" == _a.text.strip():
                _temp2_ct = self.internet_get(_a["href"])
                _temp2_txt = self.page_except(_temp2_ct)
        if _temp2_txt:
            _temp = "%s%s" % (_temp1, _temp2_txt)
        else:
            _temp = _temp1
        return _temp

    def mulu_except(self, mulu_bs):
        """
        目录页分析
        """
        for _a in mulu_bs.findAll("a"):
            if "全部章节" in _a.text.strip():
                # print("发现全部章节")
                mulu_bs = self.internet_get(_a["href"])
        for _li in mulu_bs.findAll("li"):
            _zj = dict()
            _num_re = re.compile("\[\d+\]")
            if _num_re.search(_li.text):
                _tt_re = re.compile("\](.*)")
                _tt = _tt_re.search(_li.text)
                if _tt:
                    _zj["章节名"] = _tt.group(1)
                    _zj["href"] = _li.a["href"]
                    # print(_zj)
                    self.get_novel_mulu.append(_zj)
        for _a in mulu_bs.findAll("a"):
            if "下一页" in _a.text.strip():
                mulu_bs = self.internet_get(_a["href"])
                self.mulu_except(mulu_bs)

    def bookzip(self, bookdir, bookfile="all.txt"):
        """
        合并指定目录内的所有txt文件
        bookdir --- 目录可以是相对目录或者绝对目录
        bookfile --- 合并后的文件名，默认为all.txt
        """
        if not os.path.exists(bookdir):
            print("%s目录不存在" % bookdir)
            return
        _flist = list()
        for root, dirs, files in os.walk(bookdir):
            for f in files:
                if f != bookfile and f[-4:] == ".txt":
                    _flist.append(f)
        _flist.sort()
        # _finsh = 1
        print("开始合并%s内文件..." % bookdir)
        with open(bookfile, "w", encoding="utf8", errors="ignore") as h_file:
            for f in _flist:
                # print("合并第%s个文件%s，剩余%s" % (_finsh, f, _all_number-_finsh))
                # _finsh += 1
                with open("%s/%s" % (bookdir, f),
                          "r",
                          encoding="utf8",
                          errors="ignore") as r_file:
                    temp = r_file.read()
                    h_file.write(temp)
                os.remove("%s/%s" % (bookdir, f))
        print("合并完成")


def main():
    aa = novel_serch()
    isExit = False
    while not isExit:
        print("*"*40)
        serch = input("请输入搜索的书名或者作者名，输入e退出：")
        print("-"*30)
        if serch:
            if serch.lower() == "e":
                isExit = True
                continue
            # 搜索并显示结果
            aa.serch(serch)
            gets = aa.serch_show()
            if not gets:
                print("未搜索到或者搜索异常，请重试")
                continue
            _number = 0
            isShow = True
            print("序号\t书名")
            while isShow:
                if gets:
                    for _g in gets:
                        print("%s\t%s" % (_number, _g["name"]))
                        _number += 1
                isInput = True
                while isInput:
                    print("+"*25)
                    _input = input("请输入相应序号，回车下一页，e放弃搜索：")
                    if not _input:
                        gets = aa.serch_show()
                        isInput = False
                        break
                    if "e" == _input.lower():
                        isShow = False
                        break
                    if _input.isalnum and int(_input) < _number:
                        _get_number = int(_input)
                        _get_book = aa.serch_gets[_get_number]
                        _ysdown = input("是否下载:%s\n %s\n"
                                        "直接回车下载，其他放弃:"
                                        % (_get_book["name"],
                                           _get_book["about"])
                                        )
                        if not _ysdown:
                            aa.downbook(_get_book)
                            isInput = False
                            isShow = False
                        else:
                            continue
                    else:
                        print("输入序号错误，请重新输入")
    """
    """


if __name__ == "__main__":
    main()