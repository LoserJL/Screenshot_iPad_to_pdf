#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import wda
from PIL import Image
import sys
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
import os
import PyPDF2 as PyPDF2
import codecs

c = wda.Client()#参数为空，需要终端运行命令iproxy 8100 8100
s = c.session('com.360buy.lebook')#打开京东阅读客户端
print(s.window_size())#打印京东阅读客户端的UIKit Size
time.sleep(2)#停留2s，等待看客户端启动完成
s.tap(30, 580)#点击这个位置的书籍
time.sleep(3)#停留3s，等待书籍打开稳定
for i in range(int(sys.argv[1])):#根据书籍页数进行截屏
	print('Screenshot %d page' % i)
	c.screenshot('%04d' % i + '.png')#截屏，保存为四位数字（前面自动填0）的文件名
	s.tap(600, 200)#点击屏幕翻页
	time.sleep(1)#等待翻页稳定
	
ims = [m for m in os.listdir() if m.endswith('.png')]#获取目录下所有png图片的文件名
ims.sort(key=lambda x:int(x[0:4]))#listdir居然不按文件名排序，真他妈操蛋，没办法自己排序

(maxw, maxh) = Image.open(ims[0]).size#获取图片尺寸，用来建立pdf尺寸

for i, im in enumerate(ims):
	print('start to single page pdf %d' % i)
	c = canvas.Canvas(('%04d' % i) + '.pdf', pagesize=portrait((maxw, maxh)))#按照图片尺寸，创建pdf，命名和图片一致
	c.drawImage(im, 0, 0, maxw, maxh)#将图片画在pdf上
	c.showPage()
	c.save()#保存

pdfwrite = PyPDF2.PdfFileWriter()#新建一个空白pdf，这个pdf用来合成所有pdf
ff = []#用来保存所有打开的单页pdf
for i in range(len(ims)):
	print('start to compose pdf %d' % i)
	file = open(('%04d' % i) + '.pdf', 'rb')#打开单页pdf
	ff.append(file)#添加到已打开的列表里面，方便后面删除之前关闭
	pdfreader = PyPDF2.PdfFileReader(file)#将打开的单页pdf读取出来
	pdfwrite.addPage(pdfreader.getPage(0))#向空白pdf添加读取的单页pdf

with codecs.open('book.pdf', 'wb') as f:#新建一个book.pdf，用来保存合成的pdf
	pdfwrite.write(f)#保存book.pdf
print('Compose success')

for i in range(len(ims)):
	print('start to remove single page pdf %d' % i)
	ff[i].close()#将之前打开的单页pdf关闭
	os.remove(('%04d' % i) + '.pdf')#删除中间生成的单页pdf

print('Start to delete png')
for im in ims:
	os.remove(im)#删除所有截屏
print('Delete png finish')
