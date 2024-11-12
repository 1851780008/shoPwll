#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author = EASY
import sys
import shodan
import os
import time
import math
import json
from config import api_key,Save_Path
from rich import print

def print_nested_dict(indent, d, result): 
    for key, value in d.items():
        if isinstance(value, dict):
            result.append("  " * indent + f"{key}:")
            print("  " * indent + f"{key}:")
            print_nested_dict(indent + 1, value, result)
        elif isinstance(value, list):
            result.append("  " * indent + f"{key}:")
            print("  " * indent + f"{key}:")
            for item in value:
                if isinstance(item, dict):
                    print_nested_dict(indent + 1, item, result)
                else:
                    result.append("  " * (indent + 1) + str(item))
                    print("  " * (indent + 1) + str(item))
        else:
            result.append("  " * indent + f"{key}: {value}")
            print("  " * indent + f"{key}: {value}")


class Shodan:
    def __init__(self):
        self.result = []
        self.login()
        api = shodan.Shodan(self.api_key)
        self.query = input("[*] 请输入Shodan搜索关键词:").strip()
        total = api.search(self.query)['total']
        print("[*] 共搜索到结果:{}".format(total))
        if total == 0:
            sys.exit("没有搜索到结果，请检查关键词！！")
        self.limit = int(input("[*] 请输入你需要的数量:").strip())
        page = math.ceil(self.limit / 1000) 
        
        try:
            for i in range(1, page + 1):
                # 每次搜索的limit为1000或者剩余的数量，取较小者
                current_limit = min(self.limit, 1000)
                # 执行搜索并更新context
                context = api.search(self.query, offset=0, page=i, limit=current_limit)
                # 更新剩余需要搜索的数量
                self.limit -= current_limit
                if 'matches' in context:
                    for match in context['matches']:
                        print("--------------------------\n")
                        answer = match.get('ip_str') 
                        answer += '|' + str(match.get('port'))
                        answer += '|' + str(match.get('domains'))
                        answer += '|' + str(match.get('location').get('country_name'))
                        self.result.append(answer)
                        # print(ip_port)
                else:
                    self.result = []
        except Exception as e:
            pass
        self.save()

    def login(self):
        self.api_key = api_key
        if not self.api_key:
            print("[*] Automatic authorization failed.Please input your Shodan API Key (https://account.shodan.io/)")
            self.api_key = input('API_KEY >').strip()
        try:
            api = shodan.Shodan(self.api_key)
            account_info = api.info()
            print("[*] login success！")
            print("[*] Available Shodan query credits: %d" % account_info.get('query_credits'))

        except Exception as e:
            exit(0)

    def save(self):
        filename_str = self.query.replace(":", "_").replace(" ", "_").replace('"', '0')
        path = os.path.join(Save_Path,f"{filename_str}.txt")
        with open(path,'w',encoding="utf-8") as file:
            for line in self.result:
                file.write(line + '\n')
        print("")
        print("[*] 结果保存在:{}".format(path))
