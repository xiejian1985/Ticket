# coding: utf-8

"""命令行火车票查看器

Usage:
	tickets [-gdtkz] <from> <to> <date>

Options:
	-h,--help     显示帮助菜单
	-g            高铁
	-d            动车
	-t            特快
	-k            快速
	-z            直达

Example:
	tickets 北京 上海 2017-04-12
	tickets -dg 北京 上海 2017-04-12
"""

from docopt import docopt
from stations import stations
import requests


class TrainsCollection:
	header = '车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无坐'.split()

	def __init__(self, avaiable_trains, options):
		"""查询到的火车班次集合

		:param avaiable_trains:一个列表，包含可获得的火车班次，每个火车班次啥一个字典
		:param options:查询的选项，如高铁，动车，ETC...
		"""
		self.avaiable_trains = avaiable_trains
		self.options = options

	def _get_duration(self, raw_train):
		duration = raw_train.get('lishi').replace(':', '小时') + '分'
		if duration.startswith('00'):
			return duration[4:]
		if duration.startswith('0'):
			return duration[1:]
		return duration

	@property
	def trains(self):
		for raw_train in self.avaiable_trains:
			train_no = raw_train['queryLeftNewDTO']['station_train_code']
			initial = train_no[0].lower()
			if not self.options or initial in self.options:
				train = [
					train_no,
					'\n'.join([raw_train['queryLeftNewDTO']['from_station_name'],raw_train['queryLeftNewDTO']['to_station_name']]),
					'\n'.join([raw_train['queryLeftNewDTO']['start_time'],raw_train['queryLeftNewDTO']['arrive_time']]),
					self._get_duration(raw_train),
					raw_train['queryLeftNewDTO']['zy_num'],    #一等坐
					raw_train['queryLeftNewDTO']['ze_num'],    #二等坐
					raw_train['queryLeftNewDTO']['rw_num'],    #软卧
					raw_train['queryLeftNewDTO']['yw_nuw'],    #硬卧
					raw_train['queryLeftNewDTO']['yz_num'],    #硬座
					raw_train['queryLeftNewDTO']['wz_num'],    #无坐
				]
				#生成器
				yield train

	def pretty_print(self):
		pt = PrettyTable()
		pt._set_field_names(self.header)
		for train in self.trains:
			pt.add_row(train)
		print(pt)

def cli():
	"""command-line interface"""
	arguments = docopt(__doc__)
	from_station = stations.get(arguments['<from>'])
	to_station = stations.get(arguments['<to>'])
	date = arguments['<date>']
	# 构建URL
	url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
		date, from_station, to_station)
    #print(arguments)

	options = ''.join([key for key, value in arguments.item() if value is True])
	
	#添加verify=False参数，不验证SSL证书
	r = requests.get(url, verify=False)
	available_trains = r.json()['data']
	#print(available_trains)
	TrainCollection(available_trains, options).pretty_print()

if __name__ == '__main__':
    cli()
