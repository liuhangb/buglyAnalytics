# coding=utf-8
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import time


# 过滤条件
needUploadTime = "2021-12-06"
needVersion = "4.4.8.0"
# 统计前Top的崩溃, 设置80基本就等于一整天的崩溃量, 设置100接口不支持
crashTopLimit = '80'
# 聚合的崩溃列表一页的数量, 官方接口支持, 前100基本可以算出当天当前崩溃数量
crashListLimit = '100'


# 获取聚合的崩溃列表记录
def getCrashList(issueId, rows):
    headers = {
        'Cookie': 'pgv_pvi=6210273280; pgv_pvid=2973940544; RK=m/bAWGR8EL; ptcz=ffddf61b849b4ff82cd58236f210ccf23f16213268bf14427082c5bf94b58db6; pac_uid=1_1542951820; XWINDEXGREY=0; o_cookie=1542951820; vc=vc-891a33e3-7005-4042-be9f-ad59a952723b; vc.sig=NPUE-LkCob1BvEEOO5fxGEOGyfQKVXSPdewSypMDNQk; vc=vc-8948812b-8a63-4352-ba34-b0ba0881d796; tvfe_boss_uuid=ac0db876661daf7e; _tc_unionid=c88233ea-0ac4-4132-81e4-51b95dece700; iip=0; _ga_WPDFHTRGMP=GS1.1.1624970155.2.0.1624970155.0; _ga=GA1.2.741657917.1573613963; fqm_pvqid=81ac626a-9b8d-44fa-88da-3190f8d0ea9b; pgv_info=ssid=s8116303631; uin=o1542951820; skey=@mbb1l2kl8; btcu_id=2d75ccbb-d936-4f97-894d-abf32d6eab76; token-skey=910006d1-8be4-e868-8642-f6990ec9809f; token-lifeTime=1638874833; bugly-session=s%3AcLAFRkLg9EBOxhDvvMzllnTu5rnnOxTG.KZGa885OmT6o%2FxV0uDqKSh3Cjj%2B5S%2Bku5IxHJq8rAvI; bugly_session=eyJpdiI6IitXMEJOdEo0XC9OU0pRc3drMGJWRGZBPT0iLCJ2YWx1ZSI6Ilg4b0VKZ0hXZjA4WXpSYWRIZGRqYmV0aXBET0NOajNcL3lGaWgyTVFZMU40ck05SjNMUWdUbStQN2hHa0p3eVk2ODRcL08rY3FneDU3UitiN0hNaE8yN2c9PSIsIm1hYyI6ImIzY2NkZDNmNTk2ODFkNWQzY2NlYmYxN2U4MGI2MDc0MmNlZTljNzdmYzY5ZTE0OWJkOWY5NjVmNmNhMmU0ZGIifQ%3D%3D; referrer=eyJpdiI6InR3NkppKzA3em5lU2grWHZcL3JJd1F3PT0iLCJ2YWx1ZSI6Im1NVlI3RzJRbzcyZDJ1M2xhZGczWEhXNjFmTnl4a2VpS1NLQzRDUTdqbXFYUjh4dld6eld6N2NJMVcwTGRLcEhFd0ZjYkR4Y1lwYmhmZHFcLzBkSiswRFBQcU5JNEoxYkFZTHZhM2gzVUpwcDBSNndHRzNYcEJFaExBNjgycndud3Y0MWNUckVMWjFYNkJOeTVRY2x4OUhUZ1p5cXpPUTcwbmZYbXRBcmpiTjNKTDJXUktIWGQ0c1FhaTZ1cjJTQnJDaGlaOW85RDgwWXEwXC9SelgxMUVyZXlKb3hETlhMRm96UjBuXC9wNFJ5dk09IiwibWFjIjoiMTA5YzVkMmMzYTU3NTM4MTk0NThmODZmOTU2NDdhMzI5OWE0MzA5NDI3YjFjNDg0MGUwZWIzZWJiNmUxZTFlYiJ9'
    }
    url = "https://bugly.qq.com/v4/api/old/get-crash-list?start=0&searchType=detail&exceptionTypeList=Crash,Native,ExtensionCrash&pid=1&crashDataType=unSystemExit&platformId=1&issueId=" + issueId + "&rows=" + rows + "&appId=c0f5bcfee9&fsn=6db6d0ba-6874-4f58-875b-3de08f52eb87"
    response = requests.get(url, headers=headers)
    return response.content


# 计算聚合的崩溃数量
def getCrashNum(issueId):
    content = getCrashList(issueId, crashListLimit)
    crashList = json.loads(content)
    # print content
    print "getCrashNum before:" + issueId
    if crashList["code"] != 200:
        print content
        return -1

    data = crashList["data"]
    crashIdList = data["crashIdList"]
    crashDatas = data["crashDatas"]

    count = 0
    for list in crashIdList:
        crashDataItem = crashDatas[list]
        productVersion = crashDataItem["productVersion"]
        uploadTime = crashDataItem["uploadTime"]
        if (productVersion == needVersion) & (needUploadTime in uploadTime):
            count += 1

    return count

