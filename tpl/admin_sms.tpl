<html>
<head>
    <title>短信记录</title>
    <style type="text/css">
    table, td {border:1px solid #000;}
    </style>
    <script type="text/javascript">
    </script>
</head>
<body>
%if user == 'admin':
    <div>
    下面是所有短信记录：
    </div>
    <table>
    <thead>
    <tr><td>用户</td><td>日期</td><td>发信人</td><td>收信人</td><td>短信内容</td></tr>
    </thead>
    <tbody>
    % for item in sms:
        <tr><td>{{item.uname}}</td><td>{{item.rtime}}</td><td>{{item.sfrom}}</td><td>{{item.sto}}</td><td>{{item.text}}</td></tr>
    % end
    </tbody>
    </table>
%else:
    <div>非 admin 用户无法查看</div>
%end
</body>
</html>

