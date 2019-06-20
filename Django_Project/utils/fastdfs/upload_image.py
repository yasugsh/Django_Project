# 1. 导入FastDFS客户端扩展
from fdfs_client.client import Fdfs_client


# 2. 创建FastDFS客户端实例
client = Fdfs_client('./client.conf')

# 3. 调用FastDFS客户端上传文件方法
result = client.upload_by_filename('/home/python/Desktop/upload_Images/01.jpeg')
print(result)


"""
result = {
'Group name': 'group1',  # FastDFS服务端Storage组名
'Remote file_id': 'group1/M00/00/00/wKgThF0LMsmATQGSAAExf6lt6Ck10.jpeg',  # 文件存储的位置(索引)，可用于下载
'Status': 'Upload successed.',  # 文件上传结果反馈
'Local file name': '/home/python/Desktop/upload_Images/02.jpeg',  # 所上传文件的真实路径
'Uploaded size': '76.00KB',  # 文件大小
'Storage IP': '192.168.19.132'}  # FastDFS服务端Storage的IP
"""
