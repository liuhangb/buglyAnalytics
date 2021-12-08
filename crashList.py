# coding=utf-8
import requests
import json
import time

# 查询的崩溃时间
needUploadTime = "2021-12-07"
# 筛选目标版本
needVersion = "4.4.8.0"
# 聚合的崩溃列表一页的数量, 官方接口支持, 前100基本可以算出当天当前崩溃数量
crashListLimit = '100'
# cookie需要自己更新
headers = {
    'Cookie': 'pgv_pvi=6210273280; pgv_pvid=2973940544; RK=m/bAWGR8EL; ptcz=ffddf61b849b4ff82cd58236f210ccf23f16213268bf14427082c5bf94b58db6; pac_uid=1_1542951820; XWINDEXGREY=0; o_cookie=1542951820; vc=vc-891a33e3-7005-4042-be9f-ad59a952723b; vc.sig=NPUE-LkCob1BvEEOO5fxGEOGyfQKVXSPdewSypMDNQk; vc=vc-8948812b-8a63-4352-ba34-b0ba0881d796; tvfe_boss_uuid=ac0db876661daf7e; _tc_unionid=c88233ea-0ac4-4132-81e4-51b95dece700; iip=0; _ga_WPDFHTRGMP=GS1.1.1624970155.2.0.1624970155.0; _ga=GA1.2.741657917.1573613963; fqm_pvqid=81ac626a-9b8d-44fa-88da-3190f8d0ea9b; pgv_info=ssid=s8116303631; uin=o1542951820; skey=@mbb1l2kl8; btcu_id=2d75ccbb-d936-4f97-894d-abf32d6eab76; token-skey=10452e49-9a0a-626a-2feb-99fa0c2e1df4; token-lifeTime=1638946435; bugly-session=s%3AYGxxEzVm-gToEnvs77-fsGKnyBzjDD6L.UGHxepHTfFbCGzabBtpQpTcg364oJ6nY3JQtSv5JBw8; before_login_referer=https%3A%2F%2Fbugly.qq.com%2Fv2%2Fcrash-reporting%2Fdashboard%2Fc0f5bcfee9%3Fpid%3D1; bugly_session=eyJpdiI6InFmdXhpdlY0MUZvT2w1dnRvcWt2cnc9PSIsInZhbHVlIjoib2F0MnJPUjRaaGx0ZEtBdlp6V0RcLzZvaGc5TGtBS05ENHRQOXg1WjVLWXFLa3ZmNmFoc0R3VlRvUm1meXlWVlFPQ2VrbGg0SFdsenRLcDJMb3ByYmx3PT0iLCJtYWMiOiIxMGZmMjZjMmQ1OWJiMmMxMGUyOGNjNzgyYzA0NWRhYmNmMWE2N2MzZGE2ZmZiOGQ2MGJjYWIwMjMyYjJiMzIxIn0%3D; referrer=eyJpdiI6ImxSdllOMUV4MjYxdnZYUFhHRmQzdHc9PSIsInZhbHVlIjoiUWhPUjNjWVhsR0NuazFSRW01YkNhVWJGNXZOVGF1bDRMYlpPOEY5d1pYTXdPWkhYSXUzVGg0MWZ1UmlFM1wvSXlVUWRkQmt5TjEwY1VcL0FyQ2pHRlJSXC9mM0NFaEFUeGVYbHpyQnErTTNJenliSFwvTGtGdUREanBicVNURVk0NVwvUXozMjJpYUVlMlB0RVhqYkNkTWErUTl6VGxlS2wrbXJFZllhV0dEdG00UEVCUGRxaUNCeXJpbjVqVzdrXC91dldyMUY0UDQ0QU4zWWRLdjlNbUpCZFFkOTgweEZUekpGM0liTUhSdmVBSDJyND0iLCJtYWMiOiI0YzUxMjE5MmM2ZDA4M2RlYmRmYzQ5NTRlYWFmZWJkY2UwMDg0MzE0NzE1N2JjMDAxYzZmMDUzY2U5YmE3ZjM0In0%3D'
}

