# MySQLdb只适用于Python2.x的版本，Python3.x的版本中使用PyMySQL替代MySQLdb
from pymysql import install_as_MySQLdb


install_as_MySQLdb()
