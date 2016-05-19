<html>
<head>
    <title>用户管理</title>
    <style type="text/css">
    table, td {border:1px solid #000;}
    .adduser {
    margin-top: 10px;
    }
    </style>
    <script type="text/javascript">
    function $(id) {
        return document.getElementById(id);
    }
    function addUser() {
        // TODO do some check
        var uname = $('uname').value;
        var upass = $('upass').value;
        $('adduser_form').submit();
    }
    function addDev() {
        // TODO do some check
        var dname = $('dname').value;
        $('adddev_form').submit();
    }
    </script>
</head>
<body>
%if user == 'admin':
    <div>
    下面是已经存在的所有用户：
    </div>
    <table>
    <thead>
    <tr><td>代号</td><td>密码</td><td>总数</td></tr>
    </thead>
    <tbody>
    % for item in users:
        <tr><td>{{item.name}}</td><td>{{item.password}}</td><td>{{item.total}}</td></tr>
    % end
    </tbody>
    </table>
    <div class="adduser">
    增加用户：
    <form action="/adduser" method="POST" name="adduser_form" id="adduser_form">
    <table>
    <tr><td>用户代号</td> <td><input type="text" name="uname" id="uname" size="20"> </td></tr>
    <tr> <td>密码（可为空）</td><td><input type="text" name="upass" id="upass" size="20"> </td></tr>
    <tr><td>&nbsp;</td></td><td><input type="button" value="增加用户" id="adduser" name="adduser" onclick="javascript:addUser();" /></td></tr>
    </table>
    </form>
    </div>
    <div>
    <a href="/admin/phones">显示电话号码 </a> <br />
    <a href="/logout">退出登录 </a>
    </div>
    <div>
    下面是已经存在的所有机器（设备）：
    </div>
    <table>
    <thead>
    <tr><td>名称</td><td>IP</td><td>UUID</td><td>状态</td></tr>
    </thead>
    <tbody>
    % for item in devs:
        <tr><td>{{item.dname}}</td><td>{{item.ip}}</td><td>{{item.duuid}}</td><td>{{item.status}}</td></tr>
    % end
    </tbody>
    </table>
    <div class="adduser">
    <form action="/adddev" method="POST" name="adddev_form" id="adddev_form">
    <table>
    <tr><td>机器（设备）名称</td><td><input type="text" name="dname" id="dname" size="20" maxlength="20" /></td></tr>
    <tr><td>密码</td><td><input type="text" name="dname" id="dpass" size="20" maxlength="64" /></td></tr>
    <tr><td>&nbsp;</td><td><input type="button" value="增加机器" id="adddev" name="adddev" onclick="javascript:addDev();" /></td></tr>
    </table>
    </form>
    </div>
%else:
    <div>非 admin 用户无法查看</div>
%end
</body>
</html>

