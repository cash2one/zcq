<html>
<head>
    <title>号码注册记录</title>
    <style type="text/css">
    table, td {border:1px solid #000;}
    </style>
    <script type="text/javascript">
    </script>
</head>
<body>
%if user == 'admin':
    <div>
    下面是所有QQ号码记录(<strong>注：除了QQ号码之外，其他项均可能发生改变</strong>)：
    </div>
    <table>
    <thead>
    <tr><td>QQ</td><td>密码</td><td>昵称</td><td>电话</td><td>地区</td><td>生日</td><td>性别</td></tr>
    </thead>
    <tbody>
    % for item in uin:
        <tr><td>{{item.uin}}</td><td>{{item.password}}</td><td>{{item.nick}}</td><td>{{item.phone}}</td><td>{{item.country}}-{{item.province}}-{{item.city}}</td><td>{{item.birth}}</td><td>{{'男' if item.gender == 1 else '女'}}</td></tr>
    % end
    </tbody>
    </table>
%else:
    <div>非 admin 用户无法查看</div>
%end
</body>
</html>


