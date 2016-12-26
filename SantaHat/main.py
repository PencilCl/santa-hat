from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from os import path
from os import makedirs

from utils import add_cap

# get a unique id by uuid.uuid4()
import uuid

# setttings
from django.conf import settings
UploadSettings = {
	"ALLOW_FILES_TYPE": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
	"OUTPUT_PATH": path.join(settings.BASE_DIR, 'static/upload')
}

def save_upload_file(PostFile,FilePath):
	'''
		save upload file
	'''
	try:
		f = open(FilePath, 'wb')
		for chunk in PostFile.chunks():
			f.write(chunk)
	except Exception,E:
		f.close()
		return u"writing file error:"+ E.message
	f.close()
	return u"SUCCESS"

def get_output_file_path(output_path, extension):
	'''
		get output file name by uuid.uuid4()
		find a unuserd filename
		return:
			the final file path
	'''
	uuid_str = uuid.uuid4().urn[9:]
	output_file_name = uuid_str + extension
	output_file_path = path.join(output_path, output_file_name)
	# if dir is not exist then create
	if not path.exists(output_path):
		makedirs(output_path)

	# find a unused filename
	while path.exists(output_file_path):
		output_file_name = uuid_str + extension
		output_file_path = path.join(output_path, output_file_name)

	return (output_file_path, output_file_name)

@csrf_exempt
def uploadImg(req):
	'''
		handle upload files
	'''
	# check method's type
	if req.method != "POST":
		return HttpResponse("error|request.method!=post")

	# get the upload file
	file = req.FILES.get('upload_img', None)
	if file is None:
		return HttpResponse("error|get file error")

	upload_file_name = file.name
	upload_file_size = file.size

	# get upload original name and file's extension
	upload_original_name,upload_original_ext = path.splitext(upload_file_name)

	# check file's type
	ALLOW_FILES_TYPE = UploadSettings['ALLOW_FILES_TYPE']
	if not upload_original_ext.lower() in ALLOW_FILES_TYPE:
		return HttpResponse("error|file type error")

	# get ouput_file_path
	OUTPUT_PATH = UploadSettings['OUTPUT_PATH']
	output_file_path, output_file_name = get_output_file_path(OUTPUT_PATH, upload_original_ext)

	# write file
	state = save_upload_file(file, output_file_path)

	if state != "SUCCESS":
		return HttpResponse("error|" + state)

	savePath = path.join(OUTPUT_PATH, '../', output_file_name)
	add_cap(output_file_path, path.join(settings.BASE_DIR, 'SantaHat/cap.png'), savePath)
	# csrf
	response = HttpResponse('http://' + req.get_host() + '/static/' + output_file_name)
	response["Access-Control-Allow-Origin"] = "*"
	response["Access-Control-Allow-Methods"] = "POST"
	response["Access-Control-Max-Age"] = "1000"
	response["Access-Control-Allow-Headers"] = "*"
	return response