# encoding: utf-8
import requests
import json
import random
import time
from lxml import etree
from datetime import datetime 

class IPProxyMiddleware(object):

    def fetch_proxy(self):
        '''increase prxoy ,return a proxy fommat like "111.42.175.236:9091" '''
        proxy_data = freeProxy01()
        if proxy_data:
            return proxy_data
        else:
            proxy_data = freeProxy02()
            return proxy_data

            
    def process_request(self,request,spider):
        proxy_data = self.fetch_proxy()
        
        if proxy_data:
            current_proxy = f'http://{next(proxy_data)}'
            spider.logger.debug(f"current proxy:{current_proxy}")
            request.meta['proxy'] = current_proxy
            # print(current_proxy)
        else:
            print("proxy has been banned")



class ParseNetwork:
    _proxy = '120.196.188.21:9091'  # A China mainland proxy use to interview proxy website
    _proxies = {'http':'http://'+ _proxy }
    _USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)"
    ]
    
    _headers = {'Connection': 'close',
           'User-Agent': random.choice(_USER_AGENTS)
           }
    _TIMEOUT = 10
    _NETWORK_STATUS = True # 判断状态变量
    
    def get_response(self,url):
        try:
            resp = requests.get(url,timeout = self._TIMEOUT,verify= False,headers= self._headers,proxies=self._proxies)
            if resp.status_code == 200:
                return resp
            else:
                print('This URL can not be interviewed, network errcode is {} '.format(resp.status_code))
                return None
            
        except requests.exceptions.Timeout:
            self._NETWORK_STATUS = False
            if self._NETWORK_STATUS == False:
                for i in range(1,10):
                    print("request timeout, the {} repeat!".format(i))
                    resp = requests.get(url,timeout=self._TIMEOUT,verify=False,headers=self._headers,proxies=self._proxies)
                    time.sleep(5)
                    if resp.status_code == 200:
                        return resp
                    else:
                        return None
                    
        except requests.exceptions.ConnectionError:
            time.sleep(5)
            resp = requests.get(url,timeout=self._TIMEOUT,verify=False,headers=self._headers,proxies=self._proxies)
            if resp.status_code == 200:
                return resp
            else:
                return None
            
        

def freeProxy02():
    url = "https://www.zdaye.com/dayProxy.html"
    p = ParseNetwork()
    resp = p.get_response(url)
    try:
        if resp:
            html_tree = etree.HTML(resp.text)
            latest_page_time = html_tree.xpath('//span[@class="thread_time_info"]/text()')[0].strip()
            interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
            print(interval.seconds)
            if interval.seconds < 300:  # 只采集5分钟内的更新
                target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
                sub_resp = p.get_response(target_url)
                sub_html_tree = etree.HTML(sub_resp.text)
                for tr in sub_html_tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = sub_html_tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                time.sleep(5)
            else:
                return None         
        else:
            print("can not get right response")
            return None
    except Exception as e:
        print(e)

def freeProxy01():
    url = "http://proxylist.fatezero.org/proxy.list"
    p = ParseNetwork()
    resp = p.get_response(url)
    try:
        if resp:
            for each in resp.text.split("\n"):
                #print(each)
                json_info = json.loads(each)
                if json_info.get("country") == "CN":
                    yield "%s:%s" % (json_info.get("host", ""), json_info.get("port", ""))
        else:
            print("can not get right response")
            return None
    except Exception as e:
        print(e)

