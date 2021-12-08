# coding=utf-8
# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import time
import math


# 查询崩溃的起始时间
START_UPLOAD_TIME = "2021-12-06"
# 查询崩溃的时间间隔
DAY_INTERNAL = 1
NEED_VERSION = "4.4.8.0"
# 统计前Top的崩溃, 设置80基本就等于一整天的崩溃量, 设置100接口不支持
CRASH_TOP_LIMIT = '80'
# 聚合的崩溃列表一页的数量, 官方接口支持, 前100基本可以算出当天当前崩溃数量
CRASH_LIST_LIMIT = '100'
# cookie需要自己更新
HEADERS = {
    'Cookie': 'pgv_pvi=6210273280; pgv_pvid=2973940544; RK=m/bAWGR8EL; ptcz=ffddf61b849b4ff82cd58236f210ccf23f16213268bf14427082c5bf94b58db6; pac_uid=1_1542951820; XWINDEXGREY=0; o_cookie=1542951820; vc=vc-891a33e3-7005-4042-be9f-ad59a952723b; vc.sig=NPUE-LkCob1BvEEOO5fxGEOGyfQKVXSPdewSypMDNQk; vc=vc-8948812b-8a63-4352-ba34-b0ba0881d796; tvfe_boss_uuid=ac0db876661daf7e; _tc_unionid=c88233ea-0ac4-4132-81e4-51b95dece700; iip=0; _ga_WPDFHTRGMP=GS1.1.1624970155.2.0.1624970155.0; _ga=GA1.2.741657917.1573613963; fqm_pvqid=81ac626a-9b8d-44fa-88da-3190f8d0ea9b; pgv_info=ssid=s8116303631; uin=o1542951820; skey=@mbb1l2kl8; btcu_id=2d75ccbb-d936-4f97-894d-abf32d6eab76; token-skey=10452e49-9a0a-626a-2feb-99fa0c2e1df4; token-lifeTime=1638946435; bugly-session=s%3AYGxxEzVm-gToEnvs77-fsGKnyBzjDD6L.UGHxepHTfFbCGzabBtpQpTcg364oJ6nY3JQtSv5JBw8; before_login_referer=https%3A%2F%2Fbugly.qq.com%2Fv2%2Fcrash-reporting%2Fdashboard%2Fc0f5bcfee9%3Fpid%3D1; referrer=eyJpdiI6InRTVndKZDJHZHB5aDRYSURhaVRtS1E9PSIsInZhbHVlIjoiUEhTb2lhYVluV2RoRklON3JTYVkySHJzSW9IeVJ1aUJOYkgzeXBtRlkrbDN2TStPVlFRRmhDcWNrTlVseWFcLzJCWDNzQTNaWW90ejVcL1AxdXZJWFZzTVBZM2N5NWdNeERSaWpGQnlvSG9cLzYxRW1EYVlCcVlDd2ZySllHdERvUHBVRE1rQkl6UTVwV1hJaGoxM0Y4YW5WYUNnajNmbXRTVGtVM1JPaGs1WjlBSyt5ZHE2UWtcL1wvSFdUTWNNdWZpbnciLCJtYWMiOiJjZmQ0MDEwNTI0NmNiNjQ2M2NjZmExNDBlMTVmMzM2MjJhODc5N2NmYmY2ZDRjZDlkM2IyMGEwYjc1NDZlNTE0In0%3D; bugly_session=eyJpdiI6InMrY3ZkdEMxSlF2ejJPYU5hZGJrMHc9PSIsInZhbHVlIjoiaDVzVG5mR3JcL3VvcFNUemJoOVpTTUF2WUNYWFNZK2Y2Y2pwMGZUZ1NkZjkzaTc3ekk2aTBtMUNQUEl2UnJRT1wvNUVlXC90MGhIdWhoOEszQkc3UkNwWGc9PSIsIm1hYyI6Ijk2MWY4NGI0ZDhjYTIwZWIzNTdkNDU3ODhjZjMwMzkzOGQzNjgyMTVkNzAxZTZlYjU1N2E5M2Q3OTMwMTgzODgifQ%3D%3D'
}
# 记录当前查询崩溃的时间
needUploadTime = "2021-12-06"


# 获取聚合的崩溃列表记录
# bugly过滤时间的参数没有任何作用，目前只能获取全部的数据; 但过滤版本的参数有效, 可以减少数据量
def getCrashList(issueId, rows, start):
    url = "https://bugly.qq.com/v4/api/old/get-crash-list?start=" + start + "&searchType=detail&exceptionTypeList=Crash,Native,ExtensionCrash&pid=1&crashDataType=unSystemExit&platformId=1&issueId=" + issueId + "&version=" + NEED_VERSION + "&rows=" + rows + "&appId=c0f5bcfee9&fsn=6db6d0ba-6874-4f58-875b-3de08f52eb87"
    response = requests.get(url, headers=HEADERS)
    return response.content


