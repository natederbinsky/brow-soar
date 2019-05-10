from flask import Flask, request, url_for
app = Flask(__name__)

import html
import json

###############################
###############################

import sys
from os import environ as env

sys.path.append(env['SOAR_HOME'])
import Python_sml_ClientInterface as sml

kernel = sml.Kernel_CreateKernelInCurrentThread(True, 0)


prints = {}

def callback_print_message(mid, user_data, agent, message):
	global prints
	prints[user_data].append(message.strip())

###############################
###############################

SITE_TITLE = 'Soar'

def _out(l):
	return "\n".join(l)

def _header(ret, title):
	ret.append('<!doctype html>')
	ret.append('<html lang="en">')
	ret.append('<head>')
	ret.append('<!-- Required meta tags -->')
	ret.append('<meta charset="utf-8">')
	ret.append('<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">')
	ret.append('<link href="{}" rel="stylesheet">'.format(url_for('static', filename="bootstrap.min.css")))
	ret.append('<title>{} - {}</title>'.format(html.escape(SITE_TITLE), html.escape(title)))

	ret.append('<link rel="apple-touch-icon" sizes="57x57" href="{}">'.format(url_for('static', filename="apple-icon-57x57.png")))
	ret.append('<link rel="apple-touch-icon" sizes="60x60" href="{}">'.format(url_for('static', filename="apple-icon-60x60.png")))
	ret.append('<link rel="apple-touch-icon" sizes="72x72" href="{}">'.format(url_for('static', filename="apple-icon-72x72.png")))
	ret.append('<link rel="apple-touch-icon" sizes="76x76" href="{}">'.format(url_for('static', filename="apple-icon-76x76.png")))
	ret.append('<link rel="apple-touch-icon" sizes="114x114" href="{}">'.format(url_for('static', filename="apple-icon-114x114.png")))
	ret.append('<link rel="apple-touch-icon" sizes="120x120" href="{}">'.format(url_for('static', filename="apple-icon-120x120.png")))
	ret.append('<link rel="apple-touch-icon" sizes="144x144" href="{}">'.format(url_for('static', filename="apple-icon-144x144.png")))
	ret.append('<link rel="apple-touch-icon" sizes="152x152" href="{}">'.format(url_for('static', filename="apple-icon-152x152.png")))
	ret.append('<link rel="apple-touch-icon" sizes="180x180" href="{}">'.format(url_for('static', filename="apple-icon-180x180.png")))
	ret.append('<link rel="icon" type="image/png" sizes="192x192"  href="{}">'.format(url_for('static', filename="android-icon-192x192.png")))
	ret.append('<link rel="icon" type="image/png" sizes="32x32" href="{}">'.format(url_for('static', filename="favicon-32x32.png")))
	ret.append('<link rel="icon" type="image/png" sizes="96x96" href="{}">'.format(url_for('static', filename="favicon-96x96.png")))
	ret.append('<link rel="icon" type="image/png" sizes="16x16" href="{}">'.format(url_for('static', filename="favicon-16x16.png")))
	ret.append('<link rel="manifest" href="{}">'.format(url_for('static', filename="manifest.json")))
	ret.append('<meta name="msapplication-TileColor" content="#ffffff">')
	ret.append('<meta name="msapplication-TileImage" content="{}">'.format(url_for('static', filename="ms-icon-144x144.png")))
	ret.append('<meta name="theme-color" content="#ffffff">')

	ret.append('</head>')
	ret.append('<body>')
	ret.append('<div class="container">')
	ret.append('<h1>{}</h1>'.format(html.escape(title)))

def _footer(ret, js=[]):
	ret.append('</div>')
	ret.append('<script src="{}"></script>'.format(url_for('static', filename='jquery-3.3.1.min.js')))
	ret.append('<script src="{}"></script>'.format(url_for('static', filename='popper.min.js')))
	ret.append('<script src="{}"></script>'.format(url_for('static', filename='bootstrap.min.js')))
	ret.append('<script>')
	ret.append(_out(js))
	ret.append('</script>')
	ret.append('</body>')
	ret.append('</html>')

def _has_needed_post(l):
	for n in l:
		if n not in request.form:
			return False
	return True

def _has_needed_get(l):
	for n in l:
		if n not in request.args:
			return False
	return True

###############################
###############################

