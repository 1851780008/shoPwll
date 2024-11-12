import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox,QTableWidgetItem
from PyQt5 import QtCore, QtWidgets
from PySide6.QtUiTools import QUiLoader
from configobj import ConfigObj
from configparser import ConfigParser
import requests
import jsonpath
import base64
import csv
import json
from jsonpath import jsonpath
import shodan
import time
import re
import threading
import urllib.parse
from threading import Thread
from shodan_ui import Ui_MainWindow

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.save_api_button.clicked.connect(self.save_config)
        self.change_api_button.clicked.connect(self.shodan_xiugai)
        self.search_button.clicked.connect(self.shodan_search)
        self.clear_results_button.clicked.connect(self.clear_results)
        self.clear_log_button.clicked.connect(self.clear_log)
        self.save_button.clicked.connect(self.export)

    def save_config(self):
        try:
            choice = QMessageBox.question(
                self,
                '确认',
                '是否保存？')

            if choice == QMessageBox.Yes:
                config = ConfigObj()
                config.filename = 'config.ini'

                # shodan
                your_shodan_api = self.api_in.text()

                config['shodan_api'] = {}
                config['shodan_api']['your_api'] = your_shodan_api

                config.write()
                QMessageBox.information(
                    self,
                    '成功',
                    '配置成功')
            elif choice == QMessageBox.No:
                pass
        except Exception as e:
            QMessageBox.critical(
                self,
                '错误',
                f'保存配置时发生错误: {e}')

    def shodan_xiugai(self):
        choice = QMessageBox.question(
            self,
            '确认',
            '是否修改shodan配置？')
        try:

            if choice == QMessageBox.Yes:
                conf_ini = "config.ini"
                config = ConfigObj(conf_ini, encoding='UTF8')
                config['shodan_api']['your_api'] = self.api_in.text()
                config.write()
                QMessageBox.information(
                    self,
                    '成功',
                    '修改成功  ')
            if choice == QMessageBox.No:
                pass
        except:
            QMessageBox.information(
                self,
                '提示',
                '没有检测到第一次配置，请先点击保存  ')

    def shodan_search(self):
        try:
            # 尝试读取文本文件
            search_host = self.search_in.text()
            file_n=self.search_in.text().replace(":", "_").replace(" ", "_").replace('"', '0')
            file_name = f"../output/{file_n}.txt"  # 假设文件名与搜索关键词相同
            try:
                with open(file_name, 'r') as file:
                    results = file.read()
                    self.log_out.append(f"从文件 {file_name} 中读取结果" + '\n')
                    # 处理文件中的结果
                    self.ip11 = []
                    self.port11 = []
                    self.domain11 = []
                    self.country11 = []
                    lines = results.splitlines()  # 将文件内容按行分割
                    for line in lines:
                        parts = line.split('|')  # 假设每行数据以'|'分隔
                        if len(parts) == 4:  # 确保分割后的数据有4个部分
                            ip_str1, port1, domains1, country_name1 = parts

                            row = self.result_out.rowCount()  # 获取所有列
                            self.result_out.insertRow(row)  # 插入row

                            # 创建表格项并设置文本
                            self.result_out.setItem(row, 0, QTableWidgetItem(ip_str1))
                            self.result_out.setItem(row, 1, QTableWidgetItem(port1))
                            self.result_out.setItem(row, 2, QTableWidgetItem(domains1))
                            self.result_out.setItem(row, 3, QTableWidgetItem(country_name1))


                            # 将数据添加到列表中
                            self.ip11.append(ip_str1)
                            self.port11.append(port1)
                            self.domain11.append(domains1)
                            self.country11.append(country_name1)
                        else:
                            # 如果行数据格式不正确，可以在这里处理错误
                            print(f"数据格式错误: {line}")
            except FileNotFoundError:
                # 文件不存在，进行API搜索
                self.log_out.append(f"文件 {file_name} 不存在，进行API搜索" + '\n')
                try:
                    cf = ConfigParser()
                    cf.read('config.ini')
                    self.shodan_api = cf.get('shodan_api', 'your_api')
                    search_host = self.search_in.text()
                    page = self.search_page.text()

                    shodan_api = cf.get('shodan_api', 'your_api')
                    self.api = shodan.Shodan(shodan_api)

                    self.log_out.append(f'shodan正在查询 ==> {search_host}，速度稍慢，请耐心等待...' + '\n')

                    thread = Thread(target=self.shodan_threadSend,
                                    args=(search_host, page)
                                    )
                    thread.start()
                except:
                    QMessageBox.information(
                        self,
                        '提示',
                        '请先配置shodan API  ')

        except Exception as e:
            QMessageBox.information(
                self,
                '提示',
                f'发生错误: {e}'
            )

    def combine_all_matches(self, results_list):
        all_matches = []
        for result in results_list:
            if 'matches' in result:
                all_matches.extend(result['matches'])
        return all_matches

    def shodan_threadSend(self, search_host, Page):
            try:
                page = 1
                total = '-1'
                self.ip11 = []
                self.port11 = []
                self.domain11 = []
                self.country11 = []
                while True:
                    results = self.api.search(search_host, page=page, limit=1000)
                    if(total == '-1'):
                        total = str(results['total'])
                    for result in results['matches']:
                        ip_str1 = result['ip_str']
                        port1 = result['port']
                        domains1 = result['domains']
                        country_name1 = result['location']['country_name']

                        row = self.result_out.rowCount()  # 获取所有列
                        print(row)
                        self.result_out.insertRow(row)  # 插入row
                        item = QTableWidgetItem()
                        item.setText(str(ip_str1))
                        item1 = QTableWidgetItem()
                        item1.setText(str(port1))
                        item2 = QTableWidgetItem()
                        item2.setText(','.join(domains1))
                        item3 = QTableWidgetItem()
                        item3.setText(str(country_name1))

                        self.result_out.setItem(row, 0, item)
                        self.result_out.setItem(row, 1, item1)
                        self.result_out.setItem(row, 2, item2)
                        self.result_out.setItem(row, 3, item3)

                        self.ip11.append(ip_str1)
                        self.port11.append(port1)
                        self.domain11.append(','.join(domains1))
                        self.country11.append(country_name1)
                    if results['matches']:
                        page += 1
                        if page > int(Page):
                            break
                    else:
                        break
                self.count_label.setText(total + ' ' + '条')
                self.log_out.append('已找到：' + total + ' 条结果' + '\n')

            except shodan.APIError as e:
                self.log_out.append('shodan提示：' + str(e) + '\n' + '-' * 29)
                print('[-]Error:', e)


            self.log_out.append('查询状态：完成' + '\n' + '-' * 29)




    def clear_results(self):
        self.result_out.setRowCount(0)
        self.count_label.setText('')
        # 设置标题栏复原
        self.result_out.setColumnWidth(0, 116)
        self.result_out.setColumnWidth(1, 116)
        self.result_out.setColumnWidth(2, 116)
        self.result_out.setColumnWidth(3, 116)
        self.result_out.setColumnWidth(4, 116)
        self.result_out.setColumnWidth(5, 116)
        self.result_out.setColumnWidth(6, 116)
        self.result_out.setColumnWidth(7, 116)
        self.result_out.setColumnWidth(8, 116)

    def clear_log(self):
        self.log_out.clear()

    def export(self):  #导出
        choice = QMessageBox.question(
            self,
            '确认',
            '确定导出吗？'
        )
        try:
            if choice == QMessageBox.Yes:
                t = time.time()
                self.date_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(t))
                # 使用self.results而不是self.ip11等变量
                folder = "../output"  # 目标文件夹
                os.makedirs(folder, exist_ok=True)  # 创建文件夹，如果文件夹已存在不会抛出错误

                file_nn = self.search_in.text().replace(":", "_").replace(" ", "_").replace('"', '0')
                file_path = os.path.join(folder, f"{file_nn}.txt")

                len_1 = len(self.ip11)
                if len_1 > 0:
                    with open(file_path, "w", newline='', encoding='utf-8') as f:
                        index = 0  # 初始化索引

                        # 使用 while 循环遍历列表
                        while index < len_1:
                            # 将当前元素写入文件
                            f.write(str(self.ip11[index]) + '|' + str(self.port11[index]) + '|' + str(self.domain11[index]) + '|' + str(self.country11[index]) + '\n')  # 每个元素后添加换行符
                            index += 1  # 移动到下一个元素

                    QMessageBox.information(
                        self,
                        '完成',
                        '导出成功，请在软件目录下查看'
                    )
                else:
                    QMessageBox.information(
                        self,
                        '提示',
                        '导出失败，没有可导出的数据！'
                    )

            elif choice == QMessageBox.No:
                pass

        except Exception as e:
            QMessageBox.information(
                self,
                '提示',
                f'导出失败: {e}，请重试！'
            )

if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec_())