# java崩溃类型：Crash，native崩溃类型: Native
def getIssueList(crashType):
    url = "https://bugly.qq.com/v4/api/old/get-issue-list?start=0&searchType=errorType&exceptionTypeList=" + crashType + "&pid=1&platformId=1&date=last_7_day&sortOrder=desc&version=" + needVersion + "&rows=" + crashListLimit +"&sortField=uploadTime&appId=c0f5bcfee9&fsn=0dd91a76-1029-446e-bc52-1666078e8ecd"
    response = requests.get(url, headers=headers)
    content = json.loads(response.content)
    checkData(content, 'getIssueList')
    return content


# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getIssueListWithRetry(crashType):
    content = getIssueList(crashType)
    while content['code'] != 200:
        time.sleep(1)
        content = getIssueList(crashType)
    return content

#校验数据, 并打印错误数据
def checkData(data, tag):
    print data['code']
    if data["code"] != 200:
        print "[" + tag + "]", data

# 获取聚合的崩溃列表记录
def getCrashList(issueId, rows):
    url = "https://bugly.qq.com/v4/api/old/get-crash-list?start=0&searchType=detail&exceptionTypeList=Crash,Native,ExtensionCrash&pid=1&crashDataType=unSystemExit&platformId=1&issueId=" + issueId + "&rows=" + rows + "&appId=c0f5bcfee9&fsn=6db6d0ba-6874-4f58-875b-3de08f52eb87"
    response = requests.get(url, headers=headers)
    return response.content

# 计算聚合的崩溃数量
def getCrashNum(issueId):
    content = getCrashList(issueId, crashListLimit)
    crashList = json.loads(content)
    checkData(crashList, 'getCrashNum')
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

# 只要多拉几条记录必定会遇到500错误, 需要多重试几次
def getCrashNumWithTry(issueId):
    count = getCrashNum(issueId)
    while(count < 0):
        time.sleep(1)
        print "try again getCrashNum"
        count = getCrashNum(issueId)

    print {"issueId": issueId, "count": count}
    return count

# 时间戳转换成指定格式时间
def convertTime(timeStamp):
    time_local = time.localtime(timeStamp)
    dt = time.strftime("%Y-%m-%d", time_local)
    return dt


def converDataToTime(startTime, type):
    if (type == 1):
        format = '%Y-%m-%d %H:%M:%S %f'
    else:
        format = '%Y-%m-%d'

    # 转换成时间数组
    startTimeArray = time.strptime(startTime, format)
    # 转换成时间戳,单位秒
    startTimeStamp = time.mktime(startTimeArray)
    return startTimeStamp

# 计算指定时间间隔后的日期
def calucateTime(startTime, days):
    startTimeStamp = converDataToTime(startTime)
    return convertTime(startTimeStamp + (days * 24 * 60 * 60))

# 计算某个类型崩溃的数量
def getCrashTotalNum(crashType):
    crashList = getIssueListWithRetry(crashType)
    issueList = crashList['data']['issueList']
    count = 0
    for issue in issueList:
        # 过滤查询崩溃时间之前的崩溃
        lastestUploadTime = issue['lastestUploadTime']
        if converDataToTime(lastestUploadTime, 1) < converDataToTime(needUploadTime, 2):
            continue

        # print 'lastestUploadTime:' + lastestUploadTime
        count += getCrashNumWithTry(issue['issueId'])

    return count


javaCount = getCrashTotalNum("Crash")
nativeCount = getCrashTotalNum("Native")
print "===============统计结果==================="
print "nativeCount" + str(nativeCount) + ",java:" + str(javaCount)
print {"NativeCrashNum": nativeCount,  "JavaCrashNum": javaCount, "TotalNum": nativeCount + javaCount, "time": needUploadTime, "version": needVersion }