@app.route("/", methods=['POST', 'GET'])
def hello():
	global kernel

	doc = []
	js = []
	_header(doc, 'Home')

	doc.append('<hr />')

	doc.append('<div class="row" style="margin-bottom: 10px">')
	doc.append('<div class="col">')

	doc.append('<h2>New Agent</h2>')

	doc.append('<form id="fA">')
	doc.append('<div class="form-row">')
	doc.append('<div class="col-9"><input type="text" class="form-control" id="newName" value="" placeholder="Enter agent name" /></div>')
	doc.append('<div class="col"><input type="submit" class="btn btn-primary" id="create" value="create" /></div>')
	doc.append('</div>')
	doc.append('</form>')

	doc.append('</div>')
	doc.append('</div>')

	#

	doc.append('<div class="row">')
	doc.append('<div class="col">')

	doc.append('<h2>Existing Agents</h2>')
	doc.append('<div id="agents" class="card-columns">')
	doc.append('</div>')

	doc.append('</div>')
	doc.append('</div>')

	#

	doc.append('</div>')

	##

	js.append('function refreshList() {')
	js.append('var agentList = $("#agents");')
	js.append('agentList.empty();')
	js.append('$.ajax({ url:"/agents", type: "GET", dataType: "json", data:{}, success:function(data) { ')
	js.append('for (i=0; i<data.length; i++) {')
	js.append('agentList.append($("<div></div>", {"class":"card"}).append($("<div></div>", {"class":"card-body"}).append([$("<h5></h5>", {"class":"card-title"}).text(data[i]), $("<a></a>", {"class":"btn btn-primary", "href":"/debug?agent="+data[i], "target":"_blank"}).text("debug"), $("<span></span>").text("   "), $("<button></button>", {"class":"btn btn-danger", "onclick":"removeAgent(\'" + data[i] + "\');"}).text("remove")])));')
	js.append('}')
	js.append('}});')
	js.append('}')

	js.append('function removeAgent(name) {')
	js.append('$.ajax({ url:"/remove", type: "POST", dataType: "json", data:{ "name":name }, success:function(data) { ')
	js.append('refreshList();')
	js.append('}});')
	js.append('}')

	js.append('$(document).ready (function() {')

	js.append('$("#fA").submit(function(event) {')
	js.append('event.preventDefault();')
	js.append('var c = $("#newName")[0].value;')
	js.append('if ($.trim(c).length > 0)')
	js.append('$.ajax({ url:"/create", type: "POST", dataType: "json", data:{ "name":c }, success:function(data) { ')
	js.append('if (data.result) {')
	js.append('$("#newName")[0].value="";')
	js.append('refreshList();')
	js.append('} else {')
	js.append('alert("Error creating agent!")')
	js.append('}')
	js.append('}});')
	js.append('});')

	js.append('refreshList();')

	js.append('});')

	_footer(doc, js)

	return _out(doc)

@app.route("/create", methods=['POST'])
def create():
	global kernel
	global prints

	ret = { "result":False }
	if _has_needed_post(["name"]):
		ret["result"] = (kernel.CreateAgent(request.form["name"]) is not None)
		if ret["result"]:
			prints[request.form["name"]] = []
			kernel.GetAgent(request.form["name"]).RegisterForPrintEvent(sml.smlEVENT_PRINT, callback_print_message, request.form["name"])

	return json.dumps(ret)

@app.route("/remove", methods=['POST'])
def remove():
	global kernel
	global prints

	ret = { "result":False }
	if _has_needed_post(["name"]):
		ret["result"] = kernel.DestroyAgent(kernel.GetAgent(request.form["name"]))
		if ret["result"]:
			prints.pop(request.form["name"])

	return json.dumps(ret)


@app.route("/agents", methods=['GET'])
def agents():
	global kernel

	ret = []
	for i in range(kernel.GetNumberAgents()):
		ret.append(kernel.GetAgentByIndex(i).GetAgentName())

	return json.dumps(ret)