# 计算聚合的崩溃数量
def getCrashNum(issueId):
    count = getCurrentCrashTotalNum(issueId)
    if (count <= 0):
        return 0
    page = int(math.ceil(count / float(100)))
    print page
    result = 0
    for i in range(page):
        temp = getCrashNumSinglePageWithTry(issueId, i)
        result += temp

    return result


# 计算一页崩溃列表的数量
def getCrashNumInSinglePage(issueId, start):
    content = getCrashList(issueId, CRASH_LIST_LIMIT, start)
    crashList = json.loads(content)
    checkData(crashList, 'getCrashNumInSinglePage')
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
        print "productVersion: " + productVersion + ",needUploadTime:" + needUploadTime + ",uploadTime: " + uploadTime
        if (productVersion == NEED_VERSION) & (needUploadTime in uploadTime):
            count += 1

    return count

# 获取指定崩溃对应数据, 用来获取聚合的崩溃总数
def getCurrentCrashContent(issueId):
    # header = {
    #     'Cookie': 'pgv_pvi=6210273280; pgv_pvid=2973940544; RK=m/bAWGR8EL; ptcz=ffddf61b849b4ff82cd58236f210ccf23f16213268bf14427082c5bf94b58db6; pac_uid=1_1542951820; XWINDEXGREY=0; o_cookie=1542951820; vc=vc-891a33e3-7005-4042-be9f-ad59a952723b; vc.sig=NPUE-LkCob1BvEEOO5fxGEOGyfQKVXSPdewSypMDNQk; vc=vc-8948812b-8a63-4352-ba34-b0ba0881d796; tvfe_boss_uuid=ac0db876661daf7e; _tc_unionid=c88233ea-0ac4-4132-81e4-51b95dece700; iip=0; _ga_WPDFHTRGMP=GS1.1.1624970155.2.0.1624970155.0; _ga=GA1.2.741657917.1573613963; fqm_pvqid=81ac626a-9b8d-44fa-88da-3190f8d0ea9b; pgv_info=ssid=s8116303631; uin=o1542951820; skey=@mbb1l2kl8; btcu_id=2d75ccbb-d936-4f97-894d-abf32d6eab76; token-skey=10452e49-9a0a-626a-2feb-99fa0c2e1df4; token-lifeTime=1638946435; bugly-session=s%3AYGxxEzVm-gToEnvs77-fsGKnyBzjDD6L.UGHxepHTfFbCGzabBtpQpTcg364oJ6nY3JQtSv5JBw8; before_login_referer=https%3A%2F%2Fbugly.qq.com%2Fv2%2Fcrash-reporting%2Fdashboard%2Fc0f5bcfee9%3Fpid%3D1; bugly_session=eyJpdiI6InFmdXhpdlY0MUZvT2w1dnRvcWt2cnc9PSIsInZhbHVlIjoib2F0MnJPUjRaaGx0ZEtBdlp6V0RcLzZvaGc5TGtBS05ENHRQOXg1WjVLWXFLa3ZmNmFoc0R3VlRvUm1meXlWVlFPQ2VrbGg0SFdsenRLcDJMb3ByYmx3PT0iLCJtYWMiOiIxMGZmMjZjMmQ1OWJiMmMxMGUyOGNjNzgyYzA0NWRhYmNmMWE2N2MzZGE2ZmZiOGQ2MGJjYWIwMjMyYjJiMzIxIn0%3D; referrer=eyJpdiI6ImxSdllOMUV4MjYxdnZYUFhHRmQzdHc9PSIsInZhbHVlIjoiUWhPUjNjWVhsR0NuazFSRW01YkNhVWJGNXZOVGF1bDRMYlpPOEY5d1pYTXdPWkhYSXUzVGg0MWZ1UmlFM1wvSXlVUWRkQmt5TjEwY1VcL0FyQ2pHRlJSXC9mM0NFaEFUeGVYbHpyQnErTTNJenliSFwvTGtGdUREanBicVNURVk0NVwvUXozMjJpYUVlMlB0RVhqYkNkTWErUTl6VGxlS2wrbXJFZllhV0dEdG00UEVCUGRxaUNCeXJpbjVqVzdrXC91dldyMUY0UDQ0QU4zWWRLdjlNbUpCZFFkOTgweEZUekpGM0liTUhSdmVBSDJyND0iLCJtYWMiOiI0YzUxMjE5MmM2ZDA4M2RlYmRmYzQ5NTRlYWFmZWJkY2UwMDg0MzE0NzE1N2JjMDAxYzZmMDUzY2U5YmE3ZjM0In0%3D'
    # }
    url = "https://bugly.qq.com/v4/api/old/get-issue-info?appId=c0f5bcfee9&pid=1&issueId="+ issueId + "&exceptionTypeList=Crash,Native,ExtensionCrash&crashDataType=undefined&fsn=a7d93a32-549e-4aba-9ac3-ee0fa420336d"
    response = requests.get(url, headers=HEADERS)
    print response
    content = json.loads(response.content)
    checkData(content, 'getCurrentCrashContent')
    return content

