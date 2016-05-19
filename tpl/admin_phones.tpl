<html>
<head>
    <title>用户电话号码</title>
    <style type="text/css">
    table, td {border:1px solid #000;}
    </style>
    <script type="text/javascript">
    </script>
</head>
<body>
%if user == 'admin':
    <div>
    下面是已经存在的所有电话：
    </div>
    <table>
    <thead>
    <tr><td>号码</td><td>用户</td><td>增加日期</td><td>更新日期</td><td>状态</td><td>总数</td></tr>
    </thead>
    <tbody>
    % for item in phones:
        <tr><td>{{item.phone}}</td><td>{{item.uname}}</td><td>{{item.adate}}</td><td>{{item.udate}}</td><td>{{item.status}}</td><td>{{item.total}}</td></tr>
    % end
    </tbody>
    </table>
%else:
    <div>非 admin 用户无法查看</div>
%end
</body>
</html>

