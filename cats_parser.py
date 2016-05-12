from os import listdir
from os.path import isdir
import re
def getAllProgs():
	allcats=[name for name in listdir("/usr/portage") if isdir("/usr/portage/"+name)]
	dic={}
	for cat in allcats:
		if re.match("(?P<main>.+)\-(?P<sub>.+)",cat):
			found=re.match("(?P<main>.+)\-(?P<sub>.+)",cat)

			if not dic.get(found.group("main")):
				dic.update({ found.group("main"):{ found.group("sub"):[] } })
			else:
				dic.get( found.group("main") ).update( {found.group("sub"):[] } )

			dic.get( found.group("main") ).get( found.group("sub") ).extend(
					[
					name for name in listdir(
						"/usr/portage/{}-{}".format(
						found.group("main"),found.group("sub")
						)
					) if isdir("/usr/portage/{}-{}/{}".\
					format(found.group("main"),found.group("sub"),name ) )
					]
			)
	return dic
def getEbuilds(main,sub,prog,dic=getAllProgs()):
	d=[name for name in listdir("/usr/portage/{main}-{sub}/{prog}".format(main=main,sub=sub,prog=prog)) if name.endswith(".ebuild")]
	return d

def search(string):
	main=sub=name=None
	if re.search("main:(?P<a>(\w|\-)+)",string):
		main=re.search("main:(?P<a>(\w|\-)+)",string).group("a")
	if re.search("sub:(?P<a>\w+)",string):
		sub=re.search("sub:(?P<a>(\w|\-)+)",string).group("a")
	if re.search("name:(?P<a>(\w|\-)+)",string):
		name=re.search("name:(?P<a>(\w|\-)+)",string).group("a")
	if not (main or sub or name):
		string=re.sub("(.+)","name:\g<1>",string)
		name=re.search("name:(?P<a>(\w|\-)+)",string).group("a")

	found_lst=[]
	progs_lst=getAllProgs()
	for x in progs_lst.keys():
		if main:
			if re.search(main,x):
				f=re.search("(\w+)*("+main+")(\w+)*",x)
				for sb in progs_lst.get(x).keys():
					for nm in progs_lst[x][sb]:
						toapp=[main,x,"-",sb,"/",nm]
						found_lst.append(toapp)
		if sub:
			for sb in progs_lst.get(x).keys():
				if re.search(sub,sb):
					for nm in progs_lst[x][sb]:
						f=re.search("(\w+)*("+sub+")(\w+)*",sb)
						toapp=[sub,x,"-",sb,"/",nm]
						found_lst.append(toapp)
		if name:
			are_name_and_category_equeal=False
			for sb in progs_lst.get(x).keys():
				for nm in progs_lst[x][sb]:
					if re.search(name,nm):
						if not are_name_and_category_equeal and (name in sb or name in x):
							are_name_and_category_equeal=True
						if are_name_and_category_equeal and (name in sb or name in x):
							continue
						f=re.search("([\w\-]+)*("+name+")([\w\-]+)*",nm)
						toapp=[name,x,"-",sb,"/"]
						for g in f.groups():
							if g:
								toapp.append(g)
						found_lst.append(toapp)
	return found_lst

def getInsProgs():
	import os
	import re
	installed=[os.path.join(root, f)
		for root, subdirs, files in os.walk(os.path.expanduser("/var/db/pkg"))
			for f in subdirs
			]
	r_installed=[]
	for ins in installed:
		if re.match("/.+/.+/.+/(.+)/(.+)\-(.+)",ins):
			pkg=re.match("/.+/.+/.+/(.+)/(.+)\-(\d+|\.)+",ins)
			r_installed.append(pkg.groups()[0]+"/"+pkg.groups()[1])
	return r_installed

def getInfo(main,sub,name):
	to_return=[]
	for package in getEbuilds(main,sub,name):
		f=open("/usr/portage/{main}-{sub}/{prog}/{package}".format(
		main=main,sub=sub,prog=name,package=package
		))
		ebuild_info=f.read()
		f.close()
		to_app={"Version: ":str(re.search(name+"-?(.+)\.ebuild",package).group(1))}
		if re.search("DESCRIPTION=\".+\"",ebuild_info):
			x=re.search("DESCRIPTION=\"(?P<x>.+)\"",ebuild_info).group("x")
			to_app.update({"Description: ":x})
		if re.search("HOMEPAGE=\".+\"",ebuild_info):
			x=re.search("HOMEPAGE=\"(?P<x>.+)\"",ebuild_info).group("x")
			to_app.update({"Homepage: ":x})
		if re.search("LICENSE=\".+\"",ebuild_info):
			x=re.search("LICENSE=\"(?P<x>.+)\"",ebuild_info).group("x")
			to_app.update({"License: ":x})
		if re.search("KEYWORDS=\".+\"",ebuild_info):
			x=re.search("KEYWORDS=\"(?P<x>.+)\"",ebuild_info).group("x")
			to_app.update({"Keywords: ":x})
		if re.search("IUSE=\".+\"",ebuild_info):
			x=re.search("IUSE=\"(?P<x>.+)\"",ebuild_info).group("x")
			to_app.update({"IUSE: ":x})
		to_return.append(to_app)
	return to_return