#获取当天Top的崩溃堆栈
def getTopCrashList(limit):
    headers = {
        'Cookie': 'pgv_pvi=6210273280; pgv_pvid=2973940544; RK=m/bAWGR8EL; ptcz=ffddf61b849b4ff82cd58236f210ccf23f16213268bf14427082c5bf94b58db6; pac_uid=1_1542951820; XWINDEXGREY=0; o_cookie=1542951820; vc=vc-891a33e3-7005-4042-be9f-ad59a952723b; vc.sig=NPUE-LkCob1BvEEOO5fxGEOGyfQKVXSPdewSypMDNQk; vc=vc-8948812b-8a63-4352-ba34-b0ba0881d796; tvfe_boss_uuid=ac0db876661daf7e; _tc_unionid=c88233ea-0ac4-4132-81e4-51b95dece700; iip=0; _ga_WPDFHTRGMP=GS1.1.1624970155.2.0.1624970155.0; _ga=GA1.2.741657917.1573613963; fqm_pvqid=81ac626a-9b8d-44fa-88da-3190f8d0ea9b; pgv_info=ssid=s8116303631; uin=o1542951820; skey=@mbb1l2kl8; btcu_id=2d75ccbb-d936-4f97-894d-abf32d6eab76; token-skey=910006d1-8be4-e868-8642-f6990ec9809f; token-lifeTime=1638874833; bugly-session=s%3AcLAFRkLg9EBOxhDvvMzllnTu5rnnOxTG.KZGa885OmT6o%2FxV0uDqKSh3Cjj%2B5S%2Bku5IxHJq8rAvI; bugly_session=eyJpdiI6IitXMEJOdEo0XC9OU0pRc3drMGJWRGZBPT0iLCJ2YWx1ZSI6Ilg4b0VKZ0hXZjA4WXpSYWRIZGRqYmV0aXBET0NOajNcL3lGaWgyTVFZMU40ck05SjNMUWdUbStQN2hHa0p3eVk2ODRcL08rY3FneDU3UitiN0hNaE8yN2c9PSIsIm1hYyI6ImIzY2NkZDNmNTk2ODFkNWQzY2NlYmYxN2U4MGI2MDc0MmNlZTljNzdmYzY5ZTE0OWJkOWY5NjVmNmNhMmU0ZGIifQ%3D%3D; referrer=eyJpdiI6InR3NkppKzA3em5lU2grWHZcL3JJd1F3PT0iLCJ2YWx1ZSI6Im1NVlI3RzJRbzcyZDJ1M2xhZGczWEhXNjFmTnl4a2VpS1NLQzRDUTdqbXFYUjh4dld6eld6N2NJMVcwTGRLcEhFd0ZjYkR4Y1lwYmhmZHFcLzBkSiswRFBQcU5JNEoxYkFZTHZhM2gzVUpwcDBSNndHRzNYcEJFaExBNjgycndud3Y0MWNUckVMWjFYNkJOeTVRY2x4OUhUZ1p5cXpPUTcwbmZYbXRBcmpiTjNKTDJXUktIWGQ0c1FhaTZ1cjJTQnJDaGlaOW85RDgwWXEwXC9SelgxMUVyZXlKb3hETlhMRm96UjBuXC9wNFJ5dk09IiwibWFjIjoiMTA5YzVkMmMzYTU3NTM4MTk0NThmODZmOTU2NDdhMzI5OWE0MzA5NDI3YjFjNDg0MGUwZWIzZWJiNmUxZTFlYiJ9'
    }
    url = "https://bugly.qq.com/v4/api/old/get-top-issue?appId=c0f5bcfee9&pid=1&version=4.4.8.0&type=crash&date=20211206&limit=" + limit + "&topIssueDataType=unSystemExit&fsn=ecbc7232-2229-488d-9f18-c933e920a4eb"
    response = requests.get(url, headers=headers)
    return response.content

# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getCrashNumWithTry(issueId):
    count = getCrashNum(issueId)
    while(count < 0):
        time.sleep(1)
        print "try again getCrashNum"
        count = getCrashNum(issueId)
    return count

#获取当天Top80的崩溃数量
def getTopCrashTotalNum():
    topData = getTopCrashList(crashTopLimit)
    topData = json.loads(topData)
    topIssueList = topData["data"]["data"]["topIssueList"]
    totalNum = 0
    nativeNum = 0
    javaNum = 0
    print "=========topIssueList size: " + str(len(topIssueList)) + "============"
    for issue in topIssueList:
        issueId = issue["issueId"]
        exceptionName = issue["exceptionName"]
        keyStack = issue["keyStack"]
        num = getCrashNumWithTry(str(issueId))
        totalNum += num
        # 分别计算native和java崩溃数量
        if exceptionName.startswith("SIG"):
            nativeNum += num
        else:
            javaNum += num
        print "nativeNum: " + str(nativeNum)
        result = {"issueId": issueId, "exceptionName": exceptionName, "keyStack": keyStack, "crashNum": num}
        print (result)

    return {"totalNum": totalNum, "nativeNum": nativeNum, "javaNum": javaNum}

totalNum = getTopCrashTotalNum()

print "===============统计结果==================="
print str(totalNum) + ",time: " + needUploadTime + ",version: " + needVersion