@app.route("/debug", methods=['GET'])
def debug():
	global kernel

	agent_name = request.args['agent']
	agent = kernel.GetAgent(agent_name)

	doc = []
	js = []
	_header(doc, agent.GetAgentName())

	doc.append('<div class="row">')

	##

	doc.append('<div class="col-6">')

	doc.append('<div style="margin-bottom: 1rem"><form id="f1">')
	doc.append('<div class="form-row">')
	doc.append('<div class="col-9"><input type="text" class="form-control" id="cmd" value="" placeholder="Enter command" /></div>')
	doc.append('<div class="col"><input type="submit" class="btn btn-primary" id="go" value="Go!" /></div>')
	doc.append('<div class="col"><input type="button" class="btn btn-secondary" id="clear" value="Clear" /></div>')
	doc.append('</div>')
	doc.append('</form></div>')
	doc.append('<ul id="things" class="list-group">')
	doc.append('</ul>')
	doc.append('</div>')

	##

	doc.append('<div class="col-6">')

	doc.append('<ul class="nav nav-tabs" id="myTab" role="tablist" style="margin-bottom: 1rem">')
	doc.append('<li class="nav-item"><a class="nav-link active" id="stack-tab" data-toggle="tab" href="#stack" role="tab" aria-controls="stack" aria-selected="true">State Stack</a></li>')
	doc.append('<li class="nav-item"><a class="nav-link" id="state-tab" data-toggle="tab" href="#state" role="tab" aria-controls="state" aria-selected="false">State</a></li>')
	doc.append('<li class="nav-item"><a class="nav-link" id="source-tab" data-toggle="tab" href="#source" role="tab" aria-controls="source" aria-selected="false">Source File</a></li>')
	doc.append('</ul>')

	#####

	doc.append('<div class="tab-content" id="myTabContent">')

	doc.append('<div class="tab-pane show active" id="stack" role="tabpanel" aria-labelledby="stack-tab">')
	doc.append('<ul id="stackContent" class="list-group">')
	doc.append('</ul>')
	doc.append('</div>')

	doc.append('<div class="tab-pane" id="state" role="tabpanel" aria-labelledby="state-tab">')
	doc.append('<ul id="stateContent" class="list-group">')
	doc.append('</ul>')
	doc.append('</div>')

	doc.append('<div class="tab-pane" id="source" role="tabpanel" aria-labelledby="source-tab">')
	doc.append('<form id="f2">')
	doc.append('<div class="form-group">')
	doc.append('<label for="sourceFile">Upload Agent file</label>')
	doc.append('<input type="file" class="form-control-file" id="sourceFile">')
	doc.append('</div>')
	doc.append('<input type="submit" class="btn btn-primary" id="go" value="Upload" />')
	doc.append('</form>')
	doc.append('</div>')

	#####

	doc.append('</div>')

	##

	doc.append('</div>')


	js.append('var refreshList = [')
	js.append('["stackContent", "p --stack"],')
	js.append('["stateContent", "p -d 2 <s>"],')
	js.append('];')

	js.append('function refresh() {')
	js.append('for (var i=0; i<refreshList.length; i++) {')
	js.append('var r = refreshList[i];')
	js.append('var x = $("#" + r[0]);')
	js.append('$.ajax({ url:"/do", type: "POST", dataType: "json", data:{ "cmd":r[1], "tag":i, "agent":"' + agent_name + '" }, success:function(data) { ')
	js.append('var r2 = refreshList[parseInt(data.tag)];')
	js.append('var x2 = $("#" + r2[0]);')
	js.append('x2.empty();')
	js.append('x2.append($("<li></li>", { "class":"list-group-item" }).append($("<code></code>").text(r2[1]), $("<pre></pre>").text(data.result)));')
	js.append('}});')
	js.append('}')
	js.append('}')

	js.append('$(document).ready (function() {')

	js.append('$("#clear").click(function(event) {')
	js.append('$("#things").empty();')
	js.append('});')

	js.append('$("#f1").submit(function(event) {')
	js.append('event.preventDefault();')
	js.append('var c = $("#cmd")[0].value;')
	js.append('if ($.trim(c).length > 0)')
	js.append('$.ajax({ url:"/do", type: "POST", dataType: "json", data:{ "cmd":c, "print":"Y", "agent":"' + agent_name + '" }, success:function(data) { ')
	js.append('$("#things").prepend($("<li></li>", { "class":"list-group-item" }).append($("<code></code>").text(c), $("<pre></pre>").text(data.print), $("<pre></pre>").text(data.result)));')
	js.append('refresh();')
	js.append('}});')
	js.append('$("#cmd")[0].value = "";')
	js.append('$("#cmd")[0].focus();')
	js.append('});')

	js.append('$("#f2").submit(function(event) {')
	js.append('event.preventDefault();')
	js.append('var file = $("#sourceFile")[0].files[0];')
	js.append('var reader = new FileReader();')
	js.append('reader.onload = function (event) {')
	js.append('$.ajax({ url:"/do", type: "POST", dataType: "json", data:{ "cmd":event.target.result, "print":"Y", "agent":"' + agent_name + '" }, success:function(data) { ')
	js.append('$("#things").prepend($("<li></li>", { "class":"list-group-item" }).append($("<code></code>").text("source " + $("#sourceFile")[0].files[0].name), $("<pre></pre>").text(data.print), $("<pre></pre>").text(data.result)));')
	js.append('$("#sourceFile")[0].value=null;')
	js.append('}});')
	js.append('};')
	js.append('reader.readAsText(file);')
	js.append('});')

	js.append('refresh();')

	js.append('});')

	_footer(doc, js)

	return _out(doc)

@app.route("/do", methods=['POST'])
def do():
	global kernel
	global prints

	agent_name = request.form['agent']
	agent = kernel.GetAgent(agent_name)

	ret = { "result":"", "print":"", "tag":"" }
	if _has_needed_post(["cmd"]):
		ret["result"] = agent.ExecuteCommandLine(request.form["cmd"])

	if _has_needed_post(["print"]):
		ret["print"] = _out(prints[agent_name])
		prints[agent_name].clear()

	if _has_needed_post(["tag"]):
		ret["tag"] = request.form["tag"]

	return json.dumps(ret)

if __name__ == '__main__':
	app.run()