# 带重试机制
def getCurrentCrashContentWithTry(issueId):
    content = getCurrentCrashContent(issueId)
    while content['code'] != 200:
        time.sleep(1)
        content = getCurrentCrashContent(issueId)

    return content

#获取当前版本崩溃的总数量
def getCurrentCrashTotalNum(issueId):
    content = getCurrentCrashContentWithTry(issueId)
    issueList = content["data"]["issueList"][0]
    issueVersions = issueList["issueVersions"]
    count = 0
    for issue in issueVersions:
        if issue["version"] == NEED_VERSION:
            count = issue["count"]
            break
    return count


# 获取当天Top的崩溃堆栈
def getTopCrashList(limit, date):
    url = "https://bugly.qq.com/v4/api/old/get-top-issue?appId=c0f5bcfee9&pid=1&version=4.4.8.0&type=crash&date=" + date + "&limit=" + limit + "&topIssueDataType=unSystemExit&fsn=ecbc7232-2229-488d-9f18-c933e920a4eb"
    response = requests.get(url, headers=HEADERS)
    return response.content


# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getCrashNumSinglePageWithTry(issueId, start):
    count = getCrashNum(issueId)
    while (count < 0):
        time.sleep(1)
        print "try again getCrashNum"
        count = getCrashNumInSinglePage(issueId, start)
    return count


# 获取当天Top80的崩溃数量
def getTopCrashTotalNum(date):
    date = date.strip('-')
    topData = getTopCrashList(CRASH_TOP_LIMIT, date)
    topData = json.loads(topData)
    checkData(topData, 'getTopCrashTotalNum')

    topIssueList = topData["data"]["data"]["topIssueList"]
    totalNum = 0
    nativeNum = 0
    javaNum = 0
    print "=========topIssueList size: " + str(len(topIssueList)) + "============"
    for issue in topIssueList:
        issueId = issue["issueId"]
        exceptionName = issue["exceptionName"]
        if issue.has_key('keyStack'):
            keyStack = issue["keyStack"]
        else:
            keyStack = "Not Found"
        num = getCrashNum(str(issueId))
        totalNum += num
        # 分别计算native和java崩溃数量
        if exceptionName.startswith("SIG"):
            nativeNum += num
        else:
            javaNum += num
        result = {"issueId": issueId, "exceptionName": exceptionName, "keyStack": keyStack, "crashNum": num}
        print (result)

    return {"totalNum": totalNum, "nativeNum": nativeNum, "javaNum": javaNum}

# 校验数据, 数据不合规时打印错误信息
def checkData(data, tag) :
    isSuccess = True
    if data['code'] != 200:
        print "[" + str(tag) + "]" , data
        isSuccess = False

    return isSuccess

# 时间戳转换成指定格式时间
def convertTime(timeStamp):
    time_local = time.localtime(timeStamp)
    dt = time.strftime("%Y-%m-%d", time_local)
    return dt


# 计算指定时间间隔后的日期
def calucateTime(startTime, days):
    # 转换成时间数组
    startTimeArray = time.strptime(startTime, "%Y-%m-%d")
    # 转换成时间戳,单位秒
    startTimeStamp = time.mktime(startTimeArray)
    return convertTime(startTimeStamp + (days * 24 * 60 * 60))


# 获取指定时间区间内每天的崩溃数量
def getCrashTotalNumInRange(startTime, days):
    # 转换成时间数组
    startTimeArray = time.strptime(startTime, "%Y-%m-%d")
    # 转换成时间戳,单位秒
    startTimeStamp = time.mktime(startTimeArray)
    totalNum = 0
    nativeNum = 0
    javaNum = 0

    for i in range(days):
        # 修改全局变量前需要先申明
        global needUploadTime
        needUploadTime = convertTime(startTimeStamp + (i * 24 * 60 * 60))
        print "============calculate crash num in " + str(needUploadTime) + "================"
        result = getTopCrashTotalNum(needUploadTime)
        print "=============" + str(result) + ",time: " + needUploadTime + ",version: " + NEED_VERSION +"============="

        totalNum += result["totalNum"]
        nativeNum += result["nativeNum"]
        javaNum += result["javaNum"]

    return {"totalNum": totalNum, "nativeNum": nativeNum, "javaNum": javaNum}


result = getCrashTotalNumInRange(START_UPLOAD_TIME, DAY_INTERNAL)

print "===============统计结果==================="
print str(result) + ",time:[ " + START_UPLOAD_TIME + "," + str(
    calucateTime(START_UPLOAD_TIME, DAY_INTERNAL - 1)) + "]" + ",version: " + NEED_VERSION
