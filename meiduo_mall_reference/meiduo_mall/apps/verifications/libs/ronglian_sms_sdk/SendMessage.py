import json

from .SmsSDK import SmsSDK


# accId = '容联云通讯分配的主账号ID'
# accToken = '容联云通讯分配的主账号TOKEN'
# appId = '容联云通讯分配的应用ID'
#
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '容联云通讯创建的模板'
#     mobile = '手机号1,手机号2'
#     datas = ('变量1', '变量2')
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)
#
#
# send_message()

def singleton(cls):
    instance = {}

    def inner():
        if cls not in instance:
            instance[cls] = cls()
        return instance[cls]

    return inner


@singleton
class CCP(object):
    accId = '8aaf070881ad8ad401821444c9ec19b4'
    accToken = '23e828a5dc484a8f90348562fbc5ccf5'
    appId = '8aaf070881ad8ad401821444caff19bb'

    def send_template_sms(self, to, datas, temp_id):
        sdk = SmsSDK(self.accId, self.accToken, self.appId)
        tid = temp_id
        mobile = to
        datas = datas
        result = sdk.sendMessage(tid, mobile, datas)
        result = json.loads(result)
        if result['statusCode'] == '000000':
            return 0
        else:
            return -1


if __name__ == '__main__':
    CCP().send_template_sms('18674115441', ('123456', 5), 1)
