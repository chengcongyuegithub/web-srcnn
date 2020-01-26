from app import app, db
from werkzeug.utils import secure_filename
from models import Picture, Result
from flask import render_template, redirect, request, flash, get_flashed_messages, send_from_directory, jsonify, \
	make_response
import os
import string
import random
from PIL import Image
import json
from model import SRCNN
import tensorflow as tf

flags = tf.app.flags
flags.DEFINE_string("checkpoint_dir", "checkpoint", "checkpoint directory名字")
flags.DEFINE_string("sample_dir", "myTest", "sample directory名字")
FLAGS = flags.FLAGS


@app.route('/')
def index():
	pics = Picture.query.filter_by(action='Thumbnail_50x50').order_by(Picture.changetime.desc()).limit(10).all()
	return render_template('index.html', pics=pics)


# 上传图片
@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		# 判断是否是图片
		name = f.filename
		suffix = name[name.find('.') + 1:]
		if suffix != 'bmp' and suffix != 'jpg' and suffix != 'jpeg' and suffix != 'png':
			return jsonify(code=500, message="the file is not pic")
		# 存入数据库
		# 重新生成名字
		randomCode = get_code()
		name = randomCode + '.' + suffix
		# 设置url
		url = request.url
		url = url[0:url.rfind('/') + 1] + 'pic/' + randomCode
		pic = Picture(name, url, 'Origin', -1)
		# 添加
		db.session.add(pic)
		db.session.commit()
		# 上传图片
		basepath = os.path.dirname(__file__)
		upload_path = os.path.join(basepath, 'myTest', secure_filename(name))
		f.save(upload_path)
		# 保存缩略图50x50
		url = convertToThumbnail(name, url, suffix)
		return jsonify(code=200, message="success upload", url=url, name=name)


# 点击图片访问该图片的详情
@app.route('/detail/<picname>', methods=['GET', 'POST'])
def detail(picname):
	pictures = Picture.query.filter(Picture.name.like(picname + "%")).all()
	print(type(pictures))
	return render_template('detail.html', pictures=pictures)


# 通过url访问图片
@app.route('/pic/<picName>', methods=['GET', 'POST'])
def indexPic(picName):
	picture = Picture.query.filter(Picture.name.like(picName + "%")).first()
	suffix = picture.suffix
	picName = os.path.join(os.getcwd(), 'myTest', picName + '.' + suffix)
	print(picName)
	image_data = open(picName, "rb").read()
	response = make_response(image_data)
	response.headers['Content-Type'] = 'image/png'
	return response


@app.route('/upscaling', methods=['GET', 'POST'])
def upscaling():
	data = json.loads(request.get_data(as_text=True))
	times = data['times']
	picname = data['picname']
	# 判断是否重复
	timespic = picname[0:picname.find('.')] + times + "x_"
	picture = Picture.query.filter(Picture.name.like(timespic + "%")).first()
	if picture != None:
		return jsonify(code=400, message="The picture has been processed")
	# 路径
	path = os.path.join(os.getcwd(), FLAGS.sample_dir, picname)
	print(path)
	# 名字
	picture = Picture.query.filter_by(name=picname).first()
	picname = picname[0:picname.find('.')] + times + 'x_.' + picture.suffix
	# url
	url = picture.url
	url = url[0:url.rfind('/')] + '/' + picname[0:picname.find('_') + 1]
	# 放大图片
	with tf.Session() as sess:
		srcnn = SRCNN(sess,
					  checkpoint_dir=FLAGS.checkpoint_dir,
					  sample_dir=FLAGS.sample_dir)
		srcnn.upscaling(picname,
						path,
						FLAGS, int(times))
	# 保存数据库
	action = 'Upscale_' + times + 'X'
	newpic = Picture(picname, url, action, picture.id)
	db.session.add(newpic)
	db.session.flush()
	db.session.commit()

	return jsonify(code=200, message="success upscaling", name=picname, id=newpic.id, url=url, action=action)


@app.route("/delete", methods=["POST", "GET"])
def delete():
	data = json.loads(request.get_data(as_text=True))
	pictureId = data['pictureId']
	pictureAction = data['pictureAction']
	picture = Picture.query.filter_by(id=pictureId).first()
	os.remove(os.path.join(os.getcwd(), 'myTest', picture.name))
	db.session.delete(picture)
	db.session.commit()
	# 如果是原图,则删除全部
	if pictureAction == 'Origin':
		pictures = Picture.query.filter_by(orig_id=pictureId).all();
		for pic in pictures:
			print(pic.name)
			os.remove(os.path.join(os.getcwd(), 'myTest', pic.name))
			db.session.delete(pic)
		db.session.commit()
		return jsonify(code=200, message="The original and related pictures have been deleted ")
	else:
		return jsonify(code=201, message="This picture has been deleted ", pictureId=data['pictureId'],
					   pictureAction=data['pictureAction'])


# 缩略图的保存
def convertToThumbnail(name, url, suffix):
	# 缩略图的保存
	path = os.path.join(os.getcwd(), 'myTest', name)
	img = Image.open(path)
	img = img.resize((50, 50), Image.BILINEAR)
	newname = name[0:name.find('.')] + '_50x50.' + suffix
	newpath = os.path.join(os.getcwd(), 'myTest', newname)
	img.save(newpath)
	# 缩略图记录的保存
	url = url + '_50x50'
	orig_pic = Picture.query.filter_by(name=name).first()
	pic = Picture(newname, url, 'Thumbnail_50x50', orig_pic.id)
	db.session.add(pic)
	db.session.commit()
	return url


# 随机32位乱码
def get_code():
	return ''.join(random.sample(string.ascii_letters + string.digits, 32))
