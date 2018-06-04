#!/usr/bin/env python
# Author: 'JiaChen'

from django.utils.safestring import mark_safe


class Page(object):
    """分页类"""
    def __init__(self, current_page, total_items, per_items=20, page_num=11):
        """
        :param current_page: 当前页数
        :param total_items: 数据总数
        :param per_items: 每页显示数
        :param page_num: 最多显示页码数
        """
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        self.current_page = current_page
        self.total_items = total_items
        self.per_items = per_items
        self.page_num = page_num

    @property
    def total_page(self):
        if not self.total_items:
            self.total_items = 0
        val = self.total_items / self.per_items + 1 if self.total_items % self.per_items > 0 else self.total_items / self.per_items
        return int(val)

    @property
    def start(self):
        val = (self.current_page - 1) * self.per_items
        return val

    @property
    def end(self):
        val = self.current_page * self.per_items
        return val

    def pager(self, base_url, host_group_id=None, host_id=None, template_id=None, application_id=None):
        """
        :param base_url: 基础页的url
        :param host_group_id: 主机组ID
        :param host_id: 主机ID
        :param template_id: 模板ID
        :return:
        """
        page_html = []
        page = self.current_page            # 当前页
        all_page_count = self.total_page    # 总页数
        total_items = self.total_items      # 数据总数

        if host_group_id is not None and host_id is None:
            # 首页
            first_html = "<li><a href='%s?groupid=%d&p=1'>首页</a></li>" % (base_url, host_group_id)
            page_html.append(first_html)
            # 上一页
            if page <= 1:
                prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
            else:
                prev_html = "<li><a href='%s?groupid=%d&p=%d'>上一页</a></li>" % (base_url, host_group_id, page - 1)
            page_html.append(prev_html)
            # 11个页码
            if all_page_count < 11:
                begin = 0
                end = all_page_count
            # 总页数大于 11
            else:
                #
                if page < 6:
                    begin = 0
                    end = 11
                else:
                    if page + 6 > all_page_count:
                        begin = page - 6
                        end = all_page_count
                    else:
                        begin = page - 6
                        end = page + 5
            for i in range(begin, end):
                # 当前页
                if page == i + 1:
                    a_html = "<li class='active'><a href='javascript:void(0)'>%d</a></li>" % (i + 1)
                else:
                    a_html = "<li><a href='%s?groupid=%d&p=%d'>%d</a></li>" % (base_url, host_group_id, i + 1, i + 1)
                page_html.append(a_html)
            # 下一页
            if page + 1 > all_page_count:
                next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
            else:
                next_html = "<li><a href='%s?groupid=%d&p=%d'>下一页</a></li>" % (base_url, host_group_id, page + 1)
            page_html.append(next_html)
            # 尾页
            end_html = "<li><a href='%s?groupid=%d&p=%d'>尾页</a></li>" % (base_url, host_group_id, all_page_count)
            page_html.append(end_html)
            # 页码概要
            end_html = "<li><a href='javascript:void(0)'>共 %d页 / %d 条数据</a></li>" % (all_page_count, total_items)
            page_html.append(end_html)
            # 将列表中的元素拼接成页码字符串
            page_str = mark_safe(''.join(page_html))
        elif host_group_id is not None and host_id is not None:
            # 首页
            first_html = "<li><a href='%s?groupid=%d&hostid=%d&p=1'>首页</a></li>" % (base_url, host_group_id, host_id)
            page_html.append(first_html)
            # 上一页
            if page <= 1:
                prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
            else:
                prev_html = "<li><a href='%s?groupid=%d&hostid=%d&p=%d'>上一页</a></li>" % (base_url,
                                                                                         host_group_id,
                                                                                         host_id,
                                                                                         page - 1)
            page_html.append(prev_html)
            # 11个页码
            if all_page_count < 11:
                begin = 0
                end = all_page_count
            # 总页数大于 11
            else:
                #
                if page < 6:
                    begin = 0
                    end = 11
                else:
                    if page + 6 > all_page_count:
                        begin = page - 6
                        end = all_page_count
                    else:
                        begin = page - 6
                        end = page + 5
            for i in range(begin, end):
                # 当前页
                if page == i + 1:
                    a_html = "<li class='active'><a href='javascript:void(0)'>%d</a></li>" % (i + 1)
                else:
                    a_html = "<li><a href='%s?groupid=%d&hostid=%d&p=%d'>%d</a></li>" % (base_url,
                                                                                         host_group_id,
                                                                                         host_id,
                                                                                         i + 1,
                                                                                         i + 1)
                page_html.append(a_html)
            # 下一页
            if page + 1 > all_page_count:
                next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
            else:
                next_html = "<li><a href='%s?groupid=%d&hostid=%d&p=%d'>下一页</a></li>" % (base_url,
                                                                                         host_group_id,
                                                                                         host_id,
                                                                                         page + 1)
            page_html.append(next_html)
            # 尾页
            end_html = "<li><a href='%s?groupid=%d&hostid=%d&p=%d'>尾页</a></li>" % (base_url,
                                                                                   host_group_id,
                                                                                   host_id,
                                                                                   all_page_count)
            page_html.append(end_html)
            # 页码概要
            end_html = "<li><a href='javascript:void(0)'>共 %d页 / %d 条数据</a></li>" % (all_page_count, total_items)
            page_html.append(end_html)
            # 将列表中的元素拼接成页码字符串
            page_str = mark_safe(''.join(page_html))
        elif template_id is not None:
            # 首页
            first_html = "<li><a href='%s?templateid=%d&p=1'>首页</a></li>" % (base_url, template_id)
            page_html.append(first_html)
            # 上一页
            if page <= 1:
                prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
            else:
                prev_html = "<li><a href='%s?templateid=%d&p=%d'>上一页</a></li>" % (base_url, template_id, page - 1)
            page_html.append(prev_html)
            # 11个页码
            if all_page_count < 11:
                begin = 0
                end = all_page_count
            # 总页数大于 11
            else:
                #
                if page < 6:
                    begin = 0
                    end = 11
                else:
                    if page + 6 > all_page_count:
                        begin = page - 6
                        end = all_page_count
                    else:
                        begin = page - 6
                        end = page + 5
            for i in range(begin, end):
                # 当前页
                if page == i + 1:
                    a_html = "<li class='active'><a href='javascript:void(0)'>%d</a></li>" % (i + 1)
                else:
                    a_html = "<li><a href='%s?templateid=%d&p=%d'>%d</a></li>" % (base_url, template_id, i + 1, i + 1)
                page_html.append(a_html)
            # 下一页
            if page + 1 > all_page_count:
                next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
            else:
                next_html = "<li><a href='%s?templateid=%d&p=%d'>下一页</a></li>" % (base_url, template_id, page + 1)
            page_html.append(next_html)
            # 尾页
            end_html = "<li><a href='%s?templateid=%d&p=%d'>尾页</a></li>" % (base_url, template_id, all_page_count)
            page_html.append(end_html)
            # 页码概要
            end_html = "<li><a href='javascript:void(0)'>共 %d页 / %d 条数据</a></li>" % (all_page_count, total_items)
            page_html.append(end_html)
            # 将列表中的元素拼接成页码字符串
            page_str = mark_safe(''.join(page_html))
        elif application_id is not None:
            # 首页
            first_html = "<li><a href='%s?applicationid=%d&p=1'>首页</a></li>" % (base_url, application_id)
            page_html.append(first_html)
            # 上一页
            if page <= 1:
                prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
            else:
                prev_html = "<li><a href='%s?applicationid=%d&p=%d'>上一页</a></li>" % (base_url, application_id, page - 1)
            page_html.append(prev_html)
            # 11个页码
            if all_page_count < 11:
                begin = 0
                end = all_page_count
            # 总页数大于 11
            else:
                #
                if page < 6:
                    begin = 0
                    end = 11
                else:
                    if page + 6 > all_page_count:
                        begin = page - 6
                        end = all_page_count
                    else:
                        begin = page - 6
                        end = page + 5
            for i in range(begin, end):
                # 当前页
                if page == i + 1:
                    a_html = "<li class='active'><a href='javascript:void(0)'>%d</a></li>" % (i + 1)
                else:
                    a_html = "<li><a href='%s?applicationid=%d&p=%d'>%d</a></li>" % (base_url, application_id, i + 1, i + 1)
                page_html.append(a_html)
            # 下一页
            if page + 1 > all_page_count:
                next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
            else:
                next_html = "<li><a href='%s?applicationid=%d&p=%d'>下一页</a></li>" % (base_url, application_id, page + 1)
            page_html.append(next_html)
            # 尾页
            end_html = "<li><a href='%s?applicationid=%d&p=%d'>尾页</a></li>" % (base_url, application_id, all_page_count)
            page_html.append(end_html)
            # 页码概要
            end_html = "<li><a href='javascript:void(0)'>共 %d页 / %d 条数据</a></li>" % (all_page_count, total_items)
            page_html.append(end_html)
            # 将列表中的元素拼接成页码字符串
            page_str = mark_safe(''.join(page_html))
        else:
            # 首页
            first_html = "<li><a href='%s?p=1'>首页</a></li>" % base_url
            page_html.append(first_html)
            # 上一页
            if page <= 1:
                prev_html = "<li class='disabled'><a href='javascript:void(0)'>上一页</a></li>"
            else:
                prev_html = "<li><a href='%s?p=%d'>上一页</a></li>" % (base_url, page - 1)
            page_html.append(prev_html)
            # 11个页码
            if all_page_count < 11:
                begin = 0
                end = all_page_count
            # 总页数大于 11
            else:
                #
                if page < 6:
                    begin = 0
                    end = 11
                else:
                    if page + 6 > all_page_count:
                        begin = page - 6
                        end = all_page_count
                    else:
                        begin = page - 6
                        end = page + 5
            for i in range(begin, end):
                # 当前页
                if page == i + 1:
                    a_html = "<li class='active'><a href='javascript:void(0)'>%d</a></li>" % (i + 1)
                else:
                    a_html = "<li><a href='%s?p=%d'>%d</a></li>" % (base_url, i + 1, i + 1)
                page_html.append(a_html)
            # 下一页
            if page + 1 > all_page_count:
                next_html = "<li class='disabled'><a href='javascript:void(0)'>下一页</a></li>"
            else:
                next_html = "<li><a href='%s?p=%d'>下一页</a></li>" % (base_url, page + 1)
            page_html.append(next_html)
            # 尾页
            end_html = "<li><a href='%s?p=%d'>尾页</a></li>" % (base_url, all_page_count)
            page_html.append(end_html)
            # 页码概要
            end_html = "<li><a href='javascript:void(0)'>共 %d页 / %d 条数据</a></li>" % (all_page_count, total_items)
            page_html.append(end_html)
            # 将列表中的元素拼接成页码字符串
            page_str = mark_safe(''.join(page_html))
        return page_str
